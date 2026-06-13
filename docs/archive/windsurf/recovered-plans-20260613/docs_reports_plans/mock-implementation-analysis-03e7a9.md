# Mock Implementation Analysis Report
**Generated:** 2026-03-30  
**Scope:** `tests/` directory comprehensive mock analysis using ADG insights  
**Files Analyzed:** 96 test files with mock usage  
**ADG Accelerator Used:** Yes - for component dependency mapping

---

## Executive Summary

| Category | Count | Justified | Needs Review |
|----------|-------|-----------|--------------|
| **Internal Component Mocks** | 11 files | 6 | **5** |
| **External Service Mocks** | 15 files | 15 | 0 |
| **Filesystem Mocks** | 58 files | 58 | 0 |
| **Config/Environment Mocks** | 35 files | 35 | 0 |
| **Total with mocks** | 96 files | 114 | **5** |

---

## 1. Internal Component Mocks (REQUIRES ATTENTION)

These files mock internal `agentic_core`, `apps_*`, `tools`, or `system_learning` components. Per architectural guidelines, internal component mocks should be minimized in favor of:
- **Unit tests** with real dependencies (for leaf nodes)
- **Integration tests** with test containers/doubles
- **Contract tests** verifying interface compatibility

### 1.1 Files with Internal Mocks - Detailed Analysis

#### **🔴 NEEDS REVIEW** `tests/sovereign_hardening/test_ssot_pipeline_protocol.py` (41 mocks)
- **Mocks:** `execute_ssot` pipeline components, decision engines, state managers
- **ADG Analysis:** Tests L0 routing scripts (orchestration pipeline)
- **Current Pattern:** Heavy MagicMock usage for internal pipeline adapters
- **Recommendation:** 
  - ✅ **KEEP** for negative control testing (tamper detection)
  - ⚠️ **REFACTOR** structural completeness tests to use minimal real adapters
  - Consider using `SubphaseResult` real objects instead of MagicMock returns

#### **🔴 NEEDS REVIEW** `tests/unit/test_execute_ssot_integration.py` (24 mocks)
- **Mocks:** Lifecycle trace contract emitters, meta learning intake
- **ADG Analysis:** Tests P0-P4 emitter integration in execute_ssot
- **Current Pattern:** `patch()` on internal emitter functions
- **Recommendation:**
  - ⚠️ **REFACTOR** - These are infrastructure tests; should use real emitters with captured output
  - Emitter calls are side-effect-only; verify via log capture, not mocking

#### **🟢 JUSTIFIED** `tests/unit/apps_shared/utils/test_governed_prompt_adapter.py` (23 mocks)
- **Mocks:** `GovernedPromptAdapter` internal methods
- **ADG Analysis:** Tests apps_shared → L2 execution integration
- **Current Pattern:** `@patch` on adapter's `_build_prompt_bom`, `_assemble_artifact`, `_execute_artifact`
- **Recommendation:**
  - ✅ **KEEP** - This is a legitimate unit test pattern (test one method, mock collaborators)
  - Methods being mocked are within the same class (self-collaboration)

#### **🔴 NEEDS REVIEW** `tests/integration/test_prompt_lifecycle_pipeline.py` (13 mocks)
- **Mocks:** `_get_version_store`, `template_registry`
- **ADG Analysis:** Tests L0 routing → L4 state integration
- **Current Pattern:** Registry and version store mocking
- **Recommendation:**
  - ⚠️ **REFACTOR** - Integration tests should use in-memory registries, not mocks
  - Use `InMemoryVersionStore` or test doubles instead of MagicMock

#### **🔴 NEEDS REVIEW** `tests/integration/test_ci_adg_migration.py` (12 mocks)
- **Mocks:** `ADGQueryBridge` and subprocess calls
- **ADG Analysis:** CI migration integration tests
- **Current Pattern:** `Mock(spec=ADGQueryBridge)` 
- **Recommendation:**
  - ⚠️ **REFACTOR** - Use real ADG query bridge with test SQLite database
  - Subprocess mocking is acceptable for isolation

