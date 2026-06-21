---
name: ask-user-question-recommendation
description: Single SSOT for shaping a native AskUserQuestion call on an Author-Gate-class decision (>=2 approaches, different blast radius). Use before invoking AskUserQuestion: recommended option first, its label ends (Recommended), every option description begins with numeric [confidence=0.NN], the recommended one with [RECOMMENDED ⭐ confidence=0.NN], and every option includes Pros: and Cons:.
trigger: model_decision
---

# AskUserQuestion Recommendation Convention (SSOT)

The **one** authoring convention for native question tools (`AskUserQuestion` in Claude Code,
`request_user_input` in Codex) on **Author-Gate-class** decisions (constitutional §6 /
AGENTS.md Author-Gate). This skill is the sole survivor of the
retired Author-Gate UI pipeline: the W1 native-supersession (ADR-093 /
`claude-native-supersession-9d3f7a`) dropped the bespoke packet-builder → ui-renderer →
`AUTHOR_GATE_PACKET:`/`DECISION_CAPTURED:` → ledger machinery that used to *manufacture* a
recommendation marker and a confidence band. The native tool gives a clickable option list;
the recommendation + confidence now live **in the option text**, produced by hand to this
convention. The companion deterministic check is
`.codex/governance/scripts/pre_ask_user_question_recommendation_gate.py` (PreToolUse hook
`before_ask_user_question.py`), which blocks a marked recommendation that lacks visible
numeric confidence, the recommendation star, pros/cons, or flip criteria.

> There is exactly **one** convention — this file. The legacy `author-gate-packet-builder`
> and `author-gate-ui-renderer` skills were retired and archived (ADR-093); do not invoke
> them, do not emit `AUTHOR_GATE_PACKET:` / `DECISION_CAPTURED:` markers, and do not build
> packet JSON or a 6-line card. One `AskUserQuestion` call is the whole mechanism.

> RCA precedent (2026-06-08): two AskUserQuestion calls shipped with neither a
> `(Recommended)` marker nor a confidence signal. This skill + gate close that gap.

## When this fires

Use when ≥2 plausible approaches have **different blast radius** and **no unambiguous user
directive** — i.e. a genuine Author-Gate decision. Do **not** apply to symmetric preference
questions ("which color theme?") where no option is objectively recommended (a question with
no `(Recommended)` option is fine there — the gate treats it as advisory, not a miss).

The two legal moves at a decision point are: **fire the native question tool** (this convention)
or **decide-and-proceed** when one option dominates. A prose "do you want X or Y?" menu is the
forbidden third move (see memory `no-prose-options-menus`).

## The required shape (canonical — user directives 2026-06-13 and 2026-06-15)

1. **Recommended option goes first**, and its `label` ends with `(Recommended)`.
2. **Every option's `description` begins with a numeric `[confidence=0.NN]` prefix.** The
   accepted range is `0.00` through `1.00`; word bands like `high` do not satisfy the UI contract.
3. The **recommended option's `description` begins with `[RECOMMENDED ⭐ confidence=0.NN]`** —
   the `⭐` appears exactly once, on the recommended option only.
4. After the prefix, each description carries `Pros:` and `Cons:` in one line; the recommended
   one also names the single fact that would **flip** the recommendation.

This single shape satisfies all live constraints at once: the native-tool convention
(`(Recommended)` label), the gate (`(Recommended)` + a confidence token, recommended first),
the numeric `[confidence=0.NN]` user directive, and the explicit pros/cons criterion.

### Template

