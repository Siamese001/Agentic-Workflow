# Live Runtime Exit-Control & Evaluation — v4

**Supersedes**: `05_Live_Runtime_Exit_Control_&_Evaluation_v3.md`
**Gap register**: `gap_analysis_v3_vs_industry_2026.md` (G1–G10)
**Companions**: `grader_composition_spec.md`, `runtime_to_regression_dataset_flow.md`
**Hardening**: `v4_hardening_addendum.md` — reward-hacking defense, agent-as-judge controls, break-glass (X3E), jailbreak taxonomy, OTel wire-up, `pass^k` threshold math, fault-injection matrix, operator runbook. **Read after v4 before operationalizing.**
**Date**: 2026-04-24

## What changed from v3

v4 preserves the v3 topology (X1 → X3A/B/C/D, HITL H1-H4, UWG → L4, BUS P/T exhaust) and adds two new gates, a consistency modifier, and two eval-track discriminators:

| New in v4 | Closes gap | Purpose |
|---|---|---|
| **X1E — Trajectory quality** | G1 | Tool selection, arg precision, step efficiency, handoff correctness |
| **X1F — Adversarial resilience** | G5 | Prompt-injection resistance, bias check, robustness under malformed input |
| **X1G — Consistency (`pass^k`) modifier** | G2 | Stochastic reliability gate on commit-path runs |
| **Capability / Regression track split** | G3 | X1A now carries a `track` label: capability (hill-climb) vs regression (drift-guard) |
| **Grader composition contract** | G4, G6, G7, G9 | Each gate declares: grader-type, rubric dimensions, binary / weighted / hybrid, partial credit, abstain protocol, bypass hardening |
| **Per-trial isolation invariant** | G8 | Stated as first-class invariant on X1C |
| **BUS T → golden-set promotion link** | G10 | Named edge, spec in `runtime_to_regression_dataset_flow.md` |

## v4 Flow (ASCII)

