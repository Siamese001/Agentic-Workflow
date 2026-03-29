# File Classification Agent Validation & Remediation Plan

**Status:** Analysis Complete | **Date:** 2026-03-29 | **Agent:** FileClassificationAgent.py

---

## Executive Summary

The `FileClassificationAgent.py` (284KB, ~6,000 lines) is the primary governance agent responsible for enforcing file classification and naming conventions. This analysis validates its alignment with `docs/reference/File Naming/Agent vs. Script.md` and identifies gaps, redundancies, and inconsistencies requiring remediation.

### Key Finding
The agent implements **20 distinct file types** (AGENT, SCRIPT, CLASS, MIXIN, UTILITY, PROTOCOL, ENGINE, ORCHESTRATOR, VALIDATOR, CONFIG, FACTORY, TYPES, STRATEGY, ADAPTER, EXCEPTION, SERVICE, GATEWAY, STUB, TEST, ENFORCER) while the specification defines a **binary Script vs. Agent** distinction. This scope creep creates overlapping classification rules and inconsistent enforcement.

---

## 1. GAP ANALYSIS: Implementation vs. Specification

### 1.1 AGENT Classification - PARTIAL ALIGNMENT

| Spec Requirement | Implementation Status | Gap |
|-----------------|----------------------|-----|
| Class with methods (PascalCase) | ✅ `*Agent.py` suffix detection | None |
| Reusable, imported across contexts | ✅ Inheritance from `*Agent` detection | None |
| Stateful (tracks items/violations/stats) | ⚠️ Score-based, not behavior-verified | Gap: No instance state validation |
| Encapsulated business logic | ✅ AST class detection | None |
| reasoning/ directory placement | ✅ Enforced | None |
| Iterative flow model | ⚠️ Batch processing only | Gap: No per-item iteration validation |
| Error behavior: detect→log→continue | ✅ Via `ClassificationResult` | None |

### 1.2 SCRIPT Classification - PARTIAL ALIGNMENT

| Spec Requirement | Implementation Status | Gap |
|-----------------|----------------------|-----|
| Procedural functions (snake_case) | ✅ Detection via `__main__` guard | None |
| One-shot, runs and exits | ✅ No-class file detection | None |
| Stateless across runs | ⚠️ Assumed, not verified | Gap: No state persistence check |
| ops_scripts/, tools/, scripts/ dirs | ✅ Enforced | None |
| Linear flow model | ⚠️ Single-pass classification | Gap: No sequence validation |
| `python script.py` invocation | ✅ `__main__` guard detection | None |
| CLI, CI/CD execution role | ⚠️ Folder-based, not role-based | Gap: No execution context analysis |

### 1.3 Critical Gaps Identified

#### Gap G1: EXECUTOR vs SCRIPT Overlap
- **Issue:** `Executor` classes (e.g., `InspectorExecutor.py`) classified as AGENT but share SCRIPT-like characteristics
- **Evidence:** Line 1060+ shows base_agents/ detection, but no executor-specific logic
- **Impact:** Files with executor naming may be misclassified

#### Gap G2: ORCHESTRATOR vs AGENT Boundary
- **Issue:** ORCHESTRATOR treated as distinct from AGENT, but spec says orchestrators are "specialized form of agent"
- **Evidence:** `is_agent_or_orchestrator()` exists but ORCHESTRATOR has separate type
- **Impact:** Dual classification path creates ambiguity

#### Gap G3: STRATEGY/ADAPTER/FACTORY as AGENT Subtypes
- **Issue:** Spec's binary model doesn't account for STRATEGY/ADAPTER/FACTORY as distinct types
- **Evidence:** Line 5486+ shows type-specific folder mappings
- **Impact:** Over-classification beyond spec's Script vs Agent distinction

#### Gap G4: No Determinism Verification
- **Issue:** Spec distinguishes deterministic vs adaptive agents; implementation doesn't verify
- **Evidence:** `classify_execution_mode()` exists in kernel but agent doesn't use it for classification
- **Impact:** Cannot enforce "deterministic by default" rule

#### Gap G5: Missing Reusability Validation
- **Issue:** Spec requires "imported by scripts, orchestrators, validators" for AGENT
- **Evidence:** No import analysis in classification scoring
- **Impact:** Files may be misclassified based on naming alone

---

## 2. REDUNDANCY ANALYSIS

### 2.1 File Type Overlap Matrix

```
                  AGENT  ORCH  STRAT  ADAPT  CLASS  MIXIN  UTIL  PROTO
AGENT (Pascal)     █     ▓     ▓      ▓      ░      ░      ░     ░
ORCHESTRATOR       ▓     █     ░      ░      ░      ░      ░     ░
STRATEGY           ▓     ░     █      ░      ▓      ░      ░     ░
ADAPTER            ▓     ░     ░      █      ▓      ░      ░     ░
CLASS              ░     ░     ▓      ▓      █      ░      ░     ▓
MIXIN              ░     ░     ░      ░      ░      █      ░     ░
UTILITY            ░     ░     ░      ░      ░      ░      █     ░
PROTOCOL           ░     ░     ░      ░      ▓      ░      ░     █
```

