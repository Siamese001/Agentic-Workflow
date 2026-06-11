---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps-lic-dry-run-findings.md'
original_relative_path: 'apps-lic-dry-run-findings.md'
source_sha256: 6c63d2cdf166e35fcf6c5eef56cb94fd4670ca1f13f224aafe4a6259cc5823a4
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Dry-Run Import Findings

## Scan Summary

- **Total .py files scanned**: 108
- **Modules OK**: ~27
- **Modules with errors**: 81
- **Scanner**: `tools/dry_run_apps_lic.py` (AST parse + importlib.import_module)

---

## Error Category A: Missing `from typing import Any` (50+ files)

**Root cause**: Dozens of generated tool/type files use `Any` in class-level annotations or
variable declarations at module scope without importing it from `typing`.

**Error**: `NameError: name 'Any' is not defined`

**Affected directories**: `apps_lic/tools/` (40+ files), `apps_lic/types/`, `apps_lic/reasoning/`

**Representative files**:
- `apps_lic/tools/AdjustToneWeights.py` — line 10: `Logger: Any = logging.getLogger(__name__)`
- `apps_lic/tools/AggregateCampaignState.py`
- `apps_lic/tools/AssessContentRisk.py`
- `apps_lic/tools/BuildMessageFilters.py`
- (all `apps_lic/tools/` files matching the generated-on-2025-12-07 pattern)

**Fix**: Add `from typing import Any` to each file that uses `Any` at module scope.

---

## Error Category B: Missing `from enum import Enum` (6 files)

**Root cause**: Type files in `apps_lic/types/` define `Enum` subclasses but omit the import.

**Error**: `NameError: name 'Enum' is not defined`

**Affected files**:
- `apps_lic/types/action_call_generator_types.py`
- `apps_lic/types/lic_models_types.py`
- `apps_lic/types/message_route_types.py`
- `apps_lic/types/message_type_types.py`
- `apps_lic/types/recipient_archetype_types.py`
- `apps_lic/types/route_types.py`
- `apps_lic/types/validation_severity_types.py`

**Fix**: Add `from enum import Enum` to each file.

---

## Error Category C: Undefined `BaseModel` (1 file)

**Root cause**: `SpecialistDraftPacket.py` uses Pydantic `BaseModel` without importing it.

**Error**: `NameError: name 'BaseModel' is not defined`

**Affected file**: `apps_lic/types/SpecialistDraftPacket.py`

**Fix**: Add `from pydantic import BaseModel`.

---

## Error Category D: Undefined `ExecutionResult` (3 files)

**Root cause**: Tool files use `ExecutionResult` as a return type annotation at module scope
without importing or defining it.

**Error**: `NameError: name 'ExecutionResult' is not defined`

**Affected files**:
- `apps_lic/tools/call_personalization_api.py`
- `apps_lic/tools/dispatch_outreach_tools.py`
- `apps_lic/tools/invoke_message_service.py`

**Fix**: Import `ExecutionResult` from wherever it is defined (likely `apps_lic/types/` or `apps_shared`), or add a local dataclass definition.

---

## Error Category E: Undefined `FormatResult` (1 file)

**Root cause**: `PrepareOutreachContext.py` references `FormatResult` without import.

**Error**: `NameError: name 'FormatResult' is not defined`

**Affected file**: `apps_lic/tools/PrepareOutreachContext.py`

**Fix**: Import `FormatResult` from its source module.

---

## Error Category F: Undefined `CircuitBreaker` (1 file)

**Root cause**: `GoogleSearchClient.py` references `CircuitBreaker` without importing it.

**Error**: `NameError: name 'CircuitBreaker' is not defined`

**Affected file**: `apps_lic/tools/GoogleSearchClient.py`

**Fix**: Import `CircuitBreaker` from `apps_shared` or define locally.

---

## Error Category G: Undefined `Path` (1 file)

**Root cause**: `analyze_duplicates_detailed.py` uses `Path` without `from pathlib import Path`.

**Error**: `NameError: name 'Path' is not defined`

**Affected file**: `apps_lic/tools/analyze_duplicates_detailed.py`

**Fix**: Add `from pathlib import Path`.

---

## Error Category H: Wrong Import Path — `_util` suffix mismatch (5 module paths)

**Root cause**: Code imports modules by their canonical logical name, but the actual files
were renamed with a `_util` suffix during a previous refactor. The module registry was
not updated to match.

| Imported as | Actual file |
|---|---|
| `apps_lic.utils.LICAgentBase` | `apps_lic/utils/lic_agent_base_util.py` |
| `apps_lic.utils.hop_stage_capability` | `apps_lic/utils/hop_stage_capability_util.py` |
| `apps_lic.utils.lic_engine_validation_capability` | `apps_lic/utils/lic_engine_validation_capability_util.py` |

**Importers affected** (6+ files):
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- `apps_lic/reasoning/LICValidationExecutor.py`
- `apps_lic/reasoning/ValidatorAgent.py`
- `apps_lic/utils/PIISanitizerSpecialistAgent_util.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`

**Fix options** (choose one consistently):
1. Add shim modules at the old paths that re-export from `_util` files.
2. Rename `_util` files back to canonical names (risky if other references exist).
3. Update all import statements to use the `_util` suffix names.

---

## Error Category I: Wrong Import Path — wrong subpackage (3 module paths)