#### **🔴 NEEDS REVIEW** `tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py` (8 mocks)
- **Mocks:** Template registry, BOM builder internals
- **ADG Analysis:** E2E prompt lifecycle tests
- **Current Pattern:** Limited patching of internal components
- **Recommendation:**
  - ⚠️ **REFACTOR** - E2E tests should minimize internal mocking; use real registries
  - Edge case testing can use real objects with test data

#### **🟢 JUSTIFIED** `tests/unit/tools/adg/test_capability_extractor.py` (8 mocks)
- **Mocks:** `ContextWindowEstimator` (missing dependency fallback)
- **ADG Analysis:** Tools-tier ADG capability extraction
- **Current Pattern:** Conditional mocking when import fails
- **Recommendation:**
  - ✅ **KEEP** - This is defensive mocking for optional dependency
  - Pattern: Mock only when `ContextWindowEstimator` unavailable

#### **🟢 JUSTIFIED** `tests/unit/tools/adg/test_hollow_file_cleanup.py` (5 mocks)
- **Mocks:** Internal ADG file operations
- **ADG Analysis:** File cleanup utilities in tools tier
- **Recommendation:**
  - ✅ **KEEP** - Filesystem operation mocking is acceptable

#### **🟢 JUSTIFIED** `tests/unit/tools/adg/test_strip_boilerplate.py` (5 mocks)
- **Mocks:** File reading operations
- **ADG Analysis:** ADG utility functions
- **Recommendation:**
  - ✅ **KEEP** - Filesystem mocking for unit tests is acceptable

#### **🟢 JUSTIFIED** `tests/unit/tools/adg/test_boilerplate_ratio_report.py` (6 mocks)
- **Mocks:** File path operations
- **Recommendation:**
  - ✅ **KEEP** - Filesystem mocking acceptable for report generation

#### **🟢 JUSTIFIED** `tests/unit/agentic_core/L4_state/memory/test_sovereign_semantic_cache_query.py` (5 mocks)
- **Mocks:** Registry, config
- **Recommendation:**
  - ✅ **KEEP** - Config mocking is acceptable

---

## 2. External Service Mocks (ALL JUSTIFIED)

These mock external services (Redis, ChromaDB, OpenAI, Anthropic, HTTP). All are **architecturally appropriate**.

| Pattern | Files | Justification |
|---------|-------|---------------|
| Redis mocking | 3 | External state store - appropriate to mock |
| ChromaDB mocking | 2 | External vector DB - appropriate to mock |
| LLM provider mocking | 8 | External API calls - must mock for determinism |
| HTTP/request mocking | 2 | External network calls - must mock |

---

## 3. Filesystem Mocks (ALL JUSTIFIED)

58 files use `tmp_path`, `tempfile`, or file patching. All are **architecturally appropriate** for:
- Temporary test file creation
- Path isolation
- Write operation safety

---

## 4. Config/Environment Mocks (ALL JUSTIFIED)

35 files mock config or environment. All are **architecturally appropriate** for:
- Environment variable isolation
- Config state reset between tests
- Feature flag testing

---

## 5. ADG-Informed Recommendations

Based on ADG dependency analysis, the following should **NOT** be mocked:

### 5.1 Critical Path Components (Use Real Implementations)

| Component | Layer | Why Not to Mock | Alternative |
|-----------|-------|-----------------|-------------|
| `lifecycle_trace_contract` emitters | L0 | Infrastructure - verify actual output | Log capture, spy objects |
| `execute_ssot` pipeline adapters | L0 | Core orchestration - test real flow | Minimal real adapters |
| `ADGQueryBridge` | tools | Data access layer - test real queries | In-memory SQLite |
| `template_registry` | L4 | State layer - test with real registry | In-memory registry |
| `version_store` | L4 | State layer - test with real store | In-memory store |

### 5.2 Appropriate Mock Targets (Keep Mocking)

