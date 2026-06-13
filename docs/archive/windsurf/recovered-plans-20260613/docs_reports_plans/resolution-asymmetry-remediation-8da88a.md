# Resolution Asymmetry Remediation Phased Plan

This plan outlines a systematic approach to eliminate Resolution Asymmetry landmines across 27 agents with 79 total violations, using surgical AST-based healing to ensure zero-loss modifications.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 0: Infrastructure Preparation (Days 1-2)

### 0.1 Validate Surgical Infrastructure
- [ ] Verify SurgicalContext and SurgicalHealerMixin are properly installed
- [ ] Run baseline tests to ensure AST transformations work
- [ ] Create rollback mechanism for each agent batch

### 0.2 Create Migration Tools
- [ ] Build automated migration script for each agent type
- [ ] Create test harness to validate zero-loss diffs
- [ ] Set up monitoring dashboard for migration progress

### 0.3 Agent Prioritization Matrix
- **Critical Tier**: CodeHealerAgent (12 violations), CompositeGuardrailAgent (8)
- **High Tier**: ASTValidatorAgent (6), FilesystemSSOTReconcilerAgent (6), StructureHealerAgent (6)
- **Medium Tier**: Agents with 3-5 violations
- **Low Tier**: Agents with 1-2 violations

## Phase 1: Critical Tier Remediation (Days 3-5)

### 1.1 CodeHealerAgent Migration (12 violations)
**File**: `agentic_core/L5_safety/policy_engine/code_healer_agent.py`
- [ ] Analyze current string-based operations in heal_imports, heal_canon, heal_structural
- [ ] Create SurgicalContext builders for each detection method
- [ ] Implement AST-based transformations for import healing
- [ ] Implement AST-based transformations for canon compliance
- [ ] Implement AST-based transformations for structural fixes
- [ ] Run zero-loss validation tests
- [ ] Deploy with monitoring

### 1.2 CompositeGuardrailAgent Migration (8 violations)
**File**: `agentic_core/L5_safety/validators/composite_guardrail_agent_types.py`
- [ ] Update detection methods to return structured violation data
- [ ] Create SurgicalContext for guardrail violations
- [ ] Implement AST-based guardrail insertion/removal
- [ ] Validate guardrail logic preservation
- [ ] Deploy with monitoring

## Phase 2: High Tier Remediation (Days 6-10)

### 2.1 ASTValidatorAgent Migration (6 violations)
**File**: `agentic_core/L1_cognition/thought_engine/ast_validator_agent_validator.py`
- [ ] Map all validate_* methods to SurgicalContext
- [ ] Create AST fixers for bare except, empty except, eval/exec, dangerous builtins, debugger
- [ ] Ensure validate_all aggregates properly
- [ ] Test with various AST patterns

### 2.2 FilesystemSSOTReconcilerAgent Migration (6 violations)
**File**: `agentic_core/L5_safety/validators/FilesystemSSOTReconcilerAgent.py`
- [ ] Convert drift detection to structured output
- [ ] Create surgical file movement operations
- [ ] Preserve SSOT integrity during healing
- [ ] Validate zero-impact on non-target files

### 2.3 StructureHealerAgent Migration (6 violations)
- [ ] Identify specific file and location
- [ ] Analyze structural violations detected
- [ ] Implement AST-based structure modifications
- [ ] Ensure architectural compliance

## Phase 3: Medium Tier Remediation (Days 11-15)

### 3.1 Agents with 3-5 Violations
**Batch 1**: AgentCategory, ArchitectureGovernorAgent, AutonomyGuardianAgent
- [ ] Migrate AgentCategory detection/healing loop
- [ ] Update ArchitectureGovernorAgent pattern validation
- [ ] Replace string operations in AutonomyGuardianAgent

**Batch 2**: FileClassificationAgent, GovernanceAgent, HierarchyAgent
- [ ] Update FileClassificationAgent pattern detection
- [ ] Migrate GovernanceAgent validation logic
- [ ] Fix HierarchyAgent detection/healing mismatch

**Batch 3**: input_validation_guardrail_agent_config (4 violations)
- [ ] Convert validation logic to AST-based
- [ ] Preserve input validation rules
- [ ] Test with various input patterns

## Phase 4: Low Tier Remediation (Days 16-18)

### 4.1 Agents with 1-2 Violations Each
**List**: AgentPermission, AutonomousThreatEvolutionAgent, CheckpointManagerAgent, CodeDeduplicationAgent, CredentialScannerAgent, MCPGuardianAgent, NamingAgent, NervousSystemAgent, PineconeSovereignAgent, PreCommitSovereignAgent, ReportLocationAgent, RootHygieneAgent, SubAtomicRegistryAgent, SystemArchitectAgent, ValidationOrchestratorAgent

- [ ] Create generic migration template for simple violations
- [ ] Apply template to each agent
- [ ] Validate each migration individually
- [ ] Batch deploy with monitoring

## Phase 5: Integration & Validation (Days 19-20)

### 5.1 End-to-End Testing
- [ ] Run full test suite with all migrated agents
- [ ] Verify zero regressions in functionality
- [ ] Validate performance improvements
- [ ] Check for any remaining string-based operations

### 5.2 Documentation & Training
- [ ] Update agent development guidelines
- [ ] Create surgical healing best practices document
- [ ] Record training material for future agent development
- [ ] Update code review checklists

### 5.3 Monitoring & Handoff
- [ ] Deploy monitoring dashboard
- [ ] Create alerts for any regression to string-based healing
- [ ] Handoff to maintenance team
- [ ] Document lessons learned

## Success Criteria

### Technical Metrics
- [ ] 100% of 79 violations resolved
- [ ] Zero-loss diffs verified for all changes
- [ ] 100% test pass rate maintained
- [ ] No performance degradation

### Process Metrics
- [ ] All agents follow surgical healing pattern
- [ ] Detection methods return structured data
- [ ] Healing methods use SurgicalContext
- [ ] Zero information loss between detection and healing

### Quality Gates
Each phase must pass:
1. **Code Review**: All changes reviewed for surgical precision
2. **Test Validation**: 100% test pass with zero-loss verification
3. **Performance Check**: No regression in execution time
4. **Documentation**: Updated inline documentation for all changes

## Risk Mitigation

### Technical Risks
- **AST Parsing Errors**: Handle malformed AST gracefully
- **Complex Transformations**: Break down into smaller, testable steps
- **Performance Impact**: Monitor and optimize AST operations

### Process Risks
- **Rollback Plan**: Maintain git branches for each batch
- **Parallel Development**: Isolate changes to prevent conflicts
- **Knowledge Transfer**: Document all patterns and decisions

## Timeline Summary
- **Phase 0**:  (Infrastructure)
- **Phase 1**:  (Critical Tier)
- **Phase 2**:  (High Tier)
- **Phase 3**:  (Medium Tier)
- **Phase 4**:  (Low Tier)
- **Phase 5**:  (Integration)
- **Total**: 

This phased approach ensures systematic, safe elimination of all Resolution Asymmetry landmines while maintaining system stability and zero-loss code integrity.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

