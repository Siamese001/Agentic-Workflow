# Unified Pre-Write Enforcement Framework

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

This document proposes a unified enforcement framework for Windsurf's pre-write validation hooks that addresses the critical gaps identified in the gap analysis. The framework consolidates redundant skills, implements missing validations, and provides a cohesive orchestration layer.

## Framework Architecture

### Core Components

#### 1. Pre-Write Orchestrator
```
.windsurf/skills/pre-write-orchestrator/
├── main.py                 # Main orchestration logic
├── skill_registry.py       # Skill discovery and registration
├── dependency_resolver.py  # Skill dependency management
├── execution_engine.py     # Parallel skill execution
├── error_handler.py        # Error aggregation and reporting
└── status_dashboard.py     # Real-time status monitoring
```

#### 2. Critical Gap Skills
```
.windsurf/skills/
├── powershell-guard/       # §2 enforcement
├── repair-gate-validator/  # §4 enforcement  
├── agent-deletion-guard/   # §5 enforcement
├── hitl-decision-validator/ # §8 enforcement
└── guardian-exemption-validator/ # §10 enforcement
```

#### 3. Consolidated Core Skills (Existing)
```
.windsurf/skills/
├── artifact-management/    # Evidence, paths, progress
├── boundary-enforcement/   # Layers, imports, shims
├── graph-analysis/         # ADG, scope, dedup
├── operational-gates/       # Rollback, MCP validation
└── testing-framework/      # Test quality, integrity
```

## Skill Implementation Details

### 1. PowerShell Guard (§2)
```python
# .windsurf/skills/powershell-guard/skill.md
---
name: powershell-guard
description: Prevents PowerShell command execution before any shell operation. Validates all subprocess calls to ensure shell=False and no PowerShell-specific syntax.
enforcement_layer: pre-write
enforcement_timing: before_work
enforcement_type: behavioural
---

# PowerShell Guard Skill

## Files
- `powershell_detection.py` - Detects PowerShell commands and syntax
- `subprocess_validator.py` - Validates subprocess.run calls
- `forbidden_patterns.md` - List of PowerShell-specific patterns

## When to use
- Before any shell command execution
- When subprocess.run is called
- When evaluating command strings for execution

## Validation Protocol
1. Check for shell=True in subprocess calls
2. Detect PowerShell-specific syntax (cmdlets, pipelines, etc.)
3. Validate command strings against forbidden patterns
4. Block execution if PowerShell detected
```

### 2. Repair Gate Validator (§4)
```python
# .windsurf/skills/repair-gate-validator/skill.md
---
name: repair-gate-validator
description: Validates all five repair gates pass before any file edit. Ensures constitutional compliance before modifications.
enforcement_layer: pre-write
enforcement_timing: before_work
enforcement_type: structural
---

# Repair Gate Validator Skill

## Files
- `gate_checker.py` - Validates each of the 5 repair gates
- `gate_status.py` - Tracks gate status across session
- `gate_dependencies.py` - Maps gate dependencies

## Five Repair Gates
1. **ADG Freshness** - Verify ADG cache is current
2. **Dependency Graph** - Build/query AST dependency graph  
3. **Scope Validation** - Justify edit scope with graph
4. **Test Coverage** - Verify tests exist for changes
5. **Boundary Check** - Validate layer boundaries

## Validation Protocol
1. Check status of all 5 gates
2. Fail-fast if any gate not passed
3. Document gate status in evidence
4. Block edits until all gates pass
```

### 3. Agent Deletion Guard (§5)
```python
# .windsurf/skills/agent-deletion-guard/skill.md
---
name: agent-deletion-guard
description: Prevents unauthorized deletion of *Agent.py files. Requires AGENT-DELETION-AUTHORIZED marker and justification.
enforcement_layer: pre-write
enforcement_timing: before_work
enforcement_type: structural
---

# Agent Deletion Guard Skill

## Files
- `agent_detector.py` - Identifies *Agent.py files
- `authorization_checker.py` - Validates deletion authorization
- `deprecation_tracker.py` - Tracks 90-day deprecation period

## Authorization Requirements
- AGENT-DELETION-AUTHORIZED commit marker
- Specific justification for deletion
- Replacement agent specified
- 90-day deprecation period
- Zero active references

## Validation Protocol
1. Detect *Agent.py file deletion attempts
2. Check for authorization marker
3. Validate all requirements met
4. Block deletion if unauthorized
```

