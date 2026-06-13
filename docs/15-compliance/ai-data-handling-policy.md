# AI Data Handling Policy

## Allowed AI input

- job title and requirements
- sanitized CV structured data
- work descriptions
- education fields
- language levels
- cover letter

## Disallowed by default

- phone
- email
- exact address
- raw Kando payload
- API keys
- unrelated personal attributes

## Required metadata

Every AI run stores:

- provider
- model name
- prompt version
- input hash
- output schema version
- status
