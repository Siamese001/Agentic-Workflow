---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\MRO-Refactoring-Implementation-Plan-78a187.md'
original_relative_path: 'MRO-Refactoring-Implementation-Plan-78a187.md'
source_sha256: a58a49cac4d9402ae98e5c950594ae52a645d9971b90b5fec384b024a7c952ef
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MRO Refactoring Implementation Plan

This plan implements a phased approach to refactor the Agentic-Workflow's mixin inheritance architecture, reducing complexity from 72/100 to 85+ architectural health score while maintaining all existing functionality.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Critical Fixes (Week 1)

### 1.1 Remove Redundant Mixin Inheritance (Day 1-2)
**Target:** 5 agents with redundant `SubatomicTestingMixin`

**Sub-phase 1.1.1: Inventory and Backup**
- Create list of affected agents from audit report
- Generate backup of current inheritance patterns
- Run existing test suite to establish baseline

**Sub-phase 1.1.2: Refactor Agents**
- `HOP1ProfileAnalysisAgent`: Remove `SubatomicTestingMixin` from bases
- `HOP2ResearchAgent`: Remove `SubatomicTestingMixin` from bases
- `AppContentValidatorAgent`: Inherit from `SovereignBaseAgent` instead
- `GapClosureArchitectAgent`: Remove redundant mixin
- `HOPOrchestratorAgent`: Remove redundant mixin

**Sub-phase 1.1.3: Validation**
- Run full test suite
- Verify MRO depth reduced by 1 for each agent
- Confirm no functionality lost

### 1.2 Fix DispatchResumeToolsAgent Base Class (Day 3)
**Target:** Agent missing SovereignBaseAgent infrastructure

**Sub-phase 1.2.1: Analysis**
- Document current capabilities from `HealerMixin` and `MCPHardenedMixin`
- Identify missing core infrastructure (tracing, config, audit, etc.)

**Sub-phase 1.2.2: Migration**
- Change inheritance: `DispatchResumeToolsAgent(SovereignBaseAgent)`
- Remove direct mixin imports
- Update any method calls that relied on direct mixin access

**Sub-phase 1.2.3: Testing**
- Verify all existing functionality preserved
- Run integration tests specific to this agent
- Confirm new infrastructure capabilities available

### 1.3 Create Comprehensive Test Coverage (Day 4-5)
**Target:** Ensure refactoring safety

**Sub-phase 1.3.1: MRO Integrity Tests**
- Extend existing `test_mro_integrity.py` with new test cases
- Add tests for specific agents refactored
- Create regression tests for inheritance patterns

**Sub-phase 1.3.2: Functional Tests**
- Verify all mixin methods still accessible
- Test initialization order remains correct
- Confirm no method resolution conflicts

## Phase 2: Gateway Mixin Composition (Week 2-3)

### 2.1 Design Composition Architecture (Day 6-7)
**Target:** Replace inheritance mixins with dependency injection

**Sub-phase 2.1.1: Gateway Factory Design**
- Create `GatewayFactory` class for managing singletons
- Design lazy initialization pattern for gateways
- Define interface contracts for each gateway type

**Sub-phase 2.1.2: Migration Strategy**
- Map current mixin methods to gateway calls
- Design backward compatibility layer
- Plan deprecation timeline for mixin methods

### 2.2 Implement LLM Gateway Composition (Day 8-10)
**Target:** Replace `LLMProviderMixin` with composition

**Sub-phase 2.2.1: Create Gateway Class**
```python
class LLMGateway:
    def __init__(self):
        self._gateway = None

    async def generate(self, prompt, **kwargs):
        # Implementation from current mixin
```

**Sub-phase 2.2.2: Update SovereignBaseAgent**
- Add `self.llm = GatewayFactory.get_llm_gateway()` in `__post_init__`
- Keep mixin methods as delegation wrappers (marked deprecated)
- Update documentation to show new pattern

