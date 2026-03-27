# Phantom Import Debt Register

Phantom count: 34

| Path | Missing Name | Import Line | Suggested Fix |
| --- | --- | --- | --- |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `ImportGraph` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import ImportGraph` (line 916) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `blueprint_hash` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import blueprint_hash` (line 937) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `cross_layer` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import cross_layer` (line 937) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `emit_report_json` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import emit_report_json` (line 919) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `leaf_node` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import leaf_node` (line 937) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `make_report` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import make_report` (line 919) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `mixin_ast` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import mixin_ast` (line 937) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `territory_diff` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import territory_diff` (line 937) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `volatile_rules` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import volatile_rules` (line 937) | remove phantom import |
| `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 46) | replace import or define symbol |
| `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 42) | replace import or define symbol |
| `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 364) | replace import or define symbol |
| `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 29) | replace import or define symbol |
| `agentic_core/interfaces/structure_config.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 39) | replace import or define symbol |
| `agentic_core/interfaces/structure_config.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 29) | replace import or define symbol |
| `agentic_core/runtime/utils/sovereign_scan_util.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 79) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/refactor_l0_gravity_imports_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 18) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/refactor_mcp_imports_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 13) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/rescue_reviewer.py` | `CANON_SIGNALS` | `from agentic_core.L5_safety.config.structure_blueprint_config import CANON_SIGNALS` (line 85) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 23) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/suggest_variant_renames_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 10) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/undo_core_moves_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 10) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/workflow_review_pending_merge_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_DIR` (line 13) | replace import or define symbol |
| `tests/agentic_core/L0_routing/scripts/test_global_key_purge_validation.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 121) | replace import or define symbol |
| `tests/agentic_core/L5_safety/validators/test_void_violation_handling.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 124) | replace import or define symbol |
| `tests/agentic_core/base_agents/test_global_system_integrity.py` | `CANON_VALIDATION_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import CANON_VALIDATION_REGISTRY` (line 53) | replace import or define symbol |
| `tests/support/l1_cognition/SovereignCognitivePlaneAgent.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY` (line 22) | replace import or define symbol |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `ImportGraph` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement.import_graph import ImportGraph` (line 29) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `blueprint_hash` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import blueprint_hash` (line 21) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `cross_layer` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import cross_layer` (line 21) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `leaf_node` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import leaf_node` (line 21) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `mixin_ast` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import mixin_ast` (line 21) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `territory_diff` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import territory_diff` (line 21) | remove phantom import |
| `tests/unit/structure_blueprint/test_enforcement_counters.py` | `volatile_rules` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import volatile_rules` (line 21) | remove phantom import |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

