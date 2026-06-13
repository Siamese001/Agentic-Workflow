# Pinecone Deprecation & Removal Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

Pinecone was deprecated in favor of the **BGE+FAISS** embedding stack. The codebase contains remnants that must be removed to complete the migration.

**Migration Target:**
- **From:** Pinecone cloud vector DB + Gemini embeddings
- **To:** LocalFAISSStore + BGE embeddings (BAAI/bge-m3, 1024-dim) + EmbeddingSovereignAgent

**Status:** Pinecone marked deprecated but not fully removed. Active references remain in production code.

---

## Audit Results

### Active Production References (MUST FIX)

#### 1. Core Agent Files (4 files)

| File | Type | Impact |
|------|------|--------|
| `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py` | Deprecated agent class | **HIGH** - Still imported by 3 active modules |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | Lazy loader `_get_PineconeSovereignAgent()` | **HIGH** - Active instantiation at line 351 |
| `agentic_core/L4_state/memory/sovereign_memory_store.py` | Direct import + instantiation | **HIGH** - Line 12 import, line 28 instantiation |
| `agentic_core/interfaces/execution_agents.py` | Public API export | **MEDIUM** - Exposes PineconeSovereignAgent to L1 |

#### 2. Mixin Infrastructure (2 files)

| File | Type | Impact |
|------|------|--------|
| `agentic_core/mixins/pinecone_vector_mixin.py` | 353-line mixin with Pinecone MCP client | **HIGH** - Used by multiple agents via InfrastructureMixin |
| `agentic_core/mixins/infrastructure_mixin.py` | Imports PineconeVectorMixin | **MEDIUM** - Propagates to all agents using InfrastructureMixin |

#### 3. Configuration & Metadata (2 files)

| File | Type | Impact |
|------|------|--------|
| `agentic_core/L5_safety/config/structure_blueprint/semantics.py` | Agent registry entry (line 1009) | **LOW** - Metadata only |
| `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py` | Comment-out logic for Pinecone imports | **LOW** - Healing heuristic |

---

### Test Files (12+ files - can be deleted)

- `tests/unit/agentic_core/L5_safety/reasoning/test_PineconeSovereignAgent.py`
- `tests/unit/agentic_core/test_PineconeSovereignAgent.py`
- `tests/unit/agentic_core/L5_safety/validators/test_surgical_low_tier.py` (contains PineconeSovereignAgent test class)
- `tests/unit/agentic_core/test_surgical_low_tier.py` (contains PineconeSovereignAgent test class)
- `tests/_quarantine/integration/agentic_core/L5_safety/core/test_surgical_healing_e2e.py` (references in agent lists)
- `tests/_quarantine/integration/agentic_core/core_dashboard/test_arch_guard.py` (pinecone import whitelist)
- `tests/unit/test_l4_state_agent_inventory_contract.py` (UNREACHABLE_ALLOWLIST entry)
- `tests/unit/test_l5_agent_inventory_contract.py` (agent count budget comment)
- `tests/governance/test_upward_import_enforcement.py` (exempt upward import entry)
- `tests/guardian/test_subatomic_compliance.py` (agent list reference)

---

### Archive Files (50+ files - ignore)

All files under `archives/` and `.healing_backups/` contain historical references and can be ignored.

---

## Migration Strategy

### Phase 1: Replace Active Usages (CRITICAL)

**Goal:** Eliminate all runtime dependencies on PineconeSovereignAgent.

#### 1.1 Replace `sovereign_memory_store.py`

**Current:**
```python
from agentic_core.L4_state.reasoning.PineconeSovereignAgent import PineconeSovereignAgent

class SovereignMemoryStore:
    def __init__(self, ...):
        self.pinecone = PineconeSovereignAgent(Path("."))
```

**Migration:**
```python
from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent
from system_learning.engines.local_faiss_store import LocalFAISSStore

class SovereignMemoryStore:
    def __init__(self, ...):
        self.embedder = EmbeddingSovereignAgent()
        self.vector_store = LocalFAISSStore(base_path=Path("logs/faiss_store"))
```

