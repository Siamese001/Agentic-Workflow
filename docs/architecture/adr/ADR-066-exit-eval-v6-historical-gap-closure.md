# ADR-066 — Exit-Eval v6 historical gap closure (Wave 5)

**Status**: Accepted
**Date**: 2026-04-26
**Wave**: exit-eval-v6 deferred-scope Wave 5
**Closes**: 17 historical/justification rows in `gap_analysis_v3_vs_industry_2026.md` (registry IDs `GA.G1..GA.G10`, `GA.SEV.*`)

---

## Context

`docs/reference/05_Exit_Evaluation_and_Control/gap_analysis_v3_vs_industry_2026.md` is a **historical analysis document** (date: 2026-04-24) that compared the prior v3 exit-control surface against 2025-2026 industry guidance from Anthropic (A1), Google Cloud (G1), and OpenAI (O1). It identified **G1..G10** — ten gaps — and assigned **P0..P3** severity to drive the v4/v6 redesign.

The matrix (`docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`) currently treats all 17 rows from this document as `DESIGN`. This is technically correct (the document itself is historical justification, not implementation) but **uninformative** because most of these gaps have been **closed in code** — they were the *reason* v4/v6 exists.

This ADR is the closure record. It links each historical gap to its v6 runtime artifact, marks closed gaps as `OK`, and explicitly retains the severity-justification rows as `DESIGN` because they are historical metadata, not pending work.

## Gap-by-gap closure map

| Gap | Source | Severity | v6 closure | Evidence in code |
|---|---|---|---|---|
| **G1** Trajectory / process eval | A1+G1+O1 | P0 | **CLOSED** by X1E | `eval_x1e` in `agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py`; reason codes `WRONG_TOOL`, `ARG_EXTRACTION_FAIL`, `STEP_INEFFICIENT`, `REASONING_INCOHERENT`, `HANDOFF_MISROUTED`, `TRAJECTORY_SUSPECT` |
| **G2** Stochastic consistency (`pass^k`) | A1 | P1 | **CLOSED** by X1G + X1I | `eval_x1g` (consistency) + `eval_x1i` (observability surface); `grader_composition.consistency.pass_power_estimate` field carries `pass^k` over `theta` |
| **G3** Capability/regression tracks | A1 | P2 | **CLOSED** structurally | `ExitReviewPacket.track_label` field at types.py:124, defaulting to `"production"` with values `capability \| regression \| production \| shadow-candidate` |
| **G4** LLM-judge calibration | A1+G1 | P1 | **PARTIAL** (abstain only); full calibration system deferred to Wave 3 | `output.judge_abstained=True` routes to X3B with `JUDGE_ABSTAINED`; full κ/drift/cadence is Wave 3 (`exit-eval-v6-grader-composition`) |
| **G5** Adversarial / security pillar | G1 | P0 | **CLOSED** by X1F | `eval_x1f` in x1_gates.py; reason codes `PROMPT_INJECTION_DETECTED`, `SYSTEM_PROMPT_LEAK`, `JAILBREAK_DETECTED`, `BIAS_DELTA_EXCEEDED`, `ADVERSARIAL_CRASH` |
| **G6** Grader composition contract | A1 | P1 | **PARTIAL**; structural hook present, full binary/weighted/hybrid engine deferred to Wave 3 | `ExitReviewPacket.grader_composition` field at types.py:123; full composition modes are Wave 3 |
| **G7** Partial credit | A1 | P2 | **PARTIAL**; reason-code carries near-miss signal; full per-dim vector deferred to Wave 3 | `GateVerdict.reason_codes` list distinguishes failure modes; full `dimension_vector` to BUS P is Wave 3 |
| **G8** Per-trial environment isolation | A1 | P2 | **CLOSED** by X1C | `eval_x1c` emits `ENV_CONTAMINATED` (env_contaminated, learning_bus_contamination) and `TRIAL_STATE_LEAK` reason codes at x1_gates.py:152-161 |
| **G9** Grader-bypass resistance | A1 | P2 | **PARTIAL**; full bypass-resistance harness (context isolation, delimiter wrap, injection classifier on judge calls) deferred to Wave 3 | Stated as v4 invariant 7 in `05_exec.md`; full enforcement is Wave 3 |
| **G10** Runtime → regression dataset pipeline | G1 | P3 | **DEFERRED** to Wave 4 | `exit-eval-v6-bus-pt-pipeline` plan covers BUS P/T → candidate pool → curation → golden set → graduation |

