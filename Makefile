.PHONY: up down logs backend-test frontend-test lint migrate makemigration seed quality

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-test:
	docker compose exec backend pytest

frontend-test:
	docker compose exec frontend npm test

lint:
	docker compose exec backend ruff check app tests
	docker compose exec frontend npm run lint

migrate:
	docker compose exec backend alembic upgrade head

makemigration:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

seed:
	docker compose exec backend python -m app.db.seed

quality: lint backend-test frontend-test