**Files to modify:**
- `agentic_core/L4_state/memory/sovereign_memory_store.py`

**Acceptance:**
- No import errors
- `SovereignMemoryStore` instantiates without Pinecone
- Existing tests pass (or are updated)

---

#### 1.2 Replace `SubAtomicRegistryAgent.py`

**Current:**
```python
def _get_PineconeSovereignAgent():
    from agentic_core.L4_state.reasoning.PineconeSovereignAgent import PineconeSovereignAgent
    return PineconeSovereignAgent

class SubAtomicRegistryAgent:
    def __init__(self, project_root: Path):
        self.pinecone = _get_PineconeSovereignAgent()(project_root)
```

**Migration:**
```python
# Remove _get_PineconeSovereignAgent() entirely

class SubAtomicRegistryAgent:
    def __init__(self, project_root: Path):
        # Option A: Remove pinecone attribute entirely if unused
        # Option B: Replace with LocalFAISSStore if needed
        pass
```

**Files to modify:**
- `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py`

**Acceptance:**
- `_get_PineconeSovereignAgent()` function deleted
- `self.pinecone` attribute removed or replaced
- No references to `PineconeSovereignAgent` remain

---

#### 1.3 Remove from `interfaces/execution_agents.py`

**Current:**
```python
from agentic_core.L2_execution.reasoning.PineconeSovereignAgent import PineconeSovereignAgent

__all__ = [
    "EmbeddingSovereignAgent",
    "PineconeSovereignAgent",  # REMOVE
    "RedisSovereignAgent",
]
```

**Migration:**
```python
# Remove import and __all__ entry

__all__ = [
    "EmbeddingSovereignAgent",
    "RedisSovereignAgent",
]
```

**Files to modify:**
- `agentic_core/interfaces/execution_agents.py`

**Acceptance:**
- `PineconeSovereignAgent` not exported
- No import errors in dependent modules

---

### Phase 2: Remove Mixin Infrastructure (MEDIUM PRIORITY)

**Goal:** Eliminate `PineconeVectorMixin` and its usage.

#### 2.1 Audit Mixin Usage

**Action:** Grep for classes inheriting from `PineconeVectorMixin` or `InfrastructureMixin`.

**Expected:** Most agents use `InfrastructureMixin`, which includes `PineconeVectorMixin`.

**Decision:**
- If `PineconeVectorMixin` methods are **actively called**: Replace with FAISS-based equivalents
- If `PineconeVectorMixin` methods are **never called**: Remove from `InfrastructureMixin`

#### 2.2 Remove `pinecone_vector_mixin.py`

**Files to delete:**
- `agentic_core/mixins/pinecone_vector_mixin.py`

**Files to modify:**
- `agentic_core/mixins/infrastructure_mixin.py` (remove import)

**Acceptance:**
- No import errors
- All tests pass

---

### Phase 3: Delete Core Agent File (FINAL STEP)

**Goal:** Remove `PineconeSovereignAgent.py` after all references eliminated.

#### 3.1 Delete Agent File

**Files to delete:**
- `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py`

**Acceptance:**
- File deleted
- No import errors across entire codebase
- `python -m pytest -q --color=no` passes

---

### Phase 4: Clean Up Metadata & Tests (LOW PRIORITY)

**Goal:** Remove test files and metadata references.

#### 4.1 Delete Test Files

**Files to delete:**
- `tests/unit/agentic_core/L5_safety/reasoning/test_PineconeSovereignAgent.py`
- `tests/unit/agentic_core/test_PineconeSovereignAgent.py`

#### 4.2 Update Metadata Files

**Files to modify:**
- `agentic_core/L5_safety/config/structure_blueprint/semantics.py` (remove agent registry entry)
- `tests/unit/test_l4_state_agent_inventory_contract.py` (remove UNREACHABLE_ALLOWLIST entry)
- `tests/unit/test_l5_agent_inventory_contract.py` (update agent count budget)
- `tests/_quarantine/integration/agentic_core/core_dashboard/test_arch_guard.py` (remove pinecone whitelist)
- `tests/governance/test_upward_import_enforcement.py` (remove exempt import)

