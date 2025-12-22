# Orchestrator Consolidation Guide

## Overview

The "Great Consolidation" has successfully refactored 15+ orchestrator files into a unified subatomic architecture, eliminating race conditions and standardizing on Gemini 2.5/3.0 with AtomicBlackboard integration.

## Architecture Changes

### Before: Fragmented Orchestrators
- 20+ orchestrator files with duplicated logic
- Race conditions from concurrent file writes
- Inconsistent SDK usage (OpenAI, Anthropic, Gemini)
- No centralized state management
- "Whack-a-Mole" overwrites between agents

### After: Consolidated Core
- **Single Source of Truth**: `agentic_core/core/orchestrator_main.py`
- **AtomicBlackboard Integration**: HealingLease prevents race conditions
- **Gemini 2.5/3.0 Standardization**: All LLM calls use google-genai SDK
- **Specialized Agents**: App-specific logic extracted to `agentic_core/agents/specialized/`
- **Thin Wrappers**: Legacy orchestrators now delegate to consolidated core

## File Structure

```
agentic_core/
├── core/
│   ├── orchestrator.py              # Original SwarmScheduler (preserved)
│   ├── orchestrator_main.py         # NEW: Consolidated orchestrator
│   └── CONSOLIDATION_GUIDE.md       # This file
├── agents/
│   └── specialized/
│       ├── outreach_agent.py        # LinkedIn campaign logic
│       └── resume_agent.py          # Resume generation logic
└── tools/
    ├── definitions.py               # Pydantic models for tools
    ├── filesystem.py                # Sandboxed file operations
    ├── execution.py                 # Timeout-protected subprocess
    └── registry.py                  # FunctionDeclaration generator

apps_lic/L3_orchestration/
├── l5_autonomous_orchestrator.py            # Original (preserved)
└── l5_autonomous_orchestrator_wrapper.py    # NEW: Thin wrapper

apps_rg/
├── trinity_orchestrator.py                  # Original (preserved)
├── trinity_orchestrator_wrapper.py          # NEW: Thin wrapper
└── L3_orchestration/
    ├── hardened_orchestrator.py             # Original (preserved)
    └── hardened_orchestrator_wrapper.py     # NEW: Thin wrapper
```

## Migration Path

### For New Code
Use the consolidated orchestrator directly:

```python
from agentic_core.core.orchestrator_main import (
    create_orchestrator,
    OrchestratorConfig,
)
from agentic_core.domain.context import ValidationContext

config = OrchestratorConfig(
    max_cycles=5,
    enable_healing=True,
    enable_checkpointing=True
)

context = ValidationContext()
orchestrator = create_orchestrator(config=config, context=context)

results = await orchestrator.execute_workflow(
    workflow_id="my_workflow",
    agents=[agent1, agent2, agent3]
)
```

### For Legacy Code
Use the thin wrappers for backward compatibility:

```python
# LinkedIn Outreach
from apps_lic.L3_orchestration.l5_autonomous_orchestrator_wrapper import (
    run_l5_outreach_orchestrator
)

results = await run_l5_outreach_orchestrator(
    campaign_id="campaign_001",
    archetype="RECRUITER"
)

# Resume Generation
from apps_rg.trinity_orchestrator_wrapper import run_trinity_orchestrator

results = await run_trinity_orchestrator(
    user_goal="Generate resume for software engineer"
)

# Hardened Workflow
from apps_rg.L3_orchestration.hardened_orchestrator_wrapper import (
    run_hardened_orchestrator
)

results = await run_hardened_orchestrator(
    workflow_id="resume_workflow_001"
)
```

## Key Features

### 1. AtomicBlackboard Integration
All file writes now require HealingLease verification:

```python
from agentic_core.tools import write_file, WriteFileArgs

# Automatically verifies HealingLease
write_file(
    WriteFileArgs(path="file.py", content="code"),
    blackboard=context.blackboard,
    agent_id="agent_001"
)
```

### 2. Gemini 2.5/3.0 Standardization
All LLM calls use the google-genai SDK:

```python
config = types.GenerateContentConfig(
    temperature=0.2,
    thinking_config=types.ThinkingConfig(
        thinking_budget=16000
    ),
    tools=[]  # Explicitly disable tools
)

response = await asyncio.to_thread(
    client.models.generate_content,
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)
```

