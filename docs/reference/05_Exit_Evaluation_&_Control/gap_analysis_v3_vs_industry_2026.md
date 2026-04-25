# Gap Analysis — v3 Exit-Control vs. 2026 Industry State-of-the-Art

**Subject**: `05_Live_Runtime_Exit_Control_&_Evaluation_v3.md` (current runtime exit-control & evaluation flow)
**Compared against**: public 2025-2026 agentic-evaluation guidance from Anthropic, Google Cloud, and OpenAI
**Purpose**: identify missing/under-specified evaluation surfaces so v4 can close them
**Author**: Cascade (synthesized from primary sources cited below)
**Date**: 2026-04-24

---

## Primary Sources

| # | Source | Canonical contribution |
|---|---|---|
| A1 | Anthropic, *Demystifying Evals for AI Agents* (engineering blog, 2025) | Trace/transcript/trajectory as canonical eval unit; code/model/human grader taxonomy; **capability vs regression** tracks; **`pass@k` / `pass^k`** non-determinism metrics; clean-env-per-trial invariant; "grade outcomes not paths"; partial credit; LLM-judge calibration with "Unknown" escape; bypass-resistant graders. |
| G1 | Google Cloud, *A Methodical Approach to Agent Evaluation* (2025) | **3-pillar framework**: (1) agent success & quality, (2) **trajectory/process**, (3) **trust & safety**; 4-method mix: human / LLM-as-judge / programmatic / adversarial; dueling-LLM synthetic data; anonymized production → golden dataset. |
| O1 | OpenAI, *Evaluation Best Practices* (API docs, 2025) | Single- vs multi-agent eval surfaces; **instruction-following** (system-over-user conflict); **functional correctness**; **tool selection accuracy** and **data precision** (argument-extraction correctness); edge-case buckets (input variability, contextual complexity, personalization). |

---

## v3 Coverage Map

v3 defines the exit-evaluation surface as gates X1A–X1D producing a disposition (X3A deny, X3B escalate/HITL, X3C commit via UWG, X3D allow/finish):

| Gate | Question | Dimensions in v3 |
|---|---|---|
| **X1A** | Today's rules? | baselines, policy |
| **X1B** | Answered it? | prompt/format fit, schema complete |
| **X1C** | Safe to leave? | sandbox isolation, mutation authorization, environment integrity |
| **X1D** | Answer good? | groundedness, citation support |
| **X3A** | — | deny / reroute (hard-rule breach, replan to L1/L0) |
| **X3B** | — | escalate / HITL (H1 freeze → H2 packet → H3 review → H4 decision → L5 re-clear) |
| **X3C** | — | commit request → UWG → L4 |
| **X3D** | — | allow / finish → response |
| **BUS P / BUS T** | — | async learning exhaust (prefs, grades, telemetry, traces) |

**Invariant v3 asserts**: live runtime disposition is explicit; no silent fallbacks; no ungated human changes; UWG is sole ink path into L4; L5 re-clears every HITL change.

---

## Gap Register

Ten gaps, each traced to the specific industry source that defines the missing concept.

### G1 — Trajectory / Process Evaluation Missing

**Industry position** (G1, O1): The *trajectory* — the sequence of decisions, tool calls, and intermediate reasoning — is a first-class evaluation target, not a derivative of the outcome. Google's Pillar 2 explicitly separates "process" from "outcome". OpenAI's single-agent guidance enumerates **tool selection accuracy** ("correct tool?") and **data precision** ("correct arguments?") as distinct eval dimensions.

**v3 coverage**: X1B ("answered it?") and X1D ("answer good?") are outcome-only. X1C ("safe to leave?") covers environmental safety, not reasoning quality.

**Specific missing metrics**:
- Tool-selection correctness (did the agent pick the right tool at each step?)
- Argument-extraction precision (were tool arguments correctly synthesized from context?)
- Step efficiency (redundant tool calls, unnecessary loops, token waste)
- Reasoning coherence (are intermediate reasoning steps internally consistent?)
- Handoff correctness (in multi-agent runs, was the right sub-agent invoked?)

**Why it matters at runtime**: A run can produce a correct final answer via a wrong trajectory (lucky guess, tool misuse that happened to return something), and that brittle path will fail under distribution shift. Outcome-only gates reward this brittleness.

---

### G2 — No Stochastic Consistency Metric (`pass^k`)

**Industry position** (A1): Agent behavior is non-deterministic. Two canonical metrics quantify this:

