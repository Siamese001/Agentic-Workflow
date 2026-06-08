---
name: ask-user-question-recommendation
description: Use when composing a native AskUserQuestion call for an Author-Gate-class decision (architecture choice, refactor scope, deletion, dependency add, error-handling strategy) to render the recommended option and confidence band the retired Author-Gate UI pipeline used to manufacture. Use before invoking AskUserQuestion so options carry a (Recommended) marker and a confidence signal.
trigger: model_decision
---

# AskUserQuestion Recommendation Renderer

Authoring convention for native `AskUserQuestion` on **Author-Gate-class** decisions
(constitutional §6 / CLAUDE.md Author-Gate). This skill is the post-supersession successor
to the retired `author-gate-ui-renderer` skill: the W1 native-supersession (ADR-093) dropped
the structured card that *manufactured* a STAR recommendation and a confidence band, so
those two fields are now produced by hand. The companion deterministic check is
`.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py` (PreToolUse hook
`before_ask_user_question.py`), which flags any call missing them.

> RCA precedent (2026-06-08): two AskUserQuestion calls shipped with neither a
> `(Recommended)` marker nor a confidence signal. This skill + gate close that gap.

## When this fires

Use when ≥2 plausible approaches have **different blast radius** and **no unambiguous user
directive** — i.e. a genuine Author-Gate decision. Do **not** apply to symmetric preference
questions ("which color theme?") where no option is objectively recommended.

## The required shape

1. **Recommended option goes first**, and its `label` ends with `(Recommended)`.
2. **That option's `description` carries a confidence signal** — a band word
   (`high` / `medium` / `low`) and, ideally, the single fact that would flip the
   recommendation.
3. Every other option still gets a one-line trade-off.

### Template

```python
AskUserQuestion(questions=[{
  "question": "<the decision, ending with '?'>",
  "header": "<≤12 char chip>",
  "multiSelect": False,
  "options": [
    {"label": "<preferred> (Recommended)",
     "description": "<one-line trade-off>. Confidence: <high|medium|low> — flips if <condition>."},
    {"label": "<alt 1>", "description": "<one-line trade-off>"},
    {"label": "<alt 2>", "description": "<one-line trade-off>"},
  ],
}])
```

## Confidence calibration (band → when)

| Band | Use when |
|---|---|
| **high** | One option clearly dominates on blast radius/precedent; you'd proceed alone if forced. |
| **medium** | A real lean, but a named fact (cost, scope, a pending signal) could flip it. |
| **low** | Genuinely close; surfacing mostly to confirm intent, not because you have a strong read. |

State the **flip condition** explicitly — it is the load-bearing half of a confidence band
("medium — flips if CI red turns out to be caused by our diff").

## Forbidden

- ❌ A neutral menu with no `(Recommended)` option on an Author-Gate-class decision.
- ❌ A recommended option with no confidence band / flip condition.
- ❌ Placing the recommended option anywhere but first.
- ❌ Firing AskUserQuestion for typos, single-path fixes, or explicit instructions (§6).

## Bypass / strict

- Advisory by default — the gate warns but does not block.
- `ASK_REC_GUARD_STRICT=1` — gate blocks (exit 2) on a non-compliant call.
- `ASK_REC_GUARD_BYPASS=1` — gate allows and logs.

## References

- Invariant: `CLAUDE.md` § Author-Gate; `.claude/rules/constitutional.md` §6.
- Gate: `.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py`.
- Hook: `.claude/hooks/before_ask_user_question.py` (PreToolUse `AskUserQuestion`).
- Violations log: `artifacts/cursor/ask_user_question_violations.jsonl`.
- Retired predecessor: `author-gate-ui-renderer` skill (W1 supersession, ADR-093).
