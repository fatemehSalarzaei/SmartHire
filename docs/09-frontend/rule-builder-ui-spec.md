# Rule Builder UI Spec

## Required UI elements

- RuleSet version/status badge.
- RuleGroup list.
- Add/edit rule group.
- Add/edit rule.
- Field selector.
- Operator selector.
- Values input.
- Score delta.
- Missing data policy.
- Explanation required.
- AI target fields with warnings.
- Preview button.
- Validate button.
- Activate button with confirmation.

## Constraints

- Active RuleSet is read-only.
- Editing active RuleSet creates clone/new version.
- HARD_REJECT rules show warning.
- AI-based HARD_REJECT disabled by default.
- Sensitive fields require elevated permission.
