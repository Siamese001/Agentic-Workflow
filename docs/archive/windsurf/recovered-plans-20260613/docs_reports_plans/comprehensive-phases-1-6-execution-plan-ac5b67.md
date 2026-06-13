# Comprehensive Phases 1-6 Execution Plan

This plan breaks down all remaining work across Phases 1-6 into smaller, testable phases that can be completed and committed one by one to ensure success.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Assessment

Based on the chat history and reports, here's what's been completed vs remaining:

### ✅ Already Complete
- **Phase 1-3 Testing Infrastructure:** All three pillars complete (Contract, Blueprint, Soul)
- **Phase 4 Assessment:** Complete assessment and planning (4A, 4B, 4C all documented)
- **Phase 5 Baseline:** Established with 14 passing tests
- **Phase 6 Analysis:** Import analysis and namespace validation work done
- **Audit Tool Fix:** Dataclass exclusion implemented (reduced false positives by 56%)

### 🔄 Remaining Work
- **Phase 1:** Nuclear audit tool namespace validation fix
- **Phase 2:** Broken import fixes (8 agents)
- **Phase 3:** Missing heal() method implementations (10 agents)
- **Phase 4:** Execute the assessment findings ( of fixes)
- **Phase 5:** Expand test coverage to 80%+ (major effort)
- **Phase 6:** Complete namespace validation and healing

## Execution Strategy

### Guiding Principles
1. **Small, Testable Increments:** Each phase should be completable in 1-
2. **Test-Driven:** Every phase must have passing tests before commit
3. **Atomic Commits:** Each phase committed separately with clear validation
4. **Risk Mitigation:** Start with highest impact, lowest risk fixes

### Phase Breakdown Strategy

## Phase 1: Nuclear Audit Tool Fixes (2 sub-phases)

### Phase 1A: Fix Namespace Validation Logic
**Duration:** 
**Risk:** LOW
**Impact:** HIGH (fixes false positives for all agents)

**Tasks:**
1. Update NuclearAuditAgent.py to use structure_blueprint.py as SSOT
2. Fix base agent location validation (agentic_core/base_agents/ is VALID)
3. Exclude Protocols and Mixins from agent detection
4. Fix self-reference detection for SovereignBaseAgent

**Tests:**
- Run nuclear audit (should show 0 namespace violations for base agents)
- Verify base agents in correct locations are marked VALID

**Commit:** "Phase 1A: Nuclear Audit Namespace Validation Fix"

### Phase 1B: Exclude False Positives
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Exclude Protocol classes (IOrchestratorAgent, ITieredAgent)
2. Exclude Mixin classes (AutonomyMixin)
3. Exclude self-references (SovereignBaseAgent)

**Tests:**
- Run nuclear audit (should reduce agent count by removing false positives)
- Verify only actual agents are analyzed

**Commit:** "Phase 1B: Nuclear Audit False Positive Exclusions"

## Phase 2: Broken Import Resolution (3 sub-phases)

### Phase 2A: Archive L0MaintenanceBaseAgent Stub
**Duration:** 
**Risk:** LOW
**Impact:** HIGH (unblocks 4 dependent agents)

**Tasks:**
1. Move L0MaintenanceBaseAgent.py to archives/
2. Update all agents inheriting from it to use SovereignBaseAgent
3. Add SubatomicTestingMixin where needed

**Affected Agents:**
- FilesystemSSOTReconcilerAgent
- GospelSyncAgent
- MetricsWitnessAgent
- BootstrapAgent

**Tests:**
- Run nuclear audit (should reduce broken imports by 4)
- Test each fixed agent can instantiate

**Commit:** "Phase 2A: Archive L0MaintenanceBaseAgent and Fix Dependencies"

### Phase 2B: Remove Duplicate Agents
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH (eliminates architectural confusion)

**Tasks:**
1. Remove duplicate BaseAgent definitions (tool_registry, workflow_engines)
2. Remove duplicate SubAtomicAgent (tool_registry)
3. Remove duplicate RootCustomsAgent (keep scripts version, archive logs version)
4. Update any imports pointing to duplicates

**Tests:**
- Run nuclear audit (should reduce agent count and eliminate duplicates)
- Verify canonical agents still work

**Commit:** "Phase 2B: Remove Duplicate Agent Definitions"

### Phase 2C: Fix Remaining Broken Imports
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Fix MockSovereignAgent inheritance + move to tests/
2. Fix DiscoveredAgent (dataclass, not agent - update audit tool)
3. Archive or fix BiasAuditorAgent (check if already archived)

**Tests:**
- Run nuclear audit (should show 0 broken imports)
- Test all fixed agents

**Commit:** "Phase 2C: Final Broken Import Fixes"

## Phase 3: Missing heal() Methods (2 sub-phases)

### Phase 3A: Implement heal() for Core Agents
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Implement heal() for SubAtomicAgent (L3_orchestration/fission_logic)
2. Implement heal() for StructuralEngineerAgent (investigate HealerMixin)
3. Implement heal() for SubatomicHopAgent, TerritoryChangeHandlerAgent

**Tests:**
- Test each heal() method with sample violation
- Run nuclear audit (should reduce signature mismatches)

**Commit:** "Phase 3A: Core Agent heal() Method Implementation"

### Phase 3B: Implement heal() for Utility Agents
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Implement heal() for TestGeneratorAgent, TokenBudgetInspectorAgent
2. Implement heal() for TypeHintFixerAgent, TypeMechanicAgent
3. Create heal() test suite for all implementations

**Tests:**
- Run nuclear audit (should show 0 signature mismatches)
- Full heal() method test suite

**Commit:** "Phase 3B: Utility Agent heal() Method Implementation"

## Phase 4: Execute Phase 4 Findings (3 sub-phases)

