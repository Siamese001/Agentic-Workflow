# Remaining Scope Breakdown - Phases 2C-6

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State
- **Total Progress:** Phases 1-2B Complete (57% reduction in broken imports)
- **Remaining Issues:** 3 broken imports, 64 signature mismatches
- **Agents Analyzed:** 67 (cleaned up from 71)

## Phase 2C: Final Broken Import Fixes (3 sub-phases)

### Phase 2C.1: Fix FilesystemSSOTReconcilerAgent
**Duration:** 
**Risk:** LOW
**Impact:** HIGH

**Issue:** Agent inherits from L0MaintenanceBaseAgent → SovereignBaseAgent, but audit doesn't recognize indirect inheritance

**Tasks:**
1. Verify L0MaintenanceBaseAgent properly inherits from SovereignBaseAgent
2. Check if audit tool needs fix for indirect inheritance detection
3. If needed, add direct SovereignBaseAgent inheritance

**Test:** Run nuclear audit (should reduce to 2 broken imports)

### Phase 2C.2: Move MockSovereignAgent to Tests
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Issue:** MockSovereignAgent is in production code but should be in tests/

**Tasks:**
1. Move MockSovereignAgent.py to tests/ directory
2. Update any imports if needed
3. Verify it's excluded from production audit

**Test:** Run nuclear audit (should reduce to 1 broken import)

### Phase 2C.3: Handle BiasAuditorAgent
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Issue:** BiasAuditorAgent in runtime/shared_runtime (invalid namespace)

**Tasks:**
1. Check if BiasAuditorAgent is already archived
2. If active, move to correct location or archive
3. Update imports if needed

**Test:** Run nuclear audit (should achieve 0 broken imports)

## Phase 3: Missing heal() Methods (4 sub-phases)

### Phase 3.1: Core Agent heal() Implementation
**Duration:** 
**Risk:** LOW
**Impact:** HIGH

**Target Agents:** 10 high-priority agents missing heal()
1. MetaLearningAgent
2. HistorianAgent
3. RgStrategicPlannerAgent
4. ToolsmithAgent
5. ValidationOrchestratorAgent
6. OrchestratorAgent
7. SubAtomicAgent (fission_logic)
8. DAGMutatorAgent
9. DagEngineAgent
10. DagRuntimeInspectorAgent

**Tasks:**
1. Implement heal() method for each agent
2. Follow standard heal() signature pattern
3. Add appropriate violation handling logic

**Test:** Run nuclear audit (should reduce signature mismatches)

### Phase 3.2: L5 Safety Agents heal() Implementation
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Target Agents:** 8 L5 safety agents
1. GravityStateAgent
2. GravityLeakRepairAgent
3. AdversarialRedTeamerAgent
4. ConstitutionalReviewerAgent
5. MetaLearningAgent (duplicate - verify)
6. And 3 others from audit list

**Tasks:**
1. Implement heal() methods with safety-specific logic
2. Ensure proper error handling
3. Add logging for healing actions

**Test:** Run nuclear audit (continue reducing signature mismatches)

### Phase 3.3: Workflow Engine Agents heal() Implementation
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Target Agents:** 15 workflow engine agents
1. DomainPlannerAgent
2. FeasibilityAnalystAgent
3. FissionManagerAgent
4. OrchestrationHandshakeAgent
5. RiskAssessorAgent
6. StrategyCoordinatorAgent
7. StrategyScenarioSimulatorAgent
8. And 8 others

**Tasks:**
1. Implement heal() methods with workflow-specific logic
2. Handle workflow state healing
3. Add rollback capabilities where appropriate

**Test:** Run nuclear audit (significant reduction in signature mismatches)

### Phase 3.4: Remaining Agents heal() Implementation
**Duration:** 
**Risk:** LOW
**Impact:** LOW

**Target Agents:** All remaining agents with signature mismatches

**Tasks:**
1. Complete heal() implementation for remaining agents
2. Ensure consistent error handling
3. Add comprehensive logging

