# Duplicate Prevention Protocol

Run before creating any new Agent, Mixin, Orchestrator, Engine, utility function, or SSOT constant.

## Four-Step Search

1. **AST symbol search** — find all classes/functions with equivalent signatures via ADG
2. **Name pattern search** — find all symbols with overlapping name stems
3. **Behavioral search** — find symbols that read/write the same data or call the same APIs
4. **Registry check** — verify symbol is not already in agent registry or SSOT constants

## DEDUP_SEARCH Evidence Format

```
## DEDUP_SEARCH
Symbol to create: <ClassName> or <function_name> or <CONSTANT_NAME>
AST search: <N> matches found [list if >0]
Name pattern search: <N> matches found [list if >0]
Behavioral search: <N> matches found [list if >0]
Registry check: <found | not found>
Decision: <reuse | extend | create>
Justification (if create): <why no existing symbol is suitable>
```

## Decision Rules

| Result | Action |
|---|---|
| Exact duplicate found | STOP — reuse existing symbol |
| Near-duplicate found | STOP — extend existing symbol |
| No duplicate found | Proceed with creation; document justification |

**If any match found → do not create a new symbol.**