**Root cause**: Modules that live in `apps_lic/reasoning/` are imported as if they were
in `apps_lic/engines/`.

| Imported as | Actual location |
|---|---|
| `apps_lic.engines.HOPPipelineExecutor` | `apps_lic/reasoning/HOPPipelineExecutor.py` |
| `apps_lic.engines.LICValidationExecutor` | `apps_lic/reasoning/LICValidationExecutor.py` |
| `apps_lic.engines.LeadQualityAgent` | `apps_lic/reasoning/LeadQualityAgent.py` |

**Importers affected**:
- `apps_lic/reasoning/Hop1ProfileAnalysisAgent.py` through `HOP9IntegrationAgent.py` (9 files)
- `apps_lic/reasoning/CampaignBalanceAgent.py`
- `apps_lic/reasoning/DeliverabilityAgent.py`
- `apps_lic/reasoning/OutreachSignalRouterAgent.py`

**Fix**: Update import paths from `apps_lic.engines.*` to `apps_lic.reasoning.*`.

---

## Error Category J: Missing external dependency — `apps_shared.utils.AppBase` (1 file)

**Root cause**: `apps_lic/utils/lic_agent_base_util.py` imports `AppBase` from
`apps_shared.utils.AppBase`, but the actual file is `apps_shared/utils/app_base_util.py`
(snake_case + `_util` suffix).

**Error**: `ModuleNotFoundError: No module named 'apps_shared.utils.AppBase'`

**Affected file**: `apps_lic/utils/lic_agent_base_util.py`

**Fix**: Change import to `from apps_shared.utils.app_base_util import AppBase`
(verify exact class name inside that file first).

---

## Error Category K: MRO conflict — `SubatomicTestingMixin` + `SovereignBaseAgent` (2 files)

**Root cause**: `OutreachProactiveAgent` and `OutreachSignalRouterAgent` inherit from
`(SubatomicTestingMixin, SovereignBaseAgent)`. Python's MRO linearization fails because
`SubatomicTestingMixin` inherits from a class that also appears in `SovereignBaseAgent`'s
MRO, creating a diamond conflict.

**Error**: `TypeError: Cannot create a consistent method resolution order (MRO) for bases SubatomicTestingMixin, SovereignBaseAgent`

**Affected files**:
- `apps_lic/reasoning/OutreachProactiveAgent.py`
- `apps_lic/reasoning/OutreachSignalRouterAgent.py`

**Fix**: Swap the inheritance order to `(SovereignBaseAgent, SubatomicTestingMixin)`, OR
restructure `SubatomicTestingMixin` to use `object` as its only base.

---

## Error Category L: `SubatomicTestingMixin` referenced but not imported (2 files)

**Root cause**: `OutreachLearningAgent.py` and `app_content_validator_agent_types.py`
reference `SubatomicTestingMixin` in class definitions but the import line is missing or placed
after the class body (in the docstring block area).

**Error**: `NameError: name 'SubatomicTestingMixin' is not defined`

**Affected files**:
- `apps_lic/reasoning/OutreachLearningAgent.py`
- `apps_lic/types/app_content_validator_agent_types.py`

**Fix**: Ensure `from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin`
is at the top of each file.

---

## Error Category M: Script side-effect on import — `FileNotFoundError` (1 file)

**Root cause**: `apps_lic/scripts/move_lics2_to_legacy.py` executes file-move operations
at module level (not inside `if __name__ == '__main__'`), causing a `FileNotFoundError`
when imported because the target file no longer exists.

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'apps_lic\engines\LicS2SupervisorAgent.py'`

**Affected file**: `apps_lic/scripts/move_lics2_to_legacy.py`

**Fix**: Wrap all imperative logic in `if __name__ == '__main__':` guard.

---

## Error Category N: `ImportError` — removed symbol `SOVEREIGN_REGISTRY` (1 file)

**Root cause**: `fix_duplicate_realagentdata.py` imports `SOVEREIGN_REGISTRY` from
`agentic_core.L5_safety.config.structure_blueprint_config`, but that symbol was removed
from the module.

**Error**: `ImportError: cannot import name 'SOVEREIGN_REGISTRY' from 'agentic_core.L5_safety.config.structure_blueprint_config'`

**Affected file**: `apps_lic/tools/fix_duplicate_realagentdata.py`

**Fix**: Remove the `SOVEREIGN_REGISTRY` import and replace the usage with the current
equivalent export from `structure_blueprint_config`.

---

## Priority Fix Order

| Priority | Category | Count | Effort |
|---|---|---|---|
| 1 | A — Missing `from typing import Any` | 50+ files | Low (bulk add) |
| 2 | B — Missing `from enum import Enum` | 7 files | Low (bulk add) |
| 3 | H — `_util` suffix mismatch (wrong module paths) | 6 importers | Medium |
| 4 | I — Wrong subpackage (`engines` vs `reasoning`) | 12 importers | Medium |
| 5 | K — MRO conflict | 2 files | Low (swap order) |
| 6 | J — `apps_shared.utils.AppBase` wrong path | 1 file | Low |
| 7 | L — `SubatomicTestingMixin` not imported | 2 files | Low |
| 8 | M — Script side-effect on import | 1 file | Low |
| 9 | C/D/E/F/G/N — misc NameError/ImportError | 8 files | Low–Medium |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

