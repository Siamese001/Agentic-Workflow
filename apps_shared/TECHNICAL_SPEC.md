# apps_shared — Technical Spec

## Purpose

Cross-cutting library for the `apps_*` tier. Every producer app depends on `apps_shared` for boundary facades, proof harness, enforcement strategies, HOP orchestration substrate, and spine emission.

## Design principles

1. **Library-only** — no app entrypoint, no HOP pipeline of its own. Exports primitives; does not invoke them.
2. **Lazy boundary imports** — cross-tree facades use PEP 562 `__getattr__` so module load does not pull in upstream peers. Enables apps to be importable without `system_learning` / `apps_rg` installed.
3. **Hardened strategies are sealed** — `validators/enforcement/Hardened*Strategy.py` are consumed via `__init__.py` re-exports; their internal state is not exposed.
4. **Proof packets are hash-stable** — `validators/proof/proof_contracts.py` defines deterministic content hashing so evidence packets across runs are verifiable.

## Folder layout — details

### `integrations/adapters/` (formerly `apps_shared/adapters/`)

Boundary-leak facades. Three facades as of 2026-05-03:
- `system_learning_facade` — 6 symbols consumed by apps (memory bridge, process bus, change package, bus, adapter registry, seal helper)
- `rg_orchestrator_facade` — `RgResumeOrchestrator`
- `research_facade` — apps_research boundary

Tests in `tests/unit/apps_shared/adapters/test_w3_boundary_facades.py` enforce: no direct `system_learning` or `apps_rg` imports in `apps_eval` or `apps_lic`.

### `validators/enforcement/` (formerly `apps_shared/enforcement/`)

Hardened strategy classes (highest fan-in in repo — 18 files, imported by every app):
- `HardenedeventbusStrategy` — publisher/subscriber with hardened delivery
- `ProvenancetrackerStrategy` — artifact lineage + source citations
- `GlobalcacheStrategy`, `CircuitbreakerStrategy`, `AdaptiveretrievalgateStrategy`, `DecomposedqueryagentStrategy`, `GuardrailStrategy`, and peers.

### `validators/proof/` (formerly `apps_shared/proof/`)

Runtime proof harness:
- `AppRunEvidencePacket` — evidence contract
- `bypass_validator.py` — ADG-driven bypass-class checks
- `proof_runner.py` — CLI entrypoint
- `runtime_drivers/` — per-app drivers emitting app-specific evidence

### `reasoning/orchestration/` (formerly `apps_shared/orchestration/`)

- `HopPipelineExecutor` — per-app inner-DAG substrate
- `HopRegistry`, `HopStageSpec`, `HopRunRecord`, `Checkpoint`, `StageStatus`

### `integrations/governed_app_runner`

Canonical entrypoint for governed app runs. Every producer app's `governed_<app>_run.py` delegates here.

## Contracts

- **Import contract** — every app may import from `apps_shared.*` freely; apps may NOT import from `apps_*` peers except via `apps_shared.integrations.adapters.*` facades.
- **Evidence contract** — every governed run emits an `AppRunEvidencePacket` with deterministic hash.
- **Enforcement contract** — every executor call is wrapped by a `Hardened*Strategy`; direct executor calls are forbidden in producer apps.

## Migration notes (ADR-082)

Compat shims at OLD paths emit `DeprecationWarning` and redirect via `sys.modules[__name__] = ...`. Sunset 2026-05-17. External consumers MUST update imports before sunset:
- `apps_shared.adapters.*` → `apps_shared.integrations.adapters.*`
- `apps_shared.data_adapters.*` → `apps_shared.integrations.data_adapters.*`
- `apps_shared.enforcement.*` → `apps_shared.validators.enforcement.*`
- `apps_shared.proof.*` → `apps_shared.validators.proof.*`
- `apps_shared.mixins.*` → `apps_shared.utils.mixins.*`
- `apps_shared.orchestration.*` → `apps_shared.reasoning.orchestration.*`

## References

- ADR-082 — folder taxonomy
- `.codex/plans/apps-runtime-first-principles-e6ba58.md` — W3 facade contract
- `.codex/plans/apps-runtime-proof-harness-9d4c2a.md` — proof harness
