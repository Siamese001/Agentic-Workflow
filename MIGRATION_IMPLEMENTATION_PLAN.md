# Archive Migration Implementation Plan

**Generated:** 2026-01-01
**Status:** Ready for Execution

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Files** | 258 |
| **Total LOC** | 78,807 |
| **Python Classes** | 880 |
| **MIGRATE** | 99 files |
| **REVIEW** | 150 files |
| **DELETE** | 6 files |
| **MERGE** | 3 files |

---

## Phase 1: Priority Migrations (Unique Valuable Code)

### 1.1 Core Runtime Components → `agentic_core/runtime/shared_runtime/`

These files contain unique implementations not present in modern codebase:

```bash
# Reflection Engine (512 LOC) - Quality gates for critique micro-stages
git mv archives/runtime/core/reflection_engine.py agentic_core/runtime/shared_runtime/reflection_engine.py

# Signal Enhancer (723 LOC) - Quality gates and claim confidence scoring  
git mv archives/runtime/core/quality/signal_enhancer.py agentic_core/runtime/shared_runtime/signal_enhancer.py
```

### 1.2 Orchestration Components → `agentic_core/L3_orchestration/`

```bash
# Dynamic DAG Manager (714 LOC) - Transactional graph mutations
git mv archives/runtime/core/dynamic_dag_manager.py agentic_core/L3_orchestration/dynamic_dag_manager.py

# Orchestrator Interface (234 LOC) - Think-Act-Observe cycle coordination
git mv archives/schemas/core_interfaces/orchestrator.py agentic_core/L3_orchestration/interfaces/orchestrator.py
```

### 1.3 Prompt Governance → `agentic_core/prompt_governance/`

```bash
# Prompt Assembler (540 LOC) - XML-based semantic fencing
git mv archives/runtime/core/prompt_assembler.py agentic_core/prompt_governance/prompt_assembler.py
```

### 1.4 Schema Models → `agentic_core/schemas/models/`

```bash
# Cognitive Contracts (511 LOC) - Plan-before-act enforcement
git mv archives/runtime/core/cognitive_contracts.py agentic_core/schemas/models/cognitive_contracts.py

# Shared Models (194 LOC) - MicroStage, HopState, RetryPolicy
git mv archives/runtime/core/shared_models.py agentic_core/schemas/models/runtime_models.py
```

### 1.5 Safety Components → `agentic_core/L5_safety/guardrails/`

```bash
# Input Validator (510 LOC) - Comprehensive input validation
git mv archives/runtime/core/security/input_validator.py agentic_core/L5_safety/guardrails/input_validator.py

# Secure Config (467 LOC) - Secure configuration management
git mv archives/runtime/core/security/secure_config.py agentic_core/L5_safety/guardrails/secure_config.py

# Secure Error (372 LOC) - Error sanitization and handling
git mv archives/runtime/core/security/secure_error.py agentic_core/L5_safety/guardrails/secure_error.py

# Secure Checkpoint (318 LOC) - Integrity-checked checkpointing
git mv archives/runtime/core/security/secure_checkpoint.py agentic_core/L5_safety/guardrails/secure_checkpoint.py

# Secure Logger (266 LOC) - PII-safe logging
git mv archives/runtime/core/security/secure_logger.py agentic_core/L5_safety/guardrails/secure_logger.py
```

### 1.6 MCP Integration → `agentic_core/L2_execution/mcp/`

```bash
# MCP Client (241 LOC) - Model Context Protocol client
git mv archives/shared/mcp/client.py agentic_core/L2_execution/mcp/archive_client.py

# MCP Factory (196 LOC) - Client instantiation
git mv archives/shared/mcp/factory.py agentic_core/L2_execution/mcp/archive_factory.py

# MCP Exceptions (34 LOC) - Error types
git mv archives/shared/mcp/exceptions.py agentic_core/L2_execution/mcp/archive_exceptions.py

# MCP Providers (87 LOC) - Provider types
git mv archives/shared/mcp/providers.py agentic_core/L2_execution/mcp/archive_providers.py

# MCP Tools (347 LOC) - Tool server implementation
git mv archives/runtime/shared/mcp_tools.py agentic_core/L2_execution/mcp/mcp_tools.py
```

### 1.7 Configuration → `agentic_core/config/`

```bash
# Shared Config (183 LOC) - Model, RAG, Governor configs
git mv archives/shared/configuration/config.py agentic_core/config/archive_config.py

# Reasoning Config (144 LOC) - Reasoning engine configuration
git mv archives/shared/configuration/reasoning_config.py agentic_core/config/reasoning_config.py
```

---

## Phase 2: Merge Operations (Archive Richer Than Modern)

### 2.1 Circuit Breaker Merge

The archive has 3 circuit breaker implementations totaling ~938 LOC while modern has only 132 LOC.

**Archive Features to Merge:**
- `archives/runtime/core/resilience/circuit_breaker.py` (357 LOC): Async support, thread-safe factory
- `archives/runtime/shared/circuit_breaker.py` (450 LOC): Registry pattern, request tracking
- `archives/shared/resilience/circuit_breaker.py` (131 LOC): Simple implementation

**Target:** `agentic_core/L4_resilience/circuit_breaker.py`

**Action Required:**
1. Review all 3 archive implementations
2. Extract unique features (async wrapper, factory singleton, registry)
3. Merge into modern implementation preserving API compatibility

```python
# Features to add to modern circuit_breaker.py:
# 1. CircuitBreakerFactory singleton with thread safety
# 2. Async call wrapper: async def call_with_breaker()
# 3. CircuitBreakerRegistry for named breakers
# 4. CriticalServiceFailure exception type
# 5. Request result tracking with timestamps
```