```
│ [ Sealed L2 Artifacts ] OR [RET] Short-Circuit from L0       │ [ Cross-Cutting L5 ]
                                ▼                                                              │
┌──────────────────────────────────────────────────┐                                           │
│ 5. EXIT EVAL & CONTROL (v4)                      ├───────[commit request]────────────────────┼────────────► ┌────────────────────────────────────────┐
│ [ THE SEALED FOLDER (L2) OR [RET] (L0) ]         │                                           │              │ X3C COMMIT REQUEST -> UWG              │
│ - ExecTrace / StateDiff / evidence bundle        │                                           │              │ U1 VERIFY BOSS: sig, cap token, hash   │
│ - validation counters / terminal classification  │                                           │              │ U2 CHECK CATALOG: scope, RBAC, diff    │
│ - track label: {capability | regression}         │                                           │              │ U3 MAKE COPY: durable commit, heal,    │
│ - grader composition vector                      │                                           │              │    hash-chain append, audit sync       │
│                                                  │                                           │              │ invariant: UWG is the sole ink path    │
│ X1 CURRENT-RUN EVALUATION (outcome + process)    │                                           │              │ into L4. No direct L2/HITL writes.     │
│ ┌──────────────────────┐ ┌─────────────────────┐ │                                           │              └───────────────────┬────────────────────┘
│ │ X1A TODAY'S RULES?   │ │ X1B ANSWERED IT?    │ │                                           │                                  │ [commits]
│ │ - baselines & policy │ │ - prompt/format fit │ │                                           │                                  ▼
│ │ - track: capability  │ │ - schema complete   │ │                                           │              ┌────────────────────────────────────────┐
│ │   or regression      │ │ - instruction follow│ │                                           │              │ L4 ARCHIVE (Durable Writes / Ledger)   │
│ └──────────────────────┘ └─────────────────────┘ │                                           │              └────────────────────────────────────────┘
│ ┌──────────────────────┐ ┌─────────────────────┐ │
│ │ X1C SAFE TO LEAVE?   │ │ X1D ANSWER GOOD?    │ │
│ │ - sandbox isolation  │ │ - groundedness      │ │
│ │ - mutation auth      │ │ - citation support  │ │
│ │ - env integrity      │ │ - faithfulness      │ │
│ │ - per-trial isolation│ │ - LLM-judge calib.  │ │
│ └──────────────────────┘ └─────────────────────┘ │
│ ┌──────────────────────┐ ┌─────────────────────┐ │
│ │ X1E TRAJECTORY OK?   │ │ X1F ADVERSARIAL OK? │ │  ◄── NEW in v4 (G1, G5)
│ │ - tool selection acc │ │ - prompt injection  │ │
│ │ - arg precision      │ │   resistance        │ │
│ │ - step efficiency    │ │ - jailbreak detect  │ │
│ │ - reasoning coherence│ │ - bias / fairness   │ │
│ │ - handoff correctness│ │ - robustness under  │ │
│ │                      │ │   malformed input   │ │
│ └──────────────────────┘ └─────────────────────┘ │
│ ┌──────────────────────────────────────────────┐ │
│ │ X1G CONSISTENCY MODIFIER (pass^k)            │ │  ◄── NEW in v4 (G2)
│ │ - commit-path only (X3C candidates)          │ │
│ │ - required: pass^k ≥ threshold for track     │ │
│ │ - k and threshold from policy (X1A)          │ │
│ └──────────────────────────────────────────────┘ │
│                                                  │
│ invariants (v4):                                 │
│ • live runtime disposition is explicit          │
│ • no silent fallbacks, no ungated human changes │
│ • per-trial environment isolation (no state    │
│   bleed between trials) [G8]                    │
│ • graders are bypass-resistant; agent cannot    │
│   influence its own grading [G9]                │
│ • LLM-judge graders must support abstain        │
│   ("Unknown") and are human-calibrated [G4]     │
└───────┬─┬─┬──────────────────────────────────────┘
        │ │ │
        │ │ └─[deny/reroute] ──► ┌────────────────────────────────┐
        │ │                      │ X3A DENY / REROUTE             │
        │ │                      │ - hard rule break / fail eval  │
        │ │                      │ - replan L1/L0                 │
        │ │                      │ reason_codes:                  │
        │ │                      │   POLICY_CONFLICT, HARD_FAIL,  │
        │ │                      │   TRAJECTORY_INVALID [NEW],    │
        │ │                      │   ADVERSARIAL_DETECTED [NEW],  │
        │ │                      │   CONSISTENCY_FAIL [NEW]       │
        │ │                      └────────────────────────────────┘
        │ │
        │ └─[escalate] ────────► ┌─────────────────────────────────────────────────────┐
        │  reason_code =         │ X3B ESCALATE / HUMAN REVIEW                         │
        │  POLICY_CONFLICT /     │ H1 Freeze: auth_state=FROZEN | write_auth=NONE      │
        │  AMBIGUITY /           │ H2 Materialize: bounded packet                      │
        │  SILENT_FAILURE /      │   - reason + evidence                               │
        │  LOW_CONFIDENCE /      │   - grader composition vector + per-dim scores [NEW]│
        │  JUDGE_ABSTAINED [NEW] │   - trajectory snapshot [NEW]                       │
        │                        │ H3 Human Review: inspect evidence, action, replay   │
        │                        │ H4 Decision: APPROVE | MODIFY_DIFF | REJECT         │
        │                        │ invariant: human input = untrusted DATA             │
        │                        ├─────────────────────────────────────────────────────┤
        │                        │ L5 RE-CLEARANCE GATE                                │
        │                        │ - REJECT -> DENY / STOP or RETURN_TO_L1             │
        │                        │ - MODIFY_DIFF -> L5 Re-clear -> Re-hydrate -> RESTART│
        │                        │ - APPROVE -> L5 Confirm -> ALLOW or COMMIT          │
        │                        │ invariant: no human change bypasses L5 re-clear     │
        │                        └───────┬─────────────────────────────────────────────┘
        │                                │
        │                                └─(resume/allow)──────────────────────────────┼────┐
        │                                                                              │    │
        │ [allow/finish]                                                               │    │
        ▼                                                                              │    │
┌──────────────────────────────────────────────────┐                                   │    │
│ X3D ALLOW / FINISH -> RESPONSE / OUTCOME         │◄──────────────────────────────────┼────┘
│ - patron answer only (no durable write here)     │                                   │
└───────────────────────┬──────────────────────────┘                                   │
                        │                                                              │
                        ▼                                                              │
            [ RETURN TO CALLER (U0) ]                                                  │
        (Runtime Evidence & Committed L4 Artifacts)                                    │
                        │                                                              │
                        │             [ ASYNC RUNTIME DATA EXHAUST — BUS P & BUS T ]   │
                        └───────(Traces, Artifacts, diffs, reason_codes, grades)       │
                                (BUS P: prefs/grades per-dimension [G7 partial credit])│
                                (BUS T: full trajectories [G10: feeds golden-set promo]│
                                 see `runtime_to_regression_dataset_flow.md`)          │
                                (invariant: learning signals do not mutate current run)│
                                                                                       │
███████████████████████████████████████████████████████████████████████████████████████│█████
██ ◄──────────────────── R U N T I M E   B O U N D A R Y ─────────────────────────────►██
████████████████████████████████████████████████████████████████████████████████████████████
                                                                               │
                                                [ SEND TO AFTER-HOURS REVIEW [6] ]
                                                [ + GOLDEN-SET CURATION PIPELINE ]
```

