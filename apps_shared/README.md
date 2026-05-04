# apps_shared — Shared infrastructure for the apps_* tier

Library-only app. Exposes reusable primitives — adapters, validators, orchestration, enforcement, proof harness, emission helpers — that every producer app (`apps_eval`, `apps_exec`, `apps_lic`, `apps_qna`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_underwriting_ai`) depends on.

## Architecture (post-ADR-082)

```
apps_shared/
├── config/                      # App-wide config (app_guardian_registry, environment, etc.)
├── contracts/                   # Cross-app contracts (L0 emit schemas)
├── spine_emission/              # Spine-boundary emission helpers
├── data/
│   ├── prompts/                 # moved from apps_shared/prompts/
│   └── templates/               # moved from apps_shared/templates/
├── integrations/
│   ├── adapters/                # moved from apps_shared/adapters/ — cross-tree boundary facades
│   └── data_adapters/           # moved from apps_shared/data_adapters/
├── reasoning/
│   └── orchestration/           # moved from apps_shared/orchestration/ — HOP pipeline executor
├── services/                    # spine-adapter + governed-app-runner
├── spine/                       # spine wiring
├── types/                       # shared Pydantic types
├── utils/
│   ├── mixins/                  # moved from apps_shared/mixins/ — tracing mixin
│   └── apps_e2e_dry_run.py      # moved from apps_shared/_apps_e2e_dry_run.py
├── validators/
│   ├── enforcement/             # moved from apps_shared/enforcement/ — Hardened*Strategy
│   └── proof/                   # moved from apps_shared/proof/ — runtime proof harness
├── tests/
└── spine_manifest.yaml
```

## Key primitives

- **`integrations/adapters/`** — PEP 562 `__getattr__` lazy facades for controlled cross-tree imports (`system_learning_facade`, `rg_orchestrator_facade`, `research_facade`). Boundary-leak tests in `tests/unit/apps_shared/adapters/` lock in the invariant that `apps_eval` / `apps_lic` may not directly import `system_learning` or `apps_rg`.
- **`validators/enforcement/`** — `Hardened*Strategy.py` classes (grandfathered CamelCase) for provenance, global cache, event bus, circuit breaker, guardrail enforcement.
- **`validators/proof/`** — runtime proof harness: `AppRunEvidencePacket`, bypass validators, negative controls, scenario-based runners.
- **`reasoning/orchestration/`** — `HopPipelineExecutor` + registry primitives consumed by `apps_rg`, `apps_lic`, `apps_underwriting_ai`, and future multi-hop apps.

## Related docs

- `TECHNICAL_SPEC.md` — detailed architecture
- `TEST_STRATEGY.md` — test strategy
- `RUNBOOK.md`, `SLO.md`, `SVP_ENGINEERING_REVIEW.md`, `STUB_CENSUS.md`
- ADR-082 — folder taxonomy
