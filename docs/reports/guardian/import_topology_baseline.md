# Import Topology Baseline Report

**Generated**: 2026-02-17

## Summary

| Metric | Value |
|--------|-------|
| Total Modules | 1908 |
| Total Import Edges | 1867 |
| Upward Violations | 238 |
| Parse Errors | 2 |

## Top 15 Imported Target Modules (Offenders)

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

## Top 10 Source Files by Violation Count

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

## Layer-to-Layer Violation Matrix

| Source | L1 | L2 | L3 | L4 | L5 | L6 |
|--------|----|----|----|----|----|----|
| L0 | 1 | 3 | 10 | 1 | 146 | 3 |
| L1 | - | 2 | 1 | 2 | 3 | - |
| L2 | - | - | 4 | 3 | 21 | - |
| L3 | - | - | - | 3 | 20 | 2 |
| L4 | - | - | - | - | 11 | - |
| L5 | - | - | - | - | - | 2 |

## Key Findings

1. **L5_safety is primary target** - 207/238 violations (87%)
2. **mutation_prohibition top offender** - 56 violations (23.5%)
3. **structure_blueprint_config second** - 51 violations (21.4%)
4. **L0_routing primary source** - 164 violations originate from L0

## Remediation Priority

1. `mutation_prohibition` - 56 violations (PURE UTILITY)
2. `structure_blueprint_config` - 51 violations (SHIM)
3. `structure_blueprint` - 12 violations (MIXED CONCERN)
4. `ArchitectureGovernorAgent` - 6 violations (SAFETY LOGIC)
5. `HierarchyAgent` - 5 violations (SAFETY LOGIC)
