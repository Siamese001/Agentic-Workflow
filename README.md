
# Deterministic Agentic Execution Framework

> Contract-first, test-enforced agentic architecture built for deterministic execution and production safety.

---

## What This Is (30-Second Context)

A layered L0–L6 agentic system that enforces execution correctness through:

- Schema-validated artifacts  
- Runtime guard decorators  
- Explicit aggregation contracts  
- Negative invariant testing  
- Immutable execution logs  

No heuristic shortcuts. No silent failures. No identifier-coupled logic.

---

## Why It’s Different

| Weak Pattern | This System |
|--------------|------------|
| Implicit aggregation | Explicit `artifact_class` enforcement |
| Identifier coupling | Contract-driven validation |
| Silent fallback logic | Deterministic rejection |
| Untested invariants | Negative regression tests |
| Logs as afterthought | Observability as first-class artifact |

---

## Architecture at a Glance

| Layer | Purpose |
|-------|---------|
| **L0** | Guarded execution entry points |
| **L1** | Deterministic orchestration |
| **L2** | Schema contract validation |
| **L3** | Controlled healing logic |
| **L4** | Indexed knowledge artifacts |
| **L5** | Human approval gating |
| **L6** | Immutable observability layer |

Execution flows down. Validation signals flow up.  
No layer bypasses contract enforcement.

---

## Core Guarantees

- Aggregate artifacts **must** include index  
- Individual artifacts **cannot** include index  
- Invalid artifacts rejected at boundary  
- No magic identifiers anywhere in validation logic  
- Deterministic outputs given identical inputs  

