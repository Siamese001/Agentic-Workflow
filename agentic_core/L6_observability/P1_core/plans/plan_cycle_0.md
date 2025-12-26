### Strategic Refactor Plan: Subatomic Governance Alignment

#### 1. Analysis of Violations
*   **Root Cause Pattern**: Monolithic Bloat and Architectural Depth Violation. The system exhibits "Large Class" and "God Object" smells in `agentic_core`, specifically within `cognitive_node.py`, `agent_logic.py`, and the `agents/` directory.
*   **Signal Impact**: `TEST_FAILURE` is likely tied to the high cyclomatic complexity (24) in `concurrency.py` and method length (120+) in `cognitive_node.py`, leading to non-deterministic state transitions.

#### 2. Phase I: Noise Reduction & Archiving
*   **Action**: Move all legacy/backup files to an out-of-scope directory to clear `Key 50` and `Key 0` violations.
*   **Targets**: 
    *   `.\\agentic_core\\agent_logic_connectivity_backup.py`
    *   `.\\agentic_core\\agent_logic_connectivity_old.py`
    *   `.\\agentic_core\\domain\\context_old.py`

#### 3. Phase II: Decomposition of Core Monoliths
*   **Action**: Split classes and methods exceeding 200 lines or complexity 10 into focused units at Depth 3-5.
*   **Targets**:
    *   **`cognitive_node.py`**: Extract `_synthesize_code` into `agentic_core/domain/service/code_synthesizer.py`. Split `CognitiveNode` into `NodeReasoner` and `NodeExecutor`.
    *   **`agents/concurrency.py`**: Extract `_analyze_leak_context` (Complexity 24) into a dedicated service: `apps_shared/services/leak_detector.py`.
    *   **`interfaces/governance.py`**: Break into `GovernanceValidator`, `DepthEnforcer`, and `ImpactAnalyzer` in `agentic_core/interfaces/governance/`.

#### 4. Phase III: Shared Logic Extraction
*   **Action**: Relocate repeated logic and multiple classes from agent files into `apps_shared/`.
*   **Targets**:
    *   Move `build_import_dependency_map` from `agents/base.py` to `apps_shared/utils/dependency_tools.py`.
    *   Move shared schemas from `engines/canon_validator_engine_zlm.py` to `apps_shared/schemas/validation_schemas.py`.
    *   Unify `intervention_server.py` logic between `agentic_core/L5_safety/` and `apps_shared/`.

#### 5. Phase IV: Dependency Graph & Blast Radius Verification
*   **Action**: Update imports using a centralized mapping to prevent `Key 7/8` (Import/Style) regressions.
*   **Verification**: 
    *   Ensure no file in `agentic_core/` exceeds 180 lines.
    *   Ensure all new services reside at depth 3 (e.g., `agentic_core/domain/service/`).
    *   Validate that `TEST_FAILURE` is resolved by isolating the `concurrency` logic.

#### 6. Atomic Fix Execution Map
1.  **File**: `agentic_core/agents/base.py` -> Split into `base_agent.py` and `dependency_resolver.py`.
2.  **File**: `agentic_core/cognitive_node.py` -> Refactor `think()` into smaller strategy-pattern calls.
3.  **File**: `agentic_core/L1_cognition/concurrency_guardian.py` -> Relocate `acquire_lock` logic to `apps_shared/`.
4.  **File**: `agentic_core/core_utils.py` -> Move to `apps_shared/utils/core_logic.py`.