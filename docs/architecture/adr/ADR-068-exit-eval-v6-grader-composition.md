# ADR-068 — Exit-Eval v6 grader composition runtime types (Wave 3)

**Status**: Accepted (scoped runtime types complete)
**Date**: 2026-04-26
**Wave**: exit-eval-v6 deferred-scope Wave 3
**Promotes**: 30 design rows → OK (§1, §2, §3, §3-table, §4, §5.1, §7) + 2 ADR-068 acceptance rows

**Current-state note (2026-06-15):** This ADR intentionally covers grader composition runtime types and BUS-P row shape. Calibration cadence, multi-judge consensus, and bypass-resistance harnesses remain separate subsystem work, not incomplete ADR-068 scope.

---

## Context

`docs/reference/05_Exit_Evaluation_and_Control/grader_composition_spec.md` is the Exit-Eval v6 grader contract, drawn from Anthropic's "Demystifying Evals for AI Agents" (A1) guidance. It defines:

- **§1 Grader taxonomy** — code-based, model-based (LLM judge), human (offline calibration only)
- **§2 Rubric structure** — named dimensions with grader_class, weight, threshold, abstain_allowed
- **§3 Composition modes** — binary (AND), weighted (sum × weight ≥ aggregate), hybrid (hard gates AND + weighted soft)
- **§3 table** — per-gate composition (X1A binary, X1B hybrid, X1C binary, X1D weighted, X1E hybrid, X1F hybrid, X1G binary)
- **§4 Partial credit** — per-dimension scores preserved on BUS-P and HITL packets
- **§5.1 Abstain protocol** — model-based dimensions return `UNKNOWN` → routes to X3B with `JUDGE_ABSTAINED`
- **§5.2 Calibration cadence** — initial κ ≥ 0.80, quarterly recalibration, weekly drift detection
- **§5.3 Rubric bug detection** — known-bad/known-good sets + 98% pass-rate flag
- **§5.4 Multi-judge consensus** — majority vote / median / unanimous-pass routing
- **§6 Bypass resistance** — context isolation, delimiter wrap, prompt-injection classifier, immutable versioning
- **§6.3 Adversarial eval** — graders themselves graded against bypass attempts
- **§7 BUS-P row contract** — exact emission shape per gate per run

Wave 3 implements the **runtime types** for §1-§4, §5.1, §7 — the contracts every grader and every gate referencing a rubric must conform to. The remaining sections are full subsystems (data store + scheduler for §5.2; judge orchestrator for §5.4; runtime context-isolation harness for §6) and are deferred.

## Decision

Add `agentic_core/L3_orchestration/exit_eval/v6/grader_composition.py` with these exports:

| Symbol | Spec section | Purpose |
|---|---|---|
| `GraderClass` enum | §1 | The 3 grader classes |
| `RubricDimension` | §2 | One named dimension with weight, threshold, hard-gate flag, abstain-allowed flag |
| `Rubric` | §2 | Rubric for a gate: `rubric_id`, `gate`, `version`, `composition`, `aggregate_threshold`, `dimensions` |
| `CompositionMode` enum | §3 | BINARY \| WEIGHTED \| HYBRID |
| `GATE_COMPOSITION_MODE: dict[gate_id, CompositionMode]` | §3 table | Per-gate mode mapping |
| `DimensionScore` | §4 | One per-dimension score: name, score, weight, threshold, passed, abstain |
| `CompositionResult` | §3+§4 | Output of `compose()`: passed, aggregate_score, abstain, failed_dimension_names, dimension_vector, reason_codes |
| `compose(rubric, scores) -> CompositionResult` | §3 | Apply composition mode |
| `ABSTAIN_REASON_CODE = "JUDGE_ABSTAINED"` | §5.1 | Reason code emitted on abstain |
| `BusPRow` + `BusPRow.from_composition(...)` | §7 | BUS-P emission contract |

### `compose()` invariants enforced

