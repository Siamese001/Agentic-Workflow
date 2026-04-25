# ADR-053 — X1F Adversarial Gate

**Status**: Accepted
**Date**: 2026-04-24
**Deciders**: L3 architecture + Security owners
**Relates to**: ADR-023 (runtime HITL), ADR-032 (LLM judge hardening), ADR-049 (L5 v4 governance plane)

## Context

v3 exit-control covered environmental safety (X1C: sandbox, mutation auth, env integrity) but had no explicit check for **input-adversarial** threats: prompt injection, jailbreaks, system-prompt leakage, bias, or robustness under malformed input. These are runtime threats, not training-time ones — a runtime control plane that emits confident dispositions on injected inputs will then hit X3C → UWG → L4 with full commit authority.

Google Pillar 3 ("Trust & Safety") and the 2026 jailbreak survey (techrxiv 1373070) enumerate 8 adversarial categories that any production LLM agent must resist.

## Decision

Add **X1F (Adversarial OK?)** as a v4 gate. Implementation: `agentic_core.L3_orchestration.exit_eval` with dedicated detector module `graders/adversarial.py`. Rubric: `config/exit_eval_rubrics/x1f_v1.yaml`.

### Dimensions

| Dimension | Grader class | Hard gate | Threshold |
|---|---|---|---|
| `prompt_injection_resistance` | code_based | yes | 1.0 |
| `system_prompt_leakage` | code_based | yes | 1.0 |
| `jailbreak_detection` | code_based | yes | 1.0 |
| `bias_fairness` | model_based (abstain) | no | 0.70 |
| `robustness` | code_based | no | 0.70 |

Composition: **hybrid**, aggregate_threshold 0.75. Any hard sub-gate failure denies (X3A).

### Required probe set (H4.2)

`data/eval/golden/adversarial/` **must** contain ≥20 cases per category. X1F is "not ready for production" on a trajectory_class until all 8 categories (H4.1) have passing probes. Gap = blocker.

### Multi-turn awareness (H4.3)

`prompt_injection_resistance` is **not** single-turn. X1F receives the full turn history and scores turn-to-turn drift. Progressive escalation attacks must be detected even when no single turn is a violation.

### Invariant

X1F runs before X3C commit **regardless of track** (capability or regression). A capability-track run that fails X1F is denied, not merely flagged. Per §6.3, detectors are themselves evaluated on an adversarial test set and retired if flippable by known bypass patterns.

## Consequences

**Positive**:
- Runtime defense-in-depth against prompt injection and jailbreak; closes G5.
- Stable taxonomy (H4.1) drives probe-set curation and rubric-diff review.
- Commit-path (X3C) becomes provably safer under adversarial inputs.

**Negative / accepted cost**:
- 8-category probe set (≥160 cases) is curation overhead; amortized via `runtime_to_regression_dataset_flow.md`.
- False-positive rate on `bias_fairness` LLM-judge may require calibration (grader spec §5.2).

**Security**:
- Bypass resistance (§6) is load-bearing. Each detector MUST pass the adversarial re-test on rubric-diff (H7.1 #5).
- System-prompt-leak detector CANNOT use regex on the system prompt itself (leaks on the detector = leaks on the gate).

## Alternatives considered

1. **Rely on X1C for adversarial detection** — rejected: X1C covers env safety, not input semantics.
2. **Treat X1F as advisory** — rejected: commit-path runs under injection must deny, not just warn.
3. **Pure LLM-judge adversarial detection** — rejected: H9 (hard sub-gates require code-based). LLM-judge alone = agentic judge = attack surface per H2.

## Open items

- Continuous adversarial-set growth (probe retirement when patterns become universally detected; new patterns added per public CVE / jailbreak disclosures).
- Bias-fairness cohort definitions: who defines cohorts? Deferred to Security team.

## References

- v4 spec §X1F
- Hardening: `v4_hardening_addendum.md` H4 (jailbreak taxonomy)
- Implementation: `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/graders/adversarial.py` (this ADR)
- Rubric: `@c:/Git/Agentic-Workflow/config/exit_eval_rubrics/x1f_v1.yaml`
