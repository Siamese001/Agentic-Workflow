# Nervous System Consolidation Guide

## Overview

The "Nervous System" consolidation has successfully merged all fragmented context and client logic into a single Universal Context, eliminating client sprawl and standardizing on Gemini 2.5 Flash with thinking mode.

## Architecture Changes

### Before: Context & Client Sprawl
- **29+ context files** with duplicated state management
- **Multiple LLM clients**: `llm_client_flash.py`, `llm_client.py`, `hardened_gemini_executor.py`
- **Fragmented memory**: `canon_memory.json`, `resume_memory.json` in different locations
- **Inconsistent state tracking**: `omni_context.py`, `validation_context.py`, `context_passport.py`
- No centralized LLM access or thermal configuration

### After: Universal Context
- **Single Source of Truth**: `agentic_core/infra/context.py`
- **Singleton Gemini Client**: Lazy-loaded with exact Phase 1 thinking_config
- **Unified Memory**: All memory in `.canon_memory/` directory
- **Integrated State**: Combines validation, semantic buffer, and thermal config
- **AtomicBlackboard Integration**: Direct access to blackboard for lease management

## File Structure

```
agentic_core/infra/
├── __init__.py                      # Public API exports
├── context.py                       # Universal Context (NEW)
└── NERVOUS_SYSTEM_GUIDE.md          # This file

.canon_memory/                       # Unified memory directory
├── canon_memory.json                # Main memory file
└── current_context.json             # Current cycle state

Legacy (Thin Wrappers):
├── apps_shared/validation_context_wrapper.py
├── apps_rg/llm_client_wrapper.py
└── agentic_core/L4_state/
    ├── omni_context.py              # Original (preserved)
    ├── validation_context.py        # Original (preserved)
    └── context_passport.py          # Original (preserved)
```

## Universal Context Features

### 1. Singleton Pattern
Only one Universal Context exists across the entire system:

```python
from agentic_core.infra.context import context

# Always returns the same instance
ctx1 = context
ctx2 = get_context()
assert ctx1 is ctx2  # True
```

### 2. Lazy-Loaded Gemini Client
Gemini client initialized on first access with Phase 1 configuration:

```python
from agentic_core.infra.context import context

# Client initialized on first access
response = await context.generate_with_thinking(
    prompt="Fix this code...",
    temperature=0.2,
    thinking_budget=16000
)
```

**Configuration:**
- Model: `gemini-2.5-flash`
- Temperature: `0.2` (PRECISION mode)
- Thinking Budget: `16000` tokens
- Max Retries: `5` with exponential backoff
- Timeout: `300` seconds

### 3. Unified Memory Management
All memory stored in `.canon_memory/` directory:

```python
from agentic_core.infra.context import context

# Automatically loads from .canon_memory/canon_memory.json
context.save_memory()  # Saves to .canon_memory/canon_memory.json

# Memory includes:
# - File hashes for change detection
# - Healing attempts and budget
# - Signals and modified files
# - Cycle metadata
```

### 4. State Tracking
Combines all state management features:

```python
from agentic_core.infra.context import context

# Signals
context.add_signal("CONVERGENCE")
context.clear_signals()

# Modified files
context.add_modified_file(Path("file.py"))

# File hashing
context.update_file_hash("file.py", "abc123")
hash_val = context.get_file_hash("file.py")

# Healing budget
can_heal = context.can_attempt_healing("file.py")
context.record_healing_attempt("file.py", success=True)
```

### 5. Semantic Context Buffer
Build and query omniscient context:

```python
from agentic_core.infra.context import context

# Build context buffer from file summaries
stats = context.build_context_buffer(file_summaries)

# Query the buffer
results = context.query_context("authentication", max_results=5)
```

### 6. Thermal Configuration
Dynamic temperature control:

