# CLI SPEC — apps_exec: Executive Brief Generator

## Entrypoints

```bash
# Canonical (recommended)
python -m apps_exec [OPTIONS]

# Direct script
python apps_exec/scripts/run_exec.py [OPTIONS]
```

---

## Arguments

| Argument         | Type    | Required | Default              | Description                                       |
|------------------|---------|----------|----------------------|---------------------------------------------------|
| `--audience`     | str     | **Yes**  | —                    | Audience persona: `recruiter`, `cto`, `svp_eng`, `board` |
| `--source-dirs`  | str...  | No       | `[]`                 | One or more source directories to ingest          |
| `--config`       | path    | No       | built-in defaults    | Path to `exec_agent_specs.json`                   |
| `--out`          | path    | No       | `reports/executive`  | Output directory for artifacts                    |
| `--dry-run`      | flag    | No       | `False`              | Assemble + validate; do not emit files            |
| `--trace-id`     | str     | No       | auto-generated       | Override trace ID for reproducibility             |
| `--json-output`  | flag    | No       | `False`              | Print JSON result summary to stdout               |
| `--log-level`    | str     | No       | `INFO`               | Logging verbosity: `DEBUG`, `INFO`, `WARNING`     |

---

## Usage Examples

```bash
# Minimum viable invocation — recruiter brief from empty source set
python -m apps_exec --audience recruiter

# Full run with source dirs
python -m apps_exec --audience cto \
  --source-dirs docs/architecture agentic_core \
  --out reports/executive

# Dry run — validate only
python -m apps_exec --audience svp_eng \
  --source-dirs docs/ \
  --dry-run

# Board brief with fixed trace ID for reproducibility
python -m apps_exec --audience board \
  --trace-id board-brief-2024-q4 \
  --out reports/executive

# JSON output for CI consumption
python -m apps_exec --audience recruiter --json-output
```

---

## JSON Output Schema (when `--json-output`)

Printed to `stdout`. All other logging goes to `stdout` via the logging handler.

```json
{
  "trace_id": "string",
  "status": "complete | failed | dry_run",
  "audience": "string",
  "quality_score": 0.0,
  "sections": 0,
  "gate_violations": [],
  "artifacts": []
}
```

---

## Exit Codes

| Code | Condition                                      |
|------|------------------------------------------------|
| `0`  | Complete or DRY_RUN (even with WARN violations)|
| `1`  | FAILED (BLOCK gate violation or error)         |

---

## Argument Validation

- `--audience` outside enum → `argparse` error (pre-flight, non-zero exit, no pipeline start)
- `--source-dirs` pointing to non-existent path → logged WARNING, path added to `skipped_paths`
- `--out` directory not existing → created automatically by `ExecOrchestrator`
- `--trace-id` with spaces → accepted as-is; used verbatim in file names (no path traversal check needed, only alphanumeric + `-` recommended)

---

## Configuration Override

The `--config` flag accepts a path to a JSON file conforming to `ExecAgentSpecs` schema.
Unknown fields are ignored. Missing fields fall back to Pydantic defaults.
If the file cannot be read or parsed, a warning is logged and built-in defaults are used.
The run does NOT fail due to a bad config file.

---

## Combining Flags

- `--dry-run` + `--json-output`: valid; JSON output still printed, no files written
- `--dry-run` + `--out`: `--out` is ignored in dry-run mode
- `--json-output` + `--log-level DEBUG`: both apply; debug logs go to stdout before JSON summary
