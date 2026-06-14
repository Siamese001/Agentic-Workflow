---
name: author-gate-packet-builder
description: DEPRECATED — do not invoke. The Author-Gate packet pipeline (AUTHOR_GATE_PACKET emission, schema-validated decision packets, ledger capture) was retired in W1 (ADR-093, claude-native-supersession-9d3f7a). At an Author-Gate-class decision, call the native AskUserQuestion tool directly and follow the ask-user-question-recommendation skill. No packet, no marker, no ledger.
metadata:
  enforcement_layer: cursor
  enforcement_timing: before_author_gate
  enforcement_type: behavioural
---

# DEPRECATED — superseded by native AskUserQuestion (W1, ADR-093)

> ⛔ Retired W1 (`claude-native-supersession-9d3f7a`, ADR-093). The packet-builder →
> ui-renderer → `AUTHOR_GATE_PACKET:` → `DECISION_CAPTURED:` → SQLite-ledger pipeline
> emulated a structured-choice tool that Claude Code now provides natively. **Do not invoke
> this skill, do not run `emit_packet.py` / `precedent_injector.py`, and do not emit any
> `AUTHOR_GATE_PACKET:` / `HITL_PACKET:` marker.**

## What to do instead

When ≥2 plausible approaches have different blast radius and no unambiguous user directive,
call the native **`AskUserQuestion`** tool and shape it per the
**[`ask-user-question-recommendation`](../ask-user-question-recommendation/SKILL.md)** skill
(recommended option first, label ends `(Recommended)`, every description begins
`[confidence=0.NN]`, the recommended one `[RECOMMENDED ⭐ confidence=0.NN]`). One tool call is
the whole mechanism. For typos / single-path fixes / explicit instructions, just proceed.

Invariant SSOT: `CLAUDE.md` § Author-Gate + `.claude/rules/constitutional.md` §6.

> The `emit_packet.py`, `precedent_injector.py`, and `packet_template.md` files in this
> directory are dormant residue retained only so existing tests/imports do not break. Their
> full teardown (with the coupled governance scripts, dormant CI gates, and packet schema) is
> tracked as a follow-up; see `docs/reports/governance/claude_native_supersession_coupling_map.md`
> (surface S1).