- **`pass@k`** — probability of ≥1 success in k attempts. Rises with k. Use when one success suffices (code agents searching for a fix).
- **`pass^k`** — probability that **all** k attempts succeed. Falls with k. Use when **consistency is product-critical** (customer-facing agents, commit-producing agents).

**v3 coverage**: v3 treats each run as a single-shot pass/fail through X1A-D. There is no explicit gate that asks "does this agent succeed *reliably* on this class of task?"

**Why it matters at runtime**: The X3C commit path writes to L4 durable storage. An agent with 75% per-trial success rate and no consistency check will corrupt the ledger ~25% of the time on high-stakes writes. Consistency needs to be a gate input, not only a post-hoc analytic.

---

### G3 — No Capability vs. Regression Track Separation

**Industry position** (A1): Mature eval programs run two separate suites:

- **Capability evals** — tasks the agent currently struggles with. Low initial pass rate. Purpose: hill-climbing target.
- **Regression evals** — tasks the agent has already mastered. Near-100% pass rate. Purpose: drift detection. A drop signals breakage.

As capability evals are solved, they *graduate* into the regression suite.

**v3 coverage**: X1A references "baselines & policy" but does not distinguish drift-guard from hill-climb. BUS P emits "prefs/grades" asynchronously but has no promotion pipeline to a regression suite.

**Why it matters**: Without a named regression track, silent quality regressions after prompt/policy/model changes are detected only by aggregate metrics — slowly, and often after user-visible harm.

---

### G4 — LLM-Judge Calibration Discipline Absent

**Industry position** (A1, G1): When an LLM grades another LLM, specific disciplines are required:

- **Structured rubrics per dimension** (grade each dimension with an isolated judge rather than one judge for all dimensions).
- **"Unknown" escape** (the judge must be able to abstain when evidence is insufficient — prevents confident hallucination in the grade itself).
- **Human calibration** (periodic inter-annotator agreement check between judge and SME; misalignment triggers re-prompting or judge-model upgrade).
- **Graders per grader type weighted** per Anthropic: "scoring can be weighted (combined grader scores hit a threshold), binary (all graders pass), or hybrid".

**v3 coverage**: X1D names "groundedness" and "citation support" as dimensions but does not specify whether the check is deterministic (code-based), LLM-judged, or human. No rubric structure, no abstain mechanism, no calibration cadence.

**Why it matters**: An un-calibrated LLM judge is indistinguishable from no gate. It produces green lights with the same confidence whether it is correctly grading or hallucinating the grade.

---

### G5 — Adversarial / Security Pillar Under-Specified

**Industry position** (G1): Pillar 3 (*Trust & Safety*) measures reliability **under adversarial and edge conditions**:

- **Robustness** — error handling under malformed/unexpected input.
- **Security** — prompt-injection resistance, system-prompt leakage resistance.
- **Fairness** — bias mitigation across user cohorts.

**v3 coverage**: X1C covers environmental integrity (sandbox, mutation auth) but not input-adversarial hardening. X1A's "baselines & policy" could in principle include safety policies, but the doc does not name prompt injection, jailbreak detection, or bias checks as gate inputs.

**Why it matters at runtime**: Prompt injection is a runtime threat, not a training-time one. A runtime exit-control surface that does not explicitly check for it will emit confidently-wrong dispositions on injected inputs, and those dispositions will then hit X3C → UWG → L4 with full commit authority.

---

### G6 — No Grader Composition Contract

**Industry position** (A1): Per-task scoring strategies:

- **Binary** — all graders must pass (AND).
- **Weighted** — combined score ≥ threshold.
- **Hybrid** — some graders are hard gates, others contribute weighted votes.

**v3 coverage**: X1A–D are implicitly binary AND. There is no mechanism for a disposition to be "allow with caveat, weight 0.82" or to fail one low-weight grader without blocking the run.

**Why it matters**: Binary AND produces false-denials on tasks where one dimension is inherently ambiguous. Weighted/hybrid composition lets the system tolerate ambiguity on low-stakes dimensions while keeping hard rules on high-stakes ones.

---

### G7 — No Partial Credit

**Industry position** (A1): "For tasks with multiple components, build in partial credit. A support agent that correctly identifies the problem and verifies the customer but fails to process a refund is meaningfully better than one that fails immediately."

**v3 coverage**: Terminal classification in v3 is all-or-nothing. A partially-successful run is dispositioned identically to a wholly-failed one.