1. **§2** — every `RubricDimension` is enforced: `abstain_allowed=True` rejected if `grader_class != MODEL_BASED`; `scale_min < scale_max`.
2. **§2** — every `Rubric` requires ≥1 dimension; HYBRID requires ≥1 hard-gate dimension.
3. **§3** — `compose()` requires every rubric dimension to have a corresponding `DimensionScore`.
4. **§3.1 BINARY** — all dimensions must `passed=True` for the result to pass.
5. **§3.2 WEIGHTED** — `aggregate = Σ(weight × normalized_score) / Σ(weight)`; result.passed iff `aggregate ≥ aggregate_threshold`.
6. **§3.3 HYBRID** — hard_gates AND + weighted_soft AND. Either failing denies.
7. **§4** — `CompositionResult.dimension_vector` always contains all input scores (preserved for BUS-P + HITL packets).
8. **§5.1** — any abstaining dimension flips `result.abstain=True` AND forces `result.passed=False`, even if the numeric aggregate clears the threshold. Reason code `JUDGE_ABSTAINED` added.

### `BusPRow` emission contract

- One row per gate per run (append-only; downstream consumers do not edit).
- Pre-built `BusPRow.from_composition(run_id, rubric, result, track, trajectory_class)` factory ensures the §7 schema is honored exactly.
- `dimension_vector` is a list of dicts (not dataclass instances) so the row is JSON-serializable for BUS transport.

## Why §5.2-5.4 and §6 stay DESIGN

| Section | Why deferred |
|---|---|
| §5.1 abstain rate >5% trigger | Requires rolling-window abstain rate tracker (data store + scheduler) |
| §5.2 SME calibration | Needs `data/judge_calibration/` schema, κ computation pipeline, quarterly cadence runner |
| §5.3 rubric bug detection | Needs known-bad/known-good test set library + 98%-flag detector |
| §5.4 multi-judge consensus | Needs N-judge runner + majority/median/unanimous-pass orchestrator |
| §6.1 context isolation | Needs runtime-level judge harness with separate session contexts |
| §6.2 injection classifier | Needs a deployed prompt-injection classifier model + score threshold |
| §6.3 adversarial eval | SME-curated content authoring, not code |
| §6.4 immutable versioning | Partially handled by `Rubric.rubric_id` + `version` fields; full enforcement needs registry + diff tooling |

These remain DESIGN rows in the matrix and constitute Wave 4+ deferred scope.

## Implementation summary

| File | Change |
|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/grader_composition.py` | NEW module — 10 public symbols |
| `agentic_core/L3_orchestration/exit_eval/v6/__init__.py` | Re-export the 10 symbols + add to `__all__` |
| `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_grader_composition.py` | NEW — 31 unit tests covering §1, §2, §3.1, §3.2, §3.3, §3 table, §4, §5.1, §7, integration |
| `tools/analysis/exit_v6_requirements_registry.yaml` | 30 row promotions DESIGN→OK + 2 ADR-068 acceptance rows |

## Test posture

- 482 v6 tests pass (was 451 after Wave 2; +31 grader-composition tests)
- 0 v6 regressions
- All §3 composition modes round-trip through `compose()` with their named invariants
- §5.1 abstain protocol verified: `result.passed=False` even when aggregate ≥ threshold

## Consequences

**Positive**:

- Future X1B/X1D/X1E/X1F gate refactors can swap to `compose()` and emit `BusPRow` directly — the type contract is pinned.
- §4 partial-credit shape is now the SSOT — HITL `H2 Materialize` can reference `dimension_vector` without re-modelling.
- §5.1 abstain-routes-to-X3B invariant is no longer policy prose; it's enforced at type level by `compose()`.

**Negative**:

- Existing X1B/X1D/X1E/X1F gates in `x1_gates.py` do not yet use `Rubric` + `compose()` — they still emit `GateVerdict` directly with hand-rolled aggregate logic. Wire-up is a separate refactor (~10-15 LOC per gate); for now the new types are orthogonal infrastructure that future refactors will adopt.

## Linked

- Spec: `docs/reference/05_Exit_Evaluation_and_Control/grader_composition_spec.md`
- Wave 1 ADR: `docs/architecture/adr/ADR-065-x3f-break-glass-allow-disposition.md`
- Wave 2 ADR: `docs/architecture/adr/ADR-067-exit-eval-v6-hardening-tractable-subset.md`
- Wave 5 ADR: `docs/architecture/adr/ADR-066-exit-eval-v6-historical-gap-closure.md`
- Code: `agentic_core/L3_orchestration/exit_eval/v6/grader_composition.py`
- Tests: `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_grader_composition.py`
- Matrix: `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`
