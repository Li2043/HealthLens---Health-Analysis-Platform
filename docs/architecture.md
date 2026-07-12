# Architecture

## Overview

HealthLens Platform is a multi-service healthcare AI product demo. Phase 1 establishes the repository skeleton and migrates the existing FastAPI analysis pipeline into an internal AI service.

```text
React + TypeScript (frontend)
        |
        | REST API  /api/*
        v
Spring Boot (backend)
        |
        | Internal HTTP  /analyse, /health
        v
FastAPI (ai-service)
        |
        v
PostgreSQL (business data — baseline only in phase 1)
```

## Service responsibilities

| Service | Role |
| --- | --- |
| **frontend** | User-facing React SPA (replacing the legacy static JS UI) |
| **backend** | Business API, auth (future), analysis orchestration (future), persistence |
| **ai-service** | Health-text analysis pipeline: extraction, risk rules, escalation, LLM, safety validation |
| **postgres** | Relational store for users and analysis history (schema TBD) |

## Communication rules

- Browsers talk only to **backend** (`VITE_API_BASE_URL`).
- **Backend** calls **ai-service** via `AI_SERVICE_BASE_URL` (Docker DNS: `http://ai-service:8000`).
- **Backend** connects to **postgres** via JDBC (`jdbc:postgresql://postgres:5432/healthlens`).

## Legacy UI

The original vanilla JavaScript frontend is preserved under `ai-service/legacy-frontend/` and is **not** the default entry point. Enable with `ENABLE_LEGACY_FRONTEND=true` on the AI service for reference only.