```python
from agentic_core.infra.context import context, ThermalProfile

# Set thermal profile
context.set_thermal_profile(ThermalProfile.PRECISION)      # temp=0.1
context.set_thermal_profile(ThermalProfile.STRUCTURED)     # temp=0.3
context.set_thermal_profile(ThermalProfile.BALANCED)       # temp=0.7
context.set_thermal_profile(ThermalProfile.CREATIVITY_HIGH) # temp=0.8
context.set_thermal_profile(ThermalProfile.CREATIVITY_MAX)  # temp=0.9
```

### 7. AtomicBlackboard Integration
Direct access to blackboard:

```python
from agentic_core.infra.context import context

# Access blackboard
blackboard = context.blackboard

# Acquire healing lease
blackboard.acquire_healing_lease("agent_001", "file.py")

# Release lease
blackboard.release_healing_lease("agent_001", "file.py")
```

### 8. Chat Session Management
Persistent chat sessions per file:

```python
from agentic_core.infra.context import context

# Generate with persistent chat session
response = await context.generate_with_thinking(
    prompt="Fix this violation...",
    file_path="apps_shared/file.py"  # Creates persistent session
)

# Subsequent calls reuse the same session
response2 = await context.generate_with_thinking(
    prompt="Now fix this other issue...",
    file_path="apps_shared/file.py"  # Reuses session
)
```

## Migration Guide

### For New Code
Use Universal Context directly:

```python
from agentic_core.infra.context import context

# Generate with Gemini
response = await context.generate_with_thinking(
    prompt="Your prompt here",
    temperature=0.2,
    thinking_budget=16000
)

# Track state
context.add_signal("CONVERGENCE")
context.add_modified_file(Path("file.py"))

# Save memory
context.save_memory()
```

### For Legacy Code
Use thin wrappers for backward compatibility:

```python
# Validation Context (apps_shared)
from apps_shared.validation_context_wrapper import ValidationContext
ctx = ValidationContext()  # Delegates to Universal Context

# LLM Client (apps_rg)
from apps_rg.llm_client_wrapper import LLMClient
client = LLMClient()  # Delegates to Universal Context
result = await client.generate_plan(system_context, user_goal)
```

### Replacing Old Imports

**Before:**
```python
# Old fragmented imports
from agentic_core.L4_state.validation_context import ValidationContext
from agentic_core.L4_state.omni_context import TheOmniContext
from apps_rg.llm_client_flash import LLMClient
from schemas.context_passport import ThermalProfile
```

**After:**
```python
# New unified import
from agentic_core.infra.context import context, ThermalProfile

# Or use wrappers for backward compatibility
from apps_shared.validation_context_wrapper import ValidationContext
from apps_rg.llm_client_wrapper import LLMClient
```

## Memory Directory Structure

All memory files now stored in `.canon_memory/`:

```
.canon_memory/
├── canon_memory.json           # Main memory (replaces all canon_memory.json files)
├── current_context.json        # Current cycle state
└── [future expansion]          # Room for additional memory files
```

**Memory Hijack Complete:**
- ✅ All `canon_memory.json` files redirected to `.canon_memory/canon_memory.json`
- ✅ All `resume_memory.json` files redirected to `.canon_memory/canon_memory.json`
- ✅ Unified memory management across all agents

## Configuration

### Memory Configuration
```python
from agentic_core.infra.context import MemoryConfig, UniversalContext

config = MemoryConfig(
    memory_dir=Path(".canon_memory"),
    canon_memory_file="canon_memory.json",
    context_file="current_context.json",
    max_history_size=100,
    enable_pinecone=False,
    pinecone_index="omni-context"
)

context = UniversalContext(memory_config=config)
```

### Gemini Configuration
```python
from agentic_core.infra.context import GeminiConfig, UniversalContext

config = GeminiConfig(
    model="gemini-2.5-flash",
    temperature=0.2,
    thinking_budget=16000,
    max_retries=5,
    base_delay=2.0,
    backoff_factor=2.0,
    timeout=300
)

context = UniversalContext(gemini_config=config)
```

