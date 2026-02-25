# Import Violation Clusters Report

**Generated**: 2026-02-17

## Summary

- **Total Modules**: 1908
- **Total Import Edges**: 1867
- **Upward Violations**: 238
- **Parse Errors**: 2

## Top 15 Imported Target Modules

| Rank | Target Module | Violations | Layer |
|------|---------------|------------|-------|
| 1 | `mutation_prohibition` | 56 | L5_safety |
| 2 | `structure_blueprint_config` | 51 | L5_safety |
| 3 | `structure_blueprint` | 12 | L5_safety |
| 4 | `ArchitectureGovernorAgent` | 6 | L5_safety |
| 5 | `HierarchyAgent` | 5 | L5_safety |
| 6 | `CodeValidatorAgent` | 4 | L5_safety |
| 7 | `LocationAgent` | 4 | L5_safety |
| 8 | `classification_kernel` | 4 | L5_safety |
| 9 | `NamingAgent` | 3 | L5_safety |
| 10 | `StructureEnforcerAgent` | 3 | L5_safety |
| 11 | `activation_gate` | 3 | L5_safety |
| 12 | `CodeEnforcerAgent` | 3 | L5_safety |
| 13 | `GovernanceAgent` | 3 | L5_safety |
| 14 | `FileClassificationAgent` | 2 | L5_safety |
| 15 | `Orchestrator` | 2 | L3_orchestration |

## Top 10 Source Files

| Rank | Source File | Violations | Layer |
|------|-------------|------------|-------|
| 1 | `execute_ssot.py` | 19 | L0_routing |
| 2 | `SubAtomicRegistryAgent.py` | 17 | L2_execution |
| 3 | `colors.py` | 9 | L0_routing |
| 4 | `complexity_visitor_util.py` | 6 | L0_routing |
| 5 | `safety_strategy.py` | 6 | L3_orchestration |
| 6 | `SSOTFolderCleanupAgent.py` | 5 | L0_routing |
| 7 | `forward_rolling_facade.py` | 5 | L0_routing |
| 8 | `NervousSystemAgent.py` | 5 | L3_orchestration |
| 9 | `run_guardian_classification_compliance.py` | 4 | L0_routing |
| 10 | `forensic_discovery_prep.py` | 3 | L0_routing |

## Layer-to-Layer Matrix

| Source | L1 | L2 | L3 | L4 | L5 | L6 |
|--------|----|----|----|----|----|----|
| L0 | 1 | 3 | 10 | 1 | 146 | 3 |
| L1 | - | 2 | 1 | 2 | 3 | - |
| L2 | - | - | 4 | 3 | 21 | - |
| L3 | - | - | - | 3 | 20 | 2 |
| L4 | - | - | - | - | 11 | - |
| L5 | - | - | - | - | - | 2 |

## Detailed Violations for Top 5 Targets

### 1. mutation_prohibition (56 violations)

Sample sources: `meta_apply.py`, `RootCustomsAgent.py`, `SSOTFolderCleanupAgent.py`, `add_dataclass_to_agents_util.py`, `colors.py`, and 51 more.

### 2. structure_blueprint_config (51 violations)

Sample sources: `execute_ssot.py`, `colors.py`, `SubAtomicRegistryAgent.py`, `safety_strategy.py`, and 47 more.

### 3. structure_blueprint (12 violations)

Sample sources: `run_guardian_hierarchy_compliance.py`, `run_guardian_location_alignment.py`, `NervousSystemAgent.py`, and 9 more.

### 4. ArchitectureGovernorAgent (6 violations)

Sample sources: `execute_ssot.py`, `SubAtomicRegistryAgent.py`, and 4 more.

### 5. HierarchyAgent (5 violations)

Sample sources: `execute_ssot.py`, `SubAtomicRegistryAgent.py`, and 3 more.

## Remediation Priority

1. `mutation_prohibition` - 56 violations
2. `structure_blueprint_config` - 51 violations
3. `structure_blueprint` - 12 violations
4. `ArchitectureGovernorAgent` - 6 violations
5. `HierarchyAgent` - 5 violations
