# CLI SPEC — apps_rfp: AI Proposal / RFP Generator

## Entrypoints

```bash
python -m apps_rfp [OPTIONS]
python apps_rfp/scripts/run_rfp.py [OPTIONS]
```

---

## Arguments

| Argument          | Type  | Required | Default           | Description                                             |
|-------------------|-------|----------|-------------------|---------------------------------------------------------|
| `--brief`         | str   | Yes*     | —                 | Client problem statement (inline)                       |
| `--brief-file`    | path  | Yes*     | —                 | Path to file containing problem statement               |
| `--industry`      | str   | No       | `technology`      | `technology`, `financial_services`, `healthcare`, `government` |
| `--posture`       | str   | No       | `cloud_first`     | `cloud_first`, `hybrid`, `sovereign`                    |
| `--timeline`      | int   | No       | `16`              | Delivery timeline in weeks (≥ 4)                        |
| `--config`        | path  | No       | built-in defaults | Path to `rfp_agent_specs.json`                          |
| `--out`           | path  | No       | `rfp`             | Output directory                                        |
| `--dry-run`       | flag  | No       | `False`           | Assemble + validate; do not emit files                  |
| `--trace-id`      | str   | No       | auto-generated    | Override trace ID                                       |
| `--json-output`   | flag  | No       | `False`           | Print JSON result summary to stdout                     |

*One of `--brief` or `--brief-file` required.

---

## Usage Examples

```bash
# Basic proposal
python -m apps_rfp --brief "We need to automate document review with AI"

# Financial services with sovereign posture
python -m apps_rfp \
  --brief "Automate compliance workflows" \
  --industry financial_services \
  --posture sovereign \
  --timeline 24

# Proposal from file
python -m apps_rfp --brief-file client_briefs/acme_corp.md --industry healthcare

# Dry run
python -m apps_rfp --brief "test problem" --dry-run

# CI integration
python -m apps_rfp --brief-file brief.md --industry technology --json-output
```

---

## JSON Output Schema (when `--json-output`)

```json
{
  "trace_id": "string",
  "status": "complete | failed | dry_run",
  "industry": "string",
  "sections": 0,
  "roadmap_phases": 5,
  "risks": 0,
  "quality_score": 0.0,
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

## Argument Validation

- Both `--brief` and `--brief-file` provided → `--brief-file` takes precedence, warning logged
- `--brief-file` not found → non-zero exit, error message
- `--brief` empty string → rejected at parse time
- Unknown `--industry` → falls back to `technology`, warning logged
- `--timeline` < 4 → warning logged; minimum 4 weeks enforced
- `--posture` outside enum → `argparse` error

---

## Industry Behavior Summary

| Industry             | Automatic Risk Flags           | Architecture Default |
|----------------------|--------------------------------|----------------------|
| `financial_services` | SOX, GDPR, MiFID II            | sovereign            |
| `healthcare`         | HIPAA, FDA 21 CFR              | hybrid               |
| `technology`         | (none)                         | cloud_first          |
| `government`         | FedRAMP, FISMA, ITAR           | sovereign            |
