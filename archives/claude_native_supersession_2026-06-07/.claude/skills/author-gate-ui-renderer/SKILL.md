---
name: author-gate-ui-renderer
description: DEPRECATED — do not invoke. The Author-Gate recommendation-card renderer was retired in W1 (ADR-093, claude-native-supersession-9d3f7a); its role is fully absorbed by the ask-user-question-recommendation skill. At an Author-Gate-class decision, call the native AskUserQuestion tool directly and put the recommendation + numeric confidence in the option text. No packet, no card, no render_card.py.
metadata:
  enforcement_layer: cursor
  enforcement_timing: before_ask_user_question
  enforcement_type: behavioural
---

# DEPRECATED — superseded by native AskUserQuestion (W1, ADR-093)

> ⛔ Retired W1 (`claude-native-supersession-9d3f7a`, ADR-093). This skill rendered a 6-line
> recommendation card from an `AUTHOR_GATE_PACKET:` before `ask_user_question`. Both the
> packet and the card are gone — the native `AskUserQuestion` tool renders clickable options,
> and the recommendation + confidence live in the option text. **Do not invoke this skill, do
> not run `render_card.py`, and do not build a card or a packet.**

## What to do instead

Shape the native **`AskUserQuestion`** call per the
**[`ask-user-question-recommendation`](../ask-user-question-recommendation/SKILL.md)** skill —
the single SSOT for the option shape:

- recommended option first; its `label` ends `(Recommended)`;
- every option `description` begins `[confidence=0.NN]`;
- the recommended option's `description` begins `[RECOMMENDED ⭐ confidence=0.NN]` (one `⭐`);
- then a one-line trade-off; the recommended one names the flip condition.

Invariant SSOT: `CLAUDE.md` § Author-Gate + `.claude/rules/constitutional.md` §6.

> `render_card.py` in this directory is dormant residue retained only so existing
> tests/imports do not break. Its full teardown (with the coupled governance scripts, dormant
> CI gates, and packet schema) is tracked as a follow-up; see
> `docs/reports/governance/claude_native_supersession_coupling_map.md` (surface S1).
