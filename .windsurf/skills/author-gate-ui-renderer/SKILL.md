---
name: author-gate-ui-renderer
description: Render a condensed, high-signal recommendation card before ask_user_question for Author-Gate decisions. Invoke AFTER author-gate-packet-builder emits the AUTHOR_GATE_PACKET block and BEFORE ask_user_question. Reads the emitted packet JSON and produces a compressed card showing the recommended option, confidence band, precedent verdict, "what would flip" top-2, blast radius, hotspot rank, and reason-code palette. Keeps reviewer attention focused on the ≤3 signals that change the decision.
metadata:
  enforcement_layer: windsurf
  enforcement_timing: before_ask_user_question
  enforcement_type: behavioural
---

# Author-Gate UI Renderer

**PURPOSE:** Compress the Author-Gate packet into a 6-line recommendation card the approver can scan in <5 seconds.

Galileo, dev.to, and codeongrass independently identify reviewer attention as the scarcest resource in HITL systems. `ask_user_question` renders `{label, description}` with ≤4 options — recommended option, confidence band, precedent verdict, and "what would flip" are dropped. This skill restores the signal BEFORE the question fires.

## When to Invoke

Immediately after `author-gate-packet-builder` emits its `AUTHOR_GATE_PACKET:` block, and immediately before `ask_user_question`. Do NOT invoke for T0/T1 edits or for packets where routing fired `dominance_fires` AND precedent verdict is `strong` (proceed without asking per `author-gate-enforcement.md`).

## Card Shape (fill in from packet)

```
🎯 Recommended: <option.id> — <one-line thesis>
   Confidence:  🟢 <score> (calibrated, n=<precedent_match_count> precedents)
   Why:         <principle_at_stake> · precedent: <verdict>
   Would flip:  <what_would_flip[0]>; <what_would_flip[1]>
   Blast:       <hops> hops · hotspot rank #<rank> · surfaces: <surfaces>
   Reason-code palette (pick ONE if overriding):
     override_recommendation | insufficient_precedent | blast_radius_too_high
     | principle_shift | test_strategy_change | dependency_risk
     | deletion_risk | other

📋 Alternatives:
   • <opt2.id>: 🟡 <score> — <one-line>
   • <opt3.id>: 🔴 <score> — <one-line>
```

## Confidence-Band Emoji Mapping

| Range | Emoji | Meaning |
|---|---|---|
| ≥ 0.85 | 🟢 | Strong recommendation, dominance fires |
| 0.72–0.85 | 🟡 | Surfaced, near-indifference band |
| < 0.72 | 🔴 | Below surface threshold — requires review |

Apply the same mapping to every alternative.

## Rules

1. **Gold star (🎯) ONLY on the recommended option** — never on alternatives.
2. **Max 6 card lines** (Recommended + Confidence + Why + Would-flip + Blast + Reason-palette).
3. **Max 2 alternatives** shown, sorted by score DESC.
4. **Precedent verdict is verb-first**: "precedent: strong" not "a strong precedent exists".
5. **Would-flip is falsifiable**: never "user prefers X"; always a concrete signal like "blast_radius>5" or "hotspot rank moves to top-10".
6. **If `routing.rule_applied == "low_confidence_ambiguity"`**, replace the gold star line with `⚠️ No recommendation — top score below 0.72 threshold. Picking is user-decision-required.`
7. **If `routing.rule_applied == "dominance_fires"` AND precedent is `strong`**, emit the card with a `⏵ Proceeding without ask_user_question` suffix and skip the question entirely.

## `ask_user_question` Option Descriptions

Each option's `description` field MUST begin with the confidence pill + recommendation flag + precedent:

```
{"label": "<thesis (≤80ch)>",
 "description": "🟢 <score> · recommended · precedent: <verdict> · flip: <cond>"}
```

For non-recommended options:

```
{"description": "🟡 <score> · precedent: <verdict> · <1-line key_tradeoff>"}
```

## Files

- `render_card.py` — Python helper that takes a packet JSON on stdin and prints the card + the enriched options JSON on stdout.

## Example Invocation

```bash
echo '<AUTHOR_GATE_PACKET JSON here>' | \
  python .windsurf/skills/author-gate-ui-renderer/render_card.py
```

Output:

```
🎯 Recommended: minimal — Extract SovereignBaseAgent only; defer siblings
   Confidence:  🟢 0.89 (calibrated, n=3 precedents)
   ...

OPTIONS_JSON: [{"label": "...", "description": "..."}, ...]
```

The caller reads the `OPTIONS_JSON:` line and passes the parsed list directly to `ask_user_question`.
