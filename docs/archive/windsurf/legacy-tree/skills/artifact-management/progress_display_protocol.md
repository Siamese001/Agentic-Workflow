# Progress Display Protocol

## Mandatory for Operations > 5 Seconds

- Colored progress bar (40-character standard format)
- Real-time status updates at least every 5 seconds
- Percentage completion
- ETA for operations > 30 seconds (Xs / Xm / Xh)
- Current item description

## Color Codes (ANSI)

| Code | Color | Use |
|---|---|---|
| `\033[92m` | Bright green | Success |
| `\033[93m` | Bright yellow | Warning / slow |
| `\033[91m` | Bright red | Error |
| `\033[94m` | Bright blue | In-progress |
| `\033[97m` | Bright white | Neutral |
| `\033[0m` | Reset | End of colored segment |

## Timeout Ranges

| Category | Range |
|---|---|
| Fast (grep, file reads, simple AST) | 5–30 s |
| Medium (graph construction, test collection) | 30–120 s |
| Heavy (full repo analysis) | 120–600 s |
| External API | 10–60 s |

## Forbidden

- Operations > 5 s with no progress display
- Progress updates less frequent than every 5 seconds
- Monochrome output
- Missing percentage completion
- Missing ETA for operations > 30 s
