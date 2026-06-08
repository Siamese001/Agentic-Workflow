---
name: refactor-decision-memory
description: Consult historical refactor and Author-Gate decisions before opening a new Author-Gate packet. Queries the local SQLite decision ledger for precedent matching the current decision type and intent, returning a strong/suggestive/none verdict with matched decisions to bias or enrich the next Author-Gate packet. (1 supporting file)
metadata:
  enforcement_layer: cursor
  enforcement_timing: before_hitl
  enforcement_type: behavioural
---

# Refactor Decision Memory Skill

**PURPOSE:** Surface historical refactor/Author-Gate decisions to bias or enrich upcoming Author-Gate packets.
This skill is the lookup engine — it does **not** replace `author-gate-enforcement.md` as policy SSOT.

## When to Invoke

Invoke before opening Author-Gate for any of these decision classes (per `author-gate-decision-points.md` §AG-1):

- Architecture choice (§1.1)
- Refactoring scope (§1.2)
- Anti-pattern resolution (§1.3)
- Test modification strategy (§1.4)
- Dependency addition (§1.5)
- File/module deletion (§1.6)
- Error handling strategy (§1.8)

Per `refactor-decision-memory.md` rule — this skill runs before the Author-Gate packet is assembled.

## Files

- **`lookup_refactor_decisions.py`** — SQLite + FTS5 query engine; returns JSON verdict

## Usage

```bash
echo '{
  "decision_type": "refactor_scope",
  "normalized_intent": "Extract L2 execution adapter into a dedicated module",
  "repo_area": "agentic_core/L2_execution",
  "limit": 5
}' | python .claude/skills/refactor-decision-memory/lookup_refactor_decisions.py
```

Valid `decision_type` values:
`architecture_choice` | `refactor_scope` | `anti_pattern` | `dependency_addition` |
`test_strategy` | `deletion_strategy` | `error_handling` | `unknown`

## Output Shape

```json
{
  "verdict": "strong",
  "matches": [
    {
      "strength": "strong",
      "decision_id": "dec_abc123...",
      "decision_type": "refactor_scope",
      "request_summary": "...",
      "normalized_intent": "...",
      "selected_option_id": "Minimal scope — single file",
      "selection_rationale": "...",
      "repo_area": "agentic_core/L2_execution",
      "file_path": "agentic_core/L2_execution/adapters.py",
      "tests_passed": true,
      "promote_to_pattern": true,
      "created_at": "2026-04-10T09:55:00Z"
    }
  ],
  "query_echo": { ... }
}
```

## Verdict Routing

| Verdict | Author-Gate Action |
|---------|-------------|
| `strong` | Reuse or heavily bias toward matched precedent. State: "Historical precedent recommends: …" Consider bypassing Author-Gate if dominance rule fires and `promote_to_pattern=true` and no regression. |
| `suggestive` | Include precedent summary in Author-Gate framing. Add "Prior decision (YYYY-MM-DD): …" in the question packet header. |
| `none` | Proceed with standard Author-Gate per `author-gate-enforcement.md`. No precedent bias. |

## Cold Start

If the ledger does not exist (no decisions captured yet), the script returns:

```json
{"verdict": "none", "matches": [], "reason": "no ledger found — no decisions captured yet"}
```

Proceed with standard Author-Gate.

## Ledger Location

`.claude/state/refactor_decisions/refactor_decision_ledger.sqlite`

Auto-created on first Author-Gate capture by the `post_agent_response` hook.

Schema tables: `decisions`, `decision_scope`, `decision_outcomes`, `decisions_fts` (FTS5 virtual).
