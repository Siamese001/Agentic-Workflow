# ADR-095 — L6 Observability Dependency Hygiene

Status: **Accepted** · 2026-05-02 · Tier: T2 governance · Layer: L6

## Context

`agentic_core/L6_observability/` originally accumulated **39 cross-layer imports** to L0/L1/L2/L3/L4/L5. By doctrine (`adg-canonical-invariants.md` §6), L6 has the lowest layer multiplier (×0.75) — it is meant to be a **leaf observer**, not a hub. Cross-layer reads and writes from L6 invert the gravity arrows.

Three categories of L6→lower edges existed (per parent plan `l6-gravity-hybrid-7c4e2a`):

| Cat | Count | Targets | Why they exist |
|---|---:|---|---|
| **A — Types/constants** | ~10 | `L0/types/determinism_types.py`, `L0/config/path_constants.py`, `L3/types/human_decision_artifact_types.py`, `L0/enforcement/mutation_prohibition.py` | Cross-layer type contracts (HumanDecisionArtifact, SemanticClock, etc.) — semantically required, not refactor-able away |
| **B — L5 enforcement calls** | 6 | `L5/.../three_tier_compliance_enforcer.py`, `L5/.../ssot_structure_validation_enforcer.py`, `L5/.../registry_verification_enforcer.py` | Observability-of-enforcement — L6 trace-grades L5 enforcer outcomes; necessary instrumentation coupling |
| **C — L2 infrastructure** | 21 | `L2/utils/providers.py`, `L2/audit/telemetry_bus.py`, `L2/utils/write_gateway.py`, `L2/utils/execution_proof_emitter.py`, `L2/types/sealed_l2_artifact.py` | Clock providers, telemetry bus, write gateway — infrastructure crossings |

The historical "fix" was inline `# guardian: allow-layer-violation` comments at import sites, plus a long-tail effort to move reporter-class files out of L6. Without a coherent strategy, the practice was inconsistent and the count drifted.

## Decision

**Three-pronged hygiene policy**, codified here so that future Codex sessions and human authors apply it consistently:

### 1. Reporter-class files MUST move to `L_OPS` (`ops_scripts/reports/`)

A "reporter-class file" is one whose primary purpose is producing an artifact (JSON, YAML, Markdown, ledger row) consumed downstream by ops tooling. **Such files are not core observability** — they are operations on observability data.

- **Done as of 2026-05-02**: `integrity_report_generator_util.py` moved (W1.P2 + W2.P2 of `l6-gravity-hybrid-7c4e2a`, eliminated 9 L6→L2 edges)
- **Pending** (per `session-burndown-2026-05-02-c8f3a4` plan W2a/W2b/W2c):
  - `governed_handoff.py` (3 edges)
  - `async_eval_packet.py` (3 edges, highest fanout — ~12 consumer files including `tools/eval/retrieval_benchmark.py` with 28 refs)
  - `desk_d_governed_board.py` (3 edges, HITL Path D meta-learning chain)
- **Move pattern** (per parent plan §Rules):
  1. Create `ops_scripts/reports/<filename>.py` with full file content (now layer = L_OPS)
  2. Replace original L6 path with re-export shim: `from ops_scripts.reports.<name> import *  # noqa: F401, F403`
  3. Mark shim with `DeprecationWarning` and 90-day removal calendar (constitutional §3 — agent/file deletion grace period)
  4. Consumer migration is OPTIONAL during the 90-day window (shim re-exports preserve symbol availability); migrate proactively or wait for the deprecation cliff

### 2. Type-only crossings MUST keep guardian comments

Where the import is genuinely type-only (TypedDict, dataclass, Enum) and serves a cross-layer contract (e.g., `HumanDecisionArtifact` shared between L3 originator and L6 consumer), the import stays at L6 with an inline guardian comment:

```python
from agentic_core.L3_orchestration.types.human_decision_artifact_types import (  # guardian: allow-layer-violation -- Path D HITL meta-learning consumer reads canonical L3 HumanDecisionArtifact contract; type-only import, no behavior coupling
    HumanAction,
    HumanDecisionArtifact,
)
```

Guardian-comment audit (2026-05-02): **25 of 30 L6→{L1..L5} edges have inline guardian comments. The remaining 5 are L6→L0 imports, which are universally allowed per `_constants.py` doctrine** ("L0 can be imported by any layer"). **100% real-violation coverage.**

### 3. L0 imports are universally allowed (no guardian needed)

L0 is the **path-constants and determinism-types leaf**. Every layer including L6 may import from L0. The ADG layer-violation gate must NOT flag L6→L0 edges as violations. (Confirmed by inline doctrine in `agentic_core/L5_safety/config/structure_blueprint/_constants.py`: "Import canonical constants from L0 (L0 is allowed for all layers).")

