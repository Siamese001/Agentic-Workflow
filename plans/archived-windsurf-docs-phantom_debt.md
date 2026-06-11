---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phantom_debt.md'
original_relative_path: 'phantom_debt.md'
source_sha256: c79a0ac5a234f6672e417f0298c5e9945fdeabb40aceca68f29226f355f88268
recovered_status: LOST_RECOVERED
last_commit: 'c7f029413d3'
last_commit_date: '2026-04-06 06:05:12 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phantom Import Debt Register

Phantom count: 16

| Path | Missing Name | Import Line | Suggested Fix |
| --- | --- | --- | --- |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `blueprint_hash` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import blueprint_hash` (line 956) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `cross_layer` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import cross_layer` (line 956) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `leaf_node` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import leaf_node` (line 956) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `mixin_ast` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import mixin_ast` (line 956) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `territory_diff` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import territory_diff` (line 956) | remove phantom import |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | `volatile_rules` | `from agentic_core.L5_safety.config.structure_blueprint.enforcement import volatile_rules` (line 956) | remove phantom import |
| `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | `SOVEREIGN_REGISTRY` | `from agentic_core.L5_safety.config.structure_blueprint import SOVEREIGN_REGISTRY` (line 119) | replace import or define symbol |
| `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 124) | replace import or define symbol |
| `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 108) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/refactor_l0_gravity_imports_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 18) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/refactor_mcp_imports_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 13) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/rescue_reviewer.py` | `CANON_SIGNALS` | `from agentic_core.L5_safety.config.structure_blueprint import CANON_SIGNALS` (line 237) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 23) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/suggest_variant_renames_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 10) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/undo_core_moves_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 88) | replace import or define symbol |
| `ops_scripts/dev_tools/l0_scripts/workflow_review_pending_merge_util.py` | `SCRIPTS_DIR` | `from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_DIR` (line 91) | replace import or define symbol |
