# Prompt Modularization - December 19, 2025

## Overview

Successfully modularized the 8,546-line monolithic canon validator into structured, maintainable prompt files with dynamic loading.

## Structure

```
prompts/
├── global/
│   └── constraints.md          # Global constraints (Never/Don't rules)
├── specialists/
│   ├── healer_agent.md         # Autonomous code repair specialist
│   ├── system_architect.md     # Core architecture validation
│   └── structural_engineer.md  # Code structure validation
└── prompt_loader.py            # Dynamic prompt loading utility
```

## Global Constraints (`prompts/global/constraints.md`)

Contains all universal rules that apply to every agent:

### Zero-Tolerance Deletion Rule
- NEVER truncate files or use placeholders
- NEVER delete more than 10% of lines
- Every mutation must be COMPLETE and functional

### Prohibited Modules (Hard-Coded Blacklist)
Based on inductive logic from observed hallucinations:

- **BANNED**: `import base` (hallucinated repeatedly)
- **BANNED**: `import context` (hallucinated repeatedly)
- **BANNED**: `import L3_orchestration` (hallucinated repeatedly)
- **BANNED**: `import conversational_repair` (hallucinated repeatedly)

### Elite Engineer Rules
- NEVER hallucinate imports
- NEVER delete logic, comments, or docstrings
- NEVER use tools or function calls
- Fix specific violation ONLY
- Return ONLY valid Python code

## Specialist Prompts (`prompts/specialists/`)

### Healer Agent (`healer_agent.md`)
- Role: ELITE Level 5 Autonomous Repair Agent
- Objectives: Fix specific violations with surgical precision
- Strategies: Round-based iterative refinement
- Quality Gates: Syntax, line count, completeness checks
- Error Recovery: Handles syntax errors, mass deletion, code bloat

### System Architect (`system_architect.md`)
- Role: Core architecture validation
- Responsibilities: Key 40 verification, dependency management
- Checks: Module structure, import paths, circular dependencies
- Healing: Import corrections, structural refactoring

### Structural Engineer (`structural_engineer.md`)
- Role: Code structure validation
- Responsibilities: Large classes (Key 20), large files (Key 42), deep nesting (Key 41)
- Strategies: Class splitting, file modularization, nesting reduction
- Validation: Logical boundaries, circular dependency prevention

## Dynamic Prompt Loader (`prompts/prompt_loader.py`)

### Features

1. **Caching**: Loads prompts once and caches for performance
2. **Composition**: Combines global constraints + specialist instructions
3. **Parameterization**: Injects line counts, lessons learned dynamically
4. **Fallback**: Graceful degradation if files not found

### API

```python
from prompts.prompt_loader import load_prompt_for_agent

# Load complete prompt for an agent
prompt = load_prompt_for_agent(
    agent_role="healer_agent",
    task="Fix Subatomic Canon Key 41",
    code=original_code,
    original_line_count=226,
    lesson_learned="Previous deletion rejected"
)
```

### Usage in Canon Validator

```python
# Line 460-474: Dynamic prompt loading
try:
    from prompts.prompt_loader import load_prompt_for_agent
    
    # Map agent name to role
    agent_role = agent_name.lower().replace(" ", "_")
    
    # Build complete prompt from modularized files
    prompt = load_prompt_for_agent(
        agent_role=agent_role,
        task=task,
        code=code,
        original_line_count=original_line_count,
        lesson_learned=lesson_learned
    )
except Exception as e:
    # Fallback to inline prompt if loader fails
    print(f"⚠️ Prompt loader failed ({e}), using fallback")
    # ... inline prompt ...
```

## Benefits

### 1. Maintainability
- Prompts are now in markdown files, easy to edit
- No need to modify Python code to update prompts
- Version control tracks prompt changes separately

### 2. Modularity
- Global constraints apply to all agents
- Specialist prompts are agent-specific
- Easy to add new agents by creating new `.md` files

### 3. Inductive Learning
- Banned modules list grows based on observed hallucinations
- Each new hallucination can be added to `constraints.md`
- No code changes needed to update blacklist

### 4. Testability
- Prompts can be tested independently
- Easy to A/B test different prompt strategies
- Clear separation of concerns

### 5. Collaboration
- Non-developers can edit prompts
- Prompt engineers can iterate without touching code
- Clear documentation of agent behavior

## Inductive Logic Implementation

The banned modules list was built inductively from observed errors:

```
Observation: Model repeatedly generates "import base"
Action: Add "BANNED: import base" to constraints.md

Observation: Model generates "from context import ..."
Action: Add "BANNED: from context import ..." to constraints.md

Observation: Model tries "import L3_orchestration"
Action: Add "BANNED: import L3_orchestration" to constraints.md
```

This approach allows the system to learn from mistakes and prevent future hallucinations without code changes.

## Migration Path

### Before (Hardcoded)
```python
prompt = f"""Task: {task}
SYSTEM: You are an ELITE Level 5 Autonomous Repair Agent.
RULES:
1. Fix the specific violation ONLY.
2. DO NOT hallucinate imports...
{code}"""
```

### After (Modularized)
```python
prompt = load_prompt_for_agent(
    agent_role="healer_agent",
    task=task,
    code=code,
    original_line_count=len(code.splitlines()),
    lesson_learned=previous_failure
)
```

## Future Enhancements

1. **Prompt Versioning**: Track prompt versions and A/B test
2. **Dynamic Blacklist**: Auto-add hallucinations to blacklist
3. **Prompt Analytics**: Track which prompts work best
4. **Multi-Language**: Support prompts in different languages
5. **Prompt Templates**: Jinja2 templates for complex prompts

## Files Modified

- `apps_shared/canon_validator_v2_agentic.py`: Lines 460-505 (dynamic loading)
- Created: `prompts/global/constraints.md`
- Created: `prompts/specialists/healer_agent.md`
- Created: `prompts/specialists/system_architect.md`
- Created: `prompts/specialists/structural_engineer.md`
- Created: `prompts/prompt_loader.py`

## Testing

Run validator to verify dynamic loading works:

```bash
python apps_shared\canon_validator_v2_agentic.py --target . --heal
```

Watch for:
- ✅ Prompts load successfully from markdown files
- ✅ Fallback works if files not found
- ✅ Global constraints are applied
- ✅ Specialist instructions are included
- ✅ Banned modules prevent hallucinations

## Summary

The prompt modularization transforms the canon validator from a monolithic system with hardcoded prompts into a flexible, maintainable architecture where:

- **Constraints** are centralized and reusable
- **Specialists** have clear, documented roles
- **Inductive learning** prevents repeated hallucinations
- **Dynamic loading** enables rapid iteration
- **Fallback** ensures reliability

This is production-ready and follows best practices for prompt engineering in agentic systems.