**Legend:** █ = Mutually exclusive | ▓ = Potential overlap | ░ = No overlap

### 2.2 Specific Redundancies

#### R1: STRATEGY vs AGENT (High Overlap)
- **Location:** Lines 3527-3547, 5076-5090
- **Issue:** STRATEGY scored via `primary_name.endswith("Strategy")` but also inherits AGENT detection
- **Redundancy:** STRATEGY could be AGENT subtype; separate type creates dual-path classification

#### R2: ADAPTER vs CLASS (Medium Overlap)
- **Location:** Lines 459-461, 519-521
- **Issue:** ADAPTER detection checks `endswith("Adapter", "Wrapper", "Bridge")` but CLASS detection also catches these
- **Redundancy:** ADAPTER could be CLASS subtype

#### R3: Multiple Config Types
- **Location:** Lines 533-562
- **Issue:** CONFIG, CONFIG_WITH_LOGIC as distinct types
- **Redundancy:** CONFIG_WITH_LOGIC is a violation state, not a file type

#### R4: Duplicate Folder Mappings
- **Location:** Lines 5068-5078, 5834-5835
- **Issue:** Same type mapped to multiple folders in different code paths
- **Redundancy:** Folder-to-type logic scattered across methods

---

## 3. INCONSISTENCY ANALYSIS

### 3.1 Classification Priority Inconsistencies

#### I1: Priority 9 (ORCHESTRATOR) vs Priority 10 (AGENT)
- **Issue:** ORCHESTRATOR checked before AGENT, but spec says orchestrators are agents
- **Location:** Lines 499-505
- **Impact:** Files named `*OrchestratorAgent.py` may misclassify

#### I2: EXCEPTION Priority (6) Before MIXIN (7)
- **Issue:** Exception classes detected before Mixins, but both are structural types
- **Location:** Lines 487-493
- **Impact:** `*MixinError.py` would classify as EXCEPTION, not MIXIN

#### I3: ROUTER as ENGINE (11.7) vs AGENT Detection
- **Issue:** `_router.py` suffix forces ENGINE, bypassing AGENT detection
- **Location:** Lines 430-432
- **Impact:** Router agents misclassified as ENGINE

### 3.2 Enforcement Inconsistencies

#### I4: Apps Naming Inconsistency
- **Location:** Lines 5834-5845 (apps-aware hardening)
- **Issue:** Apps files "immune" to suffix stripping, but core files are not
- **Evidence:** `is_app = any(p.startswith("apps_") for p in path.parts)`
- **Impact:** Divergent naming rules between core and apps

#### I5: ENFORCEMENT Immunity for AGENT
- **Location:** Lines 5336-5337
- **Issue:** `if "enforcement" in path.parts and file_type == "AGENT": return None`
- **Impact:** AGENT files allowed in enforcement/, contrary to spec's reasoning/ rule

#### I6: Base Agent Naming Exception
- **Location:** Lines 1080-1095
- **Issue:** `SovereignBaseAgent` explicitly exempted from `Base` suffix rule
- **Impact:** Special-case handling breaks uniform rules

### 3.3 Scoring Inconsistencies

#### I7: Asymmetric Score Values
- **AGENT:** +20 for class name, +20 for inheritance (Line 3542-3547)
- **SCRIPT:** No score-based detection; only `__main__` guard (Lines 384-396)
- **Issue:** AGENT has weighted scoring; SCRIPT has binary detection

#### I8: Missing SCRIPT Score in Classification
- **Location:** `_classify()` method
- **Issue:** No `scores["SCRIPT"]` initialization or increment
- **Impact:** SCRIPT classification entirely separate from scoring system

---

## 4. DETAILED WAVE-BASED REMEDIATION PLAN

### Wave 1: Documentation & Test Baseline (Est. 8K tokens)

**Objective:** Establish e2e test coverage and document current behavior

#### Tasks:
1. **Create comprehensive e2e test suite** (Est. 4K tokens)
   - Test AGENT classification on all `*Agent.py` files in reasoning/
   - Test SCRIPT classification on all files in ops_scripts/, tools/
   - Test boundary cases (Executor, Orchestrator, Strategy files)
   - Test classification confidence scores

2. **Document current classification behavior** (Est. 2K tokens)
   - Generate classification report for all repo files
   - Identify files with ambiguous classifications
   - Document edge cases and special handling

3. **Create specification alignment matrix** (Est. 2K tokens)
   - Map each implemented rule to spec requirement
   - Mark gaps, redundancies, inconsistencies
   - Prioritize fixes by severity

