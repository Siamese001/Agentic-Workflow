# Dedup Decision Tree

When pre-creation checklist finds a potential duplicate, follow this tree.
STOP at the first matching branch.

---

## Decision Flow

```
Pre-creation search found a match?
│
├─► 1. EXACT semantic duplicate found (same behavior, same data)?
│       YES → Reuse the existing symbol.
│             Update your call sites to use the existing symbol.
│             Do NOT create a new one.
│             Document in evidence: "Reused existing <SymbolName> at <path>"
│             DONE.
│
├─► 2. NEAR-duplicate found (similar behavior, missing one feature)?
│       YES → Extend the existing symbol.
│             Add the missing feature to the existing class/function.
│             Do NOT create a parallel class.
│             Write tests for the new feature (§1.1).
│             Document in evidence: "Extended existing <SymbolName> at <path>"
│             DONE.
│
└─► 3. No duplicates found in all 4 searches?
        → Create the new symbol.
          MANDATORY: Attach documented justification (pre_creation_checklist.md Step 6).
          Register in appropriate SSOT after creation.
          DONE.
```

---

## Hard Rules

- Branch 1 takes absolute precedence. If an exact duplicate exists, reuse it.
- Branch 2 must extend the MOST CANONICAL existing symbol (closest to L0, or the one already in constants/registry).
- Branch 3 requires written proof from all 4 searches.
- "I didn't find it" is not acceptable — run the searches, record the output.

---

## Special Cases

### Constants

If creating a new path constant:
- Check `agentic_core/L0_routing/config/path_constants.py` FIRST
- If constant value already exists under a different name → use existing name (Branch 1)
- If constant is new → add to `path_constants.py` (not inline in the calling file)

### Agents

If creating a new Agent class:
- Check `artifacts/discovery/agent_discovery_full.json` for existing agents with same purpose
- Check `apps_rg/reasoning/`, `apps_lic/reasoning/`, `agentic_core/L5_safety/` for existing agents
- If a healing/validation agent already covers the domain → extend it (Branch 2)

### Mixins

If creating a new Mixin:
- Check `agentic_core/base_agents/` and all `mixins/` directories for equivalent behavior
- Prefer decomposing an existing overly-large mixin (Branch 2) over creating a new one
