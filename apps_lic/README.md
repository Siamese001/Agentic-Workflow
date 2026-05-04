# apps_lic — Lifecycle Intelligence & Communication

Multi-hop agent application that profiles, researches, grounds, and authors outbound communication (email/LinkedIn) via a governed HOP pipeline. Replaces ad-hoc outbound tooling with a deterministic, auditable spine.

## Quickstart

```bash
python -m apps_lic --input-profile <path-to-profile.yaml> --mode=ENVELOPE_FIRST
```

See `RUNBOOK.md` for operational semantics and `SLO.md` for runtime budgets.

## Architecture

- **`engines/`** — HOP1..HOPn agent engines (profile, research, grounding, authoring)
- **`reasoning/`** — planners, scorers, HOP pipeline executor, message/profile planners (post-ADR-082: `L1_cognition/` merged here)
- **`validators/policy/`** — decision tables consumed by `DecisionRouter` (replaces imperative classifier chains)
- **`services/`** — persistence (SQLite-backed durability) + observability (telemetry bus + subscribers)
- **`engines/outreach/`** — outreach-specific engine helpers
- **`integrations/`** — governed run entrypoints + execution adapter
- **`validators/`** — schema/contract validators
- **`types/`** — Pydantic models

## Related docs

- `TECHNICAL_SPEC.md` — detailed architecture
- `TEST_STRATEGY.md` — test pyramid + coverage targets
- `RUNBOOK.md` — ops runbook
- `SLO.md` — budgets and error-rate targets
- `SVP_ENGINEERING_REVIEW.md` — engineering review snapshot
- `THREAT_MODEL.md` — external-input threat surface
- `spine_manifest.yaml` — spine wiring
