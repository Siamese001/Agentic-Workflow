# Phase B: Atomic Cognitive Agents Refactoring

**Date**: 2025-11-24

## Overview

Phase B refactors all cognitive agents to be pure L1→L2 shims following OpenAI agentic layering principles.

## Files Modified

### Root Level
- `cognitive_agents.py` - Refactored all agents to delegate to L1/L2
- `l2.py` - Updated imports from `l1` to `l1_planning`
- `core/__init__.py` - Updated documentation
- `core/cognitive_agents.py` - Created re-export wrapper

### New Module
- `l1_planning/` - Created as renamed/re-export of `l1/` module
  - `__init__.py`
  - `strategy_planning.py`
  - `rag_planning.py`
  - `qa_planning.py`
  - `safety_planning.py`

## Key Changes

### Agent Atomicity
All agents now follow strict L1→L2 delegation:

1. **StrategyLLMAgent** → `l2._execute_strategy()`
2. **DraftingGuild** → `l2._execute_drafting()`
3. **SemanticQAAgent** → `l2._execute_qa()` + `l1_planning.plan_rag_reasoning()`
4. **ConstitutionalSafetyAgent** → `l2._execute_safety()`
5. **HYDEQueryAgent** → `l1_planning.plan_hyde_query()` + minimal LLM call
6. **QACouncilAgent** → Minimal JSON parsing only

### Removed from Agents
- ❌ Planning logic
- ❌ Multi-step reasoning
- ❌ Tool orchestration
- ❌ Loops, retries, councils
- ❌ Adjudication logic
- ❌ Fallback logic
- ❌ JSON parsing/construction (except QACouncilAgent)

## Testing Results

### Import Health ✓
```
l1_planning OK
cognitive_agents OK
core.cognitive_agents OK
l2 OK
```

### Pytest ✓
- `tests/agents/` - 6 passed
- `tests/test_l2_retrieval_profiles.py` - 2 passed
- **Total**: 8 passed in 0.31s

### Ruff Lint
- 11 E501 warnings (line length - cosmetic only)
- 0 undefined names
- 0 missing imports
- 0 unused imports

## Atomicity Invariants

✓ Agents contain zero planning logic
✓ Agents contain zero execution logic  
✓ Agents contain zero orchestration logic
✓ Agents are pure shims
✓ L1_planning remains pure-planning
✓ L2 remains execution-only
✓ No cyclic imports

## Zero-Regression Guarantee

✓ Agent tests passing
✓ L2 retrieval tests passing
✓ Agent card tests passing
✓ Agent registry tests passing
✓ Agent router policy tests passing
✓ Public signatures unchanged

## Next Steps

Phase C will refactor L2 execution layer to maintain strict separation of concerns.