### Phase 4A: Fix High-Priority Agents
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Tasks:**
1. Fix ArchitectureGovernorAgent import issues
2. Fix FilesystemSSOTReconcilerAgent inheritance (from Phase 2A)
3. Fix GovernanceAgent MRO issues
4. Test all 7 high-priority agents

**Tests:**
- Run Phase 4A test suite (should pass 100%)
- Verify all high-priority agents functional

**Commit:** "Phase 4A: High-Priority Agent Fixes Complete"

### Phase 4B: Fix Medium-Priority Agents
**Duration:** 
**Risk:** MEDIUM
**Impact:** MEDIUM

**Tasks:**
1. Fix 8 broken import agents (from Phase 4B assessment)
2. Fix 7 signature mismatch agents (namespace issues)
3. Deduplicate where needed

**Tests:**
- Run nuclear audit (should show significant improvement)
- Test each fixed agent

**Commit:** "Phase 4B: Medium-Priority Agent Fixes Complete"

### Phase 4C: Execute Archival
**Duration:** 
**Risk:** LOW
**Impact:** LOW

**Tasks:**
1. Archive 7 confirmed low-priority agents
2. Create deprecation manifest
3. Update imports and agent discovery
4. Clean up any remaining false positives

**Tests:**
- Run nuclear audit (should show clean state)
- Verify no breakage from archival

**Commit:** "Phase 4C: Low-Priority Agent Archival Complete"

## Phase 5: Test Coverage Expansion (3 sub-phases)

### Phase 5A: Fix Test Infrastructure
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Tasks:**
1. Fix 679 test collection errors (from Phase 5 baseline)
2. Establish measurable baseline coverage
3. Create test templates for each agent type
4. Fix import issues in test files

**Tests:**
- Run pytest --collect-only (should collect all tests without errors)
- Establish baseline coverage report

**Commit:** "Phase 5A: Test Infrastructure Fixed"

### Phase 5B: Expand Core Coverage
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Tasks:**
1. Generate 50+ unit tests for core agents
2. Add 10+ integration tests for cross-layer workflows
3. Add 5+ e2e tests for full validation pipelines
4. Target 50%+ coverage

**Tests:**
- Run pytest with coverage (should show 50%+ coverage)
- All new tests passing

**Commit:** "Phase 5B: Core Test Coverage Expanded"

### Phase 5C: Achieve Target Coverage
**Duration:** 
**Risk:** MEDIUM
**Impact:** MEDIUM

**Tasks:**
1. Complete remaining tests for all 213 agents
2. Achieve 80%+ line coverage target
3. Ensure 100% agent coverage (all agents have tests)
4. Add heal() method test cases

**Tests:**
- Run pytest with coverage (should show 80%+ coverage)
- All 213 agents have test coverage

**Commit:** "Phase 5C: Target Test Coverage Achieved"

## Phase 6: Namespace Validation (2 sub-phases)

### Phase 6A: Complete Namespace Fixes
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Tasks:**
1. Complete remaining import fixes from Phase 6 analysis
2. Move misplaced agents to correct locations per structure_blueprint.py
3. Update all imports across codebase
4. Fix circular dependencies

**Tests:**
- Run nuclear audit (should show 0 namespace violations)
- All imports working correctly

**Commit:** "Phase 6A: Namespace Validation Complete"

### Phase 6B: Final Validation
**Duration:** 
**Risk:** LOW
**Impact:** HIGH

**Tasks:**
1. Re-run agent discovery to update manifest
2. Run full nuclear audit (should show clean state)
3. Run complete test suite (should pass 100%)
4. Generate final compliance report

**Tests:**
- Complete nuclear audit (0 broken imports, 0 signature mismatches, <10% stubs)
- Full test suite (80%+ coverage, 100% pass)
- Agent discovery updated

**Commit:** "Phase 6B: Final Validation Complete"

## Success Metrics

### Phase Completion Criteria
Each phase must meet these criteria before commit:
1. **All Tests Passing:** 100% pass rate for phase-specific tests
2. **Nuclear Audit Improvement:** Measurable reduction in issues
3. **No Regressions:** Previous functionality still works
4. **Documentation Updated:** Phase completion documented

### Overall Success Criteria
1. **Zero Broken Imports:** All agents inherit correctly
2. **Zero Signature Mismatches:** All agents have heal() methods
3. **<10% Stub Agents:** Only truly incomplete agents remain
4. **80%+ Test Coverage:** Comprehensive test suite
5. **100% Namespace Compliance:** All agents in correct locations

## Risk Mitigation

### High-Risk Areas
1. **Import Fixes:** May break existing functionality
2. **Agent Movement:** May break import chains
3. **Test Expansion:** May introduce flaky tests

### Mitigation Strategies
1. **Incremental Testing:** Test after each change
2. **Rollback Ready:** Keep commits atomic for easy rollback
3. **Baseline Protection:** Never break existing passing tests
4. **Documentation:** Document all changes for traceability

## Timeline Estimate

**Total Duration:** 18- across 6 phases
- Phase 1:  (Audit tool fixes)
- Phase 2:  (Broken imports)
- Phase 3:  (Missing heal() methods)
- Phase 4:  (Execute Phase 4 findings)
- Phase 5:  (Test coverage expansion)
- Phase 6:  (Namespace validation)

**Session Distribution:**
- Session 1: Phases 1-2 ()
- Session 2: Phase 3-4 ()
- Session 3: Phase 5-6 ()

## Next Steps

1. **Review Plan:** User confirms this comprehensive plan
2. **Start Phase 1A:** Begin with nuclear audit namespace validation fix
3. **Execute Sequentially:** Complete each phase, test, and commit
4. **Track Progress:** Update phase completion status as we go

This plan ensures success through small, testable increments with clear validation criteria at each step.

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