**Why it matters**: This is both a fairness issue (the eval signal is coarser than reality) and a learning-signal issue (BUS P cannot distinguish near-miss from total miss, reducing the value of the async learning exhaust).

---

### G8 — Per-Trial Environment Isolation Not an Invariant

**Industry position** (A1): Anthropic discovered Claude was gaining unfair advantage on some internal evals by examining the git history left over from previous trials. Clean-environment-per-trial is now stated as an invariant: "Each trial should be 'isolated' by starting from a clean environment. Unnecessary shared state between runs (leftover files, cached data, resource exhaustion) can cause correlated failures."

**v3 coverage**: X1C names "sandbox isolation" but the invariant listed is "live runtime disposition is explicit. No silent fallbacks, no ungated human changes." It does not assert "no shared state between trials" as a first-class invariant.

**Why it matters at runtime**: At runtime, leaked state manifests as conversation-memory bleed, unreset tool state, or cached partial results that skew subsequent runs. The evaluation layer has to enforce isolation explicitly, or subtle state-bleed will produce inflated reliability numbers.

---

### G9 — No Grader-Bypass-Resistance Invariant

**Industry position** (A1): "Make your graders resistant to bypasses or hacks. The agent shouldn't be able to easily 'cheat' the eval. Tasks and graders should be designed so that passing genuinely requires solving the problem rather than exploiting unintended loopholes."

**v3 coverage**: No invariant in v3 asserts that graders are non-manipulable by the agent being graded. This matters particularly for LLM-as-judge graders that share context with the agent.

**Why it matters**: A confused-deputy failure in which the agent's own output influences the grader's scoring produces a silent validity failure — the gate appears to work but is actually self-validating.

---

### G10 — Runtime → Regression Dataset Promotion Undefined

**Industry position** (G1): Real-world use patterns and edge cases should flow from anonymized production interactions into a "golden dataset" that captures actual use patterns. Human-in-the-loop curators save valuable interactive sessions from logs or traces as permanent test cases, continuously enriching the test suite with meaningful examples.

**v3 coverage**: BUS P and BUS T are named as async learning exhaust ("prefs/grades" and "telem/trace"), with the invariant "learning signals do not mutate current run." But there is no specified pipeline from BUS T traces → curated golden set → regression suite consumed by a future X1A.

**Why it matters**: Without a named promotion path, the async exhaust accumulates but does not close the loop back into exit-control. The system has telemetry but no compounding evaluation asset.

---

## Severity & Sequencing

| Gap | Severity | Why this order |
|---|---|---|
| G1 Trajectory eval | **P0** | Closes the biggest outcome-vs-process blind spot; unlocks tool-selection / arg-precision metrics used by G4/G6. |
| G5 Adversarial pillar | **P0** | Runtime threats (prompt injection) must be gated *before* other evaluation improvements become meaningful. |
| G2 `pass^k` consistency | **P1** | Direct commit-path (X3C) safety improvement. |
| G4 LLM-judge discipline | **P1** | Precondition for G3 and G6 — judges need to be reliable before tracks/composition make sense. |
| G6 Grader composition | **P1** | Enables G7 partial credit as a mechanical consequence. |
| G3 Capability/regression tracks | **P2** | Structural improvement; gains compound once G4 is in place. |
| G7 Partial credit | **P2** | Follows directly from G6. |
| G8 Per-trial isolation invariant | **P2** | Invariant is cheap to state; enforcement is a separate wave. |
| G9 Grader bypass resistance | **P2** | Stated invariant; hardening is a separate wave. |
| G10 Runtime → regression pipeline | **P3** | Requires G3 in place to have a target; natural capstone. |

---

## Out of Scope (intentional)

- **Benchmarks**: SWE-bench, τ-bench, GAIA, etc. are capability benchmarks, not exit-control gates. They inform X1A baselines but don't change v3's control flow.
- **Offline scorecards**: after-hours review (v3's `[6]` handoff at the runtime boundary) is a separate concern from live gating.
- **Model-card / safety-case documentation**: governance artifact, not a runtime gate.

---

## Downstream Artifacts (companion docs in this folder)

- `05_Live_Runtime_Exit_Control_&_Evaluation_v4.md` — v4 flow with gaps closed
- `grader_composition_spec.md` — concrete grader-composition contract (G4, G6, G7, G9)
- `runtime_to_regression_dataset_flow.md` — BUS P/T → golden-set promotion pipeline (G3, G10)

Each gap is addressed by exactly one or two downstream artifacts. Cross-references are explicit so an operator reading v4 can find the underlying evidence.