### 4. HITL Decision Validator (§8)
```python
# .windsurf/skills/hitl-decision-validator/skill.md
---
name: hitl-decision-validator
description: Ensures Human-in-the-Loop discipline for multi-option decisions. Validates HITL presentation and user choice documentation.
enforcement_layer: pre-write
enforcement_timing: during_work
enforcement_type: behavioural
---

# HITL Decision Validator Skill

## Files
- `decision_detector.py` - Identifies multi-option decision points
- `hitl_validator.py` - Validates HITL process
- `choice_tracker.py` - Tracks user choices and rationale

## HITL Requirements
- Present 2-4 concrete options with trade-offs
- Wait for explicit user selection (A/B/C/D)
- Document user choice and reasoning
- No assumption of defaults or "best" options

## Validation Protocol
1. Detect decision points requiring HITL
2. Validate options were presented
3. Confirm user choice documented
4. Block action without HITL completion
```

### 5. Guardian Exemption Validator (§10)
```python
# .windsurf/skills/guardian-exemption-validator/skill.md
---
name: guardian-exemption-validator
description: Validates guardian exemption comments have specific justifications. Prevents generic exemptions that bypass anti-patterns.
enforcement_layer: pre-write
enforcement_timing: before_work
enforcement_type: structural
---

# Guardian Exemption Validator Skill

## Files
- `exemption_detector.py` - Finds # guardian: allow-* comments
- `justification_validator.py` - Validates justification format
- `exemption_registry.py` - Tracks all exemptions

## Justification Requirements
- Format: `# guardian: allow-<type> -- <specific justification>`
- Forbidden words: "needed", "required", "temporary", "legacy"
- Must reference specific anti-pattern being bypassed
- Must explain why alternative approaches fail

## Validation Protocol
1. Detect guardian exemption comments
2. Validate justification format
3. Check for forbidden generic words
4. Require HITL approval for new exemptions
5. Block invalid exemptions
```

## Pre-Write Orchestrator Implementation

### Main Orchestration Logic
```python
# .windsurf/skills/pre-write-orchestrator/main.py
class PreWriteOrchestrator:
    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.dependency_resolver = DependencyResolver()
        self.execution_engine = ExecutionEngine()
        self.error_handler = ErrorHandler()
    
    def validate_pre_write(self, context: ValidationContext) -> ValidationResult:
        """Execute all relevant pre-write validations"""
        # 1. Determine relevant skills based on context
        relevant_skills = self.skill_registry.get_relevant_skills(context)
        
        # 2. Resolve skill dependencies
        execution_order = self.dependency_resolver.resolve(relevant_skills)
        
        # 3. Execute skills in parallel where possible
        results = self.execution_engine.execute_parallel(execution_order, context)
        
        # 4. Aggregate results and handle errors
        return self.error_handler.aggregate_results(results)
```

### Skill Registry
```python
# .windsurf/skills/pre-write-orchestrator/skill_registry.py
class SkillRegistry:
    def __init__(self):
        self.skills = self._discover_skills()
        self.rule_mappings = self._build_rule_mappings()
    
    def get_relevant_skills(self, context: ValidationContext) -> List[Skill]:
        """Return skills relevant to the current validation context"""
        relevant = []
        for skill in self.skills:
            if skill.is_applicable(context):
                relevant.append(skill)
        return relevant
    
    def get_skills_for_rule(self, rule_section: str) -> List[Skill]:
        """Return skills that enforce a specific constitutional rule"""
        return self.rule_mappings.get(rule_section, [])
```

### Dependency Resolution
```python
# .windsurf/skills/pre-write-orchestrator/dependency_resolver.py
class DependencyResolver:
    def resolve(self, skills: List[Skill]) -> List[SkillGroup]:
        """Resolve skill dependencies and create execution groups"""
        # Build dependency graph
        graph = self._build_dependency_graph(skills)
        
        # Topological sort for execution order
        execution_order = self._topological_sort(graph)
        
        # Group skills that can run in parallel
        parallel_groups = self._create_parallel_groups(execution_order)
        
        return parallel_groups
```

### Parallel Execution Engine
```python
# .windsurf/skills/pre-write-orchestrator/execution_engine.py
class ExecutionEngine:
    def execute_parallel(self, groups: List[SkillGroup], context: ValidationContext) -> List[SkillResult]:
        """Execute skill groups in parallel where possible"""
        results = []
        
        for group in groups:
            # Execute skills in group in parallel
            with ThreadPoolExecutor(max_workers=len(group.skills)) as executor:
                futures = {
                    executor.submit(skill.validate, context): skill 
                    for skill in group.skills
                }
                
                group_results = []
                for future in as_completed(futures):
                    skill = futures[future]
                    try:
                        result = future.result(timeout=skill.timeout)
                        group_results.append(result)
                    except Exception as e:
                        group_results.append(SkillResult.error(skill, e))
                
                results.extend(group_results)
                
                # Fail fast if any skill in group failed
                if any(not result.passed for result in group_results):
                    break
        
        return results