---

## Gate Specifications

Each gate declares: **grader type**, **rubric dimensions**, **composition mode**, **partial credit rules**, **abstain protocol**, **bypass hardening**. Details live in `grader_composition_spec.md`; this section names the contract each gate fulfills.

### X1A — Today's Rules?

- **Input**: policy manifest, baseline thresholds, agent identity, **track label** (`capability` | `regression`).
- **Grader type**: code-based (deterministic policy lookup).
- **Composition**: binary (policy must match or denies are issued).
- **Track label emission**: required on every run. Drives the `pass^k` threshold used by X1G and the dataset path used by `runtime_to_regression_dataset_flow.md`.
- **Failure reason code**: `POLICY_CONFLICT`.

### X1B — Answered It?

- **Input**: agent output, requested output schema, system prompt.
- **Grader type**: code-based (schema validation, format checks) + optional LLM-judge for instruction-following assessment.
- **Rubric dimensions**: `schema_complete`, `format_fit`, `instruction_following_sys_over_user`.
- **Composition**: hybrid — `schema_complete` is binary; `instruction_following` is weighted.
- **Partial credit**: yes — partial schemas with non-optional fields present are distinguishable from empty outputs.
- **Failure reason codes**: `SCHEMA_VIOLATION`, `FORMAT_MISMATCH`, `INSTRUCTION_BYPASS`.

### X1C — Safe to Leave?

- **Input**: sandbox state, mutation ledger, env integrity snapshot, **trial isolation receipt** (new in v4).
- **Grader type**: code-based.
- **Rubric dimensions**: `sandbox_ok`, `mutation_authorized`, `env_clean`, `no_prior_trial_leakage` (new).
- **Composition**: binary (all must pass).
- **Invariant additions**: per-trial isolation. If the trial consumed state produced by another trial not explicitly in its declared inputs, this gate fails.
- **Failure reason codes**: `SANDBOX_BREACH`, `UNAUTHORIZED_MUTATION`, `ENV_CONTAMINATED`, `TRIAL_STATE_LEAK`.

### X1D — Answer Good? (outcome quality)

- **Input**: agent output, source context, citations.
- **Grader type**: LLM-as-judge (with mandatory abstain protocol) + code-based citation link validator.
- **Rubric dimensions**: `groundedness`, `citation_support`, `faithfulness`, `relevance`.
- **Composition**: weighted per dimension; dimension weights come from X1A policy; threshold per track.
- **Abstain protocol**: judge returns `UNKNOWN` when evidence is insufficient; `UNKNOWN` routes to X3B with reason `JUDGE_ABSTAINED` rather than a false-positive pass.
- **Bypass hardening**: judge is run in a context isolated from the agent's tool outputs that could influence scoring (no self-validation).
- **Calibration cadence**: see `grader_composition_spec.md` §LLM-Judge Calibration.
- **Failure reason codes**: `UNGROUNDED`, `CITATION_INVALID`, `LOW_FAITHFULNESS`, `JUDGE_ABSTAINED`.

### X1E — Trajectory OK? (NEW — closes G1)

- **Input**: full trajectory (ExecTrace: tool calls, arguments, intermediate reasoning, handoffs).
- **Grader type**: code-based (deterministic checks on tool-call structure, arg types, step count) + LLM-as-judge (reasoning coherence).
- **Rubric dimensions**:
  - `tool_selection_accuracy` — at each decision point, was the chosen tool appropriate for the observable state?
  - `arg_precision` — were tool arguments correctly extracted from the conversation/context?
  - `step_efficiency` — redundant calls, loops, or wasteful retries?
  - `reasoning_coherence` — are intermediate reasoning steps internally consistent and consistent with actions taken?
  - `handoff_correctness` — in multi-agent runs, was the right sub-agent invoked at each handoff?
- **Composition**: weighted. `tool_selection_accuracy` and `arg_precision` are hard (binary sub-gates); the rest are weighted.
- **Partial credit**: yes — partially correct trajectories that reach the wrong answer are distinguishable from totally broken ones.
- **Anthropic guidance applied**: grade outcomes primarily, but trajectory is a secondary signal. A correct output via an obviously broken trajectory is surfaced via reason code `TRAJECTORY_SUSPECT`.
- **Failure reason codes**: `WRONG_TOOL`, `ARG_EXTRACTION_FAIL`, `STEP_INEFFICIENT`, `REASONING_INCOHERENT`, `HANDOFF_MISROUTED`, `TRAJECTORY_SUSPECT`.

### X1F — Adversarial OK? (NEW — closes G5)

