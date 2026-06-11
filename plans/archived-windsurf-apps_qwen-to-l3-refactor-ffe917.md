---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps_qwen-to-l3-refactor-ffe917.md'
original_relative_path: 'apps_qwen-to-l3-refactor-ffe917.md'
source_sha256: 0d1bf48c262b296d3bd52b5f6c86bbe761336f16a5dba22fc45423e3fbd805a9
recovered_status: LOST_RECOVERED
last_commit: '57532db9e54'
last_commit_date: '2026-04-06 09:14:35 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Refactor apps_qwen to agentic_core/L3_orchestration/inference/qwen_vllm

This plan refactors the `apps_qwen` module from the applications layer to `agentic_core/L3_orchestration/inference/qwen_vllm` to align with architectural boundaries, clarifying it as an L3 inference infrastructure service rather than a business application.

## Scope

**Files to Move:** 17 Python files
- `apps_qwen/__init__.py`
- `apps_qwen/config/__init__.py`
- `apps_qwen/config/apps_qwen_config.py`
- `apps_qwen/config/apps_qwen_telemetry.py`
- `apps_qwen/engines/__init__.py`
- `apps_qwen/engines/apps_qwen_inference.py`
- `apps_qwen/engines/hardened_vllm_client.py`
- `apps_qwen/engines/optimized_vllm_client.py`
- `apps_qwen/reasoning/__init__.py`
- `apps_qwen/reasoning/apps_qwen_gateway.py`
- `apps_qwen/tools/__init__.py`
- `apps_qwen/tools/gpu_memory_monitor.py`
- `apps_qwen/tests/__init__.py`
- `apps_qwen/tests/test_config.py`
- `apps_qwen/tests/test_engines.py`
- `apps_qwen/tests/test_gateway.py`
- `apps_qwen/tests/test_tools.py`

**Importers to Update:** 20 files across the codebase
- `tests/performance/test_qwen_vllm_performance.py`
- `tests/performance/test_hardened_vllm.py`
- `tests/performance/benchmark_runner.py`
- `tests/unit/apps_qwen/test_apps_qwen_gateway.py`
- `tests/unit/apps_qwen/test_apps_qwen_telemetry.py`
- `apps_shared/utils/vllm_advanced_features.py`
- `apps_shared/utils/vllm_shared_utils.py`
- `apps_rg/reasoning/RgResumeOrchestrator.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_research/reasoning/ResearchOrchestrator.py`
- `apps_exec/reasoning/ExecOrchestrator.py`
- `apps_rfp/reasoning/RfpOrchestrator.py`
- `apps_eval/reasoning/EvalOrchestrator.py`
- `apps_eval/engines/base_eval_engine.py`
- `apps_qwen/engines/hardened_vllm_client.py`
- `apps_qwen/engines/apps_qwen_inference.py`
- `apps_qwen/reasoning/apps_qwen_gateway.py`
- `apps_qwen/tests/*` (4 test files)

## Class Renaming Map

| Old Name | New Name |
|----------|----------|
| `AppsQwenConfig` | `QwenInferenceConfig` |
| `AppsQwenModelConfig` | `QwenModelConfig` |
| `AppsQwenPromptConfig` | `QwenPromptConfig` |
| `AppsQwenGateway` | `QwenInferenceGateway` |
| `AppsQwenRequest` | `QwenInferenceRequest` |
| `AppsQwenResponse` | `QwenInferenceResponse` |
| `AppsQwenInferenceWorker` | `QwenInferenceWorker` |
| `AppsQwenMetric` | `QwenInferenceMetric` |
| `AppsQwenSessionMetrics` | `QwenSessionMetrics` |
| `AppsQwenTelemetry` | `QwenInferenceTelemetry` |
| `apps_qwen_telemetry` | `qwen_inference_telemetry` |

**Unchanged Classes** (infrastructure-specific, no "Apps" prefix):
- `OptimizedVLLMClient`
- `HardenedVLLMClient`
- `VLLMRequest`
- `VLLMResponse`
- `CircuitBreaker`, `CircuitBreakerConfig`, `CircuitBreakerOpenError`, `CircuitState`, `RetryConfig`, `HardeningMetrics`
- `GPUMemoryInfo`, `GPUMemoryMonitor`, `GPURecommendation`

## Phase 1: Create New Directory Structure

1. Create `agentic_core/L3_orchestration/inference/qwen_vllm/` subdirectories:
   - `config/`
   - `engines/`
   - `reasoning/`
   - `tools/`

