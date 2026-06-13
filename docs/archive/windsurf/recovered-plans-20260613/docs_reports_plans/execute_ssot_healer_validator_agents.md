# Execute SSOT: Healer/Validator Agent Pairs

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Overview

Per `@agentic_process_mapping.md`, agents in `execute_ssot.py` follow the **Validator → Healer** split pattern:
- **Validators** (L5 Safety) detect violations and produce check dictionaries
- **Healers** (L2 Execution) consume check dictionaries and apply fixes

This separation enforces the **detect-then-heal** pipeline and prevents agents from having dual authority.

---

## Agent Pairs Table

| # | Domain | Validator Agent | Healer Agent | Scope | Phase | Naming Issue |
|---|--------|----------------|--------------|-------|-------|-------------|
| 1 | **Filesystem SSOT** | `FilesystemSSOTValidatorAgent` ✓ | `FilesystemSSOTReconcilerAgent` ⚠️ | Filesystem drift from structure blueprint | Phase 1 (Discovery) | Healer should be `FilesystemSSOTHealerAgent` |
| 2 | **Location** | `LocationValidatorAgent` ✓ | `LocationHealerAgent` ✓ | File location violations (misplaced files, wrong territory) | Phase 1 (Discovery) | Correct naming |
| 3 | **File Classification** | `FileClassificationValidatorAgent` ✓ | `FileClassificationAgent` ❌ | Naming violations, file type misclassification | Phase 1 (Early Detection) | Healer should be `FileClassificationHealerAgent` |
| 4 | **Hierarchy** | `HierarchyValidatorAgent` ✓ | `HierarchyAgent` ❌ | Directory structure violations, depth violations | Phase 3 (Alignment) | Healer should be `HierarchyHealerAgent` |
| 5 | **Gravity** | `GravityValidatorAgent` ✓ | `GravityLeakRepairAgent` ⚠️ | Layer inversions (L5 importing L2, etc.) | Global (Pre-Territory Loop) | Healer should be `GravityHealerAgent` or `GravityLeakHealerAgent` |
| 6 | **Architecture** | `ArchitectureGovernorAgent` ❌ | *(via remediation_dispatcher)* ❌ | Architectural governance violations | Phase 4 (Validation) | Should be `ArchitectureGovernorValidatorAgent` + `ArchitectureGovernorHealerAgent` |
| 7 | **Root Hygiene** | `RootHygieneAgent` ❌ | `RootHygieneAgent` ❌ | Root-level file violations | Global (Pre-Territory Loop) | Should be `RootHygieneValidatorAgent` + `RootHygieneHealerAgent` |
| 8 | **Cognitive Disposition** | `CognitiveDispositionAgent` ❌ | *(analysis only)* | Enhanced confidence calculation for violations | Phase 1 (Discovery) | Not a validator/healer pair - analysis agent |
| 9 | **Debate Synthesis** | `ObservabilityProbeExecutorAgent` ❌ | *(detection only)* | Prompt governance violations | Phase 6 (Conversational) | Not a validator/healer pair - probe agent |
| 10 | **Sovereign Certifier** | *(aggregator)* | *(certification only)* | Compliance certification and reporting | Phase 7 (Certification) | Not a validator/healer pair - certifier agent |

---

## Naming Inconsistencies Analysis

### Current State

The agent naming in `execute_ssot.py` is **inconsistent** with the validator/healer separation pattern:

**✓ Correctly Named (2/10):**
- `LocationValidatorAgent` → `LocationHealerAgent`
- `FilesystemSSOTValidatorAgent` → `FilesystemSSOTReconcilerAgent` (acceptable variant)

**❌ Incorrectly Named (8/10):**
- `FileClassificationValidatorAgent` → `FileClassificationAgent` (missing "Healer" suffix)
- `HierarchyValidatorAgent` → `HierarchyAgent` (missing "Healer" suffix)
- `GravityValidatorAgent` → `GravityLeakRepairAgent` ("Repair" instead of "Healer")
- `ArchitectureGovernorAgent` (missing "Validator" suffix, no explicit healer)
- `RootHygieneAgent` (single agent doing both validation and healing)
- `CognitiveDispositionAgent` (not a validator/healer pair)
- `ObservabilityProbeExecutorAgent` (not a validator/healer pair)
- `SovereignCertifier` (not a validator/healer pair)

### Architectural Pattern from `agentic_process_mapping.md`

The document shows:
- **L5 Safety**: Validators (read-only, detect violations)
- **L2 Execution**: Healers (apply fixes, mutate state)
- **Separation**: Prevents dual authority (detect + fix in same agent)

