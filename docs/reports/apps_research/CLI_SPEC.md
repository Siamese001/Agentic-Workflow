# CLI SPEC — apps_research: Autonomous Research Engine

## Entrypoints

```bash
python -m apps_research [OPTIONS]
python apps_research/scripts/run_research.py [OPTIONS]
```

---

## Arguments

| Argument       | Type    | Required | Default              | Description                                        |
|----------------|---------|----------|----------------------|----------------------------------------------------|
| `--topic`      | str     | **Yes**  | —                    | Research topic or question                         |
| `--mode`       | str     | No       | `brief`              | `brief`, `comparison`, `trend`, `position`, `thought_leadership` |
| `--audience`   | str     | No       | `technical`          | `technical`, `executive`, `market-facing`          |
| `--compare`    | str     | No       | `""`                 | Comma-separated comparison subjects                |
| `--horizon`    | str     | No       | `""`                 | Time horizon for trend mode (e.g. `"12 months"`)   |
| `--config`     | path    | No       | built-in defaults    | Path to `research_agent_specs.json`                |
| `--out`        | path    | No       | `artifacts/apps_research` | Output directory                              |
| `--dry-run`    | flag    | No       | `False`              | Assemble + validate; do not emit files             |
| `--trace-id`   | str     | No       | auto-generated       | Override trace ID                                  |
| `--json-output`| flag    | No       | `False`              | Print JSON result summary to stdout                |

---

## Usage Examples

```bash
# Topic brief (default mode)
python -m apps_research --topic "enterprise agentic AI governance"

# Framework comparison
python -m apps_research \
  --topic "agentic AI orchestration frameworks" \
  --mode comparison \
  --compare "LangGraph,AutoGen,CrewAI,agentic_core (this repo)"

# Trend scan with horizon
python -m apps_research \
  --topic "AI governance regulation" \
  --mode trend \
  --horizon "18 months"

# Executive-audience thought leadership post
python -m apps_research \
  --topic "constitutional governance in AI" \
  --mode thought_leadership \
  --audience executive

# Dry run
python -m apps_research --topic "test" --mode brief --dry-run

# CI / pipeline output
python -m apps_research --topic "determinism patterns" --json-output
```

---

## JSON Output Schema (when `--json-output`)

```json
{
  "trace_id": "string",
  "status": "complete | failed | dry_run",
  "topic": "string",
  "mode": "string",
  "quality_score": 0.0,
  "sections": 0,
  "sources": 0,
  "gate_violations": [],
  "artifacts": []
}
```

---

## Exit Codes

| Code | Condition                        |
|------|----------------------------------|
| `0`  | Complete or DRY_RUN              |
| `1`  | FAILED (gate violation or error) |

---

## Mode × Argument Interactions

| Mode                | `--compare` effect            | `--horizon` effect              |
|---------------------|-------------------------------|---------------------------------|
| `brief`             | Ignored                       | Noted in time context           |
| `comparison`        | Sets comparison subjects      | Ignored                         |
| `trend`             | Ignored                       | Appears in trend overview       |
| `position`          | Ignored                       | Ignored                         |
| `thought_leadership`| Ignored                       | Ignored                         |

---

## Argument Validation

- `--topic` empty string → rejected at parse time with error message
- `--mode` outside enum → `argparse` error
- `--compare` in non-comparison mode → silently ignored (no error)
- `--audience` outside enum → falls back to `technical`, warning logged
- `--horizon` in non-trend mode → silently ignored