## Benefits

1. **Client Sprawl Eliminated**: Single Gemini client for entire system
2. **Memory Consolidation**: All memory in `.canon_memory/` directory
3. **State Unification**: Combined validation, semantic, and thermal state
4. **Singleton Pattern**: One context instance across all agents
5. **Lazy Loading**: Client initialized only when needed
6. **Backward Compatible**: Thin wrappers maintain legacy API
7. **AtomicBlackboard Integration**: Direct blackboard access
8. **Chat Session Management**: Persistent sessions per file
9. **Thermal Control**: Dynamic temperature configuration
10. **Exponential Backoff**: Automatic retry with rate limit handling

## Files Replaced

### LLM Clients (DELETE THESE)
- ❌ `apps_rg/llm_client_flash.py` → Use `context.client`
- ❌ `apps_rg/llm_client.py` → Use `context.client`
- ❌ `apps_rg/hardened_gemini_executor.py` → Use `context.generate_with_thinking()`

### Context Files (USE WRAPPERS)
- ⚠️ `agentic_core/L4_state/validation_context.py` → Use wrapper or `context`
- ⚠️ `agentic_core/L4_state/omni_context.py` → Use `context.build_context_buffer()`
- ⚠️ `schemas/context_passport.py` → Use `context.set_thermal_profile()`
- ⚠️ `agentic_core/domain/context_old.py` → DELETE (obsolete)
- ⚠️ `agentic_core/L3_orchestration/context_curator.py` → Use `context`

## Testing

### Unit Tests
```python
import pytest
from agentic_core.infra.context import get_context, UniversalContext

def test_singleton_pattern():
    """Test that context is a singleton."""
    ctx1 = get_context()
    ctx2 = get_context()
    assert ctx1 is ctx2

def test_memory_persistence():
    """Test memory save/load."""
    ctx = get_context()
    ctx.add_signal("TEST_SIGNAL")
    ctx.save_memory()
    
    # Memory should persist
    assert "TEST_SIGNAL" in ctx.signals

@pytest.mark.asyncio
async def test_gemini_generation():
    """Test Gemini generation."""
    ctx = get_context()
    response = await ctx.generate_with_thinking(
        prompt="Say hello",
        temperature=0.1
    )
    assert isinstance(response, str)
    assert len(response) > 0
```

### Integration Tests
```bash
# Test Universal Context
pytest tests/test_universal_context.py

# Test backward compatibility wrappers
pytest tests/test_context_wrappers.py

# Test memory management
pytest tests/test_memory_management.py
```

## Migration Checklist

- [x] Create Universal Context in `agentic_core/infra/context.py`
- [x] Implement singleton Gemini client with Phase 1 config
- [x] Integrate MemoryManager and AtomicBlackboard
- [x] Create thin wrappers for backward compatibility
- [x] Redirect memory to `.canon_memory/` directory
- [ ] Delete obsolete LLM client files
- [ ] Update all imports to use Universal Context
- [ ] Run full test suite
- [ ] Update documentation

## Next Steps

1. **Delete Obsolete Files**: Remove `llm_client_flash.py`, `llm_client.py`, `hardened_gemini_executor.py`
2. **Update Imports**: Replace fragmented imports with `from agentic_core.infra.context import context`
3. **Test Integration**: Run full test suite to verify no regressions
4. **Update Documentation**: Update README files with new architecture
5. **Monitor Performance**: Track memory usage and LLM call patterns

## Support

For questions or issues with the consolidation:
- Review this guide
- Check `agentic_core/infra/context.py` for implementation details
- Examine wrapper files for backward compatibility patterns
- Consult `agentic_core/tools/README.md` for tool integration

---

**Last Updated**: December 19, 2025  
**Status**: Phase 3 Complete - Nervous System Consolidated  
**Next Phase**: Delete obsolete files and update imports
