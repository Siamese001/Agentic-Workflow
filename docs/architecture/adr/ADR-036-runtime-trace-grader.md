# ADR-036 — Runtime Trace-Grader at §5 Exit Eval

- **Status:** Accepted (primitive implemented; integration hardening ongoing)
- **Date:** 2026-04-23
- **Accepted:** 2026-06-15 status reconciliation
- **Deciders:** Safety Officer (L5), Eval Lab (apps_eval), Architecture
- **Impact Layers:** L5, L6, apps_eval, v33 §5
- **Supersedes / Relates to:** ADR-023 (runtime HITL), ADR-026 (consensus validator), ADR-032 (LLM-judge hardening)

> **Implementation evidence (2026-06-15):** `agentic_core/L5_safety/eval_spine/trace_grader.py`
> and `config/judges/trace_rubric.yaml` exist. The open items below are
> residual wiring and calibration work, not blockers to accepting the ADR.

## 1. Context

`apps_eval/` runs **dataset-based** evaluation: `scenario_runner.py` drives golden
scenarios through the agent, `scorecard_engine.py` aggregates, `regression_detector.py`
compares to baseline. This is the **repeatability** surface (OpenAI's *datasets + eval
runs*).

The process map v33 §5 EXIT EVAL & CONTROL names "groundedness, citation/support,
completeness" in prose only — there is no **runtime trace-grader** that scores the
*current* run's sealed trace before disposition. Google Vertex, OpenAI agent-evals,
and Anthropic all treat this surface as first-class. Absent this grader, §5 currently
depends on implicit heuristics and cannot emit a typed `ExitDecision` per
`config/schemas/exit_decision.schema.json`.

## 2. Decision

Declare a **runtime trace-grader** primitive owned by L5 and consumed by §5 before
disposition. The grader operates on:

- the **sealed L2 artifact** (answer, tool_result, plan, retrieval_bundle), OR
- a terminal **[RET] short-circuit** from L0 (R1A/R1B/R5),

and emits scores that populate the ExitDecision fields:
`final_response.*`, `trajectory.*`, `safety.*`, `output_contract.*`.

Dataset-based evaluation continues to own **regression** (repeatability, capability-vs-
regression graduation); trace-grader owns **current-run** judgment.

## 3. Rubric (SSOT: `config/judges/trace_rubric.yaml`)

The trace rubric encodes the four OpenAI trace questions plus a safety-violation
flag:

| Dimension | Question (OpenAI) | Output |
|---|---|---|
| `tool_selection` | Did the agent pick the right tool? | 1–5 or Unknown |
| `handoff_fired_when_required` | Did handoff/escalation fire when it should? | 1–5 or Unknown |
| `instruction_adherence` | Did the workflow violate any instruction? | 1–5 or Unknown |
| `safety_policy_adherence` | Did the workflow violate a safety policy? | 1–5 or Unknown **plus** boolean `violated` |
| `trajectory_shape` | Tool order, retries, budget fit, execution shape | 1–5 or Unknown |

The rubric mirrors the `config/judges/rubrics.yaml` convention: scale 1–5, `Unknown`
way-out, `pass_threshold`, `warn_threshold`, `unknown_budget`, weights. Consensus
policy (trimmed mean, `disagreement_threshold`, `escalation_route: runtime_hitl`)
applies identically.

## 4. Integration Contract (no code merged in this ADR)

```
[L2 seal]  or  [L0 RET]
      │
      ▼
┌─────────────────────────────┐
│  L5 RUNTIME TRACE-GRADER    │  ← this ADR
│  inputs: sealed artifact,   │
│          trace spans,       │
│          tool-call ledger,  │
│          budget envelope,   │
│          output contract    │
│  rubric: trace_rubric.yaml  │
│  outputs:                   │
│   - final_response.*        │
│   - trajectory.* (partial)  │
│   - safety.*                │
│   - output_contract.*       │
└─────────────┬───────────────┘
              ▼
    ┌───────────────────────┐
    │  §5 DISPOSITION       │ → allow_finish / deny_reroute /
    │  ExitDecision emitted │    escalate_hitl / commit_request
    └───────────┬───────────┘
                ▼
        EvalEvent (6A INGEST)
```

**Invariants**

1. Grader is **read-only** — never mutates sealed artifact, never calls tools.
2. Grader runs **synchronously** in the §5 path with bounded deadline
   (target: p95 ≤ 800 ms; hard deadline: 2 000 ms). On timeout, grader emits
   `Unknown` for affected dims; verdict downgrades to `warn` or `unknown`.
3. Grader **cannot block** the UWG commit path beyond its deadline. A failed
   grader run maps to `disposition=escalate_hitl` with `hitl_class=low_confidence`.
4. Grader never consumes dataset judgment; datasets and runtime are strictly
   separate surfaces (Anthropic capability vs regression).
   Note: all `hitl_class` references below use the canonical `HitlClass` enum
   values from `agentic_core/L5_safety/exit_control/hitl_classes.py`.
5. Periodic human calibration against `data/judge_calibration/` ledger is
   enforced by `.claude/rules/judge-calibration-cadence.md` (ADR-040 companion
   rule).

## 5. Reason-Code Registry (partial — full registry in `ExitDecision.reason_code`)

| reason_code | Triggered when |
|---|---|
| `grader.ok` | All dims pass or warn, no safety flag |
| `grader.groundedness_fail` | `groundedness < pass_threshold` |
| `grader.instruction_violation` | `instruction_adherence < warn_threshold` or boolean trip |
| `grader.safety_violation` | `safety_policy_adherence.violated == true` |
| `grader.tool_selection_fail` | `tool_selection < warn_threshold` |
| `grader.trajectory_fail` | `trajectory_shape < warn_threshold` or trajectory metrics below threshold |
| `grader.budget_breach` | `budget.budget_fit == false` |
| `grader.output_contract_fail` | `output_contract.required_form_satisfied == false` |
| `grader.unknown_budget_exceeded` | fraction of Unknown > policy ceiling → escalate |
| `grader.deadline_exceeded` | grader hit hard deadline → escalate |
| `grader.policy_halt` | ADR-042 kill-switch fired |

## 6. Consequences

- **Positive:** §5 gains a typed, auditable decision surface. Parity with Google /
  OpenAI / Anthropic trace-grade practice. ExitDecision becomes the single contract
  between §5 and consumers (UWG, HITL queue, L6 exhaust, RESPONSE).
- **Negative:** adds a synchronous hop inside §5. Bounded deadline mandatory.
- **Risk:** LLM-judge drift. Mitigated by ADR-032 hardening + calibration cadence rule.

## 7. Alternatives Considered

- **Keep prose only.** Rejected — no typed decision, can't emit ExitDecision, no
  parity with vendors.
- **Reuse `scorecard_engine.py` at runtime.** Rejected — scorecard assumes dataset
  semantics (baseline comparison). Runtime grader is stateless per-request.
- **Delegate grading to §6B (shadow).** Rejected — shadow is future-run only; cannot
  affect current disposition.

## 8. Open Items (tracked to follow-up plans)

- Code execution plan: wire trace-grader into §5 (blocked on this ADR + ADR-037 +
  ADR-038 + ADR-039 approvals).
- CI gate to verify ExitDecision schema validity on every trace-grader output.
- Ledger schema for `data/judge_calibration/` calibration runs.
