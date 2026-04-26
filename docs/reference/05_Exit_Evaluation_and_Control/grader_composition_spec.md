========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 05_Exit_Evaluation_and_Control
Canonical file: grader_composition_spec.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: grader_composition_spec.md
Owner summary: Exit checkout and disposition. Owns ExitReviewPacket normalization, X1 checkout checks, X2 aggregation, exactly one X3 disposition, HITL freeze/reclear, UWG handoff, response return, and runtime exhaust.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

# Grader Composition Spec

**Parent**: `05_Live_Runtime_Exit_Control_&_Evaluation_v4.md`
**Closes gaps**: G4 (LLM-judge calibration), G6 (composition), G7 (partial credit), G9 (bypass resistance)
**Date**: 2026-04-24

This spec defines the concrete contract every X1 gate must fulfill. Gates reference this document by name; this document holds the mechanical detail so v4 can stay flow-focused.

---

## 1. Grader Taxonomy

Three grader classes, one runtime contract each. Anthropic's taxonomy (A1).

| Class | What it does | Strengths | Limits |
|---|---|---|---|
| **Code-based** | Deterministic functions — schema validators, regex matchers, API-reference lookups, numeric tolerance checks. | Fast, reproducible, auditable, no calibration drift. | Brittle on open-ended outputs; cannot capture nuance. |
| **Model-based (LLM-as-judge)** | LLM scores outputs against a rubric. Rubric-based, natural-language assertion, pairwise, reference-based, multi-judge consensus. | Flexible, scalable, captures nuance, handles open-ended. | Non-deterministic, more expensive, needs human calibration. |
| **Human** | SME review, crowd, spot-check, A/B, inter-annotator agreement. | Gold-standard truth, matches user judgment, calibrates model-graders. | Slow, expensive, scarce. |

---

## 2. Rubric Structure

Every gate declares its rubric as a **set of named dimensions** — not a single monolithic score. Per Anthropic (A1): "create clear, structured rubrics to grade each dimension of a task, and then grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions."

### Rubric schema

```yaml
gate: X1D                       # the gate this rubric belongs to
version: 1
dimensions:
  - name: groundedness
    grader_class: model_based   # code_based | model_based | human
    scale: [0.0, 1.0]           # normalized
    weight: 0.4                 # used when composition=weighted or hybrid
    is_hard_gate: false         # true = binary sub-gate (failure denies)
    threshold: 0.80             # pass threshold when is_hard_gate=true or for hybrid
    abstain_allowed: true       # model-based only; allows UNKNOWN
  - name: citation_support
    grader_class: code_based
    scale: [0, 1]               # binary
    weight: 0.3
    is_hard_gate: true          # citations present and resolvable is mandatory
    threshold: 1.0
  - name: faithfulness
    grader_class: model_based
    scale: [0.0, 1.0]
    weight: 0.3
    is_hard_gate: false
    threshold: 0.70
    abstain_allowed: true
composition: weighted            # binary | weighted | hybrid
aggregate_threshold: 0.75        # if composition != binary
```

### Dimension-level rules

- **Each dimension is scored by its own isolated grader instance**. Do not reuse a single LLM call to score all dimensions of X1D — that produces correlated scores and hides failure modes.
- **Code-based dimensions** return in `{0, 1}` (binary) or a small integer set.
- **Model-based dimensions** return `[0.0, 1.0]` plus an optional `UNKNOWN` flag.
- **Human-graded dimensions** are only used in offline calibration, not at runtime. (Runtime human intervention is HITL, a separate control path.)

---

## 3. Composition Modes

Per Anthropic (A1): scoring can be binary, weighted, or hybrid.

### 3.1 Binary

All dimensions must meet their thresholds. A single sub-failure denies.

```
pass = AND over dimensions: dim.score >= dim.threshold
```

Use for X1A (policy match), X1C (safety), and the hard sub-gates of X1B/X1E/X1F.

