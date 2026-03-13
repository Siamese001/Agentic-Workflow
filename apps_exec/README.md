# apps_exec — Executive Brief Generator

Generates persona-targeted executive briefs from the repo's architecture documentation.
Demonstrates platform-to-strategy translation for recruiters, CTOs, SVP engineers, and board audiences.

## Quick Start

```bash
# Dry run — plan but don't emit files
python -m apps_exec --audience recruiter --dry-run

# Full run — emit brief to reports/executive/
python -m apps_exec --audience cto --source-dirs docs/architecture --out reports/executive

# JSON output for CI integration
python -m apps_exec --audience svp_eng --json-output
```

## Pipeline

```
Source Dirs → IngestionEngine → CapabilityExtractionEngine → BriefAssemblyEngine
           → StyleGateValidator → Artifact Emission → RunSummary
```

## Audience Personas

| Persona     | Tone              | Key Sections                                          |
|-------------|-------------------|-------------------------------------------------------|
| `recruiter` | recruiter-friendly| platform_summary, key_capabilities, portfolio_value   |
| `cto`       | cto-ready         | architecture_overview, governance_model, strategy     |
| `svp_eng`   | technical         | system_architecture, engineering_decisions, gates     |
| `board`     | board-ready       | strategic_value, risk_posture, differentiation        |

## Artifacts

All artifacts written to `reports/executive/` by default:

- `exec_brief_<audience>_<trace_id[:8]>.md` — formatted executive brief
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Quality Gates

- Minimum 2 evidence anchors per section (WARN if missing)
- No unsupported absolute claims (`always`, `never`, `guaranteed`) — BLOCK
- Buzzword density < 5% — BLOCK above threshold
- Every section must have a "why this matters" block — WARN if absent

## Folder Structure

```
apps_exec/
├── config/           # Pydantic config schemas + loading
├── engines/          # IngestionEngine, CapabilityExtractionEngine, BriefAssemblyEngine
├── reasoning/        # ExecOrchestrator (multi-hop pipeline)
├── scripts/          # run_exec.py CLI
├── types/            # exec_types.py (frozen dataclasses, enums)
├── utils/            # (future: shared utilities)
├── validators/       # StyleGateValidator
├── __init__.py
└── __main__.py       # python -m apps_exec entrypoint
```
