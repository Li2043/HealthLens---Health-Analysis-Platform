# Development Guide

## Prerequisites

- Docker & Docker Compose (recommended for full stack)
- Java 21 + Maven (backend)
- Node.js 20+ (frontend)
- Python 3.12+ (ai-service)

## Quick start with Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

Windows (without Make):

```powershell
docker compose up -d --build
```

## Service URLs (local)

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8080/api |
| AI service | http://localhost:8000 |
| AI docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Run services individually

### AI service

```bash
cd ai-service
python -m venv .venv
# activate venv, then:
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest -v
```

### Backend

```bash
cd backend
./mvnw spring-boot:run -Dspring-boot.run.profiles=local
./mvnw test
```

Requires PostgreSQL (start via `docker compose up postgres -d`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
npm run build
```

## Makefile targets

| Target | Action |
| --- | --- |
| `make up` | Build and start all services |
| `make down` | Stop services |
| `make build` | Build images |
| `make logs` | Follow logs |
| `make test` | Run backend + AI tests |
| `make test-backend` | Maven test |
| `make test-ai` | pytest |
| `make install-frontend` | npm install |

## Phase 1 limitations

- No JWT authentication or user registration
- No analysis history persistence in the backend
- Frontend pages are placeholders
- Backend does not yet proxy `/analyse` to the AI service
