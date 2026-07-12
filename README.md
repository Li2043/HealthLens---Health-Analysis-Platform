# HealthLens Platform — Safe AI Healthcare Consultation

<p align="right">
  <a href="./README.md">English</a> | <a href="./README_CN.md">中文</a>
</p>

**HealthLens Platform** is a full-stack healthcare AI product demo — not just a single API.
It combines a **React** frontend, **Spring Boot** backend, **FastAPI** AI pipeline, and
**PostgreSQL** persistence into one deployable platform for safe, structured health
consultation workflows.

> **Disclaimer:** This is a product-design and engineering prototype. It is **not** a
> medical device, **not** medical advice, and **must not** be used for diagnosis,
> treatment, or clinical decision-making.

---

## Overview

When someone types *"my chest feels tight and I'm short of breath"*, the interaction is
uncertain, anxiety-driven, and safety-critical. A generic chatbot may answer fluently —
and dangerously.

HealthLens routes every health note through a **designed consultation workflow**:
signal extraction → risk adjudication (rules and/or AI) → rule safety net → emergency
escalation → health-focused explanation → safety validation. The LLM explains; in **Mock
mode** rules alone decide risk; in **AI mode** AI adjudicates first and rules may only
**raise** risk, never lower it.

This repository is the **platform edition**: user accounts, JWT-protected APIs, analysis
history (including clear-all), bilingual UI (English / 中文), **Mock / AI** analysis mode,
and Docker Compose for local full-stack runs.

**Product & design documentation** (AI pipeline rationale)

| Document | What it covers |
| --- | --- |
| [`ai-service/docs/AI_HEALTH_PRD.md`](./ai-service/docs/AI_HEALTH_PRD.md) | Product requirements |
| [`ai-service/docs/CONSULTATION_WORKFLOW.md`](./ai-service/docs/CONSULTATION_WORKFLOW.md) | Staged workflow design |
| [`ai-service/docs/TRIAGE_POLICY.md`](./ai-service/docs/TRIAGE_POLICY.md) | Four-tier triage framework |
| [`ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md`](./ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md) | Five-layer safety strategy |
| [`ai-service/docs/HEALTHCARE_EVALUATION.md`](./ai-service/docs/HEALTHCARE_EVALUATION.md) | Safety & quality evaluation suite |

**Platform engineering docs**

| Document | What it covers |
| --- | --- |
| [`docs/architecture.md`](./docs/architecture.md) | Multi-service architecture |
| [`docs/api-contracts.md`](./docs/api-contracts.md) | REST API contracts |
| [`docs/development.md`](./docs/development.md) | Local development guide |
| [`docs/deployment.md`](./docs/deployment.md) | Production JWT & deployment notes |

---

## Key Features

| Feature | Description |
| --- | --- |
| **Mock / AI modes** | **AI** (default): OpenAI extraction + risk + explanation when `OPENAI_API_KEY` is set; rules safety net. **Mock**: offline rules + templates; switch shows a warning dialog |
| **Structured AI pipeline** | Extraction → risk adjudication → escalation → explanation → safety validation |
| **Emergency override** | Red-flag symptoms (chest pain, stroke signs, etc.) elevate triage even when vitals risk is low |
| **Health-focused explanations** | Risk-tier guidance: reassurance/self-care (low), causes + steps (moderate), emergency numbers + first aid (high/emergency) |
| **JWT authentication** | Register, login, protected analysis endpoints |
| **Analysis history** | Persist, browse, and **clear all** past consultations per user |
| **Bilingual UI** | Header **English / 中文** and **AI / Mock** pill toggles; API `language` syncs with UI |
| **Bilingual extraction** | English and Chinese heart rate / blood pressure patterns (e.g. `heart rate 200` and `心率200`) |
| **Docker Compose** | One command to run frontend, backend, AI service, and Postgres; frontend source volume for dev |

---

## What the platform can assess

> **Not diagnosis.** The system performs **risk triage and safety messaging** on free-text
> health notes — not clinical diagnosis.

