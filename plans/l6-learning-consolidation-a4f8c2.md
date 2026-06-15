---
plan_format: v2
title: L6_learning → L6_system_learning consolidation
slug: l6-learning-consolidation-a4f8c2
tier: T3
status: TODO
owner: feat/l6-learning-consolidation
created: 2026-06-15
adr_required: true
migration_receipt_required: true
---

# L6_learning → L6_system_learning consolidation

## Context (SCQA)

- **Situation.** L6 is doctrinally **one layer with two physical surfaces**
  ([L6_mental_model.md](docs/reference/_notes/L6_mental_model.md)):
  `agentic_core/L6_observability/` (passive) and `agentic_core/L6_system_learning/`
  (active — canonical per W5 `PATH_RENAME_CANONICAL`, 2026-05-25).
- **Complication.** A **third** folder, `agentic_core/L6_learning/` (6 modules, added
  2026-05-11, frozen 2026-05-15), does active-L6 work — completed-run evaluation, RCA
  synthesis, future-run promotion gauntlet — that **overlaps the active surface's
  chapter 06.7** (`engines/gauntlet_gate.py`, `engines/incident_rca_engine.py`,
  `pipelines/approval_gates.py`, all added 2026-05-25). It is a **pre-W5 orphan** that was
  never folded into the consolidation, yet remains **live-wired**: its
  `package_driven_l6_binding.py` is the path consumed by `UWG/package_driven_write_admission.py`,
  the **G29 firewall gate**, and `apps_underwriting_ai/runtime/l6_shadow.py`.
- **Question.** Where should `L6_learning` be consolidated — and how, without breaking the
  live UWG/G29 promotion path?
- **Answer.** Merge `L6_learning` into `agentic_core/L6_system_learning/` (chapters 06.3–06.7),
  reconciling the duplicated RCA + gauntlet logic, leaving a compat shim at the old path, and
  re-pointing the (small) consumer set. **Not** a new root `system_learning/` package — that
  name was deliberately retired in W5.

> **Canonicity resolution (from git history + ADG fan-in):** `L6_system_learning` is canonical
> (newer + doctrinally declared); `L6_learning` is the stray pre-W5 implementation that happens to
> be the operationally-wired binding. Merge direction = fold `L6_learning` **into**
> `L6_system_learning`, preserve UWG/G29 behavior, deprecate the old path.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | Canonicity ADR + scope freeze | ~40k | L6_system_learning is canonical target | DONE | ✅ ADR-105 authored; merge direction + target chapters fixed |
| W2 | P2 | Map 6 modules → 06.x chapters; reconcile RCA + gauntlet dupes | ~80k | Overlap is reconcilable, not divergent | DONE | ✅ Resolved: "dupes" are distinct lineages → cohesive relocate to `future_run_promotion/`, keep both |
| W3 | P3 | Physical move + compat shim + migration receipt | ~70k | Forward-alias shim pattern (W5 precedent) works | TODO | Files under L6_system_learning; shim+`DeprecationWarning` at old path; receipt written |
| W4 | P4 | Re-point consumers + gates (imports + string refs) | ~60k | Consumer set is small (ADG-confirmed) | TODO | All importers + firewall/string-ref gates updated; no stale `L6_learning` import |
| W5 | P5 | Verify (G29 + L6 tests + smoke) + schedule shim sunset | ~50k | G29/observer-law tests are the proof surface | TODO | G29 firewall + L6 promotion/observer-law tests green; import smoke exits 0 |

### Phase Progress

| Phase | Title | Scope | Status |
|---|---|---|---|
| P1 | Canonicity ADR | Decide + record merge direction (ADR-105) | DONE |
| P2 | Overlap reconciliation | RCA + gauntlet de-dup design | DONE |
| P3 | Move + shim | git mv + compat alias + receipt | TODO |
| P4 | Rewire consumers | imports + CI string refs | TODO |
| P5 | Verify + sunset | gates/tests + shim TTL | TODO |