```python
AskUserQuestion(questions=[{
  "question": "<the decision, ending with '?'>",
  "header": "<≤12 char chip>",
  "multiSelect": False,
  "options": [
    {"label": "<preferred> (Recommended)",
     "description": "[RECOMMENDED ⭐ confidence=0.NN] Pros: <benefit>. Cons: <cost>. Flips if <condition>."},
    {"label": "<alt 1>", "description": "[confidence=0.NN] Pros: <benefit>. Cons: <cost>."},
    {"label": "<alt 2>", "description": "[confidence=0.NN] Pros: <benefit>. Cons: <cost>."},
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

> The numeric `[confidence=0.NN]` prefix is the **only canonical form**, and the recommended
> option must use `[RECOMMENDED ⭐ confidence=0.NN]` with exactly one star. Word-band confidence
> (`high`/`medium`/`low`) is useful prose context, but it does not satisfy the output contract.

## Consult precedent before stating confidence (meta-learning loop)

Every AskUserQuestion is **captured** to the `ask_user_question_decisions` ledger
(`.codex/hooks/after_ask_user_question.py` → `post_ask_user_question_capture.py`): the
recommended option, the stated confidence, and the user's actual selection. That history is how
the confidence you state should improve over time — consult it before finalizing a number:

```bash
python -m tools.ledgers.ask_user_question_calibration "<context-slug>" 0.NN
```

The `<context-slug>` is the question `header` lower-cased with non-alphanumerics collapsed to `-`
(e.g. header `Next step` → `next-step`). It returns the empirical acceptance rate (how often
users took the recommendation in that context, Wilson-95 lower bound) and a
`calibrated_confidence` suggestion:

- **signal `none`** (n < 5) — no precedent yet; use your own read.
- **signal `suggestive` / `strong`** — bias the stated number toward `calibrated_confidence`; a
  `diverged=true` means your instinct is materially out of step with what users actually choose
  here (e.g. you keep stating 0.90 but the recommendation is overridden half the time).

The PreToolUse gate also emits an `ADVISORY (askq-calibration): …` line on a divergence —
informational only, never blocks (silence with `ASK_REC_CALIBRATION_ADVISORY=0`). The loop is
self-correcting: **state → user selects → captured → calibrates the next state.**

## Applies to RCA fix steps too

When an RCA's `Next` / fix step offers ≥2 real options, surface them via `AskUserQuestion`
with this confidence shape — never as a prose menu or a bare "I recommend X".

## Forbidden

- ❌ A neutral menu with no `(Recommended)` option on an Author-Gate-class decision.
- ❌ A recommended option with no `[confidence=0.NN]` prefix / Pros/Cons / flip condition.
- ❌ Placing the recommended option anywhere but first; more than one `⭐`.
- ❌ Emitting `AUTHOR_GATE_PACKET:` / `DECISION_CAPTURED:` or invoking the retired
  packet-builder / ui-renderer skills — the pipeline is gone (ADR-093).
- ❌ Firing AskUserQuestion for typos, single-path fixes, or explicit instructions (§6).

## Bypass / strict

- A marked recommendation with **missing confidence, Pros/Cons, or flip criteria blocks by default**
  (the core §6 / user-directive violation).
- A missing/last `(Recommended)` is **advisory** (exit 0) by default — it may be a legitimate
  symmetric question.
- `ASK_REC_GUARD_STRICT=1` — gate also blocks the advisory cases (exit 2).
- `ASK_REC_GUARD_BYPASS=1` — gate allows and logs.

## References

- Invariant: `AGENTS.md` § Author-Gate; `.codex/rules/constitutional.md` §6.
- Gate: `.codex/governance/scripts/pre_ask_user_question_recommendation_gate.py`.
- Hook: `.codex/hooks/before_ask_user_question.py` (PreToolUse `AskUserQuestion`).
- Capture (PostToolUse `AskUserQuestion`): `.codex/hooks/after_ask_user_question.py` →
  `.codex/governance/scripts/post_ask_user_question_capture.py` → `ask_user_question_decisions` ledger.
- Calibration helper: `tools/ledgers/ask_user_question_calibration.py` (precedent → calibrated confidence).
- Plan: `plans/askq-confidence-meta-learning-loop-c4e7a1.md` (the meta-learning loop).
- Prose-menu trigger auditor (Stop): `post_agent_recommendation_gate_audit.py`.
- Violations log: `artifacts/cursor/ask_user_question_violations.jsonl`.
- User directive: memory `no-prose-options-menus` (2026-06-13).
- Retired predecessors (archived): `author-gate-ui-renderer`, `author-gate-packet-builder`
  (W1 supersession, ADR-093).