2. Create test directory:
   - `tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/`

3. Create `__init__.py` files for all new directories

## Phase 2: Move and Rename Source Files

### 2.1 Configuration Files
- Move `apps_qwen/config/apps_qwen_config.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/config/qwen_config.py`
- Rename classes: `AppsQwen*` → `Qwen*`
- Update docstrings to reflect L3 orchestration context
- Update trace contract calls to use "L3_ORCHESTRATION" instead of "L2_EXECUTION"

- Move `apps_qwen/config/apps_qwen_telemetry.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/config/qwen_telemetry.py`
- Rename classes: `AppsQwen*` → `QwenInference*`

### 2.2 Engine Files
- Move `apps_qwen/engines/optimized_vllm_client.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`
- No class renames (already infrastructure-specific)
- Update internal imports to use new paths

- Move `apps_qwen/engines/hardened_vllm_client.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/engines/hardened_vllm_client.py`
- No class renames
- Update internal imports

- Move `apps_qwen/engines/apps_qwen_inference.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/engines/qwen_inference_worker.py`
- Rename `AppsQwenInferenceWorker` → `QwenInferenceWorker`
- Update imports to use renamed classes

### 2.3 Reasoning Files
- Move `apps_qwen/reasoning/apps_qwen_gateway.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py`
- Rename classes:
  - `AppsQwenGateway` → `QwenInferenceGateway`
  - `AppsQwenRequest` → `QwenInferenceRequest`
  - `AppsQwenResponse` → `QwenInferenceResponse`
- Rename functions:
  - `get_apps_qwen_gateway` → `get_qwen_inference_gateway`
  - `close_apps_qwen_gateway` → `close_qwen_inference_gateway`
- Update all imports to use renamed classes and new paths

### 2.4 Tools Files
- Move `apps_qwen/tools/gpu_memory_monitor.py` → `agentic_core/L3_orchestration/inference/qwen_vllm/tools/gpu_memory_monitor.py`
- No class renames
- Update internal imports

### 2.5 Main __init__.py
- Create `agentic_core/L3_orchestration/inference/qwen_vllm/__init__.py`
- Re-export all renamed classes and functions
- Update docstring to reflect L3 orchestration context
- Update usage examples

## Phase 3: Move and Update Test Files

### 3.1 Move Tests
- Move `apps_qwen/tests/*` → `tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/`
- Rename test class names to match new class names:
  - `TestAppsQwen*` → `TestQwenInference*`

### 3.2 Update Test Imports
- Update all imports in test files to use new paths:
  - `from apps_qwen.*` → `from agentic_core.L3_orchestration.inference.qwen_vllm.*`
- Update class references to use renamed classes
- Update function references

### 3.3 Move External Tests
- Move `tests/unit/apps_qwen/*` → `tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/`
- Update imports and class references

### 3.4 Update Performance Tests
- Update `tests/performance/test_qwen_vllm_performance.py`
- Update `tests/performance/test_hardened_vllm.py`
- Update `tests/performance/benchmark_runner.py`

## Phase 4: Update Importers in Business Applications

### 4.1 Update apps_rg
- Update `apps_rg/reasoning/RgResumeOrchestrator.py`
- Change: `from apps_qwen import AppsQwenGateway, AppsQwenInferenceWorker, AppsQwenRequest, apps_qwen_telemetry`
- To: `from agentic_core.L3_orchestration.inference.qwen_vllm import QwenInferenceGateway, QwenInferenceWorker, QwenInferenceRequest, qwen_inference_telemetry`
- Change: `from apps_qwen.apps_qwen_config import AppsQwenConfig, AppsQwenModelConfig, AppsQwenPromptConfig`
- To: `from agentic_core.L3_orchestration.inference.qwen_vllm.config.qwen_config import QwenInferenceConfig, QwenModelConfig, QwenPromptConfig`
- Update all class references in code

### 4.2 Update apps_lic
- Update `apps_lic/reasoning/GovernanceShieldAgent.py`
- Same import pattern as apps_rg
- Update all class references

### 4.3 Update apps_research
- Update `apps_research/reasoning/ResearchOrchestrator.py`
- Same import pattern
- Update all class references

### 4.4 Update apps_exec
- Update `apps_exec/reasoning/ExecOrchestrator.py`
- Same import pattern
- Update all class references

### 4.5 Update apps_rfp
- Update `apps_rfp/reasoning/RfpOrchestrator.py`
- Same import pattern
- Update all class references

