---
name: ask-user-question-recommendation
description: Single SSOT for shaping a Codex request_user_input call on an Author-Gate-class decision (>=2 approaches, different blast radius). Use before invoking request_user_input: recommended option first, label ends (Recommended), every option description begins with numeric [confidence=0.NN], the recommended one begins [RECOMMENDED ⭐ confidence=0.NN], and every option includes Pros: and Cons:.
trigger: model_decision
---

# Codex request_user_input Recommendation Convention

This is the one authoring convention for Codex `request_user_input` calls on
Author-Gate-class decisions (constitutional §6 / AGENTS.md Author-Gate).

The preferred live UI mechanism is the native Codex request tool. Do not build
custom cards, marker packets, or prose option menus. The recommendation,
confidence, pros/cons, and flip condition live in the option text so the user
can evaluate the choice directly in the Codex UI when that tool is available.

Availability rule: call `request_user_input` only when Codex exposes it in the
current mode. If the tool is unavailable, ask one plain-text clarifying question
directly in the assistant response using the same recommended-first option
labels/descriptions, and state that the native UI is unavailable in this turn.
Do not claim the UI rendered unless the tool call actually succeeds.

## When this fires

Use this skill when two or more plausible approaches have different blast radius
and the user has not already given an unambiguous directive.

The two legal moves at a decision point are:

1. Call `request_user_input` using this convention when the tool is available.
2. Ask one plain-text clarifying question with the same option shape when the
   tool is unavailable in the current mode.
3. Decide and proceed when one option clearly dominates.

A casual prose "do you want X or Y?" menu is not a compliant Author-Gate.

## Required Codex Shape

1. The recommended option goes first, and its `label` ends with `(Recommended)`.
2. Every option `description` begins with a numeric `[confidence=0.NN]` prefix.
3. The recommended option `description` begins with
   `[RECOMMENDED ⭐ confidence=0.NN]`.
4. Every option description includes `Pros:` and `Cons:`.
5. The recommended option includes `Flips if ...`.
6. Every question includes a stable Codex `id`, a short `header`, a `question`,
   and `options`.

### Template

```python
request_user_input(
    questions=[
        {
            "id": "decision_scope",
            "header": "Decision",
            "question": "Which approach should I take?",
            "options": [
                {
                    "label": "Patch narrowly (Recommended)",
                    "description": "[RECOMMENDED ⭐ confidence=0.82] Pros: fixes the known break. Cons: leaves broader cleanup for a later pass. Flips if evidence shows the break is systemic.",
                },
                {
                    "label": "Broaden cleanup",
                    "description": "[confidence=0.54] Pros: removes more debt now. Cons: larger blast radius and slower verification.",
                },
            ],
        }
    ]
)
```

## Confidence Calibration

Use numeric confidence only. Good defaults:

| Band | Numeric | Use when |
|---|---:|---|
| High | 0.80-0.95 | One option clearly dominates on risk, precedent, or blast radius. |
| Medium | 0.50-0.79 | You have a real lean, but a named fact could flip it. |
| Low | 0.20-0.49 | The options are close and user intent should decide. |

Before finalizing a number, consult prior choices when available:

```bash
python -m tools.ledgers.ask_user_question_calibration "<context-slug>" 0.NN
```

The context slug is the question `header` lower-cased with non-alphanumerics
collapsed to `-`.

## Applies To RCA Fix Steps

When an RCA's next step has two or more real options, use `request_user_input`
with this confidence shape. Do not end an RCA with a prose options menu.

## Forbidden

- A neutral menu with no `(Recommended)` option on an Author-Gate-class decision.
- A recommended option without numeric confidence, `Pros:`, `Cons:`, and
  `Flips if ...`.
- Placing the recommended option anywhere but first.
- More than one recommendation star.
- Custom marker packets, custom cards, or prose option menus.
- Invoking a question tool for typos, single-path fixes, or explicit
  instructions.

## Bypass / Strict

- `ASK_REC_GUARD_BYPASS=1` allows and logs.
- `ASK_REC_GUARD_STRICT=1` turns missing recommendation advisory findings into
  blocking findings.

## References

- Invariant: `AGENTS.md` § Author-Gate; `.codex/rules/constitutional.md` §6.
- Gate: `.codex/governance/scripts/pre_ask_user_question_recommendation_gate.py`.
- Hook: `.codex/hooks/before_ask_user_question.py`.
- Capture: `.codex/hooks/after_ask_user_question.py` →
  `.codex/governance/scripts/post_ask_user_question_capture.py` →
  `ask_user_question_decisions` ledger.
- Calibration helper: `tools/ledgers/ask_user_question_calibration.py`.
- Prose-menu trigger auditor: `post_agent_recommendation_gate_audit.py`.
