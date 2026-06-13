# apps_shared — Shared infrastructure for the apps_* tier

**Library-only app.** Exposes the reusable primitives — adapters, validators, orchestration, enforcement, proof harness, emission helpers — that every producer app (`apps_eval`, `apps_lic`, `apps_qna`, `apps_research`, `apps_rg`, `apps_underwriting_ai`) depends on. The substrate behind the **single-shape, many-apps** discipline.

## Design Patterns at Work

- **PEP-562 Lazy Boundary Adapters** — `integrations/adapters/` exposes `__getattr__` lazy facades (`system_learning_facade`, `rg_orchestrator_facade`, `research_facade`). Cross-tree imports route through these adapters; **`apps_eval` cannot reach into `apps_rg` even by accident**. Boundary-leak tests in `tests/unit/apps_shared/adapters/` lock in the invariant.
- **Hardened Strategy Enforcers** — `validators/enforcement/Hardened*Strategy.py` (grandfathered CamelCase) are runtime guard classes for provenance, global cache, event bus, circuit breaker, and guardrail enforcement. Strategy pattern, not config flags.
- **Runtime Proof Harness** — `validators/proof/` ships `AppRunEvidencePacket`, bypass validators, negative controls, and scenario-based runners. Every governed app run produces a verifiable evidence packet — the substrate behind the architecture proof pack (`ops_scripts/ci/run_architecture_proof.py`).
- **HOP Pipeline Executor** — `reasoning/orchestration/HopPipelineExecutor` is the shared declarative driver consumed by `apps_rg`, `apps_lic`, `apps_underwriting_ai`. One topology shape, many apps.
- **GovernedAppRunner + FormalExceptionEntry** — `services/governed_app_runner.py` is the single envelope used by every producer app to enter the governed runtime. Formal exceptions are typed entries, not raised Python exceptions.
- **Spine Adapter** — `services/spine_adapter.py` is the only path apps use to handshake with the runtime spine; the spine claim per app lives in `spine_manifest.yaml`.
- **Cert Plumbing** — `cert/exit_eval_hook.py` provides fail-soft `maybe_invoke_exit_eval` consumed by every app's `__main__.py` entrypoint, gated by `cert_route_registry.yaml.invoke_exit_eval`.

## Architecture (post-ADR-082)

```
apps_shared/
├── config/                      # App-wide config (app_guardian_registry, environment, ...)
├── contracts/                   # Cross-app contracts (L0 emit schemas, connection_data, outreach_history)
├── spine_emission/              # Spine-boundary emission helpers
├── data/
│   ├── prompts/                 # Shared prompt assets
│   └── templates/               # Shared template assets
├── integrations/
│   ├── adapters/                # PEP-562 lazy facades — cross-tree boundary
│   └── data_adapters/           # Data-layer adapters
├── reasoning/
│   └── orchestration/           # HopPipelineExecutor + registry primitives
├── services/                    # spine_adapter, governed_app_runner
├── spine/                       # spine wiring
├── cert/                        # exit_eval_hook (fail-soft maybe_invoke_exit_eval), exit_eval_hook init
├── types/                       # shared Pydantic types
├── utils/
│   ├── mixins/                  # tracing mixin
│   └── apps_e2e_dry_run.py
├── validators/
│   ├── enforcement/             # Hardened*Strategy runtime guards
│   └── proof/                   # runtime proof harness — AppRunEvidencePacket et al.
├── tests/
└── spine_manifest.yaml
```

## Key Primitives, Indexed

| Primitive | Where | Used by |
|---|---|---|
| `HopPipelineExecutor` | `reasoning/orchestration/` | `apps_rg`, `apps_lic`, `apps_underwriting_ai` |
| `maybe_invoke_exit_eval` | `cert/exit_eval_hook.py` | every governed app's `__main__.py` |
| `AppRunEvidencePacket` | `validators/proof/` | architecture proof pack, per-app runs |
| `GovernedAppRunner` | `services/governed_app_runner.py` | every producer app's governed entrypoint |
| `Hardened*Strategy` | `validators/enforcement/` | runtime guards across the apps tier |
| Lazy boundary adapters | `integrations/adapters/` | every cross-tree import |

## Boundary Discipline

Cross-app imports MUST route through `apps_shared/integrations/adapters/`. Direct imports across producer apps (e.g. `from apps_rg.engines import ...` inside `apps_eval`) are blocked by boundary-leak tests. The lazy adapter pattern means imports cost nothing until actually called — and stay enforceable forever.

## Companion Docs

- `TECHNICAL_SPEC.md` — detailed architecture
- `TEST_STRATEGY.md` — test strategy
- `RUNBOOK.md` — ops runbook
- `SLO.md` — performance budgets
- `SVP_ENGINEERING_REVIEW.md` — engineering review snapshot
- `STUB_CENSUS.md` — current stubs / placeholders
- ADR-082 — folder taxonomy
- `validators/proof/THREAT_MODEL.md` — proof-harness threat surface
