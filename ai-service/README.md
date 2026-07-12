# HealthLens AI Service

Internal FastAPI service for health-text analysis. Called by the Spring Boot backend over HTTP; not exposed as the primary user-facing UI.

## Responsibilities

- `POST /analyse` — run the analysis pipeline (extraction, risk rules, escalation, LLM explanation, safety validation)
- `GET /health`, `GET /version` — operational endpoints
- `GET/POST /evaluation/*` — healthcare safety & quality evaluation suite (development/regression)
- Mock and OpenAI providers via environment variables

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest -v
```

## Legacy static UI

The original vanilla JavaScript frontend lives in `legacy-frontend/`. It is **not** the platform default entry point. To expose it for reference only:

```env
ENABLE_LEGACY_FRONTEND=true
```

Then open `http://localhost:8000/legacy` (static assets under `/legacy/static/`).

## Environment variables

See `.env.example`. Never commit real `OPENAI_API_KEY` values.
