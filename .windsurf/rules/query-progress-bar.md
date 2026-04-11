---
trigger: always_on
---
# Query Progress Bar — Mandatory for Long Operations

> ⛔ ALL operations expected to take >5 seconds MUST display a colored progress bar.
> Monochrome output and missing progress on long queries are constitutional violations.

## Rule §16: Query Progress Bar

**Threshold**: Any operation that:
- Takes or is estimated to take **>5 seconds**, OR
- Iterates over **>10 items** in a loop, OR
- Calls any query/search/scan/build function on the repo, OR
- Invokes subprocess commands that may run >5s

**MUST** display a compliant progress bar before the operation begins.

---

## Required Progress Bar Format

### Standard Format (40-character bar)
```
[████████████████████████░░░░░░░░░░░░░░░░]  62% (620/1000) - ETA: 14s
```

### Components (ALL required)
- 40-character bar using `█` (filled) and `░` (empty)
- Percentage with `%` suffix
- Current/total count in `(N/M)` format
- ETA in `Xs`, `Xm`, or `Xh` format for operations expected >30s

### ANSI Color Rules (mandatory)
| Progress | Color | ANSI Code |
|---|---|---|
| ≥90% | Bright green | `\033[92m` |
| 70–89% | Bright blue | `\033[94m` |
| 40–69% | Bright yellow | `\033[93m` |
| <40% | Bright red | `\033[91m` |
| Pending/neutral | Bright white | `\033[97m` |
| Reset | (always end with) | `\033[0m` |

---

## Canonical Implementation

Use `tools/progress_display.py` `ProgressReporter` for all progress output:

```python
from tools.progress_display import ProgressReporter

reporter = ProgressReporter(total=len(items), label="Scanning modules")
for item in items:
    process(item)
    reporter.update(label=f"Scanned {item}")
reporter.done()
```

**Alternative**: `tqdm` is permitted when `ProgressReporter` is unavailable:
```python
from tqdm import tqdm
for item in tqdm(items, desc="Scanning", unit="file"):
    process(item)
```

---

## Update Frequency

| Operation duration | Minimum update frequency |
|---|---|
| 5–30 seconds | Every 2 seconds |
| 30–120 seconds | Every 5 seconds |
| >120 seconds | Every 10 seconds |

Maximum update frequency: no more than once every 0.5 seconds (avoid terminal flood).

---

## Forbidden Patterns

- ❌ `for item in items: process(item)` — long loop with no progress reporting
- ❌ Silent execution of >5s operations with no output
- ❌ Monochrome progress (plain `print("Processing...")` only)
- ❌ Missing ETA for operations expected >30s
- ❌ Progress update intervals >5 seconds
- ❌ Non-standard bar widths that reduce readability

---

## Enforcement

### CI Gate
`ops_scripts/ci/check_query_progress_bar.py` — detects:
1. For-loops >10 lines without progress indicators in key directories
2. `subprocess.run` calls without matching progress context
3. Functions named `scan_*`, `build_*`, `query_*`, `search_*`, `analyze_*` with no
   progress indicators and body length >15 lines

### Pre-commit Hook
`check-query-progress-bar` — runs on staged Python files in `agentic_core/`, `apps_*/`,
`ops_scripts/`, `tools/`, `system_learning/`.

### Detection Markers (CI recognizes these as compliant)
Any of the following satisfies the progress requirement:
- Import of `tqdm` or `ProgressReporter`
- Use of `pbar.update`, `tracker.update`, `reporter.update`
- String `"progress"` in the loop body (case-insensitive)
- Use of `rich.progress` or `alive_bar`

---

## Timeout Ranges (for progress bar ETA calibration)

| Category | Expected range | ETA required |
|---|---|---|
| Fast — grep, file reads, simple AST | 5–30 s | No |
| Medium — graph construction, test collection | 30–120 s | Yes |
| Heavy — full repo analysis, ADG build | 120–600 s | Yes |
| External API calls | 10–60 s | Yes |

---

## Error Handling in Progress Context

```python
reporter = ProgressReporter(total=len(items), label="Processing")
try:
    for item in items:
        process(item)
        reporter.update()
    reporter.done()
except KeyboardInterrupt:
    reporter.fail("Interrupted by user")
    raise
except (OSError, ValueError) as exc:
    reporter.fail(f"Failed: {exc}")
    raise
```

Never swallow exceptions inside a progress loop without surfacing them via `reporter.fail()`.

---

## References

- **Enforcement script**: `ops_scripts/ci/check_query_progress_bar.py`
- **Implementation**: `tools/progress_display.py`
- **Skill**: `.windsurf/skills/artifact-management/progress_display_protocol.md`
- **Workflow**: `.windsurf/workflows/progress-display-enforcement.md`
- **Related rule**: §14 Subprocess Timeout Required (`global_rules.md`)