| Component | Layer | Why Mocking is OK |
|-----------|-------|-------------------|
| LLM providers (OpenAI, Anthropic) | External | External APIs, cost, determinism |
| Vector DBs (ChromaDB, Redis) | External/L4 | External services, test isolation |
| Filesystem operations | OS | Temp file cleanup, path safety |
| Config/environment | OS | Test isolation, state reset |
| Self-collaboration (same class) | Any | Unit testing internal methods |

---

## 6. Priority Actions

### High Priority (5 files)
1. **`tests/unit/test_execute_ssot_integration.py`** - Replace emitter mocks with log capture
2. **`tests/integration/test_prompt_lifecycle_pipeline.py`** - Use in-memory registries
3. **`tests/integration/test_ci_adg_migration.py`** - Use real ADG bridge with test DB
4. **`tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py`** - Remove registry mocks
5. **`tests/sovereign_hardening/test_ssot_pipeline_protocol.py`** - Reduce adapter mocking scope

### Rationale
These files mock components that are:
- Part of the critical execution path
- Deterministic and fast (no I/O blocking)
- Testable with real implementations + test doubles
- Violating "test behavior, not implementation" principle

---

## 7. Testing Architecture Guidelines

Based on ADG layer analysis:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer      │  Test Type         │  Mock Policy              │
├─────────────────────────────────────────────────────────────┤
│  L0 Routing │  Unit + Contract   │  Mock L1+ dependencies      │
│  L1 Cognition│ Unit + Integration│  Mock L2+ dependencies      │
│  L2 Execution│ Unit + E2E        │  Mock external APIs only    │
│  L3 Orchestration│ Integration   │  Use real L0-L2 components  │
│  L4 State   │  Contract tests    │  Use in-memory stores       │
│  L5 Safety  │  Integration         │  Mock L6 dependencies       │
│  L6 Observability│ Unit tests    │  Mock all dependencies      │
│  External   │  Unit tests          │  Always mock                │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix: Complete Mock Usage Inventory

### Top 20 Files by Mock Count

| Count | Categories | File |
|-------|------------|------|
| 41 | INTERNAL_MOCK, CONFIG_MOCK | tests/sovereign_hardening/test_ssot_pipeline_protocol.py |
| 37 | FS_MOCK | tests/e2e/test_graphrag_e2e.py |
| 32 | FS_MOCK | tests/e2e/test_graphrag_hardened.py |
| 25 | FS_MOCK | tests/unit/test_phase24_high_severity_remaining.py |
| 24 | INTERNAL_MOCK, FS_MOCK | tests/unit/test_execute_ssot_integration.py |
| 24 | FS_MOCK | tests/unit/test_wave30_guardian_sweep.py |
| 24 | FS_MOCK, CONFIG_MOCK | tests/unit/ml_decision_support/test_phase4_components.py |
| 23 | INTERNAL_MOCK | tests/unit/apps_shared/utils/test_governed_prompt_adapter.py |
| 21 | FS_MOCK | tests/unit/test_phase23_comprehensive_v2.py |
| 18 | FS_MOCK | tests/unit/test_phase22_comprehensive_v2.py |
| 17 | CONFIG_MOCK | tests/integration/test_execute_ssot_full_e2e.py |
| 14 | FS_MOCK | tests/unit_min_deps/test_capture_evidence.py |
| 13 | INTERNAL_MOCK | tests/integration/test_prompt_lifecycle_pipeline.py |
| 13 | FS_MOCK | tests/unit/test_phase22_medium_severity_fixes.py |
| 12 | INTERNAL_MOCK, FS_MOCK | tests/integration/test_ci_adg_migration.py |
| 12 | FS_MOCK | tests/unit/test_fix_high_severity_silent_swallowers_phase21.py |
| 9 | OTHER | tests/adg/test_adg_test_selector.py |
| 9 | FS_MOCK | tests/e2e/test_uwg_determinism_e2e.py |
| 9 | FS_MOCK, CONFIG_MOCK | tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_exceptions.py |
| 8 | INTERNAL_MOCK | tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py |

---

**End of Report**
