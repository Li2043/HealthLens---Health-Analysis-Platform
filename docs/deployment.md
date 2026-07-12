# Production deployment

## JWT secret (required)

The backend signs login tokens with **HS256**. You must set a strong, unique `JWT_SECRET` in every non-local deployment.

### Generate a secret

**Windows (PowerShell):**

```powershell
cd healthlens-platform
.\scripts\generate-jwt-secret.ps1
```

**macOS / Linux:**

```bash
cd healthlens-platform
chmod +x scripts/generate-jwt-secret.sh
./scripts/generate-jwt-secret.sh
```

Example output:

```env
JWT_SECRET=7kJm9xQ2vL8nR4wY1zA6bC3dE0fG5hI8jK2lM4nP6qS9tU1vW3xY5zA7bC9dE=
```

### Configure deployment

1. Copy `.env.example` to `.env` on the server.
2. Paste the generated value:

```env
JWT_SECRET=<your-64-char-base64-secret>
JWT_EXPIRATION_MS=86400000
SPRING_PROFILES_ACTIVE=prod
POSTGRES_PASSWORD=<strong-db-password>
```

3. Never commit `.env` to git.
4. Rotate `JWT_SECRET` if it may have leaked (all existing tokens will become invalid).

### How the backend enforces this

| Environment | `SPRING_PROFILES_ACTIVE` | Weak / placeholder `JWT_SECRET` |
| --- | --- | --- |
| Local dev | `local` (default) | Allowed with **warning** in logs |
| Production | `prod` | **Startup fails** — app will not run |

Rules checked at startup:

- At least **32 characters**
- Not a known placeholder (e.g. `change-me-...`)
- In `prod` profile, `JWT_SECRET` must be set explicitly (no default in `application-prod.yml`)

### Docker Compose (production)

```bash
# .env on server must include JWT_SECRET and SPRING_PROFILES_ACTIVE=prod
docker compose up -d --build
```

`docker-compose.yml` reads `JWT_SECRET` from `.env`. Do not rely on the development default in production.

### Cloud / CI secrets

Store `JWT_SECRET` in your platform's secret manager:

| Platform | Where to set |
| --- | --- |
| GitHub Actions | Repository / environment secrets |
| Docker Swarm | `docker secret` |
| Kubernetes | `Secret` manifest or external secrets operator |
| Railway / Render / Fly.io | Environment variables UI |

Map the secret to the backend container environment variable `JWT_SECRET`.

## Related variables

| Variable | Purpose |
| --- | --- |
| `JWT_SECRET` | HMAC signing key for JWT |
| `JWT_EXPIRATION_MS` | Token lifetime (default 24h = `86400000`) |
| `SPRING_PROFILES_ACTIVE` | Use `prod` in production |
| `POSTGRES_PASSWORD` | Database password (also change from default) |
