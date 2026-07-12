.PHONY: up down build logs test test-backend test-ai install-frontend

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test: test-ai test-backend

test-backend:
	cd backend && ./mvnw test

test-ai:
	cd ai-service && python -m pytest -q

install-frontend:
	cd frontend && npm install
