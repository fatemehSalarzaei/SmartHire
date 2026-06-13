# Fixture Strategy

Fixtures must make implementation review faster.

## Required fixture groups

- `kando/`: mocked Kando API responses.
- `snapshots/`: canonical application snapshots.
- `rulesets/`: RuleSet JSON examples.
- `ai/`: AI outputs and failures.
- `expected/`: golden expected decisions, rankings, notes and API errors.

## Rules

- Fixtures must be stable.
- Expected outputs must be deterministic.
- Tests must compare actual output to expected JSON.
- Do not include real candidate data.
