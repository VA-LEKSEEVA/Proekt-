```bash
cp .env.example .env
chmod +x scripts/gen-certs.sh && ./scripts/gen-certs.sh
docker compose up -d --build
docker compose ps
curl -k https://localhost/health/deep
```

Открой <https://localhost/> (сертификат self-signed).

## Состав

| Сервис | Роль | Порт |
| --- | --- | --- |
| nginx | Reverse proxy + TLS | 80/443 |
| backend | Python HTTP-сервер | 8080 |
| postgres | БД | 5432 |
| redis | Кэш | 6379 |

## Проверки

```bash
# Сквозной health
curl -k https://localhost/health/deep

# Заголовки от nginx
curl -k https://localhost/ | python -m json.tool

# Rate limit (10 r/s, burst 20)
for i in $(seq 1 60); do
  curl -ks -o /dev/null -w "%{http_code}\n" https://localhost/
done | sort | uniq -c

# Лимит тела 10 MB → 413
head -c 20000000 /dev/zero > /tmp/big.bin
curl -k -X POST --data-binary @/tmp/big.bin https://localhost/ -o /dev/null -w "%{http_code}\n"
```

## Остановка

```bash
docker compose down       # остановить
docker compose down -v    # + удалить данные
```
