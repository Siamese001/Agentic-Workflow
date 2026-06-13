# DEPRECATED — superseded by native AskUserQuestion (W1 claude-native-supersession-9d3f7a)

> ⛔ Retired W1 (ADR-093). The Author-Gate packet-builder → ui-renderer → `AUTHOR_GATE_PACKET:` →
> `DECISION_CAPTURED:` → SQLite-ledger → queue pipeline emulated a structured-choice tool that
> Claude Code now provides natively.

## What to do instead

When ≥2 plausible approaches have different blast radius and no unambiguous user directive, call the
native **`AskUserQuestion`** tool: present each option with a one-line trade-off and mark the
recommended one. No packet, no marker, no ledger, no queue. For typos / single-path fixes / explicit
instructions, just proceed. Precedent (if useful) lives in file memory.

Invariant SSOT: `CLAUDE.md` § Author-Gate + `.claude/rules/constitutional.md` §6.
