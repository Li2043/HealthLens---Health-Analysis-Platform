# HealthLens Platform — Safe AI Healthcare Consultation

<p align="right">
  <a href="./README.md">English</a> | <a href="./README_CN.md">中文</a>
</p>

> **Live demo:** **[https://healthlens-ai.co.uk](https://healthlens-ai.co.uk)**
> &nbsp;·&nbsp; 🎬 **Video walkthrough:** [YouTube](https://youtu.be/your-video-id) · [Bilibili](https://www.bilibili.com/video/your-video-id)
>
> Try it instantly with the built-in demo account: **`demo@healthlens.demo` / `demo1234`** (20 analyses/day).

**HealthLens Platform** is a full-stack healthcare-AI product — not just a single API.
It combines a **React + TypeScript** frontend, a **Spring Boot (Java 21)** backend, a
**FastAPI (Python)** AI pipeline, and **PostgreSQL** persistence into one deployable
platform for safe, structured health-consultation workflows. It is deployed to production
behind **Nginx + HTTPS** on a Hong Kong server.

> **Disclaimer:** This is a product-design and engineering prototype. It is **not** a
> medical device, **not** medical advice, and **must not** be used for diagnosis,
> treatment, or clinical decision-making.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack-at-a-glance)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Healthcare Consultation Workflow](#healthcare-consultation-workflow)
- [Analysis Modes (Mock / OpenAI / DeepSeek)](#analysis-modes-mock--openai--deepseek)
- [Deployment & Networking Notes](#deployment--networking-notes-important)
- [Quick Start](#quick-start)
- [API Overview](#api-overview)
- [Testing & CI](#testing--ci)
- [Environment Variables](#environment-variables)
- [Safety Strategy](#safety-strategy-summary)
- [Limitations & Roadmap](#limitations)

---

## Overview

When someone types *"my chest feels tight and I'm short of breath"*, the interaction is
uncertain, anxiety-driven, and safety-critical. A generic chatbot may answer fluently —
and dangerously.

HealthLens routes every health note through a **designed consultation workflow**:
signal extraction → risk adjudication (rules and/or AI) → rule safety net → emergency
escalation → health-focused explanation → safety validation. The LLM explains; in **Mock
mode** rules alone decide risk; in **AI mode** (OpenAI/DeepSeek) AI adjudicates first and
rules may only **raise** risk, never lower it.

This repository is the **platform edition**: user accounts, JWT-protected APIs, per-user
analysis history (with clear-all), a per-account daily quota, a bilingual UI (English / 中文),
switchable **Mock / OpenAI / DeepSeek** analysis modes, Docker Compose for local full-stack
runs, GitHub Actions CI, and a production deployment.

---

## Tech Stack at a Glance

A single repository demonstrating **full-stack + AI engineering + DevOps** across three languages.

| Layer | Technologies |
| --- | --- |
| **Frontend** | React 19, TypeScript, Vite, React Router, Axios, Context API (auth / i18n / analysis-mode), Vitest, CSS (custom design) |
| **Backend** | Java 21, Spring Boot 3.3, Spring Security, JWT (jjwt), Spring Data JPA / Hibernate, Bean Validation, BCrypt, RestClient, Maven |
| **AI service** | Python 3, FastAPI, Pydantic v2, OpenAI SDK (used for both OpenAI and DeepSeek via Chat Completions), regex-based deterministic extractor, pytest |
| **Database** | PostgreSQL 16, Flyway migrations (versioned schema) |
| **Infrastructure** | Docker & Docker Compose (multi-service), Nginx reverse proxy + HTTPS, GitHub Actions CI, `.env`-based config |
| **Engineering practices** | Layered/hexagonal separation, DTO validation, global exception handling, provider abstraction (Mock/OpenAI/DeepSeek), unit + integration tests, i18n, health checks, secrets isolation |

**Highlights worth calling out in interviews**

- **Polyglot microservice architecture** — a Java orchestration layer calling a Python AI
  service over internal HTTP, with a TypeScript SPA on top.
- **Provider abstraction with safe defaults** — pluggable LLM providers (Mock / OpenAI /
  DeepSeek) selected per request; unknown providers fail loudly instead of silently using a
  paid model.
- **Safety-first AI design** — a rule engine acts as a safety net that can only *raise*
  risk, plus a keyword-based emergency escalator that overrides low vitals risk.
- **Production-grade concerns** — JWT auth, BCrypt hashing, Flyway migrations, per-account
  daily rate limiting, CORS config, global error responses, and HTTPS deployment.

---

## Key Features

| Feature | Description |
| --- | --- |
| **Mock / OpenAI / DeepSeek modes** | Per-request analysis mode selector on the analysis page; **DeepSeek is the production default**. The rule safety net always applies |
| **Structured AI pipeline** | Extraction → rule risk → AI risk adjudication → emergency escalation → explanation → safety validation |
| **Emergency override** | Red-flag symptoms (chest pain, stroke signs, breathing difficulty, bleeding…) elevate triage even when numeric vitals risk is low |
| **Risk-tiered explanations** | Reassurance/self-care (low), likely causes + steps (moderate), emergency numbers + first aid (high/emergency) |
| **JWT authentication** | Register, login, and JWT-protected analysis endpoints; passwords hashed with BCrypt |
| **Per-user analysis history** | Persist, browse, view details, and **clear all** past consultations |
| **Daily quota** | Per-account daily analysis limit (default 10; demo account 20), enforced server-side and surfaced in the UI |
| **Auto-created demo account** | A demo login is provisioned on startup so recruiters can try the product with one click |
| **Bilingual UI + extraction** | English / 中文 UI and API; bilingual vitals patterns (e.g. `heart rate 200` and `心率200`) |
| **Dockerized full stack** | One command runs frontend, backend, AI service, and Postgres; frontend source is volume-mounted for hot reload |
| **CI** | GitHub Actions runs backend, AI-service, and frontend checks |

---

## Architecture

```text
Browser (https://healthlens-ai.co.uk)
        |
        v
Nginx reverse proxy  +  HTTPS/TLS   (Hong Kong server)
        |
        |  serves SPA  &  proxies /api/*
        v
React + TypeScript (frontend :5173 dev / static build in prod)
        |
        | REST  /api/*   (JWT on protected routes)
        v
Spring Boot (backend :8080)   ── JWT auth · validation · quota · persistence
        |
        | Internal HTTP  POST /analyse
        v
FastAPI AI Service (:8000)    ── extraction · risk adjudication · escalation · explanation · safety
        |
        v
PostgreSQL (:5432)            ── users + analysis history (Flyway migrations)
```

![Platform architecture](./docs/images/01-architecture.png)

| Layer | Technology | Responsibilities |
| --- | --- | --- |
| Frontend | React 19 + TypeScript + Vite | Auth pages, analysis UI, history, i18n, mode selector, quota display |
| Backend | Spring Boot 3 + Java 21 | JWT auth, request validation, analysis orchestration, daily quota, persistence |
| AI service | FastAPI + Pydantic | Full analysis pipeline + evaluation suite; provider abstraction |
| Database | PostgreSQL + Flyway | Users (`V2`), analyses (`V3`), versioned migrations |
| Infra | Docker Compose, Nginx, GitHub Actions | Local stack, production reverse proxy + HTTPS, CI |

### Repository layout

```text
healthlens-platform/
├── frontend/          React SPA (TypeScript, Vite)
├── backend/           Spring Boot API (Java 21, Maven)
├── ai-service/        FastAPI internal AI analysis service (Python)
├── docs/              Platform architecture, API contracts, deployment
├── infra/             Postgres / nginx notes
├── docker-compose.yml Local multi-service stack
├── Makefile           Common commands (Unix)
└── .env.example       Environment template
```

---

## Healthcare Consultation Workflow

```text
User input (React) — mode: mock | openai | deepseek
   ↓
Spring Boot  POST /api/analysis  (JWT · validation · daily quota · persist)
   ↓
FastAPI AI service
   ↓
Signal extraction           (regex/mock or OpenAI/DeepSeek → structured fields)
   ↓
Rule risk (safety net)      (always computed)
   ↓
Risk adjudication           mock: rules only
                            ai:   AI risk → merge with rules (max level, no downgrade)
   ↓
Emergency escalation        (red-flag keywords → may force Emergency triage + risk)
   ↓
Explanation                 (LLM summary in AI mode + risk-tier action templates)
   ↓
Safety validation           (disclaimer, no diagnosis/dosing — en + zh)
   ↓
Saved to PostgreSQL + returned to UI
```

**Key design choice:** In **AI mode**, AI adjudicates risk first; the **rule engine is a
safety net** that may only elevate risk. In **Mock mode**, rules alone decide risk.
Symptom-only emergencies are caught by the **escalation detector**
(`ai-service/app/escalation.py`), which can override low vitals-based risk. See
[`ai-service/docs/TRIAGE_POLICY.md`](./ai-service/docs/TRIAGE_POLICY.md).

### What the platform can assess

> **Not diagnosis.** The system performs **risk triage and safety messaging** on free-text
> health notes — not clinical diagnosis.

| Category | Examples | How it is used |
| --- | --- | --- |
| **Heart rate** | `heart rate 100`, `心率200` | Threshold flags (>100 moderate, >120 high) |
| **Blood pressure** | `BP 150/95`, `血压200` | Elevated / very high systolic or diastolic |
| **Mood** | anxious, stressed, 焦虑, 心情低落 | Anxiety/stress or low-mood flags |
| **Sleep** | can't sleep, 睡不着, insomnia | Poor sleep flag |
| **Emergency symptoms** | chest pain, 胸痛, breathing difficulty, stroke signs, bleeding | Keyword escalation → **Emergency** triage (no vitals required) |
| **Free-text symptoms** | "chest tightness", "feel unwell" | Better in **AI mode**; Mock uses rules/keywords |

**Not supported today:** blood glucose, temperature, SpO₂, labs, imaging, medications, or
validated clinical protocols.

---

## Analysis Modes (Mock / OpenAI / DeepSeek)

**Default mode:** **DeepSeek** — new visitors and API requests without a `mode` use DeepSeek.
Users can still switch to **Mock**, **OpenAI**, or **DeepSeek** on the analysis page at any time.

| | **Mock** | **OpenAI** | **DeepSeek** |
| --- | --- | --- | --- |
| **Purpose** | Offline demo, CI, zero API cost | Local development or OpenAI-backed deployments | Hong Kong production (default) |
| **Extraction** | Regex / preset samples | OpenAI → structured fields | DeepSeek → structured fields; regex fallback |
| **Risk** | Rules only | AI adjudicates → rules safety net | DeepSeek adjudicates → rules safety net |
| **Explanation** | Template text | OpenAI Chat Completions + action steps | DeepSeek Chat Completions + action steps |
| **Provider badge** | `mock` | `openai` or `mock-ai` (no key) | `deepseek` |
| **Switching** | Switching from a paid mode to Mock shows a **confirmation dialog** | | |

The server env (`LLM_PROVIDER` / `EXTRACTOR_PROVIDER`) selects the backend implementation
for evaluation and default behavior; unknown values raise an error rather than silently
falling back to a paid model. API keys live only in local/server `.env` files — never in
Git, logs, or client code.

---

## Deployment & Networking Notes (Important)

The live site runs on a **Hong Kong server** behind **Nginx + HTTPS**:
**[https://healthlens-ai.co.uk](https://healthlens-ai.co.uk)**.

Please keep the following real-world constraints in mind when testing:

### 1) Access latency / packet loss from Mainland China

- The server is located in **Hong Kong** and traffic **crosses the border** to reach
  Mainland China. Cross-border routing can add **latency** and occasional **packet loss**,
  so first-load or analysis requests may feel slower or intermittently time out.
- The site is **not ICP-filed (无 ICP 备案)** for Mainland hosting, which is expected for an
  overseas/HK deployment; access from the Mainland can be less stable than from HK or
  international networks.
- **If a request is slow or fails, simply retry.** A fast, stable connection (HK, or
  international, or a good network) gives the best experience.

### 2) OpenAI regional availability

- **OpenAI's API is not available in the Hong Kong / Mainland China region.** From the HK
  server, **OpenAI mode may fail or be blocked** even with a valid key.
- For this reason, **DeepSeek is the production default** — its API is reachable from the
  HK server and is used for the live demo.
- **OpenAI mode is intended for local development** in a supported region, or for
  OpenAI-backed deployments elsewhere. If you select OpenAI mode on the live site and it
  errors out, that is the expected regional limitation — switch to **DeepSeek** (or **Mock**).
- OpenAI's list of supported countries/territories:
  <https://help.openai.com/en/articles/8660928-openai-api-supported-countries-and-territories>

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

Then open **http://localhost:5173** → Register or use the **demo account**
(`demo@healthlens.demo` / `demo1234`) → the default analysis mode is **DeepSeek**
(switchable to Mock or OpenAI on the analysis page).

After changing frontend code locally, refresh the browser (`Ctrl+Shift+R`). The Compose
file mounts `./frontend` into the container for live updates.

### Service URLs (local)

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend health | http://localhost:8080/api/health |
| AI service | http://localhost:8000/health |
| AI OpenAPI | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### Typical user flow

1. **Register** or **Login** at `/register` or `/login`. A **demo account** is created
   automatically on backend startup (`demo@healthlens.demo` / `demo1234`, **20 analyses/day**);
   the login page shows the credentials and a one-click fill button. Regular accounts use the
   default limit (`ANALYSIS_DAILY_LIMIT`, usually 10).
2. On the analysis page, toggle **English / 中文**; the default mode is **DeepSeek** (or switch
   to **Mock** / **OpenAI** manually).
3. Enter a health note (or use the sample text) and submit.
4. Review triage, vitals risk, **What this may mean**, the provider badge, and the safety check.
5. Open **History** to browse saved results, view details, or **Clear history**. The daily
   quota (used / limit) is shown at the bottom of the analysis page.

Individual service setup: [`docs/development.md`](./docs/development.md).

---

## API Overview

### Public API — Spring Boot (`/api`)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/health` | — | Backend health check |
| `POST` | `/api/auth/register` | — | Create account, returns JWT |
| `POST` | `/api/auth/login` | — | Login, returns JWT |
| `POST` | `/api/analysis` | JWT | Submit health note, persist result (quota-enforced) |
| `GET` | `/api/analysis` | JWT | List current user's history |
| `GET` | `/api/analysis/{id}` | JWT | Analysis detail |
| `GET` | `/api/analysis/quota` | JWT | Current daily quota (limit / used / remaining) |
| `DELETE` | `/api/analysis` | JWT | Clear all analyses for current user |

```http
POST /api/analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "I have chest pain and shortness of breath.",
  "language": "en",
  "mode": "deepseek"
}
```

`language`: `"en"` or `"zh"` (synced with UI). `mode`: `"mock"`, `"openai"`, `"deepseek"`,
or legacy `"ai"` (default **`deepseek`** when omitted). When the daily limit is reached the
API returns **HTTP 429** with a bilingual message.

### Internal API — FastAPI (backend → ai-service)

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/analyse` | Run the consultation workflow |
| `POST` | `/evaluation/run?provider=mock` | Run safety & quality evaluation suite |

Full contracts: [`docs/api-contracts.md`](./docs/api-contracts.md).

---

## Testing & CI

```bash
# All (Make, Unix)
make test

# AI service
cd ai-service && pip install -r requirements.txt && pytest -v

# Backend
cd backend && ./mvnw test        # Windows: .\mvnw.cmd test

# Frontend unit tests + build
cd frontend && npm ci && npm test && npm run build
```

Evaluation suite (mock, no API key):

```bash
curl -X POST "http://127.0.0.1:8000/evaluation/run?provider=mock"
```

**Continuous integration:** GitHub Actions runs the backend, AI-service, and frontend
checks on push/PR.

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
| `ANALYSIS_DAILY_LIMIT` | Per-account daily analysis limit (default 10) |
| `DEMO_ACCOUNT_*` / `DEMO_ANALYSIS_DAILY_LIMIT` | Auto-created demo account and its higher limit (default 20) |
| `LLM_PROVIDER` | `mock` \| `openai` \| `deepseek` — ai-service LLM backend (default **`deepseek`**) |
| `EXTRACTOR_PROVIDER` | Default **`deepseek`**; set to `mock` for offline demos |
| `OPENAI_API_KEY` | **OpenAI mode** — set in `.env` only (never commit) |
| `DEEPSEEK_API_KEY` | **DeepSeek mode** — required when `LLM_PROVIDER=deepseek` |
| `DEEPSEEK_BASE_URL` | Default `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Default `deepseek-v4-flash` |
| `DEEPSEEK_TIMEOUT_SECONDS` | Default `60` |
| `ENABLE_LEGACY_FRONTEND` | Expose old static UI at `/legacy` on AI service |

Never commit real secrets. Production JWT setup: [`docs/deployment.md`](./docs/deployment.md).

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
- **Vitals-centric rule engine.** Symptom emergencies rely on keyword escalation; novel
  phrasing may be missed in Mock mode.
- **Mock mode accuracy.** Regex extraction and rule-only risk are for demo/CI — use an AI
  mode for real notes.
- **Regional / network constraints.** OpenAI mode is unavailable from the HK region;
  Mainland access may see latency/packet loss (see [Deployment & Networking Notes](#deployment--networking-notes-important)).

## Roadmap

- [x] Mock / OpenAI / DeepSeek modes with rule safety net
- [x] Bilingual explanations and safety disclaimer (en / zh)
- [x] Analysis history clear-all + per-account daily quota
- [x] Production deployment (Nginx + HTTPS on Hong Kong server)
- [ ] Expand red-flag coverage and escalation metrics
- [ ] Multi-turn clarifying questions
- [ ] Clinician review workflow for thresholds and red-flag sets
- [ ] Additional vitals (e.g. temperature, SpO₂) and symptom extractors

---

## License

Portfolio / demonstration use only. Not for clinical use.