| Category | Examples | How it is used |
| --- | --- | --- |
| **Heart rate** | `heart rate 100`, `心率200` | Threshold flags (>100 moderate, >120 high) |
| **Blood pressure** | `BP 150/95`, `血压200` | Elevated / very high systolic or diastolic |
| **Mood** | anxious, stressed, 焦虑, 心情低落 | Anxiety/stress or low-mood flags |
| **Sleep** | can't sleep, 睡不着, insomnia | Poor sleep flag |
| **Emergency symptoms** | chest pain, 胸痛, breathing difficulty, stroke signs, bleeding, etc. | Keyword escalation → **Emergency** triage (no vitals required) |
| **Free-text symptoms** | “chest tightness”, “feel unwell” | Better in **AI mode** (OpenAI extractor + risk); Mock uses rules/keywords |

**Not supported today:** blood glucose, temperature, SpO₂, labs, imaging, medications, or
validated clinical protocols.

---

## Mock vs AI mode

| | **AI mode** (default) | **Mock mode** |
| --- | --- | --- |
| **Purpose** | Real analysis with OpenAI when configured | Offline demo, CI, testing |
| **Extraction** | OpenAI → structured fields; regex fallback | Regex / preset samples |
| **Risk** | AI adjudicates → rules safety net (only elevates) | Rules only |
| **Explanation** | GPT health summary + template action steps | Template “What this may mean” text |
| **Provider badge** | `openai` or `mock-ai` (no key) | `mock` |
| **Switching** | AI → Mock shows a **confirmation dialog** (inaccurate, testing only) |

Configure OpenAI (Docker):

```powershell
# In healthlens-platform/.env (never .env.example)
OPENAI_API_KEY=sk-...

docker compose up -d --build ai-service
```

---

## Screenshots & Demo Walkthrough

> Add images under [`docs/images/`](./docs/images/). See
> [`docs/images/README.md`](./docs/images/README.md) for filenames and capture notes.

### Architecture

![Platform architecture](./docs/images/01-architecture.png)

> **📷 Image placeholder:** `docs/images/01-architecture.png` — Four-service stack
> (React → Spring Boot → FastAPI → PostgreSQL) or an annotated architecture diagram.

### Login & Register

![Login page](./docs/images/02-login-en.png)

> **📷 Image placeholder:** `docs/images/02-login-en.png` — Login page in English; language
> toggle only in the header toolbar.

![Register page](./docs/images/03-register-zh.png)

> **📷 Image placeholder:** `docs/images/03-register-zh.png` — Register page in Chinese
> (邮箱 / 密码 / 注册).

### Health Analysis

![Analysis input](./docs/images/04-analysis-input.png)

> **📷 Image placeholder:** `docs/images/04-analysis-input.png` — Analysis page with **AI**
> mode selected in header, mode hint, health note textarea, **Use sample**, and **Analyse**.

![Emergency escalation](./docs/images/05-analysis-emergency.png)

> **📷 Image placeholder:** `docs/images/05-analysis-emergency.png` — Emergency input
> (e.g. chest pain + shortness of breath): **Possible emergency**, **Triage: Emergency**,
> Provider / mode badges.

![Analysis result](./docs/images/06-analysis-result.png)

> **📷 Image placeholder:** `docs/images/06-analysis-result.png` — Result panel: triage,
> vitals risk, **What this may mean**, detected signals, safety check **Passed**.

### History

![Analysis history](./docs/images/07-history.png)

> **📷 Image placeholder:** `docs/images/07-history.png` — History list with risk badges,
> timestamps, snippets, and **Clear history**.

![Analysis detail](./docs/images/08-detail.png)

> **📷 Image placeholder:** `docs/images/08-detail.png` — Detail page with original note
> and full analysis result.

### Header toggles (language + analysis mode)

![Header toggles](./docs/images/09-header-toggles.png)

> **📷 Image placeholder:** `docs/images/09-header-toggles.png` — Logged-in header:
> **English / 中文** and **AI / Mock** pill toggles (light cyan track, dark teal thumb,
> white text on active side).

![Mock mode confirmation](./docs/images/10-mock-mode-confirm.png)