**Test:** Run nuclear audit (should achieve 0 signature mismatches)

## Phase 4: Namespace Validation (2 sub-phases)

### Phase 4.1: Fix Namespace Violations
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Target:** All agents with [INVALID] namespace

**Tasks:**
1. Identify agents in wrong directories per structure_blueprint.py
2. Move agents to correct locations
3. Update all import statements
4. Handle circular dependencies

**Test:** Run nuclear audit (should show 0 namespace violations)

### Phase 4.2: Validate Namespace Rules
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Verify all agents follow namespace rules
2. Check base agents are in agentic_core/base_agents/
3. Validate subfolder depth compliance
4. Run full namespace validation

**Test:** Complete nuclear audit with 100% namespace compliance

## Phase 5: Test Coverage Expansion (3 sub-phases)

### Phase 5.1: Fix Test Infrastructure
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Issues:** 679 test collection errors

**Tasks:**
1. Fix import errors in test files
2. Resolve missing dependencies
3. Fix test configuration issues
4. Establish working baseline

**Test:** `pytest --collect-only` should collect all tests

### Phase 5.2: Core Agent Test Coverage
**Duration:** 
**Risk:** MEDIUM
**Impact:** HIGH

**Target:** 50+ core agents

**Tasks:**
1. Create unit tests for high-priority agents
2. Test heal() method implementations
3. Add integration tests for key workflows
4. Target 50% coverage

**Test:** `pytest --cov` should show 50%+ coverage

### Phase 5.3: Complete Test Coverage
**Duration:** 
**Risk:** MEDIUM
**Impact:** MEDIUM

**Target:** All 67 agents

**Tasks:**
1. Complete unit tests for remaining agents
2. Add e2e tests for critical paths
3. Achieve 80%+ line coverage
4. Ensure 100% agent coverage

**Test:** Full test suite with 80%+ coverage, 100% pass

## Phase 6: Final Validation (2 sub-phases)

### Phase 6.1: Complete Audit Validation
**Duration:** 
**Risk:** LOW
**Impact:** HIGH

**Tasks:**
1. Run complete nuclear audit
2. Verify 0 broken imports
3. Verify 0 signature mismatches
4. Verify <10% stub agents
5. Generate final compliance report

**Test:** Perfect audit results

### Phase 6.2: Integration Testing
**Duration:** 
**Risk:** LOW
**Impact:** MEDIUM

**Tasks:**
1. Run full test suite
2. Verify all phases work together
3. Check for regressions
4. Validate performance impact

**Test:** All tests pass, no regressions

## Success Metrics

### Phase Completion Criteria
Each phase must meet:
1. **100% Test Pass:** All phase-specific tests pass
2. **Measurable Improvement:** Audit shows clear progress
3. **No Regressions:** Previous functionality intact
4. **Clean Commit:** Atomic, well-documented commit

### Overall Success Targets
- **0 Broken Imports:** All agents inherit correctly
- **0 Signature Mismatches:** All agents have heal() methods
- **<10% Stub Agents:** Only truly incomplete agents remain
- **80%+ Test Coverage:** Comprehensive test suite
- **100% Namespace Compliance:** All agents in correct locations

## Timeline Estimate

**Total Remaining Duration:** 14-
- Phase 2C:  (final import fixes)
- Phase 3:  (heal() methods)
- Phase 4:  (namespace validation)
- Phase 5:  (test coverage)
- Phase 6:  (final validation)

**Session Distribution:**
- Session 1: Phases 2C-3 ()
- Session 2: Phase 4-5.1 ()
- Session 3: Phase 5.2-6 ()

## Next Steps

1. **Start Phase 2C.1:** Fix FilesystemSSOTReconcilerAgent inheritance issue
2. **Execute Sequentially:** Complete each sub-phase, test, and commit
3. **Track Progress:** Update completion status after each phase
4. **Validate Continuously:** Run audit after each change to verify improvement

This breakdown ensures success through small, testable increments with clear validation criteria at each step.

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