**Deliverable:** `docs/reports/plans/file-classification-gap-inventory.md`

---

### Wave 2: Remove Redundancies - Type Consolidation (Est. 12K tokens)

**Objective:** Eliminate overlapping file types per spec's binary model

#### Tasks:
1. **Consolidate ORCHESTRATOR into AGENT** (Est. 3K tokens)
   - Remove ORCHESTRATOR as distinct type
   - Treat `*Orchestrator*.py` as AGENT subtype
   - Update folder mappings: ORCHESTRATOR → reasoning/

2. **Consolidate STRATEGY into AGENT** (Est. 3K tokens)
   - Remove STRATEGY as distinct type
   - Treat `*Strategy.py` as AGENT subtype
   - Update validation logic

3. **Consolidate ADAPTER into CLASS** (Est. 2K tokens)
   - Remove ADAPTER as distinct type
   - Treat `*Adapter.py` as CLASS subtype
   - Preserve folder routing (reasoning/ for adapters)

4. **Remove CONFIG_WITH_LOGIC type** (Est. 2K tokens)
   - Treat as violation of CONFIG, not a type
   - Update violation detection logic

5. **Consolidate ENFORCER/FACTORY/GATEWAY** (Est. 2K tokens)
   - Map to appropriate parent types
   - Document rationale for each

**Deliverable:** `docs/reports/plans/type-consolidation-rationale.md`

---

### Wave 3: Fix Inconsistencies - Priority Reordering (Est. 10K tokens)

**Objective:** Align classification priorities with spec's decision tree

#### Tasks:
1. **Implement Spec Decision Tree** (Est. 4K tokens)
   ```
   [START: NEW COMPONENT]
              │
              ▼
   1. REUSABILITY: Will other modules ─────────── YES ───────────┐
      import and reuse this logic?                               │
              │                                                │
             NO                                                │
              │                                                │
              ▼                                                │
   2. STATE: Does it need instance ────────────── YES ───────────┤
      state across many items?                                   │
              │                                                │
             NO                                                │
              │                                                │
              ▼                                                │
   3. LOGIC: Is it enforcing rules ────────────── YES ───────────┤
      rather than just sequencing?                               │
              │                                                ▼
             NO                                       ┏━━━━━━━━━━━━━━━━━━━┓
              │                                       ┃    AGENT CLASS    ┃
              ▼                                       ┗━━━━━━━━━━━━━━━━━━━┛
     ┏━━━━━━━━━━━━━━━━━━┓
     ┃      SCRIPT      ┃
     ┗━━━━━━━━━━━━━━━━━━┛
   ```

2. **Reorder Classification Priority** (Est. 3K tokens)
   - P0: IGNORE (critical infrastructure)
   - P1: TEST (test files)
   - P2: SCRIPT (no-class + __main__ guard)
   - P3: AGENT (class *Agent or inherits *Agent)
   - P4: CLASS (other classes)
   - P5: UTILITY (no-class, no __main__)

3. **Fix Apps/Core Naming Uniformity** (Est. 3K tokens)
   - Remove `is_app` special casing
   - Apply consistent rules across all territories

**Deliverable:** `docs/reports/plans/priority-reordering-spec.md`

---

### Wave 4: Close Gaps - Missing Validations (Est. 15K tokens)

**Objective:** Implement spec requirements not currently enforced

#### Tasks:
1. **Add Reusability Validation** (Est. 4K tokens)
   - Analyze imports to detect if file is imported elsewhere
   - Score boost for widely-imported files
   - Score penalty for standalone files

2. **Add Statefulness Detection** (Est. 4K tokens)
   - AST analysis for instance variables
   - Detect `self.*` assignments in methods
   - Score based on state complexity

3. **Add Determinism Detection** (Est. 3K tokens)
   - Integrate `classify_execution_mode()` from kernel
   - Flag files with non-deterministic patterns
   - Tag as REASONING or DETERMINISTIC

4. **Add Invocation Context Analysis** (Est. 4K tokens)
   - Detect CLI entrypoints vs library imports
   - Score based on `if __name__ == "__main__"` complexity
   - Validate against spec's invocation model

**Deliverable:** `docs/reports/plans/gap-closure-validation.md`

---

### Wave 5: E2E Testing & Validation (Est. 10K tokens)

**Objective:** Verify all changes with comprehensive test coverage

#### Tasks:
1. **Build E2E Test Harness** (Est. 4K tokens)
   - Classify all files in repo
   - Compare against expected classification
   - Generate diff report

2. **Run Classification Sweep** (Est. 2K tokens)
   - Execute on full codebase
   - Collect statistics per file type
   - Identify outliers

3. **Validate Enforcement Rules** (Est. 2K tokens)
   - Test AGENT suffix → reasoning/ enforcement
   - Test SCRIPT purity in scripts/
   - Test folder-type alignment