- **Input**: user-supplied input, system-prompt + user-prompt delta, output.
- **Grader type**: code-based (pattern/heuristic detectors) + LLM-as-judge for nuanced injection detection.
- **Rubric dimensions**:
  - `prompt_injection_resistance` — did the agent follow instructions embedded in untrusted input?
  - `system_prompt_leakage` — did the output reveal protected system content?
  - `jailbreak_detection` — did the output violate refusals that policy requires?
  - `bias_fairness` — cohort-conditional output deltas within tolerance?
  - `robustness` — did the agent crash, loop, or produce malformed output under adversarial input?
- **Composition**: hybrid. `prompt_injection_resistance`, `system_prompt_leakage`, `jailbreak_detection` are binary; `bias_fairness`, `robustness` are weighted.
- **Invariant**: X1F runs before X3C commit regardless of track. A capability-track run that fails X1F is denied, not merely flagged.
- **Failure reason codes**: `PROMPT_INJECTION_DETECTED`, `SYSTEM_PROMPT_LEAK`, `JAILBREAK_DETECTED`, `BIAS_DELTA_EXCEEDED`, `ADVERSARIAL_CRASH`.

### X1G — Consistency (`pass^k`) Modifier (NEW — closes G2)

- **Scope**: gates runs that are candidates for X3C commit (durable writes to L4).
- **Mechanism**: when X1A-F pass on a commit-path run, X1G inspects recent per-trajectory-class trial history (from BUS T) and computes `pass^k` over the last k trials of the same trajectory class.
- **Threshold**: `pass^k ≥ θ` where θ comes from policy (X1A) per track:
  - Commit-path, customer-facing: θ ≥ 0.95 over k=5
  - Commit-path, internal: θ ≥ 0.85 over k=5
  - Non-commit (X3D allow only): θ is advisory, not blocking
- **On failure**: route to X3B (escalate to HITL) with reason `CONSISTENCY_FAIL`, evidence packet includes the per-trial outcomes that produced the `pass^k` estimate.
- **Why at runtime, not offline**: commit-path writes are irreversible; consistency needs to gate the commit, not merely be reported after the fact.
- **Interaction with `pass@k`**: `pass@k` is tracked on BUS P for capability-track analytics but does **not** gate runtime.

---

## X3 Dispositions (v3 unchanged, reason codes extended)

Dispositions remain X3A (deny), X3B (escalate), X3C (commit via UWG), X3D (allow). What changed:

- Reason-code vocabulary extended (see per-gate failure codes above).
- HITL packet (X3B → H2) now mandatorily includes **grader composition vector with per-dimension scores** and a **trajectory snapshot**, enabling reviewers to see *which specific dimension* triggered the escalation rather than only a top-line classification.

---

## Invariants (v4 consolidated)

1. **Explicit disposition** — every run terminates at exactly one of X3A/X3B/X3C/X3D. No silent fallbacks. *(v3)*
2. **UWG sole ink path** — L4 receives durable writes only from X3C → UWG. *(v3)*
3. **L5 re-clearance** — no HITL change bypasses L5 re-clear. *(v3)*
4. **Human input = untrusted data** — HITL decisions are data, not control flow. *(v3)*
5. **Learning signals do not mutate current run** — BUS P / BUS T are async-only. *(v3)*
6. **Per-trial environment isolation** — no state bleed between trials; trials declare their inputs explicitly. *(new, G8)*
7. **Grader bypass resistance** — graders (including LLM-judges) cannot be steered by the agent being graded. *(new, G9)*
8. **LLM-judge abstain + calibration** — LLM-judge graders must support `UNKNOWN` and undergo human calibration on a declared cadence. *(new, G4)*
9. **Consistency gating on commit path** — X3C requires X1G `pass^k` ≥ θ. *(new, G2)*
10. **Adversarial gate before commit** — X1F must pass before X3C, regardless of track. *(new, G5)*

---

## Non-Goals

- v4 does **not** alter v3's inter-layer topology (L0–L6). It only expands the X1 evaluation surface and the HITL packet contents.
- v4 does **not** define the concrete code for graders. That is the implementation pass (a downstream T3 plan, not this doc).
- v4 does **not** retire v3. v3 remains as historical reference. Implementations migrating from v3 should treat X1E, X1F, X1G as additive and may stage their adoption per the severity ordering in `gap_analysis_v3_vs_industry_2026.md`.

---

## Traceability

| v4 element | Closes gap | Industry source |
|---|---|---|
| X1E Trajectory | G1 | Google Pillar 2, OpenAI tool-selection/arg-precision |
| X1F Adversarial | G5 | Google Pillar 3 |
| X1G `pass^k` | G2 | Anthropic |
| Track label on X1A | G3 | Anthropic capability/regression |
| Grader composition contract | G4, G6, G7, G9 | Anthropic |
| Per-trial isolation invariant | G8 | Anthropic |
| BUS T → golden-set link | G10 | Google |