```

## Integration Strategy

### Phase 1: Framework Foundation (Week 1)
1. Implement pre-write orchestrator core
2. Create skill registry and dependency resolution
3. Implement parallel execution engine
4. Add error handling and aggregation

### Phase 2: Critical Gap Skills (Week 2)
1. Implement 5 critical gap skills
2. Add comprehensive test coverage
3. Integrate with orchestrator
4. Validate against constitutional rules

### Phase 3: Legacy Migration (Week 3)
1. Archive redundant skills
2. Update references to consolidated skills
3. Migrate existing configurations
4. Document migration path

### Phase 4: CI Integration (Week 4)
1. Integrate with existing CI gates
2. Add performance monitoring
3. Create status dashboard
4. Document operational procedures

## Performance Considerations

### Optimization Strategies
1. **Parallel Execution**: Run independent skills concurrently
2. **Caching**: Cache skill results where appropriate
3. **Incremental Validation**: Only validate changed components
4. **Smart Filtering**: Skip irrelevant skills based on context

### Performance Targets
- **Cold Start**: <10s for full validation suite
- **Incremental**: <2s for typical file edits
- **Parallel Efficiency**: >80% CPU utilization
- **Memory Usage**: <500MB for full validation

## Error Handling & Reporting

### Error Classification
1. **Critical Errors**: Block all operations (e.g., repair gate failures)
2. **Warning Errors**: Allow operation with documentation (e.g., style issues)
3. **Info Messages**: Log for awareness (e.g., performance metrics)

### Reporting Format
```python
# Standardized result format
@dataclass
class ValidationResult:
    passed: bool
    skill_name: str
    rule_section: Optional[str]
    message: str
    details: Dict[str, Any]
    suggestions: List[str]
    blocking: bool
```

### Dashboard Integration
```python
# Real-time status monitoring
class StatusDashboard:
    def display_validation_status(self, results: List[ValidationResult]):
        """Show real-time validation status"""
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        
        print(f"Validation Status: {passed}/{len(results)} passed")
        
        for result in results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.skill_name}: {result.message}")
```

## Testing Strategy

### Unit Tests
- Individual skill validation logic
- Orchestrator component testing
- Error handling scenarios
- Performance benchmarks

### Integration Tests
- End-to-end validation flows
- Skill dependency resolution
- Parallel execution correctness
- CI pipeline integration

### Regression Tests
- Constitutional rule coverage
- Backward compatibility
- Performance regression
- Error handling robustness

## Success Metrics

### Coverage Metrics
- **Rule Coverage**: 100% of constitutional rules covered
- **Skill Coverage**: All skills tested and documented
- **Scenario Coverage**: 95%+ of common validation scenarios

### Performance Metrics
- **Latency**: <5s for typical validations
- **Throughput**: >100 validations/minute
- **Resource Usage**: <1GB memory peak

### Reliability Metrics
- **Success Rate**: 99.9% validation success
- **Error Rate**: <0.1% false positives
- **Availability**: 99.9% uptime

## Maintenance & Evolution

### Skill Lifecycle
1. **Proposal**: New skill requirements identified
2. **Design**: Skill interface and dependencies defined
3. **Implementation**: Skill developed and tested
4. **Integration**: Added to orchestrator registry
5. **Monitoring**: Performance and effectiveness tracked
6. **Evolution**: Updated based on usage patterns

### Governance Process
1. **Change Review**: All skill changes reviewed for compliance
2. **Impact Analysis**: Assess effects on existing validations
3. **Testing**: Comprehensive test coverage required
4. **Documentation**: Update skill documentation and guides
5. **Deployment**: Coordinated deployment with monitoring

## Conclusion

The unified pre-write enforcement framework provides:

1. **Complete Coverage**: All constitutional rules enforced
2. **Optimal Performance**: Parallel execution and smart caching
3. **Maintainable Architecture**: Clear skill boundaries and dependencies
4. **Robust Error Handling**: Comprehensive error classification and recovery
5. **Future-Proof Design**: Extensible for new rules and skills

This framework addresses all critical gaps identified in the assessment while consolidating redundant skills into a cohesive, performant system.

---

*Framework proposal completed: 2025-03-26*
*Estimated implementation: *
*Dependencies: Existing consolidated skills, CI infrastructure*
## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