**Sub-phase 2.2.3: Migrate Agents**
- Search for direct `LLMProviderMixin` usage
- Replace with `self.llm.generate()` calls
- Run tests to verify functionality

### 2.3 Implement Embedding Gateway Composition (Day 11-12)
**Target:** Replace `EmbeddingMixin` with composition

**Sub-phase 2.3.1: Mirror LLM Gateway Pattern**
- Create `EmbeddingGateway` class
- Add to `GatewayFactory`
- Update `SovereignBaseAgent` initialization

**Sub-phase 2.3.2: Migration**
- Update direct mixin usage
- Maintain backward compatibility
- Test embedding operations

### 2.4 Implement Validator/Healing Composition (Day 13-14)
**Target:** Replace orchestrator mixins

**Sub-phase 2.4.1: Validator Gateway**
- Create `ValidatorGateway` wrapping `ValidatorOrchestrator`
- Update `ValidatorMixin` to delegate
- Migrate direct usage

**Sub-phase 2.4.2: Healing Gateway**
- Create `HealingGateway` wrapping `HealingSovereignOrchestrator`
- Update `HealingStrategyMixin` to delegate
- Migrate direct usage

### 2.5 Validation and Documentation (Day 15)
**Target:** Ensure migration success

- Run complete test suite
- Measure MRO depth reduction (target: -30%)
- Update developer documentation
- Create migration guide for future development

## Phase 3: PerformanceMixin Decomposition (Week 4)

### 3.1 Analyze PerformanceMixin Dependencies (Day 16)
**Target:** Understand coupling before splitting

**Sub-phase 3.1.1: Dependency Mapping**
- Identify which agents use which PerformanceMixin features
- Map method usage across codebase
- Document interdependencies between features

**Sub-phase 3.1.2: Design Split Strategy**
- `CachingMixin`: LRU cache, `cache_get/set/invalidate`, `@cached` decorator
- `MetricsMixin`: Performance metrics, `@timed` decorator, metrics collection
- `BatchingMixin`: Batch operations, queues, async pooling

### 3.2 Implement CachingMixin (Day 17-18)
**Target:** Extract caching functionality

**Sub-phase 3.2.1: Create New Mixin**
- Copy caching-related methods to `CachingMixin`
- Remove from `PerformanceMixin`
- Update imports and dependencies

**Sub-phase 3.2.2: Update Infrastructure**
- Add `CachingMixin` to `infrastructure_mixin` inheritance
- Update `SovereignBaseAgent` if needed
- Test caching functionality in isolation

### 3.3 Implement MetricsMixin (Day 19-20)
**Target:** Extract metrics functionality

**Sub-phase 3.3.1: Create New Mixin**
- Extract metrics collection and `@timed` decorator
- Create `MetricsMixin` with clean interface
- Remove from `PerformanceMixin`

**Sub-phase 3.3.2: Integration**
- Add to inheritance chain
- Update any direct references
- Verify metrics still collected correctly

### 3.4 Implement BatchingMixin (Day 21)
**Target:** Extract batch operations

**Sub-phase 3.4.1: Extract and Create**
- Move batch methods to `BatchingMixin`
- Update async pooling functionality
- Ensure thread safety maintained

**Sub-phase 3.4.2: Testing**
- Test batch operations
- Verify async pooling works
- Check performance characteristics

### 3.5 Cleanup and Validation (Day 22)
**Target:** Complete PerformanceMixin split

- Remove remaining `PerformanceMixin` if empty
- Update all documentation
- Run full performance benchmarks
- Verify no functionality lost

## Phase 4: Infrastructure Optimization (Week 5-6)

### 4.1 Analyze InfrastructureMixin Complexity (Day 23-24)
**Target:** Evaluate 10-mixin deep infrastructure

**Sub-phase 4.1.1: Usage Analysis**
- Which mixins are essential vs. optional
- Identify agents that don't need full infrastructure
- Measure performance impact of full chain

