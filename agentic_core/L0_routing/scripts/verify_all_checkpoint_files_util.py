from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verify_all_checkpoint_files_util")
emit_determinism_digest("p0", "verify_all_checkpoint_files_util")

_emit_dispatches_healing_run("p1", "verify_all_checkpoint_files_util", "L0")
_emit_routes_through("p1", "verify_all_checkpoint_files_util", "L0")
_emit_escalates_to_human("p1", "verify_all_checkpoint_files_util", "L0")
_emit_reads_policy_state("p1", "verify_all_checkpoint_files_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_all_checkpoint_files_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_all_checkpoint_files_util", "p0_governance")
_emit_snapshots_state("p0", "verify_all_checkpoint_files_util", "state_snapshot")

"Verify archival status of all files mentioned in checkpoint summary."
import os

from agentic_core.L0_routing.config import ARCHIVES_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
edited_files = [
    "scripts/rename_UnifiedAgents.py",
    "tests/unit/test_unified_hygiene_validator.py",
    "tests/unit/test_l5_sovereignty_upgrade.py",
    "tests/unit/test_phase2_validator_consolidation.py",
    "tests/unit/test_registry_mapping.py",
    "tests/unit/test_unified_core_regression.py",
    "scripts/generate_layer_report.py",
    "scripts/detailed_territory_report.py",
]
viewed_files = ["tests/unit/test_unified_hygiene_validator.py", "agent_discovery_full.json"]
renamed_agents = [
    "agentic_core/L5_safety/unified/CodeDetectorAgent.py",
    "agentic_core/L5_safety/unified/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/unified/CodeHealerAgent.py",
    "agentic_core/L5_safety/unified/CodeValidatorAgent.py",
    "agentic_core/L5_safety/unified/ResourceManagerAgent.py",
    "agentic_core/L5_safety/unified/SafetyDetectorAgent.py",
    "agentic_core/L5_safety/unified/SafetyExecutorAgent.py",
    "agentic_core/L5_safety/unified/SecurityManagerAgent.py",
    "agentic_core/L5_safety/unified/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/unified/StructureHealerAgent.py",
    "agentic_core/L5_safety/unified/StructuralValidatorAgent.py",
]
all_files = edited_files + viewed_files + renamed_agents
active_count = 0
archived_count = 0
missing_count = 0
for file_path in all_files:
    full_path = PROJECT_ROOT / file_path
    exists_active = full_path.exists()
    filename = Path(file_path).name
    archives_path = PROJECT_ROOT / ARCHIVES_DIR
    exists_archived = False
    if archives_path.exists():
        for root, dirs, files in os.walk(archives_path):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            if filename in files:
                exists_archived = True
                break
    if exists_active and (not exists_archived):
        status = "✅ ACTIVE"
        active_count += 1
    elif not exists_active and exists_archived:
        status = "📦 ARCHIVED"
        archived_count += 1
    elif exists_active and exists_archived:
        status = "⚠️ BOTH (active + archived)"
        active_count += 1
    else:
        status = "❌ MISSING"
        missing_count += 1