4. **Performance Benchmark** (Est. 2K tokens)
   - Measure classification time per file
   - Verify no regression in scan speed
   - Document performance characteristics

**Deliverable:** `docs/reports/plans/e2e-validation-report.md`

---

## 5. TOKEN ESTIMATE SUMMARY

| Wave | Description | Est. Tokens | Cumulative |
|------|-------------|-------------|------------|
| 1 | Documentation & Test Baseline | 8K | 8K |
| 2 | Remove Redundancies | 12K | 20K |
| 3 | Fix Inconsistencies | 10K | 30K |
| 4 | Close Gaps | 15K | 45K |
| 5 | E2E Testing | 10K | 55K |
| **Total** | | **55K** | **55K** |

---

## 6. E2E TEST SPECIFICATION

### Test Suite Structure

```
tests/unit/agentic_core/L5_safety/reasoning/test_FileClassificationAgent_e2e/
├── test_agent_classification.py      # AGENT type validation
├── test_script_classification.py     # SCRIPT type validation
├── test_boundary_cases.py            # Executor, Orchestrator, Strategy
├── test_folder_enforcement.py        # Location validation
├── test_naming_conventions.py        # get_compliant_name tests
├── test_spec_compliance.py           # Full spec alignment tests
└── conftest.py                       # Shared fixtures
```

### Key Test Cases

#### TC-AGENT-01: PascalCase Agent Detection
```python
def test_agent_pascal_case_detection(agent):
    """AGENT: Files with *Agent.py suffix in reasoning/"""
    result = agent.classify_file(Path("reasoning/FileClassificationAgent.py"))
    assert result == "AGENT"
    assert agent.get_compliant_name(Path("reasoning/FileClassificationAgent.py"), result) is None
```

#### TC-SCRIPT-01: __main__ Guard Detection
```python
def test_script_main_guard_detection(agent):
    """SCRIPT: Files with __main__ guard in ops_scripts/"""
    result = agent.classify_file(Path("ops_scripts/ci/agent_validation.py"))
    assert result == "SCRIPT"
```

#### TC-SPEC-01: Decision Tree Compliance
```python
def test_spec_decision_tree(agent):
    """Verify classification follows spec's 3-question decision tree"""
    # Files with imports from multiple modules → AGENT
    # Files with instance state → AGENT
    # Files with rule enforcement → AGENT
    # Otherwise → SCRIPT
```

---

## 7. RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing classifications | High | High | Wave 1 baseline + dry-run mode |
| Performance regression | Medium | Medium | Benchmark in Wave 5 |
| Apps naming divergence | Medium | Medium | Remove is_app special case |
| Test coverage gaps | Low | High | Comprehensive e2e suite |

---

## 8. ACCEPTANCE CRITERIA

- [ ] All 20 file types consolidated to binary AGENT/SCRIPT model per spec
- [ ] Classification priorities match spec's decision tree
- [ ] E2E test suite achieves 90%+ code coverage
- [ ] No breaking changes to existing file classifications (verified by diff)
- [ ] Performance within 10% of baseline
- [ ] Documentation updated with new classification rules

---

## APPENDIX A: Current Classification Scoring

### AGENT Scoring (Lines 3527-3547)
```python
scores = {
    "AGENT": 0,
    "ORCHESTRATOR": 0,
    "CLASS": 0,
    # ... other types
}

# AGENT scoring
if is_agent:
    scores["AGENT"] += 20  # Class name ends with Agent
    if is_reasoning:
        scores["AGENT"] += 20  # Has reasoning signals
    if inherits_from_agent:
        scores["AGENT"] += 20  # Inherits from *Agent
```

### Missing: SCRIPT Scoring
```python
# SCRIPT has NO scoring - only binary detection:
# - No classes + has __main__ guard → SCRIPT
# - No classes + in scripts/ folder → SCRIPT
```

### Gap: Asymmetric scoring system favors AGENT detection

---

## APPENDIX B: File Type to Folder Mapping

| File Type | Current Folders | Spec-Compliant Folder |
|-----------|-----------------|----------------------|
| AGENT | reasoning/, enforcement/ (exempt) | reasoning/ |
| SCRIPT | ops_scripts/, tools/, scripts/, L0_routing/scripts/ | ops_scripts/, tools/, scripts/ |
| CLASS | reasoning/, base_agents/ | reasoning/ |
| MIXIN | mixins/, base_agents/ | mixins/ |
| UTILITY | utils/ | utils/ |
| PROTOCOL | types/, L3_orchestration/types/ | types/ |
| ENGINE | engines/ | engines/ |
| ORCHESTRATOR | reasoning/ | reasoning/ (consolidate to AGENT) |
| VALIDATOR | validators/ | validators/ |

---

*End of Plan*
