---
name: dedup-guard
description: Prevents creation of duplicate agents, mixins, utility functions, and constants before they proliferate. Use before creating any new agent class, mixin, utility function, or SSOT constant. Requires AST-backed search for semantically equivalent symbols first. Blocks creation without documented justification that no equivalent exists.
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

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graph PRIMARY for duplicate detection
- **§4.3:** Boundary enforcement — no duplicate enforcement surfaces across layers