> **📷 Image placeholder:** `docs/images/10-mock-mode-confirm.png` — Dialog when switching
> AI → Mock: warns Mock is for testing/offline use; **Stay on AI** / **Switch to Mock**.

![High risk Chinese result](./docs/images/11-analysis-high-risk-zh.png)

> **📷 Image placeholder:** `docs/images/11-analysis-high-risk-zh.png` — Chinese UI,
> high-risk case: explanation includes **120**, emergency steps, Provider `openai` or `mock`.

---

## Healthcare Consultation Workflow

```text
User input (React) — mode: mock | ai (default ai)
   ↓
Spring Boot  POST /api/analysis  (JWT + persist)
   ↓
FastAPI AI service
   ↓
Signal extraction           (regex/mock or OpenAI → structured fields)
   ↓
Rule risk (safety net)      (always computed)
   ↓
Risk adjudication           mock: rules only
                            ai:   AI risk → merge with rules (max level, no downgrade)
   ↓
Emergency escalation        (red-flag keywords → may force Emergency triage + risk)
   ↓
Explanation               (GPT summary in AI mode + risk-tier action templates)
   ↓
Safety validation         (disclaimer, no diagnosis/dosing — en + zh)
   ↓
Saved to PostgreSQL + returned to UI
```

**Key design choice:** In **AI mode**, AI adjudicates risk first; the **rule engine is a
safety net** that may only elevate risk. In **Mock mode**, rules alone decide risk.
Symptom-only emergencies are caught by the **escalation detector**
(`ai-service/app/escalation.py`), which can override low vitals-based risk. See
[`ai-service/docs/TRIAGE_POLICY.md`](./ai-service/docs/TRIAGE_POLICY.md).

---

## Architecture

```text
React + TypeScript (frontend :5173)
        |
        | REST  /api/*  (JWT on protected routes)
        v
Spring Boot (backend :8080)
        |
        | Internal HTTP  /analyse
        v
FastAPI AI Service (:8000)
        |
        v
PostgreSQL (:5432)   users + analysis history (Flyway migrations)
```

| Layer | Technology | Status |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | Login, register, analyse, history, i18n, Mock/AI toggle |
| Backend | Spring Boot 3 + Java 21 | JWT auth, analysis orchestration, persistence |
| AI service | FastAPI + Pydantic | Full analysis pipeline + evaluation suite |
| Database | PostgreSQL + Flyway | Users (`V2`), analyses (`V3`) |
| Infra | Docker Compose, GitHub Actions | Local stack + CI |

### Repository layout

```text
healthlens-platform/
├── frontend/          React SPA
├── backend/           Spring Boot API
├── ai-service/        FastAPI internal AI analysis service
├── docs/              Platform architecture, API, deployment
├── infra/             Postgres / nginx notes
├── docker-compose.yml Local multi-service stack
├── Makefile           Common commands (Unix)
└── .env.example       Environment template
```

---

## Quick Start

### Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up -d --build
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Then open **http://localhost:5173** → Register → ensure **AI** mode in header → run an analysis.

After changing frontend code locally, refresh the browser (`Ctrl+Shift+R`). The Compose file
mounts `./frontend` into the container for live updates.

### Service URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend health | http://localhost:8080/api/health |
| AI service | http://localhost:8000/health |
| AI OpenAPI | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### Typical user flow

1. **Register** or **Login** at `/register` or `/login`
2. In the header: toggle **English / 中文**; keep **AI** mode (or switch to Mock — confirm dialog)
3. Go to **Analyse**, enter a health note (or use sample text)
4. Review triage, vitals risk, **What this may mean**, provider badge, and safety check
5. Open **History** to browse saved results, view details, or **Clear history**

Individual service setup: [`docs/development.md`](./docs/development.md).

---

## API Overview

### Public API — Spring Boot (`/api`)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/health` | — | Backend health check |
| `POST` | `/api/auth/register` | — | Create account, returns JWT |
| `POST` | `/api/auth/login` | — | Login, returns JWT |
| `POST` | `/api/analysis` | JWT | Submit health note, persist result |
| `GET` | `/api/analysis` | JWT | List current user's history |
| `GET` | `/api/analysis/{id}` | JWT | Analysis detail |
| `DELETE` | `/api/analysis` | JWT | Clear all analyses for current user |

