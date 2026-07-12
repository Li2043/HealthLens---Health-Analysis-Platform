# PostgreSQL infrastructure notes

The `postgres` service is defined in the root `docker-compose.yml`.

Default connection (from host):

```text
jdbc:postgresql://localhost:5432/healthlens
```

From Docker network (backend container):

```text
jdbc:postgresql://postgres:5432/healthlens
```

Flyway migrations live in `backend/src/main/resources/db/migration/`.