### 4.6 Update apps_eval
- Update `apps_eval/reasoning/EvalOrchestrator.py`
- Update `apps_eval/engines/base_eval_engine.py`
- Same import pattern
- Update all class references

### 4.7 Update apps_shared
- Update `apps_shared/utils/vllm_advanced_features.py`
- Update `apps_shared/utils/vllm_shared_utils.py`
- Update imports to use new paths
- Update class references

## Phase 5: Update territories.yaml

1. Remove `apps_qwen` section entirely from territories.yaml

2. Add inference subfolder to `L3_orchestration` section:
```yaml
L3_orchestration:
  depth: 2
  purpose: "Multi-agent coordination, workflow state"
  subfolders:
    config: {purpose: "Configuration"}
    types: {purpose: "Data models"}
    reasoning: {purpose: "Decision agents"}
    enforcement: {purpose: "Guardrails"}
    utils: {purpose: "Helpers"}
    inference: {depth: 3, purpose: "Inference services for L3 orchestration"}
```

3. Add detailed inference section:
```yaml
inference:
  depth: 3
  purpose: "L3 inference services (vLLM, local models, etc.)"
  subfolders:
    qwen_vllm:
      depth: 4
      purpose: "Qwen vLLM inference service"
      subfolders:
        config: {depth: 5, purpose: "Configuration"}
        engines: {depth: 5, purpose: "vLLM clients"}
        reasoning: {depth: 5, purpose: "Inference gateway"}
        tools: {depth: 5, purpose: "GPU monitoring"}
```

## Phase 6: Delete Old Directory

1. Delete `apps_qwen/` directory entirely (including all subdirectories and __pycache__)

2. Delete `tests/unit/apps_qwen/` directory

## Phase 7: Validation

### 7.1 Import Validation
- Run `python -c "from agentic_core.L3_orchestration.inference.qwen_vllm import QwenInferenceGateway"`
- Verify no import errors

### 7.2 Test Validation
- Run `python -m pytest tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/ -v`
- All tests must pass

### 7.3 Business Application Validation
- Run targeted tests for each business app:
  - `python -m pytest tests/unit/apps_rg/ -v -k qwen`
  - `python -m pytest tests/unit/apps_lic/ -v -k qwen`
  - etc.
- Verify graceful degradation still works (try/except blocks)

### 7.4 Performance Test Validation
- Run `python -m pytest tests/performance/test_qwen_vllm_performance.py -v`
- Run `python -m pytest tests/performance/test_hardened_vllm.py -v`

### 7.5 ADG Regeneration
- Run `python tools/generate/generate_full_adg.py --zip`
- Verify no broken imports
- Verify no governance violations

## Phase 8: Commit and Sync

1. Commit with message:
```
Refactor: Move apps_qwen to agentic_core/L3_orchestration/inference/qwen_vllm

Architectural refactoring to align apps_qwen with L3 orchestration layer:
- Moved from apps_* (business applications) to agentic_core/L3_orchestration/inference (infrastructure)
- Renamed classes: AppsQwen* → QwenInference* to reflect L3 context
- Updated 20 importers across business applications
- Updated territories.yaml to reflect new structure
- Deleted old apps_qwen directory

Rationale:
- apps_qwen is a cost optimization layer for L2 execution, not a business application
- Infrastructure components belong in agentic_core/L3_orchestration
- Enables easier addition of alternative inference engines
- Clarifies dependency direction: L2 → L3 inference service
```

2. Push to GitHub

## Risk Mitigation

- **Rollback:** If validation fails, use `git revert` to rollback the commit
- **Gradual migration:** All importers use try/except blocks for graceful degradation, so missing imports won't crash business applications
- **Test coverage:** All existing tests are moved and updated, ensuring functionality is preserved

## Success Criteria

- ✅ All files moved to new location
- ✅ All classes renamed according to mapping
- ✅ All 20 importers updated
- ✅ territories.yaml updated (apps_qwen removed, L3_orchestration/inference added)
- ✅ Old apps_qwen directory deleted
- ✅ All tests pass (unit, integration, performance)
- ✅ ADG regenerates successfully with no broken imports
- ✅ No governance violations

## Estimated Time

- Phase 1: 5 minutes
- Phase 2: 30 minutes
- Phase 3: 20 minutes
- Phase 4: 30 minutes
- Phase 5: 10 minutes
- Phase 6: 2 minutes
- Phase 7: 20 minutes
- Phase 8: 5 minutes

**Total: ~2 hours**