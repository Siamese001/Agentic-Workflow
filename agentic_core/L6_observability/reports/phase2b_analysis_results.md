# Phase 2b Analysis Results: Critical Discovery

**Date:** 2026-01-06  
**Finding:** The 6 "duplicates" are NOT duplicates - they are **different implementations** with the same filename.

## Key Discovery

After diff analysis, the pattern is clear:

| Agent | "Canonical" (SSOT path) | "Duplicate" (non-SSOT) | Reality |
|-------|-------------------------|------------------------|---------|
| GovernanceAgent | L5_safety/validators (206 lines, stub) | L1_cognition/thought_engine (798 lines, **Gold Standard**) | **Different agents** |
| HealerAgent | L2_execution/ToolRegistry (602 lines) | L5_safety/guardrails (1338 lines, **Gold Standard**) | **Different agents** |
| CognitiveContractManagerAgent | L2_execution/ToolRegistry (257 lines) | schemas/models (547 lines, full impl) | **Different agents** |
| DeadCodeDetectorAgent | L5_safety/guardrails (221 lines) | utils/core_extensions (355 lines, VERSION 2.0) | **Different agents** |
| FileManagerAgent | L4_state/filesystem (232 lines) | utils/core_extensions (297 lines) | Similar, need merge |
| PromptGovernorAgent | L2_execution/ToolRegistry (257 lines) | prompt_governance/rendering (279 lines) | Similar, need merge |

## Evidence

### GovernanceAgent
- **L5_safety/validators**: Stub with missing imports (`MCPHardenedMixin`, `SubatomicTestingMixin` not imported)
- **L1_cognition/thought_engine**: Full DependencyGraph implementation with blast radius analysis, Gold Standard (2026-01-02)

### HealerAgent  
- **L2_execution/ToolRegistry**: General-purpose healer with Redis/Pinecone
- **L5_safety/guardrails**: **Gold Standard** sovereign structural conductor with multi-agent coordination

### CognitiveContractManagerAgent
- **L2_execution/ToolRegistry**: Basic implementation
- **schemas/models**: Full Plan-before-Act enforcement with Pydantic models, dataclasses

### DeadCodeDetectorAgent
- **L5_safety/guardrails**: Basic implementation
- **utils/core_extensions**: VERSION 2.0 with parent-node tracking, class-aware method analysis

## Recommendation

**DO NOT DELETE** these files blindly. They serve different purposes:

1. **GovernanceAgent (L1)** - Keep, it's the Gold Standard DependencyGraph
2. **HealerAgent (L5)** - Keep, it's the Gold Standard structural healer
3. **CognitiveContractManagerAgent (schemas)** - Keep, it's the full contract system
4. **DeadCodeDetectorAgent (utils)** - Keep, it's VERSION 2.0

**Action Required:**
- Rename files to reflect their actual purpose (e.g., `DependencyGraphAgent.py`, `StructuralHealerAgent.py`)
- OR keep both and update imports to use the correct one for each use case
- Delete only the true stubs that have broken imports

## Files to Delete (True Stubs with Broken Imports)

```bash
# Only delete if confirmed as broken stubs
git rm "agentic_core/L5_safety/validators/GovernanceAgent.py"  # Missing imports, stub
```

## Files to KEEP (Different Implementations)

- `agentic_core/L1_cognition/thought_engine/GovernanceAgent.py` - Gold Standard
- `agentic_core/L5_safety/guardrails/HealerAgent.py` - Gold Standard  
- `agentic_core/schemas/models/CognitiveContractManagerAgent.py` - Full impl
- `agentic_core/utils/core_extensions/DeadCodeDetectorAgent.py` - VERSION 2.0