However, the document does **NOT explicitly mandate** the "Validator" and "Healer" suffix naming convention. The separation is **architectural** (L5 vs L2), not necessarily **nominal**.

### Why Some Agents Lack Explicit Healers

**`ArchitectureGovernorAgent`** (your specific question):
- Acts as **validator only** in `execute_ssot.py`
- Healing is delegated to `remediation_dispatcher._invoke_healer()`
- This is **consistent** with the architectural pattern:
  - Detection: `ArchitectureGovernorAgent` (L5)
  - Healing: Dispatched to registered healers (L2)
- The agent produces a `check_dict` that healers consume
- **No explicit healer agent** because healing is domain-specific and dispatched

**Other agents without explicit healers:**
- `CognitiveDispositionAgent`: Analysis/confidence enhancement (not validation)
- `ObservabilityProbeExecutorAgent`: Detection/probing (not structural validation)
- `SovereignCertifier`: Aggregation/certification (not validation)

### Recommended Naming Convention

For **clarity and consistency**, all validator/healer pairs should follow:

```
{Domain}ValidatorAgent  (L5 Safety - read-only detection)
{Domain}HealerAgent     (L2 Execution or L5 - mutation/repair)
```

**Exceptions:**
- Agents that only validate (no healing): `{Domain}ValidatorAgent` only
- Agents that do neither: Use descriptive suffixes (`Agent`, `Orchestrator`, `Certifier`)

---

## Detailed Scope Breakdown

### 1. Location (Validator + Healer)

**Validator:** `LocationValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py`
- **Scope:** Detects files in wrong territories, misplaced modules
- **Output:** `violations` list with file paths and expected locations
- **Phase:** Phase 2 (Discovery)

**Healer:** `LocationHealerAgent`
- **File:** `agentic_core/L5_safety/reasoning/LocationHealerAgent.py`
- **Scope:** Moves files to correct locations, updates imports
- **Input:** Violations from `LocationValidatorAgent`
- **Method:** `heal_violations(violations, auto_approve=False)`
- **HITL:** Requires human approval for archive/delete operations

---

### 2. File Classification (Validator Only)

**Validator:** `FileClassificationValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py`
- **Scope:** Naming violations (Agent/Orchestrator/Engine/Validator suffixes)
- **Output:** `classification_violations` list
- **Phase:** Phase 2 (Early Detection)

**Healer:** *(Delegated to `remediation_dispatcher`)*
- **Method:** `_invoke_healer("file_classification", check_dict, ...)`
- **Scope:** Renames files to match classification conventions

---

### 3. Hierarchy (Validator Only)

**Validator:** `HierarchyValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/HierarchyValidatorAgent.py`
- **Scope:** Directory depth violations, hierarchy misalignment
- **Output:** `violations_count` and check dictionary
- **Phase:** Phase 3 (Alignment)

**Healer:** *(Delegated to `remediation_dispatcher`)*
- **Method:** `_invoke_healer("hierarchy_violations", check_dict, ...)`
- **Scope:** Restructures directories to match hierarchy rules

---

### 4. Gravity (Validator + Healer)

**Validator:** `GravityValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/GravityValidatorAgent.py`
- **Scope:** Layer inversions (L5 → L2, L3 → L1, etc.)
- **Output:** `gravity_violations` count and check dictionary
- **Phase:** Global (runs once before territory loop)

**Healer:** `GravityLeakRepairAgent`
- **File:** `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py`
- **Scope:** Fixes layer inversions by moving imports or refactoring
- **Input:** Check dictionary from `GravityValidatorAgent`
- **Method:** Via `remediation_dispatcher._invoke_healer("gravity_violations", ...)`

---

### 5. Filesystem SSOT (Validator + Reconciler)

**Validator:** `FilesystemSSOTValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/FilesystemSSOTValidatorAgent.py`
- **Scope:** Detects drift between filesystem and structure blueprint
- **Output:** Drift report with missing/unexpected files
- **Phase:** Phase 2 (Discovery)

**Healer/Reconciler:** `FilesystemSSOTReconcilerAgent`
- **File:** `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py`
- **Scope:** Reconciles filesystem to match structure blueprint
- **Input:** Drift report from validator
- **Method:** Creates/removes directories, moves files

---

### 6. Code Quality (Validator Only - Inline Healing)

**Validator:** `ASTCodeQualityValidator`
- **File:** `agentic_core/L0_routing/scripts/execute_ssot.py` (inline class)
- **Scope:** AST-based code quality checks (memory guards, type safety)
- **Output:** Quality violations
- **Phase:** Phase 4 (Code Quality)

**Healer:** *(Inline in execute_ssot)*
- **Method:** Direct AST manipulation within `execute_ssot.py`
- **Scope:** Fixes code quality issues detected by validator

