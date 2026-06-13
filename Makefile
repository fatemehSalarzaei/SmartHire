.PHONY: up down logs backend-test frontend-test lint migrate makemigration seed quality

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-test:
	docker compose run --rm --no-deps backend pytest

frontend-test:
	docker compose exec frontend npm test

lint:
	docker compose run --rm --no-deps backend ruff check app tests
	docker compose run --rm --no-deps frontend npm run lint

migrate:
	docker compose exec backend alembic upgrade head

makemigration:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

seed:
	docker compose exec backend python -m app.db.seed

quality: lint backend-test frontend-test
