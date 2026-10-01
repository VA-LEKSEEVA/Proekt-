import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg2
import redis

PG = dict(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "app"),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    dbname=os.getenv("POSTGRES_DB", "appdb"),
    connect_timeout=3,
)

REDIS = dict(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD") or None,
    socket_connect_timeout=3,
)


class Handler(BaseHTTPRequestHandler):
    server_version = "backend/1.0"

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})

        elif self.path == "/health/deep":
            checks = {}
            ok = True
            try:
                with psycopg2.connect(**PG) as conn, conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    checks["postgres"] = "ok" if cur.fetchone()[0] == 1 else "bad"
            except Exception as e:
                ok = False
                checks["postgres"] = f"error: {e.__class__.__name__}: {e}"

            try:
                r = redis.Redis(**REDIS)
                r.ping()
                r.incr("hits")
                checks["redis"] = "ok"
            except Exception as e:
                ok = False
                checks["redis"] = f"error: {e.__class__.__name__}: {e}"

            self._send(200 if ok else 503,
                       {"status": "ok" if ok else "degraded", "checks": checks})

        elif self.path == "/":
            headers = {k.lower(): v for k, v in self.headers.items()}
            self._send(200, {
                "service": "backend",
                "hostname": socket.gethostname(),
                "client": self.client_address[0],
                "headers": headers,
            })

        else:
            self._send(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"backend listening on :{port}", flush=True)
    srv.serve_forever()