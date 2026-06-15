# Old L5 Agent Wave 3 Large-Facade Blockers

Plan: `old-l5-agent-retirement-a94f6c`
Date: 2026-06-15
Source manifest: `docs/reports/agent_deprecation/old_l5_agent_retirement_manifest_20260615.json`

## Decision

The five large facades are retirement targets, not modernization targets. No W3 physical delete is safe yet because each candidate still has active reference evidence and no complete replacement proof in the manifest.

## Facade Priority

| Rank | Candidate | LOC | Raw refs | ADG fan-in | ADG fan-out | W3 action |
|---:|---|---:|---:|---:|---:|---|
| 1 | `FileClassificationAgent.py` | 4939 | 23 | 404 | 548 | Split first; migrate callers to existing `file_classification/*` and `core_kernel/classification_kernel.py` surfaces |
| 2 | `ArchitectureGovernorAgent.py` | 1433 | 15 | 139 | 287 | Split after governance runner/catalog callers have replacements |
| 3 | `CodeHealerAgent.py` | 808 | 15 | 84 | 221 | Preserve compatibility helpers until utility parity exists |
| 4 | `GravityLeakRepairAgent.py` | 923 | 11 | 92 | 195 | Split detector/repair runtime callers before delete |
| 5 | `PascalSovereigntyAgent.py` | 779 | 7 | 146 | 155 | Reconcile reasoning vs validators duplicate before delete |

## Critical Slice

`FileClassificationAgent.py` is the critical slice:

- Highest LOC: 4939.
- Highest ADG fan-in: 404.
- Highest ADG fan-out: 548.
- Highest raw reference count among large facades: 23.
- User direction: treat it as Windsurf-era technical debt; do not modernize it in place.

W3 action for `FileClassificationAgent.py` is caller migration and extraction closure, not feature work. Existing partial extraction surfaces are already present under:

- `agentic_core/L5_safety/reasoning/file_classification/`
- `agentic_core/L5_safety/reasoning/core_kernel/classification_kernel.py`
- `agentic_core/L5_safety/utils/fca_safety_gates_util.py`

## Active Blocker Samples

`FileClassificationAgent.py` still appears in active runtime or test surfaces including:

- `agentic_core/L0_routing/enforcement/safety_reasoning_seam.py`
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`
- `agentic_core/L5_safety/reasoning/file_classification_validator.py`
- `agentic_core/L5_safety/reasoning/hierarchy_healer.py`
- `agentic_core/L5_safety/reasoning/location_validator.py`
- `agentic_core/L5_safety/reasoning/root_hygiene_healer.py`
- `agentic_core/L5_safety/utils/location_healer_util.py`
- `tests/unit/agentic_core/L5_safety/reasoning/test_file_classification_agent_behavior.py`
- `tests/agentic_core/L5_safety/reasoning/test_FileClassificationAgent.py`

Other large-facade blockers:

- `ArchitectureGovernorAgent.py`: still used by `SSOTFolderCleanupAgent`, `mission_runner`, `architecture_governor_validator_util`, and L5 runner scripts.
- `CodeHealerAgent.py`: still provides `create_legacy_import_healer` compatibility used by `HealingStrategy`, `mission_preflight_validator`, `LocationHealerAgent`, and old unified-agent helper generation.
- `GravityLeakRepairAgent.py`: still used by `GravityLeakHealerAgent`, `gravity_leak_validator`, L5 runner scripts, and prompt-governance tests.
- `PascalSovereigntyAgent.py`: still appears in `agent_taxonomy_registry`, the validator duplicate shim, operational scripts, and focused tests.

## W3 Split Plan

1. First split: `FileClassificationAgent` caller migration.
   - Replace direct imports in seam/validators/healers with extracted classification surfaces where parity exists.
   - Keep behavior tests on extracted functions or a transitional compatibility shim.
   - Delete no files until parity tests pass.

2. Second split: helper parity for `CodeHealerAgent`.
   - Move `create_legacy_import_healer` compatibility to a utility or seam-safe runner.
   - Then rewrite old generated-helper strings.

3. Third split: governance and gravity facades.
   - Move `ArchitectureGovernorAgent` and `GravityLeakRepairAgent` runner dependencies to utilities or process boundaries.
   - Preserve prompt template authorship strings as historical labels unless they are executable imports.

4. Fourth split: Pascal duplicate reconciliation.
   - Establish whether reasoning or validators surface owns the canonical implementation.
   - Migrate taxonomy and operational scripts before deleting either file.

## Non-Goals

- Do not add capabilities to `FileClassificationAgent.py`.
- Do not perform broad automatic string replacement across generated baselines.
- Do not delete large facades in this branch without a separate replacement-proof packet.