## ADG_HOTSPOT_REPORT

Snapshot: `adg_indexed_06142026_1721.sqlite` (backend=sqlite, ADG fan-in via canonical `dst_id` query).

| rank | file | layer | violations | fan_in (prod imports) | impact | archetype | surfaces |
|---|---|---|---|---|---|---|---|
| 1 | `agentic_core/L6_learning/package_driven_l6_binding.py` | L6 | 0 | 1 (UWG-wired) | low | SAFETY_GATEKEEPER | Write, Security |
| 2 | `agentic_core/L6_learning/promotion_gauntlet.py` | L6 | 0 | 0 (internal) | low | SAFETY_GATEKEEPER | Security |
| 3 | `agentic_core/L6_learning/types.py` | L6 | 0 | internal | low | STATE_NODE | State |
| 4 | `agentic_core/L6_learning/completed_run_evaluator.py` | L6 | 0 | 0 | low | ORCHESTRATOR | Observability |
| 5 | `agentic_core/L6_learning/rca_synthesizer.py` | L6 | 0 | 0 | low | ORCHESTRATOR | Observability |
| 6 | `agentic_core/L6_learning/future_run_proposal_builder.py` | L6 | 0 | 0 | low | ORCHESTRATOR | State |

Real production import fan-in of the whole package = **2 files**
(`apps_underwriting_ai/runtime/l6_shadow.py`, `ops_scripts/ci/check_g29_firewall.py`) + 7 tests +
internal self-imports. Blast radius is **small** — the risk is behavioral (UWG/G29 promotion
contract), not structural breadth.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views Consulted
- `mv_graph_reverse_dependency_hotspots` — L6_learning modules absent from top reverse-dependency
  hotspots (confirms low fan-in).
- `mv_hotspot_centrality` — no L6_learning module appears as a high-centrality node.
- `mv_dependency_cone_risk` — L6_learning cone is shallow (no deep downstream cascade).

### Semantic Edges Used
- `imports` (canonical SQLite `edges.dst_id`) — inbound importers = 2 prod + 7 tests + internal.
- `covers` (test→module) — 7 test files cover the package (test surface to preserve).
- `emits_side_effect` / `resolves_callsite` — internal-only; no cross-layer side-effect fan-in.

### Pre-Built P-Views Cross-Referenced
- No `v_p0_*` / `v_p1_*` concerns intersect L6_learning (no provider-bypass / write-bypass-UWG
  flags — consistent with its observer-law "no direct L4 write" design).

### Graph-Layer-Derived Priority
The binding (`package_driven_l6_binding.py`) is the only externally-load-bearing node (UWG + G29).
All others are internal or test-only. Sequence the merge so the binding's UWG/G29 contract is
preserved and verified last (W5), not the raw file count.

## Wave W1 — Canonicity ADR + scope freeze

- Author ADR (`docs/architecture/adr/ADR-<n>-l6-learning-consolidation.md`): record that
  `L6_system_learning` is canonical (newer, W5-declared) and `L6_learning` folds in; cite the git
  timeline (L6_learning 05-11→05-15 vs 06.7 engines 05-25) and the live-wiring fact.
- Freeze scope: 6 source modules + their `__init__` re-exports; the 2 prod consumers + 7 tests +
  firewall/string-ref gates. No behavior changes in this wave.
- Decision type: `architecture_choice` — confirm via the ADR, not a code edit.

## Wave W2 — Map modules → 06.x chapters; reconcile duplicates ✅ (design resolved)

### Finding (revises the W1 assumption)

The apparent `L6_system_learning` "duplicates" are **a parallel, differently-typed lineage**, not
duplicate implementations of `L6_learning`:

