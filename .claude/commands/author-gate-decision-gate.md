---
description: Thin alias — Author-Gate HITL before significant decisions (invoke /author-gate-decision-gate)
---

# /author-gate-decision-gate

**Tier:** Workflow alias only — not policy.

## Authority map

| Layer | SSOT |
|-------|------|
| Tier 1 invariant | [003-cursor-author-gate-hitl.md](../rules/003-cursor-author-gate-hitl.md) |
| On-demand extensions | [author-gate-enforcement.md](../rules/author-gate-enforcement.md), [author-gate-decision-points.md](../rules/author-gate-decision-points.md) |
| Procedure | Skills `author-gate-packet-builder`, `author-gate-ui-renderer`, `refactor-decision-memory` |

## Invocation steps

1. Confirm a genuine Author-Gate trigger (see `003` and `author-gate-decision-points.md`).
2. Run skills in order: precedent → `emit_packet.py` → `render_card.py` (or `tools/cursor/author_gate_prepare_ask.py`).
3. Call `ask_user_question` with `OPTIONS_JSON` verbatim in the **same response**.
4. After selection: emit `DECISION_CAPTURED:` as first line when refactor-class.

⛔ No prose option menus. No hand-crafted packets or confidence strings.
