### Strategic Refactor Plan

#### 1. Analysis of Subatomic Governance
*   **Law I (Growth):** 52 files violate the 200-line limit. `agentic_core/interfaces/governance.py` is truncated, causing critical `TEST_FAILURE`.
*   **Law II (Complexity):** 50+ functions exceed complexity/length thresholds. `cognitive_node.py:think` and `concurrency.py:execute` are major offenders.
*   **Law III (Depth):** Current hierarchy is flat in `agentic_core/`, leading to monolithic file growth.

#### 2. Root Cause Identification
*   **Primary Blockers:** File truncation in `agentic_core/interfaces/governance.py` (Key 22).
*   **Pattern:** Logic saturation in base classes and interfaces. Repetitive async violations (Key 60) and circular/redundant imports (Key 7/8).

#### 3. Proposed Atomic Actions

**Phase A: Immediate Integrity Restoration**
*   **Repair `agentic_core/interfaces/governance.py`**: Restore the truncated `ArchitectureGovernor` class.
*   **Partition Interface**: Split `governance.py` interface into:
    *   `agentic_core/domain/governance/base.py` (Abstract Interfaces)
    *   `agentic_core/domain/governance/laws.py` (Law implementation)
    *   `agentic_core/domain/governance/enforcer.py` (Enforcement logic)

**Phase B: Monolith Decomposition (Depth 3-5)**
*   **Refactor `agentic_core/cognitive_node.py`**:
    *   Extract `_synthesize_code` to `apps_shared/utils/code_gen.py`.
    *   Move thinking logic to `agentic_core/domain/cognition/thinker.py`.
*   **Decompose `agentic_core/agents/concurrency.py`**:
    *   Extract leak analysis to `agentic_core/domain/service/leak_detector.py`.
*   **Consolidate Engines**: Move shared logic from `outreach_engine_zse.py` and `resume_engine_zlg.py` into `apps_shared/engines/base_engine.py`.

**Phase C: Signal Cleanup**
*   **Async Hygiene**: Replace `requests` with `httpx` in `engineering.py` and `pattern_enforcer.py`.
*   **Redundancy Removal**: Delete `*_old.py` and `*_backup.py` files identified in Key 50.

#### 4. Blast Radius Assessment
*   **Impact:** High. `ArchitectureGovernor` is a core dependency for `NervousSystem`.
*   **Mitigation:** Use `__init__.py` in `agentic_core/interfaces/` to maintain backward compatible imports while logic is moved to `domain/`.

#### 5. Verification Strategy
*   **Pre-fix:** Run `pytest test_integrity_mission.py` to confirm failure.
*   **Post-fix:** Verify `TEST_FAILURE` signal clears and file line counts drop below 200.
*   **Signal Check:** Ensure `SECURE` and `DEPS_VALID` remain green.