---
name: author-gate-ui-renderer
description: Render a condensed, high-signal recommendation card before ask_user_question for Author-Gate decisions. Invoke AFTER author-gate-packet-builder emits the AUTHOR_GATE_PACKET block and BEFORE ask_user_question. Reads the emitted packet JSON and produces a compressed card showing the recommended option, confidence band, precedent verdict, "what would flip" top-2, blast radius, hotspot rank, and reason-code palette. Keeps reviewer attention focused on the ≤3 signals that change the decision.
metadata:
  enforcement_layer: cursor
  enforcement_timing: before_ask_user_question
  enforcement_type: behavioural
---

# Author-Gate UI Renderer

**PURPOSE:** Compress the Author-Gate packet into a 6-line recommendation card the approver can scan in <5 seconds.

Galileo, dev.to, and codeongrass independently identify reviewer attention as the scarcest resource in HITL systems. `ask_user_question` renders `{label, description}` with ≤4 options — recommended option, confidence band, precedent verdict, and "what would flip" are dropped. This skill restores the signal BEFORE the question fires.

## When to Invoke

Immediately after `author-gate-packet-builder` emits its `AUTHOR_GATE_PACKET:` block, and immediately before `ask_user_question`. Do NOT invoke for T0/T1 edits or for packets where routing fired `dominance_fires` AND precedent verdict is `strong` (proceed without asking per `author-gate-enforcement.md`).

> ⛔ **Pipeline Completion Invariant**: `AUTHOR_GATE_PACKET:` → render card → `ask_user_question` MUST all occur **in the same Cursor Agent response**. Emitting the packet without a same-response `ask_user_question` is a critical violation logged by `post_cursor_agent_author_gate_pipeline_audit.py`. See plan `author-gate-ui-renderer-hardening-a7f3c2`.

**Forbidden**: emitting `AUTHOR_GATE_PACKET:` then ending the response without `ask_user_question`; splitting packet and question across responses; relying on the user to prompt for the question after seeing the card.

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

The canonical description for every surfaced option is **`candidate.surface_description`** — minted by `emit_packet.py` (plan `author-gate-four-req-enforcement-c4d2a8` W1.P1). Pass it through `OPTIONS_JSON` unchanged. The floor it guarantees is:

```
[<RECOMMENDED ⭐ if dominance_fires>confidence=0.NN] · trade-off: <key_tradeoffs[0][:80]>
```

Equivalent to the four-requirement contract in `author-gate-enforcement.md` Pipeline step 7:

| # | Requirement | Where it shows up |
|---|---|---|
| 1 | clickable | the option itself in `ask_user_question` |
| 2 | confidence | `[confidence=0.NN]` (or `[RECOMMENDED ⭐ confidence=0.NN]`) prefix |
| 3 | pros/cons | ` · trade-off: <text>` segment |
| 4 | dominance star | `⭐` iff `routing.rule_applied == "dominance_fires"`, exactly once |

### Extending the description

Callers MAY supply a richer `surface_description` on the input spec. The emitter prepends the floor automatically when the supplied text does not begin with the prefix, so the four requirements are preserved no matter how the caller composed it. Sample extended description:

```
[confidence=0.85] · trade-off: Higher coverage but bigger blast · also: rolls back cleanly via single git revert
```

### Renderer fallback for legacy packets

Pre-W1.P1 packets carry only `surface_description_prefix`. `render_card.py` falls through `surface_description` → `surface_description_floor` → locally-built description (`<pill> <score> · precedent: <verdict> · flip: <cond>`) so older packets still render, but they will fail UI-audit invariant 4 if they reach `ask_user_question`.

## Files

- `render_card.py` — Python helper that takes a packet JSON on stdin and prints the card + the enriched options JSON on stdout.

## Example Invocation

```bash
echo '<AUTHOR_GATE_PACKET JSON here>' | \
  python .cursor/skills/author-gate-ui-renderer/render_card.py
```

Output:

```
🎯 Recommended: minimal — Extract SovereignBaseAgent only; defer siblings
   Confidence:  🟢 0.89 (calibrated, n=3 precedents)
   ...

OPTIONS_JSON: [{"label": "...", "description": "..."}, ...]
```

The caller reads the `OPTIONS_JSON:` line and passes the parsed list directly to `ask_user_question`.
