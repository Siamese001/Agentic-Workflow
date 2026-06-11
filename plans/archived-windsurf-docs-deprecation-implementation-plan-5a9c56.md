---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\deprecation-implementation-plan-5a9c56.md'
original_relative_path: 'deprecation-implementation-plan-5a9c56.md'
source_sha256: f52eb80797be0d185fd2061e1a2a9fedbad490d34ca9c152023be0cfe3c3bf45
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deprecation Implementation Plan

This plan implements the recommendations from the Agent Deprecation Analysis Report, focusing on converting remaining agents to facade patterns rather than deleting them, ensuring zero-loss compatibility throughout the process.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: StructureHealerAgent Facade Conversion (Priority: High)

**Objective:** Convert StructureHealerAgent to facade shell with StructureHealingStrategy, preserving its unique gravity/hierarchy/naming/territory healing capabilities.

**Key Activities:**
- Create StructureHealingStrategy class in UnifiedAgent
- Convert StructureHealerAgent to facade pattern
- Add comprehensive tests for the new facade
- Ensure compatibility with existing StructureHealerAgent consumers

**Files to Modify:**
- `agentic_core/base_agents/UnifiedAgent.py` (add StructureHealingStrategy)
- `agentic_core/L5_safety/policy_engine/StructureHealerAgent.py` (convert to facade)
- Create `tests/unit/agentic_core/L5_safety/test_structure_healer_facade.py`

**Success Criteria:**
- All existing StructureHealerAgent tests pass
- New facade tests pass (20+ tests)
- No breaking changes to existing imports
- Gravity/hierarchy/naming/territory healing preserved

## Phase 2: Validator Agent Consolidation (Priority: Medium)

**Objective:** Convert CodeValidatorAgent and StructuralValidatorAgent to facade shells with specialized validator strategies.

**Key Activities:**
- Create CodeValidatorStrategy and StructuralValidatorStrategy
- Convert both validator agents to facades
- Ensure LocationValidatorAgent remains standalone (complementary)
- Add comprehensive test coverage

**Files to Modify:**
- `agentic_core/base_agents/UnifiedAgent.py` (add validator strategies)
- `agentic_core/L5_safety/policy_engine/CodeValidatorAgent.py`
- `agentic_core/L5_safety/policy_engine/StructuralValidatorAgent.py`
- Create test files for both facades

**Success Criteria:**
- All validator functionality preserved
- Code validation and structural validation work independently
- LocationValidatorAgent continues to work as complementary validator
- 30+ new tests passing

## Phase 3: LocationHealerAgent Facade Conversion (Priority: Medium)

**Objective:** Convert LocationHealerAgent to facade with LocationHealingStrategy, preserving its file move/delete/import fixing capabilities.

**Key Activities:**
- Create LocationHealingStrategy in UnifiedAgent
- Convert LocationHealerAgent to facade (1482 lines → ~200 lines)
- Preserve ArchivalGatekeeper integration
- Maintain all healing strategies and safety protocols

**Files to Modify:**
- `agentic_core/base_agents/UnifiedAgent.py` (add LocationHealingStrategy)
- `agentic_core/L5_safety/validators/LocationHealerAgent.py`
- Create `tests/unit/agentic_core/L5_safety/test_location_healer_facade.py`

**Success Criteria:**
- All 25+ healing methods preserved via strategy delegation
- ArchivalGatekeeper integration maintained
- Import fixing after moves preserved
- 25+ new tests passing

## Phase 4: Migration Period Monitoring (Priority: Low)

**Objective:** Monitor usage patterns and ensure zero-loss migration over 90-day period.

**Key Activities:**
- Track import usage of all agents
- Monitor test results across all phases
- Collect performance metrics
- Document any consumer issues

**Files to Create:**
- `scripts/migration_monitor.py` (usage tracking script)
- `docs/reports/MIGRATION_PROGRESS_REPORT.md`

**Success Criteria:**
- Zero import errors in CI/CD
- All 300+ tests passing
- Performance benchmarks maintained
- No consumer complaints

## Phase 5: Final Consolidation Review (Priority: Low)

**Objective:** Evaluate actual usage and determine if any agents can be safely deprecated after migration period.

**Key Activities:**
- Analyze import patterns from Phase 4
- Run comprehensive test suite
- Evaluate production usage metrics
- Make final deprecation recommendations

**Files to Create:**
- `docs/reports/FINAL_CONSOLIDATION_REVIEW.md`

**Success Criteria:**
- Data-driven deprecation decisions
- All stakeholders aligned
- Risk assessment complete
- Rollback plan documented

## Implementation Dependencies

**Critical Path:**
1. Phase 1 must complete before Phase 2 (establishes pattern)
2. Phase 2 must complete before Phase 3 (validator patterns)
3. Phase 4 runs concurrently with other phases
4. Phase 5 depends on data from Phase 4

**Risk Mitigation:**
- Each phase includes comprehensive test coverage
- All changes preserve 100% backward compatibility
- Rollback plan for each phase
- Migration monitoring in Phase 4

## Testing Strategy

**Pre-Phase Tests:**
- Run existing test suite (220+ tests)
- Verify all imports work
- Performance baseline measurement

**Phase-Specific Tests:**
- 20+ tests per facade conversion
- Parity tests (old vs new behavior)
- Integration tests with dependent systems

**Post-Phase Tests:**
- Full regression test suite
- Import compatibility verification
- Performance benchmark validation

## Timeline Estimate

- **Phase 1:** 2- (StructureHealerAgent)
- **Phase 2:** 3- (Validator agents)
- **Phase 3:** 3- (LocationHealerAgent)
- **Phase 4:**  monitoring
- **Phase 5:** 2- (final review)

**Total Estimated:** 104- with 90-day monitoring period

## Success Metrics

**Technical Metrics:**
- 300+ tests passing
- Zero import errors
- <5% performance overhead
- 100% backward compatibility

**Business Metrics:**
- Zero consumer complaints
- All existing functionality preserved
- Improved maintainability
- Reduced code duplication

## Rollback Plan

Each phase includes rollback capability:
- Keep original agent files until phase complete
- Feature flags for new facade implementations
- Automated test validation before commit
- Git revert points for each phase

This plan ensures zero-loss agent consolidation while maintaining full backward compatibility and providing a clear path for future deprecation decisions based on actual usage data.

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