| Concern | `L6_learning` (W10) | `L6_system_learning` (canonical) | Same thing? |
|---|---|---|---|
| RCA | `RCASynthesizer` → `RCAPacket` (gate-failure / judge-disagreement pattern extraction) | `IncidentRCAEngine` (S3B) → `RCAReport`/`RCAFinding` (span localization, hashable, signed) | **No** |
| Gauntlet | `PromotionGauntlet` **`GATE_ID="G29"`** → `L6GauntletResult` (10 safety checks) | `GauntletGate` (C6, 3-stage) → `GauntletResult` | **No — G29 exists ONLY in L6_learning** |
| Approval | (none) | `ApprovalGate` / `RiskTierClassifier` (G-16-28) | L6_learning has no equivalent |
| Proposal/eval | `CompletedRunEvaluator`, `FutureRunProposalBuilder` (stub-heavy W10 scaffold) | ~60 mature engines (06.3–06.6) | Overlapping concern, different contracts |

`L6_learning` is **internally cohesive** (every module imports the `__init__` type vocabulary; the
binding wires all five into `process_completed_run`) and **stub-heavy** (placeholder method bodies).
Its `RCAPacket` / `L6GauntletResult` / `ObserverLawReceipt` type vocabulary is **distinct** from the
canonical surface's `RCAReport` / `GauntletResult`.

### Decision — relocate as a cohesive submodule (keep-both, distinct roles)

Move the whole `L6_learning` package **intact** to a new chapter-06.7 submodule
**`agentic_core/L6_system_learning/future_run_promotion/`**, preserving its own type vocabulary, its
G29 `PromotionGauntlet`, the `ObserverLawValidator`, and the `PackageDrivenL6Binding`. **Do not**
dissolve its modules into the existing S3B/C6/G-16 engines.

- **Why dominant:** the type contracts differ, and **G29 is firewall/UWG-load-bearing** — collapsing
  `PromotionGauntlet` into `GauntletGate` would re-implement the firewall contract from scratch
  (high risk to `check_g29_firewall.py` + `test_l6_observer_law_prohibitions.py`) for no functional
  gain. A directory relocation preserves behavior byte-for-byte.
- **Rejected (deferred):** deep type-unification (`RCAPacket`→`RCAReport`,
  `PromotionGauntlet`→`GauntletGate`). Large rewrite, breaks G29 consumers + observer-law tests;
  belongs in a separate follow-up once both lineages are co-located and understood.

### Revised per-module mapping (cohesive move — internal paths unchanged)

| `L6_learning/` module | → `L6_system_learning/future_run_promotion/` | Notes |
|---|---|---|
| `__init__.py` (type vocab + `PromotionGauntlet` re-export) | `__init__.py` | unchanged; rewrite intra-package imports `agentic_core.L6_learning` → `…future_run_promotion` |
| `types.py` (re-export alias) | `types.py` | unchanged |
| `completed_run_evaluator.py` | `completed_run_evaluator.py` | unchanged |
| `rca_synthesizer.py` | `rca_synthesizer.py` | coexists with `engines/incident_rca_engine.py` (distinct role) |
| `future_run_proposal_builder.py` | `future_run_proposal_builder.py` | unchanged |
| `promotion_gauntlet.py` (**G29**) | `promotion_gauntlet.py` | **verbatim** — G29 + ObserverLawValidator preserved |
| `package_driven_l6_binding.py` | `package_driven_l6_binding.py` | UWG promotion entrypoint |

### Merged public API

- New canonical import root: `from agentic_core.L6_system_learning.future_run_promotion import …`
  (same symbol names: `PromotionGauntlet`, `FutureRunPromotionRequest`, `L6GauntletResult`,
  `CompletedRunEvaluator`, `RCASynthesizer`, `PackageDrivenL6Binding`, …).
- Old root `agentic_core.L6_learning` → compat shim (`sys.modules` forward-alias + `DeprecationWarning`).
- ⚠️ Hard constraint (carried from W1): `L6GauntletResult.gate_id` / G29 semantics + observer-law
  receipt fields survive **verbatim** — a relocation, not a redesign.

