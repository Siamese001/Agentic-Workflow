---
name: ask-user-question-recommendation
description: Use this skill when a material implementation decision has two or more viable options with different risk, blast radius, cost, or reversibility and the user has not already given an unambiguous directive.
metadata:
  owner: platform-team
  version: "2.0"
---

# Structured user-choice recommendation

Use the native structured-input tool when it is exposed in the current mode. Otherwise ask one focused
plain-text question. Do not construct custom marker packets, cards, or telemetry protocols merely to
present a choice.

## Decision rule

Ask only when evidence cannot safely resolve a material choice. Proceed without a question when one
option clearly dominates or the user has already approved the approach.

## Option shape

1. Put the recommended option first and end its label with `(Recommended)`.
2. Give each option a numeric confidence value.
3. State `Pros:` and `Cons:` for each option.
4. State a concrete `Flips if ...` condition for the recommendation.
5. Keep the question focused on one decision; do not bundle unrelated choices.

Example:

```text
Patch the affected boundary only (Recommended)
[confidence=0.82] Pros: smallest verified blast radius. Cons: leaves unrelated debt in place.
Flips if graph evidence shows the defect is shared by multiple boundaries.
```

## Confidence calibration

| Band | Range | Meaning |
|---|---:|---|
| High | 0.80-0.95 | Evidence strongly favors one option. |
| Medium | 0.50-0.79 | A named missing fact could change the recommendation. |
| Low | 0.20-0.49 | User intent or risk appetite should decide. |

When relevant precedent exists, consult it without allowing historical preference to override current
safety or explicit user direction.

## Do not ask for

- obvious typo or one-path fixes;
- choices already resolved by the user's instruction;
- implementation details that do not materially change outcome or risk;
- permission to perform work the user already approved.

## References

- Always-on ambiguity rule: `AGENTS.md` and `.codex/rules/constitutional.md`.
- Native-input guard: `.codex/hooks/before_ask_user_question.py`.
- Calibration helper: `tools/ledgers/ask_user_question_calibration.py`.