#### 4.3 Update Test References

**Files to modify:**
- `tests/unit/agentic_core/L5_safety/validators/test_surgical_low_tier.py` (remove `TestPineconeSovereignAgentIntegration` class)
- `tests/unit/agentic_core/test_surgical_low_tier.py` (remove `TestPineconeSovereignAgentIntegration` class)
- `tests/_quarantine/integration/agentic_core/L5_safety/core/test_surgical_healing_e2e.py` (remove from agent lists)
- `tests/guardian/test_subatomic_compliance.py` (remove from agent list)

**Acceptance:**
- All modified tests pass
- No references to `PineconeSovereignAgent` in active tests

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking `sovereign_memory_store.py` | **HIGH** | Implement FAISS replacement before deletion; add integration test |
| Breaking `SubAtomicRegistryAgent` | **MEDIUM** | Audit usage of `self.pinecone` attribute; replace or remove |
| Mixin removal breaks agents | **MEDIUM** | Grep for `vector_search()` / `vector_upsert()` calls; replace with FAISS equivalents |
| Test failures after deletion | **LOW** | Run full suite after each phase; fix incrementally |

---

## Acceptance Criteria

### Phase 1 Complete
- [ ] `sovereign_memory_store.py` uses `LocalFAISSStore` instead of `PineconeSovereignAgent`
- [ ] `SubAtomicRegistryAgent.py` has no `PineconeSovereignAgent` references
- [ ] `interfaces/execution_agents.py` does not export `PineconeSovereignAgent`
- [ ] `python -m pytest -q --color=no tests/unit/agentic_core/L4_state/` passes

### Phase 2 Complete
- [ ] `pinecone_vector_mixin.py` deleted
- [ ] `infrastructure_mixin.py` does not import `PineconeVectorMixin`
- [ ] No agents call `vector_search()` / `vector_upsert()` from mixin
- [ ] Full test suite passes

### Phase 3 Complete
- [ ] `PineconeSovereignAgent.py` deleted
- [ ] `grep -r "PineconeSovereignAgent" agentic_core/` returns 0 results (excluding comments)
- [ ] `python -m pytest -q --color=no` passes (full suite)

### Phase 4 Complete
- [ ] All test files deleted
- [ ] All metadata references removed
- [ ] Anti-pattern scanner passes: `python ops_scripts/ci/check_anti_patterns.py`
- [ ] Import boundary check passes

---

## Execution Plan

1. **Audit mixin usage** ()
   - Grep for `vector_search`, `vector_upsert`, `PineconeVectorMixin`
   - Identify active callers

2. **Phase 1: Replace active usages** (2-)
   - Fix `sovereign_memory_store.py`
   - Fix `SubAtomicRegistryAgent.py`
   - Fix `interfaces/execution_agents.py`
   - Run targeted tests

3. **Phase 2: Remove mixin** (1-)
   - Delete `pinecone_vector_mixin.py`
   - Update `infrastructure_mixin.py`
   - Run full test suite

4. **Phase 3: Delete core agent** ()
   - Delete `PineconeSovereignAgent.py`
   - Verify no import errors
   - Run full test suite

5. **Phase 4: Clean up metadata** ()
   - Delete test files
   - Update metadata files
   - Final verification

**Total estimated time:** 5-

---

## Notes

- The file `agentic_core/L2_execution/reasoning/PineconeSovereignAgent.py` is **668 lines** and marked deprecated since M4 milestone.
- The mixin `pinecone_vector_mixin.py` is **353 lines** and routes through `pinecone_mcp_client`.
- All Pinecone operations should be replaced with `LocalFAISSStore` + `EmbeddingSovereignAgent` (BGE embeddings).
- The `USE_PINECONE` feature flag in `constants_config.py` should be removed after deletion.

---

## Related Work

- **Completed:** BGE+FAISS hardening (G_RS, G_HI, G_MLA) - commit `882ab0e27`
- **Completed:** Cross-agent meta-learning persistence - commit `06193982a`
- **Pending:** Pinecone removal (this plan)

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