## Wave W3 — Physical move + compat shim + receipt

- `git mv` the **whole package** `agentic_core/L6_learning/*.py` →
  `agentic_core/L6_system_learning/future_run_promotion/` (cohesive directory move per W2 — internal
  module layout unchanged). Add `__l6_chapter__ = "06.7"` to the new package `__init__`.
- Rewrite intra-package imports inside the moved modules: `from agentic_core.L6_learning…` →
  `from agentic_core.L6_system_learning.future_run_promotion…` (6 modules cross-reference each other).
- Compat shim at `agentic_core/L6_learning/__init__.py` (+ per-module shims for the 4 submodules that
  external/test code imports directly): `sys.modules` forward-alias to the new paths +
  `DeprecationWarning` (W5 `l6-repo-reorganization` precedent).
- Write migration receipt → `artifacts/governance/migration_receipts/<ts>_l6_learning_consolidation.json`
  (classification GENERIC_INFRASTRUCTURE, justification, files, tests). Per
  [agentic-core-glob-lock.md](.claude/rules/agentic-core-glob-lock.md) + CoreAddition Author-Gate.

## Wave W4 — Re-point consumers + gates

- Import consumers: `apps_underwriting_ai/runtime/l6_shadow.py`, `ops_scripts/ci/check_g29_firewall.py`,
  7 test files.
- String-ref gates (scan/allowlist the literal path — update the path constant, not an import):
  `ops_scripts/ci/check_package_driven_l6_only.py`, `check_no_l6_direct_l4_write.py`,
  `check_no_l6_current_run_mutation.py`, `check_no_l6_x3_emit.py`, and any `L6_learning` literal in
  `UWG/package_driven_write_admission.py`.
- Leave the shim in place so a missed reference fails soft (DeprecationWarning) rather than ImportError.

## Wave W5 — Verify + schedule sunset

- Run: `python ops_scripts/ci/check_g29_firewall.py`; `python -m pytest tests/governance/test_l6_promotion_uwg_required.py tests/runtime/test_l6_learning_firewall.py tests/runtime/test_l6_observer_law_prohibitions.py tests/unit/agentic_core/L6_learning/test_promotion_gauntlet.py -q`.
- Import smoke: `python -c "import agentic_core.L6_system_learning, agentic_core.L6_learning"` exits 0 (shim resolves with DeprecationWarning).
- Regenerate ADG slice; confirm fan-in now points at L6_system_learning.
- Record shim sunset date (2 weeks → 2026-06-29) per ADR-082 migration discipline.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | ADR merged recording canonical target + merge direction | ADR file present + linked |
| 2 | 6 modules relocated under `agentic_core/L6_system_learning/`; no logic dropped | git diff + per-module mapping table |
| 3 | Duplicate RCA + gauntlet logic reconciled (one canonical each, or distinct documented roles) | W2 design doc + code review |
| 4 | Compat shim + `DeprecationWarning` at `agentic_core/L6_learning/`; migration receipt written | shim import test + receipt path |
| 5 | All importers + firewall/string-ref gates re-pointed; zero stale `L6_learning` imports | ADG fan-in re-query = 0 prod imports of old path |
| 6 | **Smoke-run:** `python -c "import agentic_core.L6_system_learning, agentic_core.L6_learning"` exits 0 | command output |
| 7 | G29 firewall gate + L6 promotion/observer-law tests green | pytest + gate output |

### Verification vs Deferral

| Item | Verify now | Defer |
|---|---|---|
| UWG/G29 promotion contract preserved | ✅ W5 | — |
| Observer-law receipt fields intact | ✅ W5 | — |
| Compat shim resolves old imports | ✅ W5 | — |
| Old-path shim physical deletion | — | After 2026-06-29 sunset |
| Deeper de-dup across L6_observability `legacy_parallel/promotion_gauntlet.py` | — | Separate plan (out of scope) |
