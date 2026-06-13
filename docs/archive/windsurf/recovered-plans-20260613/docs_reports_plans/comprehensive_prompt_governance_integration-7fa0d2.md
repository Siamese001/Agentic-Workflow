# Comprehensive Prompt Governance Integration Plan

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
Transform the fragmented prompt governance system by migrating from markdown-based injection patterns to production-grade YAML templates, establishing unified integration across both `agentic_core` and `apps_*` layers, and implementing comprehensive test coverage with backward compatibility.

## Current State Assessment

### 🚨 Critical Governance Gap Identified
- **Production YAML Templates**: 64 files in `data/prompt_governance\injections\` - **COMPLETELY UNUSED**
- **Markdown Templates**: 4 files in `data/prompt_governance\prompt_injections\` - **ACTIVELY INTEGRATED** but not production-grade
- **Integration Status**: `agentic_core` ✅ integrated, `apps_*` ❌ disconnected
- **Duplication**: `apps_shared/utils/instructional_layer.py` contains 899 lines of duplicate implementation

### Evidence Summary
- **agentic_core**: 588-line `PromptInjectionLoader`, 198-line mixin, hardcoded patterns from markdown
- **apps_* folders**: Zero imports from prompt governance data despite having infrastructure
- **YAML Structure**: Production-ready with templates, variables, success criteria, organized by 6 layers
- **Dependency Flow**: Stops at `agentic_core` - never reaches application layers

## Implementation Strategy

### Phase 1: Unified YAML Infrastructure (Days 1-3)

#### 1.1 Create Central YAML Loader
**File**: `agentic_core/config/core/yaml_injection_loader.py`
```python
class YamlInjectionLoader:
    """Load injection patterns from production-grade YAML templates"""

    def __init__(self, yaml_root: Path = None):
        self.yaml_root = yaml_root or Path("data/prompt_governance/injections")
        self.cache = {}  # LRU cache for performance

    def load_all_patterns(self) -> Dict[str, InjectionPattern]:
        """Load all 30 patterns from modular YAML structure"""

    def load_by_layer(self, layer: InjectionLayer) -> List[InjectionPattern]:
        """Load patterns for specific layer (framing, safety, etc.)"""

    def render_template(self, pattern_id: str, variables: Dict) -> str:
        """Render YAML template with variable substitution"""
```

#### 1.2 Update Core Integration
**File**: `agentic_core/runtime/config/prompt_injection_loader_config.py`
- Replace hardcoded patterns with YAML loader calls
- Maintain `PromptInjectionLoader` interface for backward compatibility
- Add fallback to markdown if YAML files missing
- Implement caching for performance (<5% impact target)

#### 1.3 Bridge Apps Integration
**File**: `apps_shared/config/prompt_governance_config.py`
```python
class AppsPromptGovernance:
    """Bridge between agentic_core YAML loader and apps_* layers"""

    def __init__(self):
        from agentic_core.config.core.yaml_injection_loader import YamlInjectionLoader
        self.yaml_loader = YamlInjectionLoader()

    def get_patterns_for_app(self, app_type: str) -> List[InjectionPattern]:
        """Get app-specific pattern filtering"""

    def render_with_context(self, pattern_id: str, app_context: Dict) -> str:
        """Render with app-specific variable context"""
```

### Phase 2: Eliminate Duplication (Days 4-5)

#### 2.1 Refactor apps_shared Duplicate Code
**File**: `apps_shared/utils/instructional_layer.py`
- Remove 899 lines of duplicate pattern definitions
- Replace with calls to `AppsPromptGovernance`
- Maintain existing function signatures for compatibility
- Add deprecation warnings for direct pattern access

#### 2.2 Update Import Chains
- Update all `apps_*` files to use centralized governance
- Replace local imports with `apps_shared.config.prompt_governance_config`
- Ensure 489 .py files in apps_* compile cleanly

#### 2.3 Enhance agentic_core Mixin
**File**: `agentic_core/mixins/instructional_injection_mixin.py`
- Update source reference from markdown to YAML
- Add YAML-based pattern loading
- Maintain backward compatibility with existing mixin interface

### Phase 3: Comprehensive Test Coverage (Days 6-7)

#### 3.1 Unit Tests
```python
# tests/unit/agentic_core/test_yaml_injection_loader.py
class TestYamlInjectionLoader:
    def test_load_all_30_patterns(self):
    def test_load_by_layer(self):
    def test_template_rendering(self):
    def test_cache_performance(self):
    def test_fallback_to_markdown(self):

# tests/unit/apps_shared/test_prompt_governance_integration.py
class TestAppsPromptGovernance:
    def test_apps_pattern_filtering(self):
    def test_context_variable_rendering(self):
    def test_backward_compatibility(self):