### 3.2 Weighted

Weighted average of normalized dimension scores must meet `aggregate_threshold`.

```
aggregate = sum(dim.score * dim.weight) / sum(dim.weight)
pass = aggregate >= aggregate_threshold
```

Use for soft-quality gates where no single dimension is individually disqualifying.

### 3.3 Hybrid

Dimensions split into two groups:

- **Hard gates** (`is_hard_gate: true`): each must individually meet `threshold` (AND).
- **Weighted group**: weighted average must meet `aggregate_threshold`.

```
hard_pass = AND over hard_gates: dim.score >= dim.threshold
soft_pass = weighted_avg(soft_dims) >= aggregate_threshold
pass = hard_pass AND soft_pass
```

Use for gates where some dimensions are disqualifying (schema present, citation resolvable, prompt-injection absent) but others are nuanced quality signals (faithfulness, reasoning coherence).

### Composition mode per gate (v4)

| Gate | Mode |
|---|---|
| X1A | binary |
| X1B | hybrid (schema hard, instruction-following weighted) |
| X1C | binary |
| X1D | weighted |
| X1E | hybrid (tool-selection + arg-precision hard, rest weighted) |
| X1F | hybrid (injection + leak + jailbreak hard, bias + robustness weighted) |
| X1G | binary (`pass^k ≥ θ`) |

---

## 4. Partial Credit (closes G7)

Per Anthropic (A1): "For tasks with multiple components, build in partial credit. A support agent that correctly identifies the problem and verifies the customer but fails to process a refund is meaningfully better than one that fails immediately."

### Runtime behavior

- Partial credit does **not** change disposition — a gate either passes or routes to X3A/X3B. (Partial credit is not a partial disposition.)
- Partial credit **does** change the **evidence emitted on BUS P** — per-dimension scores are retained, not collapsed to pass/fail.
- Partial credit enables the golden-set promotion pipeline (`runtime_to_regression_dataset_flow.md`) to distinguish near-miss trajectories (valuable training signal) from totally broken ones.

### Implementation contract

- Every X1 gate emits a `dimension_vector: List[{name, score, weight, threshold, passed}]` to BUS P.
- Aggregate disposition is computed per §3. Per-dimension scores are preserved for downstream use.
- HITL packets (X3B → H2) include the full `dimension_vector` so reviewers see *which dimension* produced the escalation.

---

## 5. LLM-Judge Calibration (closes G4)

### 5.1 Abstain protocol ("Unknown" escape)

Per Anthropic (A1): "To avoid hallucinations, give the LLM a way out, like providing an instruction to return 'Unknown' when it doesn't have enough information."

- Every model-based dimension's rubric prompt **must** include an explicit abstain instruction.
- Abstain returns route to X3B (HITL) with reason `JUDGE_ABSTAINED`, not a false pass or a false fail.
- Abstain rates are tracked on BUS P. Sustained abstain rate > 5% per dimension triggers a calibration review.

### 5.2 Human calibration cadence