**Sub-phase 4.1.2: Design Simplified Base**
- Core mixins: CostGuardrail, ContextManagement, Tracing, AuditTrail
- Optional mixins: HITL, Performance (split), ToolReliability
- Gateway mixins: Already converted to composition

### 4.2 Create LightweightAgentBase (Day 25-27)
**Target:** Alternative base for simple agents

**Sub-phase 4.2.1: Implementation**
```python
class LightweightAgentBase(
    CostGuardrailMixin,
    ContextManagementMixin,
    TracingMixin,
    AuditTrailMixin,
):
    """Minimal base for agents needing core infrastructure only"""
```

**Sub-phase 4.2.2: Migration Candidates**
- Identify agents using < 50% of infrastructure
- Create migration path
- Test with sample agents

### 4.3 Optimize SovereignBaseAgent (Day 28-30)
**Target:** Streamline full-featured base

**Sub-phase 4.3.1: Remove Redundancies**
- Eliminate duplicate `SubatomicTestingMixin`
- Remove mixins now using composition
- Flatten where possible

**Sub-phase 4.3.2: Feature Flags**
- Add optional feature loading
- Allow agents to opt-in to heavy features
- Maintain backward compatibility

## Phase 5: Advanced Architecture (Week 7-8)

### 5.1 Design Trait System (Day 31-33)
**Target:** Future-proof extensibility

**Sub-phase 5.1.1: Trait Framework**
```python
class Trait:
    def apply(self, cls):
        # Modify class dynamically
        pass

def with_traits(*traits):
    def decorator(cls):
        for trait in traits:
            trait.apply(cls)
        return cls
    return decorator
```

**Sub-phase 5.1.2: Convert Key Mixins to Traits**
- CachingTrait
- MetricsTrait
- BatchingTrait
- HITLTrait

### 5.2 Implement Trait-based Examples (Day 34-35)
**Target:** Demonstrate new pattern

**Sub-phase 5.2.1: Sample Implementation**
```python
@with_traits(CachingTrait, MetricsTrait)
class OptimizedAgent(LightweightAgentBase):
    pass
```

**Sub-phase 5.2.2: Comparison**
- Performance comparison
- Code clarity analysis
- Developer experience evaluation

### 5.3 Documentation and Training (Day 36-40)
**Target:** Ensure adoption success

**Sub-phase 5.3.1: Documentation**
- Complete architecture guide
- Migration tutorials
- Best practices document

**Sub-phase 5.3.2: Developer Resources**
- Code examples for each pattern
- Decision tree for choosing base classes
- Performance benchmarks

## Phase 6: Final Validation (Week 9)

### 6.1 Comprehensive Testing (Day 41-43)
**Target:** Verify all objectives met

**Sub-phase 6.1.1: Functional Testing**
- All existing tests pass
- New functionality works correctly
- No regressions detected

**Sub-phase 6.1.2: Architecture Testing**
- MRO depth reduced by 30%+
- Extensibility score improved to 85+
- Performance maintained or improved

### 6.2 Performance Benchmarking (Day 44-45)
**Target:** Quantify improvements

- Agent instantiation time
- Method lookup performance
- Memory usage comparison
- Startup time analysis

### 6.3 Final Audit (Day 46)
**Target:** Generate completion report

- Re-run MRO audit tool
- Compare before/after metrics
- Document lessons learned
- Plan next improvements

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Architectural Health Score | 85+ | 72 |
| MRO Depth (max) | 14 | 20+ |
| Extensibility Score | 85+ | 65 |
| Test Coverage | 95%+ | TBD |
| Performance Impact | < 5% slower | 0% (negligible) |

## Risk Mitigation

1. **Backward Compatibility**: Maintain deprecated mixin methods during transition
2. **Incremental Deployment**: Each phase can be stopped if issues arise
3. **Rollback Strategy**: Git branches and automated tests for quick reversion
4. **Documentation**: Updated at each phase to prevent knowledge loss

## Dependencies

- Full test suite must pass before starting
- Team lead approval for each phase
- Stakeholder communication for breaking changes
- Code review process for all modifications

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

