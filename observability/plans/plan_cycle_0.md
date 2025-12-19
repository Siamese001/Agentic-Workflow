### Strategic Refactor Plan: Subatomic Governance Cycle 1

#### 1. Three Laws of Subatomic Governance Recall
1.  **Integrity**: Code must remain functional; `TEST_FAILURE` must be resolved by addressing logic bloat.
2.  **Modularity**: Functions must not exceed 50 lines; files must not exceed 200 lines.
3.  **Blast Radius**: Changes must be atomic and confined to the shallowest possible depth (3-5) to prevent cascading signal failures.

#### 2. Root Cause Pattern Identification
*   **Pattern**: Monolithic Bloat and Legacy Persistence.
*   **Evidence**: Key 50/19 show high cyclomatic complexity and file size violations in `agentic_core`. Key 0/1 show legacy artifacts (`_old.py`, `_backup.py`) causing namespace pollution and potential test interference.

#### 3. Proposed Minimal Atomic Fixes
*   **Fix A: Prune Dead Weight**: Delete `agentic_core/agent_logic_connectivity_backup.py`, `agentic_core/agent_logic_connectivity_old.py`, and `agentic_core/domain/context_old.py`.
*   **Fix B: Extract Shared Logic**: 
    *   Move `core_utils.py` logic to `apps_shared/utils/core_primitives.py`.
    *   Extract `build_import_dependency_map` from `agentic_core/agents/base.py` to `apps_shared/discovery/imports.py`.
*   **Fix C: Decomposition of Cognition**:
    *   Split `agentic_core/cognitive_node.py` into `domain/service/thought_engine.py` (logic) and `domain/service/synthesis_engine.py` (code generation).
    *   Split `agentic_core/agents/concurrency.py` into separate files for `LeakAnalyzer` and `ExecutionGuardian`.

#### 4. Blast Radius Check (Dependency Graph)
*   Impact is high but controlled. `agentic_core` is the root; refactoring requires updating imports in `L1-L3` layers. 
*   **Mitigation**: Use `apps_shared` to maintain a single source of truth for moved logic, preventing circularity.

#### 5. Signal Verification Plan
*   **SECURE**: No change to encryption/auth layers.
*   **DEPS_VALID**: Import map must be updated immediately following file moves.
*   **GENERATIVE_CLEAN**: Modularization reduces LLM context window pressure.
*   **TEST_FAILURE**: Expected to clear once `cognitive_node.py` complexity is reduced and legacy path conflicts are removed.

---

### Implementation Phases

| Phase | Target | Action |
| :--- | :--- | :--- |
| **Phase 1** | Legacy Cleanup | Remove all `*_old.py` and `*_backup.py` files (Key 0/50). |
| **Phase 2** | Shared Extraction | Move `agentic_core/core_utils.py` -> `apps_shared/utils/`. |
| **Phase 3** | Monolith Splitting | Split `cognitive_node.py` and `concurrency.py` at the 200-line boundary. |
| **Phase 4** | Complexity Reduction | Refactor `think` and `execute_outreach` into private helper methods < 40 lines. |