The 5 currently-undocumented L6→L0 edges are a measurement artifact, not a refactor target.

## Consequences

### Positive

- **Predictable layer hygiene**: any new file under `agentic_core/L6_observability/` whose primary purpose is artifact emission lands at `ops_scripts/reports/` instead. The reviewer's heuristic is "does this file emit a downstream artifact?"
- **Guardian comments become first-class architectural records** instead of ad-hoc warnings. The convention can be CI-enforced (gate: every L6→{L1..L5} import edge in ADG MUST have a matching `guardian: allow-layer-violation` comment within 5 lines of the import statement).
- **90-day shim window** preserves backward compat — no flag-day breakage of the 22+ consumer files of `governed_handoff.py` / `async_eval_packet.py` / `desk_d_governed_board.py`.
- **L6→lower count target ≤21** is achievable after W2a+W2b+W2c land (drops 30→21 = 9-edge delta from 3 file moves at 3 edges each). Combined with W2.P2's −9 already landed, total reduction = −18 from baseline 39.

### Negative

- **Shim sprawl risk**: 4 historical shims now exist or are planned (integrity_report_generator_util — landed; governed_handoff — pending; async_eval_packet — pending; desk_d_governed_board — pending). After 90 days the shims must be deleted to avoid permanent dual-path indirection. Schedule a follow-up "shim deletion sweep" wave for 2026-08-02.
- **L3 `async_eval_packet.py` duplicate** discovered 2026-05-02: a parallel implementation exists at `agentic_core/L3_orchestration/utils/async_eval_packet.py` with diverged shape (no `frozen=True`, has `ShadowEvalPacket` not in L6, separate ingester semantics). This ADR does NOT resolve that duplication — it is captured as a **separate SSOT-consolidation task** (`DEFERRED_SCOPE: l3-l6-async-eval-packet-consolidation`). The L6→L_OPS move proceeds without touching the L3 duplicate.
- **Guardian-comment CI enforcement is not yet built**: the convention this ADR codifies is currently honor-system. A future gate `ops_scripts/ci/check_l6_guardian_coverage.py` should be authored to fail-closed on missing guardians.

### Neutral / unresolved

- **Cat B (L5 enforcement calls)**: 6 edges remain. These are observability-of-enforcement — L6 trace-grades L5 outcomes. They CAN'T move to L_OPS (would lose enforcement coupling) and they CAN'T be type-only (they call enforcer methods). They stay as L6→L5 with guardian comments forever. Documented as "structural exception."
- **Cat C residual after W2 moves**: ~12 edges from `providers.py` (clock), `telemetry_bus.py`, `write_gateway.py`, `sealed_l2_artifact.py`. These are infrastructure couplings — clock + bus + gateway are inherently shared across layers. Stay as guardian-marked imports.

## Cross-References

- `adg-canonical-invariants.md` §6 — Layer Criticality Multipliers (L6 = ×0.75)
- `adg-canonical-invariants.md` §3 — The 5 ADG Surfaces (Observability, Execution, Write, Security, State)
- ADR-074 — Runtime bucket as OTel view (related: how L6 emits telemetry)
- ADR-035 — Layered adapter composition is not duplication (related: when cross-layer files are NOT a violation)
- ADR-079 — L2 agent graph-layer contract (related: how lower layers consume graph data)
- Constitutional rule §22 — ADG graph-layer primary driver for refactoring
- Constitutional rule §3 — Agent deletion authorization (90-day deprecation rule applied here to shim removal)
- Parent plan: `.claude/plans/l6-gravity-hybrid-7c4e2a.md`
- Session-execution plan: `.claude/plans/session-burndown-2026-05-02-c8f3a4.md`

## Acceptance Criteria

- [x] Decision documented in writeable ADR file — `docs/architecture/adr/ADR-095-l6-observability-dependency-hygiene.md` (this file)
- [x] Three-pronged policy stated (reporter-move + guardian-comment + L0-universal-allow)
- [x] All 25 real cross-layer L6→{L1..L5} edges have inline guardian comments (verified 2026-05-02 via `artifacts/_tmp_w3_audit.py`)
- [ ] **Pending W2a/b/c**: 3 reporter files moved to `ops_scripts/reports/` with shims (drops L6→lower count 30→21)
- [ ] **Pending W2 follow-up**: 90-day shim deprecation calendar tracked; final shim-deletion wave scheduled 2026-08-02
- [ ] **Pending separate SSOT task**: L3 `async_eval_packet.py` duplicate reconciled (deferred-scope captured)
- [ ] **Pending future gate**: `ops_scripts/ci/check_l6_guardian_coverage.py` authored to enforce guardian convention CI-wide
