
# Cursor Author-Gate HITL (developer-loop)

> Governs **Author-Gate** when Cursor Agent needs a human choice before editing. NOT runtime production HITL (`agentic_core/L5_safety/`).

## When to stop and ask

Fire the pipeline before edits when ANY of these apply:

- `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`
- Two or more plausible approaches with different blast radius / reversibility
- User did not give an unambiguous directive for this exact choice

Do NOT fire for typos, single-path fixes, formatting, or explicit user instructions.

## Mandatory pipeline (same response)

1. `refactor-decision-memory` skill (precedent lookup)
2. Emit packet (canonical — never hand-craft JSON):

```bash
echo '<spec-json>' | python .claude/skills/author-gate-packet-builder/emit_packet.py
```

3. Render card + `OPTIONS_JSON` (never hand-build option descriptions):

```bash
echo '<packet-json>' | python .claude/skills/author-gate-ui-renderer/render_card.py
```

Or one step:

```bash
echo '<spec-json>' | python tools/cursor/author_gate_prepare_ask.py
```

4. **`ask_user_question`** in the **same response** — copy `OPTIONS_JSON` into `options` verbatim. Use the `question` from `ASK_PROMPT:` when present.
5. After user selects: first line `DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<id>, outcome=executed[, confidence=0.NN, ...]`

⛔ Forbidden: Markdown option menus (`**Option A**`, tables, prose lists). Forbidden: packet without `ask_user_question`. Forbidden: hand-crafted `[confidence=…]` strings.

## Cursor UI option shape

Each `ask_user_question` option:

| Field | Source |
|-------|--------|
| `label` | `candidate.surface_label` from packet (includes `⭐ Recommended —` on leading option) |
| `description` | `candidate.surface_description` (includes `[RECOMMENDED ⭐ confidence=0.NN]` or `[confidence=0.NN]` + ` · trade-off: …`) |

Leading option = highest-confidence **surfaced** candidate. Exactly one ⭐ in the whole question.

## Auto-proceed (no ask)

Skip `ask_user_question` only when `routing.rule_applied == "dominance_fires"` AND precedent `verdict == "strong"`. Still emit `AUTHOR_GATE_PACKET:` and `DECISION_CAPTURED:` if you execute without asking.

## Detail

Triggers: `author-gate-decision-points.md`. Scoring: `author-gate-enforcement.md`. Schema: `.cursor/schemas/author_gate_packet.schema.json`.