## Decision

For each row, set the registry `check` to reflect **what v6 actually does**:

| Registry ID | Old check | New check | Reason |
|---|---|---|---|
| `GA.G1.trajectory_eval` | `v6_export` (already OK) | unchanged | already OK |
| `GA.G2.passk` | `v6_export` (already OK) | unchanged | already OK |
| `GA.G3.tracks` | `design` | `ok_static` | `track_label` field present |
| `GA.G4.judge_calibration` | `design` | `design` | partial; full system Wave 3 |
| `GA.G5.adversarial` | `v6_export` (already OK) | unchanged | already OK |
| `GA.G6.composition` | `design` | `design` | structural only; Wave 3 |
| `GA.G7.partial_credit` | `design` | `design` | reason-codes only; Wave 3 for full vector |
| `GA.G8.trial_isolation` | `design` | `ok_static` | `ENV_CONTAMINATED`/`TRIAL_STATE_LEAK` codes wired |
| `GA.G9.bypass_resistance` | `design` | `design` | Wave 3 |
| `GA.G10.runtime_to_regression` | `design` | `design` | Wave 4 |
| `GA.SEV.G1_P0` .. `GA.SEV.G10_P3` (10 rows) | `design` | `design` | historical metadata; not pending work — stays DESIGN by design |

**Net effect**: 2 historical rows promoted to `ok_static` (G3, G8) with evidence pointers. The remaining 15 rows stay `DESIGN` with no change in semantics — they are either future work (G4 partial / G6 / G7 full / G9 / G10 → Waves 3 and 4) or pure historical metadata (the 10 severity rows).

## Why we keep severity rows as DESIGN

The `GA.SEV.G1_P0` through `GA.SEV.G10_P3` rows record the v3-era P0..P3 prioritization. They are **historical metadata** — useful for audit ("this is why v4 was built in this order") but not implementation. Promoting them to `ok_static` would falsely imply the severity rankings themselves are runtime-verified, which makes no semantic sense. Keeping them `DESIGN` correctly conveys: "documented decision, not a runtime invariant". Same shape as the gap text rows for G4/G6/G7/G9/G10 that are deferred to later waves — `DESIGN` is the honest classification.

## Consequences

**Positive**:

- Matrix becomes more truthful: "v6 already implements these gaps" is now visible in the OK count, not hidden behind blanket DESIGN labels.
- Wave 3 and Wave 4 scopes get clearer: G4 (partial → full calibration), G6, G7 (full vector), G9 → Wave 3; G10 → Wave 4.
- Operator reading the matrix sees that 5 of 10 historical gaps are closed at runtime today (G1, G2, G3, G5, G8); 4 are partial-and-Wave-3 (G4, G6, G7, G9); 1 is Wave-4 (G10).

**Negative**:

- None. This is a labeling pass; no production code changes.

**Neutral**:

- Total registry count unchanged (574 rows from Wave 1, plus 0 new from Wave 5).
- Closure ADR adds traceability between matrix labels and v6 source code locations.

## Linked

- Spec: `docs/reference/05_Exit_Evaluation_and_Control/gap_analysis_v3_vs_industry_2026.md`
- Registry: `tools/analysis/exit_v6_requirements_registry.yaml`
- Matrix: `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`
- Wave 1: `docs/architecture/adr/ADR-065-x3f-break-glass-allow-disposition.md`
- Wave 3 plan: `exit-eval-v6-grader-composition` (deferred-scope marker)
- Wave 4 plan: `exit-eval-v6-bus-pt-pipeline` (deferred-scope marker)
