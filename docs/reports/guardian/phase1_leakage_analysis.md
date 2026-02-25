# Phase 1: Shared Utility Leakage Analysis

**Generated**: 2026-02-17
**Baseline Violations**: 238

## Classification Results

| Rank | Module | Violations | Classification | Strategy |
|------|--------|------------|----------------|----------|
| 1 | `mutation_prohibition` | 56 | PURE UTILITY | Relocate to L0 |
| 2 | `structure_blueprint_config` | 51 | SHIM | Fix via underlying |
| 3 | `structure_blueprint` | 12 | MIXED CONCERN | Extract constants |
| 4 | `ArchitectureGovernorAgent` | 6 | SAFETY LOGIC | Dependency inversion |
| 5 | `HierarchyAgent` | 5 | SAFETY LOGIC | Dependency inversion |

## Detailed Analysis

### 1. mutation_prohibition (56 violations)

**Classification**: PURE UTILITY

- Contains only stdlib imports
- No L5-specific dependencies
- Provides generic mutation guards
- Functions are stateless

**Strategy**: Relocate to L0
**Impact**: 56 violations eliminated (23.5%)

### 2. structure_blueprint_config (51 violations)

**Classification**: SHIM

- Re-exports from structure_blueprint package
- Contains no actual logic
- Violations caused by underlying package

**Strategy**: No direct action, fix via #3
**Impact**: Indirect reduction

### 3. structure_blueprint (12 violations)

**Classification**: MIXED CONCERN

- Contains 163+ exported names
- Some pure constants (paths, patterns)
- Some L5-specific governance logic

**Strategy**: Extract pure constants to L0
**Impact**: ~12 violations eliminated

### 4. ArchitectureGovernorAgent (6 violations)

**Classification**: SAFETY LOGIC

- Agent with L5-specific governance
- Cannot move to lower layer

**Strategy**: Dependency inversion or evaluate usage
**Impact**: 6 violations

### 5. HierarchyAgent (5 violations)

**Classification**: SAFETY LOGIC

- Agent with L5-specific enforcement
- Cannot move to lower layer

**Strategy**: Dependency inversion or evaluate usage
**Impact**: 5 violations

## Remediation Priority

| Priority | Module | Action | Est. Reduction |
|----------|--------|--------|----------------|
| 1 | mutation_prohibition | Relocate to L0 | 56 violations |
| 2 | structure_blueprint | Extract constants | 12 violations |
| 3 | ArchitectureGovernorAgent | Evaluate/invert | 6 violations |
| 4 | HierarchyAgent | Evaluate/invert | 5 violations |

**Total Estimated Reduction**: 79 violations (33%)

## Structural Blockers

If 60% reduction cannot be achieved:

1. Many L0 scripts legitimately need L5 governance logic
2. Layer architecture may need redesign (out of scope)
3. Some violations may need architectural exceptions