```http
POST /api/analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "I have chest pain and shortness of breath.",
  "language": "en",
  "mode": "ai"
}
```

`language`: `"en"` or `"zh"` (synced with UI). `mode`: `"mock"` or `"ai"` (default **`ai`**;
synced with header **AI / Mock** toggle).

### Internal API — FastAPI (backend → ai-service)

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/analyse` | Run the consultation workflow |
| `POST` | `/evaluation/run?provider=mock` | Run safety & quality evaluation suite |

Full contracts: [`docs/api-contracts.md`](./docs/api-contracts.md).

---

## Running Tests

```bash
# All (Make, Unix)
make test

# AI service
cd ai-service && pip install -r requirements.txt && pytest -v

# Backend
cd backend && ./mvnw test        # Windows: .\mvnw.cmd test

# Frontend build + typecheck
cd frontend && npm ci && npm run build
```

Evaluation suite (mock, no API key):

```bash
curl -X POST "http://127.0.0.1:8000/evaluation/run?provider=mock"
```

---

## Environment Variables

Copy `.env.example` to `.env`. Key variables:

| Variable | Purpose |
| --- | --- |
| `POSTGRES_*` | Database credentials |
| `AI_SERVICE_BASE_URL` | Backend → FastAPI (`http://ai-service:8000` in Docker) |
| `VITE_API_BASE_URL` | Frontend → backend (`/api` in Docker; Vite proxies to backend) |
| `JWT_SECRET` | Token signing (**required** in production) |
| `JWT_EXPIRATION_MS` | Token lifetime (default 24h) |
| `OPENAI_API_KEY` | **AI mode** — set in `.env` only (never commit); injects into ai-service |
| `LLM_PROVIDER` / `EXTRACTOR_PROVIDER` | Default `mock`; AI mode prefers OpenAI when key is set |
| `ENABLE_LEGACY_FRONTEND` | Expose old static UI at `/legacy` on AI service |

**OpenAI setup:** copy `.env.example` → `.env`, paste key, then
`docker compose up -d --build ai-service`. Without a key, AI mode runs as **`mock-ai`**
(simulated AI risk + template explanation).

Never commit real secrets. Production JWT setup:
[`docs/deployment.md`](./docs/deployment.md).

---

## Safety Strategy (summary)

Five layers — full detail in
[`ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md`](./ai-service/docs/MEDICAL_AI_SAFETY_POLICY.md):

1. Medical scope detection
2. Unsafe advice prevention (no diagnosis / dosing)
3. Risk-aware response design
4. Emergency escalation (overrides vitals-centric risk)
5. Human referral for high-risk cases

Guiding principle: **asymmetric caution** — when uncertain, escalate rather than reassure.

---

## Limitations

- **Not clinical.** Thresholds and red-flag patterns are illustrative, not validated protocols.
- **Vitals-centric rule engine.** Symptom emergencies rely on keyword escalation; novel phrasing may be missed in Mock mode.
- **Mock mode accuracy.** Regex extraction and rule-only risk are for demo/CI — use **AI mode** for real notes.
- **Prototype auth.** Suitable for demo; production needs hardened secrets, HTTPS, rate limits.
- **OpenAI dependency.** AI mode needs a valid key and network; failures fall back to `mock-ai` or error responses.

---

## Roadmap

- [ ] Production deployment (nginx + frontend build + hardened secrets)
- [x] Mock / AI dual mode with rule safety net
- [x] Bilingual explanations and safety disclaimer (en / zh)
- [x] Analysis history clear-all
- [ ] Expand red-flag coverage and escalation metrics
- [ ] Multi-turn clarifying questions
- [ ] Clinician review workflow for thresholds and red-flag sets
- [ ] Additional vitals (e.g. temperature, SpO₂) and symptom extractors
- [ ] Remove dependency on legacy static frontend

---

## License

Portfolio / demonstration use only. Not for clinical use.
