# API Contracts (Phase 1)

## Public API — Spring Boot (`/api`)

| Method | Path | Status | Description |
| --- | --- | --- | --- |
| `GET` | `/api/health` | Implemented | Platform backend health check |
| `POST` | `/api/auth/register` | Implemented | Create account, returns JWT |
| `POST` | `/api/auth/login` | Implemented | Login, returns JWT |
| `POST` | `/api/analysis` | Implemented | Submit health note (JWT required), persists result |
| `GET` | `/api/analysis` | Implemented | List current user's analysis history |
| `GET` | `/api/analysis/{id}` | Implemented | Analysis detail for current user |
| `DELETE` | `/api/analysis` | Implemented | Clear current user's analysis history |

## Internal API — FastAPI AI Service

Called by the backend (not directly by browsers in the target architecture).

| Method | Path | Status | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | Implemented | AI service health |
| `GET` | `/version` | Implemented | Runtime metadata |
| `POST` | `/analyse` | Implemented | Run analysis pipeline (`mode`: `mock` or `ai`) |
| `GET` | `/evaluation/cases` | Implemented | List evaluation scenarios |
| `POST` | `/evaluation/run` | Implemented | Run safety & quality evaluation |

### `POST /analyse` request

```json
{
  "text": "My heart rate is 100 and I cannot sleep.",
  "language": "en",
  "mode": "mock"
}
```

`language`: `"en"` or `"zh"`. `mode`: `"mock"` (rules adjudicate) or `"ai"` (AI adjudicates, rules safety net).

Response includes `structured_input`, `risk_result`, `escalation`, `explanation`, `safety_check`, and provider metadata.

## Error shape (Spring Boot)

```json
{
  "timestamp": "2026-05-30T12:00:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Human-readable message",
  "path": "/api/example"
}
```