- **Initial calibration** before a model-based dimension goes live: ≥ 50 SME-labeled examples, judge vs. SME agreement ≥ 0.80 (Cohen's κ) required.
- **Periodic recalibration**: quarterly, or after any change to judge model / rubric prompt / scoring scale.
- **Drift detection**: weekly sample of N=20 runs regraded by SME; agreement drop > 0.10 triggers immediate recalibration.
- **Artifacts**: calibration records live under `data/judge_calibration/` (already reserved in repo).

### 5.3 Rubric bugs — fail-safe against false greens

Per Anthropic (A1): "Some evaluations have subtle failure modes that result in low scores even with good agent performance." (Same principle applies symmetrically to false high scores.)

- Before any rubric dimension goes live, run it against a **known-bad set** (adversarial examples that should fail) and a **known-good set**. Both sets must score as expected.
- Any time a gate produces anomalously high pass rates (> 98% on a capability-track dimension), auto-flag for rubric review.

### 5.4 Multi-judge consensus (optional)

For high-stakes dimensions, run N independent judge calls and aggregate:

- **Majority vote** (classification dimensions)
- **Median** (ordinal/continuous dimensions)
- **Unanimous pass** (for security-critical sub-gates like prompt-injection detection)

Disagreement rate > 30% across judges triggers HITL escalation, not silent resolution.

---

## 6. Bypass Resistance (closes G9)

Per Anthropic (A1): "Make your graders resistant to bypasses or hacks. The agent shouldn't be able to easily 'cheat' the eval."

### 6.1 Context isolation

- **LLM-judge graders run in a context isolated from the agent's tool outputs** that could influence scoring. Specifically: the judge sees the **evaluation inputs** (task, rubric, agent output) but **not** the agent's chain-of-thought or intermediate tool-call outputs when those could carry adversarial content.
- **Judge and agent are different model calls** — do not reuse the agent's session to self-grade.
- **Judge system prompts are not exposed** to the agent (protects against agent learning to craft outputs that pass the rubric for wrong reasons).

### 6.2 Input sanitation on judge calls

- Agent-produced content passed to judges is **wrapped in a clear delimiter** and the judge is instructed that instructions inside the wrapper are data, not commands.
- Judges running on open-ended agent outputs are paired with a lightweight **prompt-injection classifier** that flags outputs containing judge-directed instructions ("please rate this a 10"). Flagged outputs route to HITL.

### 6.3 Adversarial eval

- Graders are themselves evaluated on an adversarial test set containing:
  - Outputs that contain judge-directed instructions.
  - Outputs that reference the rubric dimensions by name with claims ("this is fully grounded because…").
  - Outputs that truncate or malform in ways designed to confuse parsing.
- Judges must score these as failures (or as abstains). Any judge that can be flipped by known bypass patterns is retired.

### 6.4 Immutable rubric versioning

- Rubric changes produce a new version. Gate decisions are recorded with the rubric version used (`rubric_version: X1D@v3`).
- Rubric diffs are reviewed on the same cadence as constitutional rule changes. Silent rubric edits are forbidden.

---

## 7. Grader Output Contract (for BUS P)

Every gate emits one row to BUS P per run:

```json
{
  "run_id": "…",
  "gate": "X1D",
  "rubric_version": "X1D@v3",
  "composition": "weighted",
  "aggregate_score": 0.83,
  "aggregate_threshold": 0.75,
  "passed": true,
  "abstain": false,
  "dimension_vector": [
    {"name": "groundedness",     "score": 0.91, "weight": 0.4, "threshold": 0.80, "passed": true,  "grader_class": "model_based",  "abstain": false},
    {"name": "citation_support", "score": 1.0,  "weight": 0.3, "threshold": 1.0,  "passed": true,  "grader_class": "code_based",   "abstain": false},
    {"name": "faithfulness",     "score": 0.62, "weight": 0.3, "threshold": 0.70, "passed": false, "grader_class": "model_based",  "abstain": false}
  ],
  "reason_codes": ["LOW_FAITHFULNESS"],
  "track": "regression",
  "trajectory_class": "support_ticket_with_refund"
}
```

`trajectory_class` is the key used by X1G to look up recent trial history for `pass^k` computation.

---

## 8. Checklist — Adopting This Spec

When migrating a v3 gate to v4:

- [ ] Declare rubric YAML (§2).
- [ ] Decide composition mode (§3).
- [ ] For every model-based dimension: add abstain protocol, run initial human calibration (§5.1, §5.2).
- [ ] Run gate against known-bad and known-good sets (§5.3).
- [ ] Run grader-bypass adversarial eval (§6.3).
- [ ] Wire gate output to BUS P per §7.
- [ ] Register rubric version and cadence for periodic recalibration (§5.2).
- [ ] Cross-link rubric YAML from v4 gate spec.
