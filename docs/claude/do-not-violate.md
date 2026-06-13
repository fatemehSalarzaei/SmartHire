# Do Not Violate

Claude must never violate these rules.

## Kando

- Do not implement Kando write calls.
- Do not invent Kando write endpoints.
- Do not mutate Kando status/stage/note/tag.
- Do not use browser automation to mutate Kando.

## Workflow

- Do not make daily screening/ranking manual.
- Do not expose manual run as HR primary action.
- Do not skip Celery-based automation.

## AI

- Do not make AI final decision-maker.
- Do not hard reject solely from AI output.
- Do not send phone/email/API keys/raw payload to AI.
- Do not accept free-form AI output; validate JSON schema.

## Rule Engine

- Do not hardcode customer-support rules in Python.
- Do not edit active RuleSet in place.
- Do not skip reason/audit capture.

## API

- Do not return English-only errors.
- Do not expose stack traces.
- Do not expose secrets.
- Do not implement unpaginated list endpoints.

## Database

- Do not change schema without Alembic migration.
- Do not make audit logs editable/deletable.
- Do not make Kando cache manually editable.

## Frontend

- Do not reimplement backend business decisions.
- Do not call Kando directly.
- Do not show raw payload/AI prompt to HR.


## Overengineering

- Do not convert the system into microservices.
- Do not introduce Kubernetes, service mesh, Kafka, RabbitMQ, CQRS, event sourcing, or GraphQL.
- Do not split AI analysis, ranking, screening, or Kando integration into separately deployed services.
- Do not create generic plugin frameworks or excessive abstraction layers.
- Do not implement multi-tenant architecture unless explicitly requested.
- Do not build custom admin UI for technical administration when SQLAdmin is sufficient.
- Do not use asynchronous infrastructure to solve simple in-process domain logic.
- Do not add caching layers beyond PostgreSQL/Redis unless performance evidence requires it.
- Do not optimize for thousands of users; optimize for fewer than 100 internal users and background resume processing.
