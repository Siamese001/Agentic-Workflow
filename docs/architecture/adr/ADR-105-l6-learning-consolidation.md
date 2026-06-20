# ADR-105 — Consolidate `agentic_core/L6_learning/` into `agentic_core/L6_system_learning/`

- **Status:** Accepted
- **Date:** 2026-06-15
- **Branch:** `feat/l6-learning-consolidation`
- **Plan:** [plans/l6-learning-consolidation-a4f8c2.md](../../../plans/l6-learning-consolidation-a4f8c2.md)
- **Builds on:** ADR / plan `l6-repo-reorganization-mental-model-c4e8f2` (W5 `PATH_RENAME_CANONICAL`, 2026-05-25),
  which established the two-surface L6 model and the canonical active path
  `agentic_core/L6_system_learning/`.

## Context

L6 is doctrinally **one layer with two physical surfaces**
([docs/reference/_notes/L6_mental_model.md](../../reference/_notes/L6_mental_model.md)):

- `agentic_core/L6_observability/` — the **passive** surface (exhaust capture).
- `agentic_core/L6_system_learning/` — the **active** surface (learn from exhaust → propose →
  gauntlet → UWG promotion). Canonical install path per W5 `PATH_RENAME_CANONICAL` (2026-05-25),
  `__l6_surface__ = "active"`, ~100 modules across 27 chapter subpackages.

A **third** folder exists outside that model: `agentic_core/L6_learning/` (6 modules). Its own
docstring describes "W10 — Package-Driven Completed-Run Evaluation & Future-Run Promotion." Its
modules do active-L6 work that **overlaps chapter 06.7** ("Gauntlet → Approval → UWG Promotion →
Future Run") and 06.3–06.6 of the canonical active surface:

| `L6_learning` module | Overlaps in `L6_system_learning` |
|---|---|
| `rca_synthesizer.py` | `engines/incident_rca_engine.py`, `types/rca_types.py` |
| `promotion_gauntlet.py` | `engines/gauntlet_gate.py`, `pipelines/approval_gates.py` |
| `completed_run_evaluator.py` / `future_run_proposal_builder.py` | 06.3–06.6 engines/pipelines |
| `types.py` | `types/` (promotion/RCA dataclasses) |
| `package_driven_l6_binding.py` | 06.7 UWG promotion entrypoint |

### Evidence consulted

- **Git timeline.** `L6_learning` modules were added **2026-05-11** and frozen **2026-05-15**. The
  `L6_system_learning` 06.7 engines (`gauntlet_gate.py`, `incident_rca_engine.py`,
  `approval_gates.py`) were added **2026-05-25** — i.e. the W5 consolidation, **14 days later**, and
  `L6_system_learning` is the doctrinally-declared canonical active surface. ⇒ `L6_learning` is a
  **pre-W5 orphan**, not a newer replacement.
- **ADG fan-in** (canonical snapshot `adg_indexed_06142026_1721.sqlite`, `edges.dst_id` query). Real
  production importers of the whole `L6_learning` package = **2 files**:
  `apps_underwriting_ai/runtime/l6_shadow.py` and `ops_scripts/ci/check_g29_firewall.py`; plus 7
  test files and internal self-imports. The earlier grep hits in
  `UWG/package_driven_write_admission.py`, `check_package_driven_l6_only.py`, and `check_no_l6_*.py`
  are **string references** (path scans / allowlists), not Python import edges.
- **Live-wiring.** Despite being the older artifact, `package_driven_l6_binding.py` is the
  operationally-wired promotion binding (consumed by UWG + the G29 firewall gate +
  `apps_underwriting_ai`). The merge is therefore behavioral-risk-bearing, not a cosmetic move.

## Decision

1. **Consolidate `agentic_core/L6_learning/` into `agentic_core/L6_system_learning/`**, mapping its
   six modules onto chapters 06.3–06.7, and **reconciling the duplicated RCA and gauntlet logic**
   (keep one canonical implementation each, or keep both with explicitly documented distinct roles).
2. **`L6_system_learning` is the canonical target** — it is the newer, doctrinally-declared active
   L6 surface. `L6_learning` folds in; the merge direction is one-way.
3. **Reject a new root `system_learning/` package.** That name was the **pre-W5** package name and
   was deliberately renamed into `agentic_core/L6_system_learning/` in W5. Re-creating a root
   package would reverse a landed canonical decision. (The user's "system_learning" instinct is
   directionally correct; the canonical home is the `agentic_core/L6_system_learning/` package, not
   a root one.)
4. **Preserve the UWG/G29 promotion contract verbatim.** `L6GauntletResult.gate_id` / G29 semantics
   and the observer-law receipt fields must survive unchanged — the G29 firewall gate and
   `test_l6_observer_law_prohibitions.py` depend on them.
5. **Archival over deletion.** Leave a `sys.modules` forward-alias **compat shim** +
   `DeprecationWarning` at `agentic_core/L6_learning/` (the W5 precedent), with a 2-week sunset
   (→ 2026-06-29). No hard delete in this change.
6. **Migration receipt required** (`agentic_core/**` edit) per
   [.codex/rules/agentic-core-glob-lock.md](../../../.codex/rules/agentic-core-glob-lock.md) +
   the CoreAddition Author-Gate.

## Scope freeze (W1)

**In scope:** the 6 `L6_learning` source modules + their `__init__` re-exports; the 2 production
consumers; the 7 covering tests; the firewall + string-ref gates listed above; this ADR; the
migration receipt; the compat shim.

**Out of scope (deferred to a separate plan):** deeper de-duplication against
`agentic_core/L6_observability/shadow_eval/legacy_parallel/promotion_gauntlet.py` and the parallel
`utils/evaluation/` gauntlet copies — that is a wider L6 cleanup, not this consolidation.

## Consequences

- **Positive.** Restores the documented two-surface L6 model; removes a stray third active-L6 folder;
  collapses duplicate RCA/gauntlet code paths onto one canonical surface. Blast radius is small
  (ADG-confirmed: 2 prod importers + 7 tests).
- **Negative / risk.** The merge is a de-dup, not a clean move — RCA/gauntlet reconciliation (W2) is
  the real work and the place a behavior could silently drift. Mitigated by: (a) sequencing the
  UWG-wired binding's verification last (W5), (b) the compat shim making any missed reference fail
  *soft* (DeprecationWarning) rather than ImportError, (c) gating on the G29 firewall +
  observer-law/promotion tests as the proof surface.
- **Reversibility.** Until the 2026-06-29 shim sunset, the old import paths still resolve, so the
  change is reversible by reverting the consumer re-points and restoring the modules at the old path.

## References

- Plan: [l6-learning-consolidation-a4f8c2.md](../../../plans/l6-learning-consolidation-a4f8c2.md)
- L6 mental model: [docs/reference/_notes/L6_mental_model.md](../../reference/_notes/L6_mental_model.md)
- Core edit guard: [.codex/rules/agentic-core-glob-lock.md](../../../.codex/rules/agentic-core-glob-lock.md)
- Prior consolidation precedent: `l6-repo-reorganization-mental-model-c4e8f2` (W5 PATH_RENAME_CANONICAL)
