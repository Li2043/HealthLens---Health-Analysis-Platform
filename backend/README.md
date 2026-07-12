# HealthLens Platform Backend

Spring Boot business backend for the HealthLens platform.

## Phase 1 scope

- Application bootstrap and configuration
- PostgreSQL + Flyway baseline migration
- `/api/health` endpoint
- `POST /api/analysis` — proxies to AI service and **persists** result to PostgreSQL
- `GET /api/analysis` — list current user's saved analyses
- `GET /api/analysis/{id}` — analysis detail (ownership enforced)
- JWT register/login and protected analysis APIs
- FastAPI client (`AiServiceClient`)

## Local development

Requires Java 21. Maven is bundled via the Maven Wrapper (`mvnw` / `mvnw.cmd`). PostgreSQL must be running (see root `docker-compose.yml`).

```bash
# Windows
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=local

# macOS / Linux
./mvnw spring-boot:run -Dspring-boot.run.profiles=local
```

## Tests

```bash
# Windows
.\mvnw.cmd test

# macOS / Linux
./mvnw test
```

## Try analysis API

```bash
curl -X POST http://localhost:8080/api/analysis \
  -H "Content-Type: application/json" \
  -d '{"text":"My heart rate is 100 and I cannot sleep","language":"en"}'
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `POSTGRES_DB` | `healthlens` | Database name |
| `POSTGRES_USER` | `healthlens` | Database user |
| `POSTGRES_PASSWORD` | `change_me` | Database password |
| `AI_SERVICE_BASE_URL` | `http://localhost:8000` | Internal FastAPI base URL |
| `JWT_SECRET` | dev placeholder | HMAC key for JWT signing — **must** be strong in production |
| `JWT_EXPIRATION_MS` | `86400000` | Token lifetime (24 hours) |
| `SPRING_PROFILES_ACTIVE` | `local` | Use `prod` in production |

Production JWT setup: see [`docs/deployment.md`](../docs/deployment.md).
