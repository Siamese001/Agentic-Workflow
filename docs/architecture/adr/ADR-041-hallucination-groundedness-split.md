# ADR-041 — Split Hallucination from Groundedness

- **Status:** Accepted (implemented)
- **Date:** 2026-04-23
- **Deciders:** Eval Lab, Architecture
- **Impact Layers:** apps_eval, config/judges, L5, v33 §5
- **Relates to:** ADR-026 (consensus validator), ADR-032 (LLM-judge hardening)

Current-state note (2026-06-15): implemented in `config/schemas/exit_decision.schema.json`, `agentic_core/L5_safety/eval_spine/claim_extractor.py`, and the exit-eval final-response path that separates groundedness from hallucination.

## 1. Context

`config/judges/rubrics.yaml` defines a single `groundedness` dimension scored
1–5 by an LLM rubric. Google Vertex distinguishes two concepts:

- **Groundedness** — rubric judgment: "are claims supported by context".
- **Hallucination** — metric grounded to agent **configuration and tool usage**,
  independent of the LLM-rubric path.

Collapsing both into one rubric dimension means:
- We cannot emit a Vertex-compatible hallucination score.
- Tool-grounded contradictions (agent claimed it ran tool X but trace has no
  such call) are invisible unless a rubric judge happens to notice.

## 2. Decision

Keep the existing `groundedness` **rubric** dimension (1–5) in `rubrics.yaml`.
Add a **distinct `hallucination` metric** owned by the trace-grader, populated
deterministically, and projected into
`ExitDecision.final_response.hallucination` as:

```
{
  "score_0_1": float,           # 1.0 = no hallucinations, 0.0 = dominated by unsupported claims
  "unsupported_claim_count": int,
  "tool_grounded": bool          # true iff every tool claim matches the trace ledger
}
```

### 2.1 Computation

- Extract claims from the final response via a claim extractor (LLM or code).
- For each claim, determine support source:
  - `context` — supported by retrieved evidence (populates groundedness rubric).
  - `tool_output` — supported by an actual tool call + result in the trace.
  - `parametric` — supported only by model parametric knowledge.
  - `unsupported` — no support found.
- `unsupported_claim_count` = count(unsupported).
- `tool_grounded` = every claim that references a tool result has a matching
  tool call in the trace with matching args_hash.
- `score_0_1 = 1 - (unsupported_claim_count / max(1, total_claims))`.

### 2.2 Separation of concerns

| Surface | Scale | Judge type | Authority |
|---|---|---|---|
| `rubrics.yaml → groundedness` | 1–5 | Model-based (LLM rubric) | dataset + §5 (via trace-grader projection) |
| `ExitDecision.final_response.hallucination` | 0.0–1.0 + counts + bool | Code-based (claim extractor + trace diff) | §5 deterministic |

Disagreement between the two is a **signal**, not an error. High groundedness +
low hallucination score = rubric confirms tool-grounding. Low groundedness + high
hallucination score = classic unsupported claims. Any other combination triggers
`reason_code = grader.groundedness_hallucination_disagreement` → WARN.

## 3. Consequences

- **Positive:** Vertex parity; tool-grounded hallucinations detectable
  deterministically; cheaper than rubric-only grading for the hard cases.
- **Negative:** claim extractor is a new moving part.
- **Risk:** claim extractor mis-segments sentences. Mitigated by simple
  start: code-based extractor with conservative defaults; upgrade path to LLM
  extractor under the same interface.

## 4. Alternatives Considered

- **Collapse both into rubric.** Status quo — rejected (see §1).
- **Replace rubric with deterministic only.** Rejected — rubric catches
  subtleties claim-diff cannot (tone, partial support).

## 5. Open Items

- Claim extractor spec and interface.
- Tool-ledger canonicalization shared with ADR-037 args_hash rules.
- Rubrics.yaml delta: documentation update noting the split (no metric removal).
