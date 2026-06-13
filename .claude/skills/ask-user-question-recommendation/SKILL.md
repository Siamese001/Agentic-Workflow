---
name: ask-user-question-recommendation
description: THE single SSOT for how to shape a native AskUserQuestion call on an Author-Gate-class decision (architecture choice, refactor scope, deletion, dependency add, error-handling strategy). Use before invoking AskUserQuestion so the recommended option is first, its label ends "(Recommended)", and every option description begins with a numeric [confidence=0.NN] prefix (the recommended one with [RECOMMENDED ⭐ confidence=0.NN]). Absorbs the role of the retired author-gate-packet-builder / author-gate-ui-renderer skills (W1, ADR-093).
trigger: model_decision
---

# AskUserQuestion Recommendation Convention (SSOT)

The **one** authoring convention for native `AskUserQuestion` on **Author-Gate-class**
decisions (constitutional §6 / CLAUDE.md Author-Gate). This skill is the sole survivor of the
retired Author-Gate UI pipeline: the W1 native-supersession (ADR-093 /
`claude-native-supersession-9d3f7a`) dropped the bespoke packet-builder → ui-renderer →
`AUTHOR_GATE_PACKET:`/`DECISION_CAPTURED:` → ledger machinery that used to *manufacture* a
recommendation marker and a confidence band. The native tool gives a clickable option list;
the recommendation + confidence now live **in the option text**, produced by hand to this
convention. The companion deterministic check is
`.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py` (PreToolUse hook
`before_ask_user_question.py`), which blocks a marked recommendation that carries no
confidence signal.

> There is exactly **one** convention — this file. The legacy `author-gate-packet-builder`
> and `author-gate-ui-renderer` skills are retired stubs; do not invoke them, do not emit
> `AUTHOR_GATE_PACKET:` / `DECISION_CAPTURED:` markers, and do not build packet JSON or a
> 6-line card. One `AskUserQuestion` call is the whole mechanism.

> RCA precedent (2026-06-08): two AskUserQuestion calls shipped with neither a
> `(Recommended)` marker nor a confidence signal. This skill + gate close that gap.

## When this fires

Use when ≥2 plausible approaches have **different blast radius** and **no unambiguous user
directive** — i.e. a genuine Author-Gate decision. Do **not** apply to symmetric preference
questions ("which color theme?") where no option is objectively recommended (a question with
no `(Recommended)` option is fine there — the gate treats it as advisory, not a miss).

The two legal moves at a decision point are: **fire `AskUserQuestion`** (this convention) or
**decide-and-proceed** when one option dominates. A prose "do you want X or Y?" menu is the
forbidden third move (see memory `no-prose-options-menus`).

## The required shape (canonical — user directive 2026-06-13)

1. **Recommended option goes first**, and its `label` ends with `(Recommended)`.
2. **Every option's `description` begins with a numeric `[confidence=0.NN]` prefix.**
3. The **recommended option's `description` begins with `[RECOMMENDED ⭐ confidence=0.NN]`** —
   the `⭐` appears exactly once, on the recommended option only.
4. After the prefix, each description carries a one-line trade-off; the recommended one
   names the single fact that would **flip** the recommendation.

This single shape satisfies all three live constraints at once: the native-tool convention
(`(Recommended)` label), the gate (`(Recommended)` + a confidence token, recommended first),
and the numeric `[confidence=0.NN]` user directive.

### Template

```python
AskUserQuestion(questions=[{
  "question": "<the decision, ending with '?'>",
  "header": "<≤12 char chip>",
  "multiSelect": False,
  "options": [
    {"label": "<preferred> (Recommended)",
     "description": "[RECOMMENDED ⭐ confidence=0.NN] <one-line trade-off>. Flips if <condition>."},
    {"label": "<alt 1>", "description": "[confidence=0.NN] <one-line trade-off>"},
    {"label": "<alt 2>", "description": "[confidence=0.NN] <one-line trade-off>"},
  ],
}])
```

## Confidence calibration (0.NN → when)

| Band | Numeric | Use when |
|---|---|---|
| **high** | ≈ 0.80–0.95 | One option clearly dominates on blast radius/precedent; you'd proceed alone if forced. |
| **medium** | ≈ 0.50–0.79 | A real lean, but a named fact (cost, scope, a pending signal) could flip it. |
| **low** | ≈ 0.20–0.49 | Genuinely close; surfacing mostly to confirm intent, not because you have a strong read. |

Always emit the **number** (`[confidence=0.72]`), not the band word. State the **flip
condition** explicitly — it is the load-bearing half of a confidence signal
("`[RECOMMENDED ⭐ confidence=0.72]` … flips if CI red turns out to be caused by our diff").

> The live gate tolerates a bare `high`/`medium`/`low` word as a legacy fallback so it never
> hard-blocks an older-style call, but the numeric `[confidence=0.NN]` prefix is the **only
> canonical form** — author every option that way.

## Applies to RCA fix steps too

When an RCA's `Next` / fix step offers ≥2 real options, surface them via `AskUserQuestion`
with this confidence shape — never as a prose menu or a bare "I recommend X".

## Forbidden

- ❌ A neutral menu with no `(Recommended)` option on an Author-Gate-class decision.
- ❌ A recommended option with no `[confidence=0.NN]` prefix / flip condition.
- ❌ Placing the recommended option anywhere but first; more than one `⭐`.
- ❌ Emitting `AUTHOR_GATE_PACKET:` / `DECISION_CAPTURED:` or invoking the retired
  packet-builder / ui-renderer skills — the pipeline is gone (ADR-093).
- ❌ Firing AskUserQuestion for typos, single-path fixes, or explicit instructions (§6).

## Bypass / strict

- A marked recommendation with **no confidence signal blocks by default** (the core §6 /
  user-directive violation).
- A missing/last `(Recommended)` is **advisory** (exit 0) by default — it may be a legitimate
  symmetric question.
- `ASK_REC_GUARD_STRICT=1` — gate also blocks the advisory cases (exit 2).
- `ASK_REC_GUARD_BYPASS=1` — gate allows and logs.

## References

- Invariant: `CLAUDE.md` § Author-Gate; `.claude/rules/constitutional.md` §6.
- Gate: `.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py`.
- Hook: `.claude/hooks/before_ask_user_question.py` (PreToolUse `AskUserQuestion`).
- Prose-menu trigger auditor (Stop): `post_agent_recommendation_gate_audit.py`.
- Violations log: `artifacts/cursor/ask_user_question_violations.jsonl`.
- User directive: memory `no-prose-options-menus` (2026-06-13).
- Retired predecessors (now stubs): `author-gate-ui-renderer`, `author-gate-packet-builder`
  (W1 supersession, ADR-093).
