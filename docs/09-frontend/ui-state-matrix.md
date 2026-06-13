# UI State Matrix

| State | Display |
|---|---|
| Loading | skeleton/loading indicator |
| Empty | Persian empty state with next action |
| Error | Persian backend message + retry if retryable |
| Permission denied | Persian access denied card |
| Partial data | warning badge and explanation |
| AI failed | show `AI Failed` badge; do not block decision view |
| Sync running | show status badge |
| Screening pending | show pending state |
| Needs review | separate queue and yellow warning |