```

#### 3.2 Integration Tests
```python
# tests/integration/test_prompt_governance_end_to_end.py
class TestPromptGovernanceE2E:
    def test_yaml_to_agentic_core_flow(self):
    def test_agentic_core_to_apps_flow(self):
    def test_full_pipeline_integration(self):
    def test_performance_under_load(self):
```

#### 3.3 Regression Tests
- Verify all existing functionality preserved
- Test migration scenarios (markdown → YAML)
- Validate apps_* compilation after changes

### Phase 4: Migration & Cleanup (Days 8-9)

#### 4.1 Gradual Migration Strategy
- Use feature flags for controlled rollout
- Maintain markdown files during transition period
- Add deprecation warnings to markdown-based code
- Monitor performance and error rates

#### 4.2 Documentation Updates
- Update all source references in code headers
- Add integration documentation for apps developers
- Create migration guide for existing code

#### 4.3 Final Cleanup
- Remove duplicate implementations once migration complete
- Archive markdown files (don't delete immediately)
- Update CI/CD pipelines to validate YAML integrity

## Technical Implementation Details

### YAML Structure Utilization
```
data/prompt_governance/injections/
├── misc/                    # Monolithic files (backup)
│   ├── framing.yaml        # All 5 framing patterns
│   ├── safety.yaml         # All 5 safety patterns
│   └── ...
└── modular/                # Granular files (primary)
    ├── framing/
    │   └── v5_framing_injections.yaml
    ├── safety/
    │   └── v5_safety_injections.yaml
    └── ...
```

### Variable System Enhancement
Extend existing YAML variable format for complex scenarios:
```yaml
prompt_template: |
  Global Objective: {goal_state}
  Success Criteria: {quality_threshold}
  Context Variables: {user_context}
  App-Specific: {app_type}_{specific_var}
```

### Caching Strategy
- **LRU Cache**: 1024 template limit
- **Cache Invalidation**: On file modification or explicit clear
- **Performance Target**: <5% overhead vs hardcoded patterns

### Error Handling
- **Graceful Degradation**: Fallback to markdown if YAML fails
- **Validation**: Schema validation for YAML files
- **Logging**: Comprehensive error tracking and performance metrics

## Success Criteria & Metrics

### Functional Requirements
1. ✅ All 30 injection patterns load from YAML files
2. ✅ Both `agentic_core` and `apps_*` use same YAML source
3. ✅ Existing functionality 100% preserved (backward compatibility)
4. ✅ Zero compilation errors in 489 apps_* Python files
5. ✅ Performance impact <5% with caching enabled

### Quality Requirements
1. ✅ Test coverage >90% for new code paths
2. ✅ Zero duplicate pattern definitions
3. ✅ Single source of truth established
4. ✅ Production-grade YAML templates fully utilized
5. ✅ Comprehensive error handling and logging

### Governance Requirements
1. ✅ Centralized prompt governance across all layers
2. ✅ Consistent variable system and template rendering
3. ✅ Version-controlled YAML templates
4. ✅ Audit trail for pattern changes
5. ✅ Security validation for all templates

## Risk Mitigation

### Technical Risks
- **Breaking Changes**: Feature flags + gradual migration
- **Performance Issues**: Aggressive caching + performance monitoring
- **Integration Complexity**: Maintain existing APIs, change internals only
- **Data Loss**: Never delete markdown files, only archive

### Operational Risks
- **Deployment Issues**: Comprehensive test suite + canary deployments
- **Rollback Complexity**: Keep markdown fallback during transition
- **Team Adoption**: Clear documentation + migration guides

## Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | Days 1-3 | YAML loader, core integration, apps bridge |
| Phase 2 | Days 4-5 | Duplication removal, import updates |
| Phase 3 | Days 6-7 | Comprehensive test suite |
| Phase 4 | Days 8-9 | Migration, cleanup, documentation |

**Total Duration**:  with parallel execution where possible

## Post-Implementation State

### Architecture Overview
```
data/prompt_governance/injections/ (YAML Templates)
    ↓
agentic_core/config/core/yaml_injection_loader.py
    ↓
├── agentic_core/runtime/config/prompt_injection_loader_config.py
└── apps_shared/config/prompt_governance_config.py
    ↓
├── agentic_core agents (via mixin)
└── apps_* agents (via shared config)
```

### Benefits Achieved
1. **Production-Grade Templates**: YAML structure with validation
2. **Unified Governance**: Single source of truth across all layers
3. **Eliminated Duplication**: 899 lines of duplicate code removed
4. **Enhanced Maintainability**: Centralized pattern management
5. **Improved Performance**: Cached template rendering
6. **Better Testing**: Comprehensive coverage for all scenarios

This consolidated plan provides a complete roadmap from current fragmented state to unified, production-grade prompt governance across the entire system.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

