# ADR-052 — X1E Trajectory Gate

**Status**: Accepted
**Date**: 2026-04-24
**Deciders**: L3 architecture owners
**Supersedes**: —
**Relates to**: ADR-023 (runtime HITL exit control), ADR-032 (LLM judge hardening), ADR-036 (runtime trace grader), ADR-037 (trajectory metrics)

## Context

v3 exit-control (`05_Live_Runtime_Exit_Control_&_Evaluation_v3.md`) evaluates **outcomes only** (X1B "answered it?", X1D "answer good?"). A run can produce a correct final answer via a broken trajectory (lucky tool choice, incorrect arg extraction that accidentally returned viable data) and v3 will clear it. Industry guidance (Google Pillar 2; OpenAI tool-selection/arg-precision) treats the trajectory — the sequence of tool calls, arguments, intermediate reasoning, and handoffs — as a first-class evaluation target.

## Decision

Add **X1E (Trajectory OK?)** as a v4 gate in `05_Live_Runtime_Exit_Control_&_Evaluation_v4.md`. Implementation in `agentic_core.L3_orchestration.exit_eval` — rubric in `config/exit_eval_rubrics/x1e_v1.yaml`.

### Dimensions (per `grader_composition_spec.md` §3)

| Dimension | Grader class | Hard gate | Why |
|---|---|---|---|
| `tool_selection_accuracy` | code_based | yes | Wrong tool = broken plan; objective check against plan catalog |
| `arg_precision` | code_based | yes | Arg extraction is deterministic; wrong args = downstream noise |
| `step_efficiency` | code_based | no | Redundant calls are wasteful, not fatal |
| `reasoning_coherence` | model_based (abstain) | no | Nuanced; LLM-judge with abstain protocol |
| `handoff_correctness` | code_based | no | Multi-agent handoff integrity |

Composition: **hybrid** (`aggregate_threshold: 0.70`). Hard sub-gates deny (X3A) on failure; soft score ≥ 0.70 required.

### Failure reason codes (from `disposition.ReasonCode`)

`WRONG_TOOL`, `ARG_EXTRACTION_FAIL`, `STEP_INEFFICIENT`, `REASONING_INCOHERENT`, `HANDOFF_MISROUTED`, `TRAJECTORY_SUSPECT`.

## Consequences

**Positive**:
- Brittle trajectories (right answer, wrong path) no longer slip into X3C commit.
- Failures surface at the specific dimension via per-dimension BUS P vector (§7 of grader spec).
- H2.2 non-agentic fallback requirement applies — `reasoning_coherence` judge must have a code-based fallback when the agentic judge is unavailable.

**Negative / accepted cost**:
- Trajectory capture adds span-event volume on BUS T (mitigated by OTel sampling — H5.3).
- Initial `tool_selection_accuracy` rubric may false-positive on unfamiliar tools until catalog matures; treat the first 2 weeks as shadow-mode (H7.3).

**Risks**:
- `reasoning_coherence` LLM-judge is the highest bypass-risk surface (§6.1-§6.3). Must run under the same X1F adversarial gate as the primary agent (H2.1). Version-pin judge model (H2.1 #4).

## Alternatives considered

1. **Skip trajectory eval, rely on X1D outcome scoring** — rejected: misses latent brittleness (see v3 coverage in `gap_analysis_v3_vs_industry_2026.md` §G1).
2. **Trajectory as advisory only (no X3A path)** — rejected: hard sub-gates (`tool_selection_accuracy`, `arg_precision`) carry safety-adjacent semantics (unauthorized tool selection = safety boundary).
3. **Pure LLM-judge trajectory grading** — rejected: fails H9 invariant (hard sub-gates require code-based graders).

## Open items

- `tool_selection_accuracy` requires a maintained plan-catalog. Owner: L1 cognition team. Tracked in plan `.claude/plans/x1e-trajectory-gate-catalog-TBD.md`.
- `reasoning_coherence` judge calibration: initial SME κ ≥ 0.80 before production (grader spec §5.2).

## References

- v4 spec: `docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v4.md` §X1E
- Hardening: `v4_hardening_addendum.md` H2 (agent-as-judge controls), H8 (fault matrix)
- Grader composition: `grader_composition_spec.md`
- Implementation: `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/`
- Rubric: `@c:/Git/Agentic-Workflow/config/exit_eval_rubrics/x1e_v1.yaml`
