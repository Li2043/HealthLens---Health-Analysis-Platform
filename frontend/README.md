# HealthLens Platform Frontend

React + TypeScript + Vite user interface for the HealthLens platform.

## Phase 1 scope

- Route skeleton: login, register, analyse, history, history detail
- Axios client with `VITE_API_BASE_URL`
- **Analysis page** — submit health notes to `POST /api/analysis` and display results
- Login, register, and history pages remain placeholders

## Local development

```bash
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

## Build

```bash
npm run build
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8080/api` | Spring Boot API base URL |