---

### 7. Structure (Not Primary in execute_ssot)

**Validator:** `StructuralValidatorAgent`
- **File:** `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py`
- **Scope:** Structural integrity checks
- **Usage:** Referenced but not primary workflow in execute_ssot

**Healer:** `StructureHealerAgent`
- **File:** `agentic_core/L5_safety/reasoning/StructureHealerAgent.py`
- **Scope:** Structural repairs
- **Usage:** Referenced but not primary workflow in execute_ssot

---

## Healing Dispatch Pattern

### Remediation Dispatcher

Most healers are invoked via the **remediation dispatcher** pattern:

```python
from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

heal_result = _invoke_healer(
    check_id="hierarchy_violations",  # or "gravity_violations", etc.
    check_dict=validator_check_dict,
    repo_root=REPO_ROOT,
    apply=True
)
```

**Registered Healers:**
- `hierarchy_violations` → `HierarchyHealer`
- `gravity_violations` → `GravityLeakRepairAgent`
- `file_classification` → `FileClassificationHealer`
- `code_quality` → `CodeQualityHealer`

---

## Score-Based Routing System

Execute SSOT uses a **multi-gate score-based routing system** to determine healing tier:

### Score Calculation

```python
S = 3*C + 4*B + 3*A + 2*N + 4*F
```

**Factors:**
- **C** = Complexity (0-3)
- **B** = Blast radius (0-3)
- **A** = Autonomy risk (0-3)
- **N** = Novelty (0-3)
- **F** = Failure severity (0-3)
- **L** = Latency sensitivity (0-3, used in tie-breakers)

### Routing Tiers (Score Thresholds)

- `S <= 13` → **DETERMINISTIC** (local agent, no LLM)
- `14 <= S <= 26` → **QWEN** (Qwen2.5-14B-Instruct-AWQ via VLLM)
- `S > 26` → **GEMINI** (gemini-3-flash-preview)

### Sequential Gates (Override Score)

1. **GATE 0**: Replay mode → always DETERMINISTIC
2. **GATE 1**: Retry count >= 3 → GEMINI
3. **GATE 2**: Structural failures → DETERMINISTIC or GEMINI
4. **GATE 3**: Critical surface mechanical → DETERMINISTIC
5. **GATE 4**: Extreme risk (B=3, F=3) → GEMINI
6. **GATE 5**: Score thresholds (13, 26)
7. **GATE 6**: Latency tie-breaker (boundary zones)
8. **GATE 7**: Qwen-disallowed failures → GEMINI or DETERMINISTIC
9. **GATE 8**: Provider prohibition checks → FAIL_CLOSED

**Note:** Old confidence-based thresholds (0.75/0.40) exist in legacy code but are **not used** in current `execute_ssot.py` routing.

---

## Meta-Learning Integration

All healing actions are recorded for meta-learning:

```python
_record_healing_action(
    state_mgr,
    agent="LocationAgent",
    territory=territory,
    routing_tier="DETERMINISTIC",
    confidence=confidence.value,
    fix_summary=f"Healed {healed_count} violations",
    outcome="SUCCESS"
)
```

This feeds into:
- `HealingOutcomeAggregator` → aggregates healing outcomes
- `HealingOutcomeIntakeAdapter` → builds intake records
- `MetaLearningPipeline` → optimizes healing strategies

---

## Architecture Notes

### Validator Responsibilities (L5 Safety)
- **Detect** violations via AST/filesystem scans
- **Produce** check dictionaries with violation details
- **No mutation** - validators are read-only
- **Layer:** L5 (Safety)

### Healer Responsibilities (L2 Execution)
- **Consume** check dictionaries from validators
- **Apply** fixes via AST manipulation, file moves, refactoring
- **Record** outcomes for meta-learning
- **Layer:** L2 (Execution) or L5 (for structural healers)

### Separation Rationale
Per `agentic_process_mapping.md`:
- Prevents agents from having dual authority (detect + fix)
- Enforces **fail-closed** behavior (validator failure blocks healing)
- Enables **confidence-based routing** (validators assess, router decides)
- Supports **meta-learning** (healing outcomes feed back to improve detection)

---

## References

- **Source:** `agentic_core/L0_routing/scripts/execute_ssot.py`
- **Architecture:** `docs/technical/agentic_process_mapping.md`
- **Validators:** `agentic_core/L5_safety/reasoning/*ValidatorAgent.py`
- **Healers:** `agentic_core/L5_safety/reasoning/*HealerAgent.py` + `agentic_core/L2_execution/scripts/remediation_dispatcher.py`

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