---

## Phase 3: Delete Operations (Obsolete/Duplicate)

```bash
# Empty init stubs
rm archives/runtime/__init__.py
rm archives/shared/core/__init__.py
rm archives/shared/errors/__init__.py
rm archives/shared/internal/__init__.py

# Obsolete - modern version uses dependency injection
rm archives/runtime/core/subatomic_hop.py

# Obsolete - modern version has semantic embedding matching
rm archives/shared/caching/semantic_cache.py
```

---

## Phase 4: Schema Migrations (Bulk Move)

### 4.1 Core Models

```bash
# Create target directory
mkdir -p agentic_core/schemas/models/archive_models

# Move schema files
git mv archives/schemas/core_models/budget_profile.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/context_profile.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/llm_profile.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/safety_profile.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/l4_types.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/simulation_models.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/meta_metacognition_models.py agentic_core/schemas/models/archive_models/
git mv archives/schemas/core_models/golden_state_models.py agentic_core/schemas/models/archive_models/
```

### 4.2 Core Interfaces

```bash
git mv archives/schemas/core_interfaces/action_plane.py agentic_core/schemas/models/interfaces/
git mv archives/schemas/core_interfaces/cognitive_plane.py agentic_core/schemas/models/interfaces/
```

### 4.3 Data Assets

```bash
mkdir -p agentic_core/schemas/models/data_assets

git mv archives/schemas/data_assets/*.json agentic_core/schemas/models/data_assets/
```

---

## Phase 5: Import Path Updates

After migrations, update all import paths:

```bash
# PowerShell script for Windows
Get-ChildItem -Path "agentic_core" -Recurse -Include "*.py" | ForEach-Object {
    (Get-Content $_.FullName) `
        -replace 'from archives\.runtime', 'from agentic_core.runtime' `
        -replace 'from archives\.schemas', 'from agentic_core.schemas' `
        -replace 'from archives\.shared', 'from agentic_core.utils' `
        | Set-Content $_.FullName
}
```

---

## Phase 6: Compliance Fixes

### 6.1 PascalCase Class Violations (10 files)

| File | Class | Fix |
|------|-------|-----|
| `executive_title_composer.py` | `Executive_Title_Composer` | `ExecutiveTitleComposer` |
| `gap_closure_architect.py` | `Gap_Closure_Architect` | `GapClosureArchitect` |
| `k1_routing_agent.py` | `K1_RoutingAgent` | `K1RoutingAgent` |
| `k3_message_body_agent.py` | `K3_MessageBodyAgent` | `K3MessageBodyAgent` |
| `k5_cta_agent.py` | `K5_CTAAgent` | `K5CTAAgent` |
| `k5a_agent.py` | `K5A_GenerationAgent` | `K5AGenerationAgent` |
| `k7_assembly_agent.py` | `K7_AssemblyAgent` | `K7AssemblyAgent` |
| `strategist_biowriter.py` | `Strategist_BioWriter` | `StrategistBioWriter` |

### 6.2 Raw Prompt String Violations (6 files)

These files contain raw f-string prompts that should use `PromptAssembler`:
- `reflection_engine.py`
- `persona_router.py`
- `architecture_visualizer_agent.py`
- `cultural_decoder_agent.py`
- `executive_brief_agent.py`
- `onboarding_planner_agent.py`

---

## Phase 7: Validation Commands

```bash
# 1. Run full test suite
python -m pytest tests/ -v --tb=short

# 2. Type checking
python -m mypy agentic_core/ --ignore-missing-imports

# 3. Import validation
python -c "from agentic_core.runtime.shared_runtime import reflection_engine; print('OK')"
python -c "from agentic_core.L3_orchestration import dynamic_dag_manager; print('OK')"

# 4. Agent discovery count
python -c "
from pathlib import Path
agents = list(Path('agentic_core').rglob('*_agent.py'))
print(f'Agent count: {len(agents)}')
"

# 5. Canon validator (if available)
python -m agentic_core.L5_safety.validators.compliance_orchestrator
```

---

## Files Requiring Manual Review (150 files)

These files need human review before migration decisions:

### High Priority (Complex Logic)
- `runtime/shared/unified_signal_pipeline.py` (1,348 LOC)
- `runtime/shared/knowledge_graph_agent.py` (741 LOC)
- `runtime/shared/unified_executor.py` (703 LOC)
- `runtime/shared/titanium_rag_pipeline.py` (664 LOC)
- `runtime/shared/brand_voice_enforcer.py` (617 LOC)

### Medium Priority (Utility Functions)
- `runtime/shared/health_check.py` (588 LOC)
- `runtime/shared/retry_policy.py` (502 LOC)
- `runtime/shared/rate_limiter.py` (591 LOC)

### Low Priority (Test Files)
- All `test_*.py` files (move to `tests/` directory)

---

## Rollback Plan

If issues arise:

```bash
# Revert all migrations
git checkout HEAD~1 -- agentic_core/
git checkout HEAD~1 -- archives/

# Or reset entire branch
git reset --hard origin/main
```

---

## Success Criteria

- [ ] All 99 MIGRATE files moved to target locations
- [ ] All 6 DELETE files removed
- [ ] Circuit breaker merge completed with all features
- [ ] Import paths updated across codebase
- [ ] PascalCase violations fixed
- [ ] Test suite passes
- [ ] Type checking passes
- [ ] Agent discovery count unchanged or increased
