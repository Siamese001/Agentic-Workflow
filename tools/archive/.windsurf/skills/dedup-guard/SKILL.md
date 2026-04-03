---
name: dedup-guard
description: Prevents creation of duplicate agents, mixins, utility functions, and constants before they proliferate. Use before creating any new agent class, mixin, utility function, or SSOT constant. Requires AST-backed search for semantically equivalent symbols first. Blocks creation without documented justification that no equivalent exists.
enforcement_layer: both
enforcement_timing: before_work
enforcement_type: behavioural_primary_structural_secondary
---

# Dedup Guard Skill

Enforces an AST-backed duplicate search before any new symbol, agent, or constant is created.

## Files

- **`pre_creation_checklist.md`** — Mandatory checklist before creating any new agent, mixin, utility, or constant. Steps: search for equivalent by AST, by name pattern, by signature. Decision: reuse / extend / create-with-justification.

- **`dedup_decision_tree.md`** — Three-branch decision tree: (1) exact semantic duplicate found → reuse, (2) near-duplicate found → extend existing, (3) no duplicate → create with written justification documenting the search.

## When to use

- Before creating any new class ending in `Agent`, `Mixin`, `Orchestrator`, `Engine`
- Before adding a new constant to any config or constants file
- Before creating a new utility function that operates on files, imports, or AST
- When a session involves "consolidation" or "deduplication" work

## Search Protocol (MANDATORY before creation)

1. **AST symbol search** — Find all classes/functions with equivalent signatures
2. **Name pattern search** — Find all symbols with overlapping name stems
3. **Behavioral search** — Find all symbols that read/write the same data or call the same APIs
4. **Registry check** — Verify symbol is not already registered in agent registry or SSOT constants

If any match found → STOP, document finding, choose branch 1 or 2.
Only proceed to create if all four searches return no match AND justification is written.

## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE creating any new Agent, Mixin, Orchestrator, Engine, utility function, or SSOT constant:**

1. **Execute 4-step search**:
   - AST symbol search (find all classes/functions with equivalent signatures)
   - Name pattern search (find all symbols with overlapping name stems)
   - Behavioral search (find all symbols that read/write same data or call same APIs)
   - Registry check (verify not in agent registry or SSOT constants)

2. **Document search results**: Write to evidence section titled `## DEDUP_SEARCH`

3. **Make decision**:
   - If exact duplicate found → STOP, reuse existing
   - If near-duplicate found → STOP, extend existing
   - If no duplicate found → proceed with creation, document justification

**Format required**:
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

**IF any match found → STOP. Do not create duplicate.**

Only after `DEDUP_SEARCH` section is written with decision="create" may you create the new symbol.

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graph PRIMARY for duplicate detection
- **§4.3:** Boundary enforcement — no duplicate enforcement surfaces across layers