### 3. Sandboxed File Operations
All file I/O goes through sandboxed tools:

```python
from agentic_core.tools import read_file, ReadFileArgs

# Automatically validates sandbox
content = read_file(ReadFileArgs(path="apps_shared/file.py"))
```

### 4. Timeout-Protected Execution
Subprocess calls have timeout protection:

```python
from agentic_core.tools import execute_command, ExecuteCommandArgs

returncode, stdout, stderr = execute_command(ExecuteCommandArgs(
    command="pytest",
    args=["tests/"],
    timeout=60  # Max 300s
))
```

## Configuration Options

### OrchestratorConfig
```python
@dataclass
class OrchestratorConfig:
    max_cycles: int = 5                    # Maximum convergence cycles
    quality_threshold: float = 0.75        # Quality threshold for completion
    enable_intervention: bool = True       # Human-in-the-loop
    enable_checkpointing: bool = True      # Atomic state checkpointing
    checkpoint_dir: str = "./checkpoints"  # Checkpoint directory
    gemini_model: str = "gemini-2.5-flash" # Gemini model
    temperature: float = 0.2               # LLM temperature
    thinking_budget: int = 16000           # Thinking budget
    enable_healing: bool = True            # Enable autonomous healing
    max_healing_per_file: int = 8          # Max healing attempts per file
    global_healing_budget: int = 50        # Global healing budget
```

## Specialized Agents

### OutreachAgent
Handles LinkedIn campaign orchestration:
- Campaign-specific validation
- Archetype-based personalization
- Quality threshold enforcement
- Message template management

### ResumeAgent
Handles resume generation workflows:
- Trinity architecture (Cognitive + Action)
- Hardened routing with provider fallback
- Atomic state checkpointing
- Titanium RAG integration

## Testing

### Integration Tests
Update integration tests to target the new orchestrator:

```python
# Before
from apps_rg.L3_orchestration.hardened_orchestrator import (
    HardenedWorkflowOrchestrator
)

# After
from agentic_core.core.orchestrator_main import create_orchestrator
```

### Running Tests
```bash
# Run all integration tests
pytest tests/integration/

# Run specific orchestrator tests
pytest tests/integration/test_hardened_orchestrator_comprehensive.py
```

## Cleanup Completed

✅ **Bytecode Cleanup**: All `.pyc` files removed from `__pycache__` directories  
✅ **Backup Cleanup**: All `.bak` files removed  
✅ **Schema Alignment**: `schemas/core_interfaces/orchestrator.py` updated  
✅ **Syntax Fixes**: All syntax errors resolved  

## Benefits

1. **Race Condition Elimination**: AtomicBlackboard HealingLease prevents concurrent writes
2. **SDK Standardization**: Single Gemini 2.5/3.0 SDK reduces complexity
3. **Code Reuse**: Specialized agents eliminate duplication
4. **Type Safety**: Pydantic models prevent validation errors
5. **Sandboxing**: File operations protected from path traversal
6. **Timeout Protection**: Subprocess calls can't livelock
7. **Maintainability**: Single source of truth for orchestration logic

## Migration Checklist

- [x] Create consolidated orchestrator in `agentic_core/core/orchestrator_main.py`
- [x] Extract specialized agents to `agentic_core/agents/specialized/`
- [x] Create thin wrappers for legacy orchestrators
- [x] Update schema alignment in `schemas/core_interfaces/orchestrator.py`
- [x] Clean up bytecode (`.pyc`) files
- [x] Clean up backup (`.bak`) files
- [ ] Update integration tests to target new orchestrator
- [ ] Update documentation and README files
- [ ] Run full test suite to verify no regressions

## Next Steps

1. **Update Integration Tests**: Modify tests to use consolidated orchestrator
2. **Performance Testing**: Benchmark new vs old orchestrators
3. **Documentation**: Update README files with new architecture
4. **Deprecation Plan**: Plan timeline for removing legacy orchestrators
5. **Monitoring**: Add observability for orchestrator execution

## Support

For questions or issues with the consolidation:
- Review this guide
- Check `agentic_core/core/orchestrator_main.py` for implementation details
- Examine wrapper files for migration patterns
- Consult `agentic_core/tools/README.md` for tool usage

---

**Last Updated**: December 19, 2025  
**Status**: Phase 3 Complete - Toolset & Sandbox Shield Integrated
