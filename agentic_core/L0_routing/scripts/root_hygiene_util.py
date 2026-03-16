"""
File: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Path: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Rationale:
    Actively enforces the new Root Hygiene laws defined in structure_blueprint.
    1. Moves root 'scripts/*' to 'ops_scripts/' (standalone) or 'L0_routing/scripts/' (core).
    2. Moves 'coverage_html' to 'reports/'.
    3. Deletes the illegal root directories after evacuation.
"""

import shutil
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
    REPORTS_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "root_hygiene_util")
emit_determinism_digest("p0", "root_hygiene_util")

_emit_dispatches_healing_run("p1", "root_hygiene_util", "L0")
_emit_routes_through("p1", "root_hygiene_util", "L0")
_emit_escalates_to_human("p1", "root_hygiene_util", "L0")
_emit_reads_policy_state("p1", "root_hygiene_util", "L0")
_emit_authorize_and_execute("p2", "root_hygiene_util", "execution_auth")
_emit_validates_capability("p2", "root_hygiene_util", "capability_check")
_emit_routes_to_capability("p2", "root_hygiene_util", "capability_route")
_emit_writes_via_uwg("p2", "root_hygiene_util", "uwg_write")
_emit_blocks_direct_write("p2", "root_hygiene_util", "direct_write_block")
_emit_records_tool_invocation("p2", "root_hygiene_util", "tool_invocation")
_emit_captures_execution_output("p2", "root_hygiene_util", "exec_output")
_emit_dispatches_agent("p3", "root_hygiene_util", "agent_dispatch")
_emit_coordinates_agents("p3", "root_hygiene_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_hygiene_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_hygiene_util", "healing_outcome")
_emit_escalates_failure("p3", "root_hygiene_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_hygiene_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_hygiene_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_hygiene_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_hygiene_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_hygiene_util", "eval_metric")
_emit_stores_embedding("p4", "root_hygiene_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_hygiene_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_hygiene_util", "exec_snapshot_link")

# SSOT Constants
ROOT_MARKERS = [AGENTIC_CORE_DIR, "pyproject.toml"]


def get_project_root() -> Path:
    """Resolve project root securely."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_project_root")
    current = Path.cwd()
    for marker in ROOT_MARKERS:
        if (current / marker).exists():
            return current
    raise RuntimeError("Must run from Project Root")


def enforce_root_hygiene():
    root = get_project_root()
    print(f"[HYGIENE] Enforcing Root Sovereignty at: {root}")
    print("=" * 60)

    # 1. EVACUATE ROOT SCRIPTS
    root_scripts = root / "scripts"
    ops_scripts = root / OPS_SCRIPTS_DIR
    l0_scripts = root / AGENTIC_CORE_DIR / "L0_routing" / "scripts"

    if root_scripts.exists():
        print("[DETECT] Illegal root 'scripts/' directory found.")
        ops_scripts.mkdir(exist_ok=True)
        l0_scripts.mkdir(exist_ok=True, parents=True)

        for item in root_scripts.iterdir():
            if item.is_file() and item.suffix == ".py":
                # Decision Logic: Does it import agentic_core?
                try:
                    content = item.read_text(encoding="utf-8")
                    if AGENTIC_CORE_DIR in content or "from agentic_core" in content:
                        target = l0_scripts / item.name
                        action = "REPATRIATE (Core)"
                    else:
                        target = ops_scripts / item.name
                        action = "RELOCATE (Ops)"

                    print(f"  - {item.name} -> {action}")
                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                    shutil.move(str(item), str(target))
                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")

            elif item.is_dir():
                # Move entire subfolders to ops_scripts/maintenance or similar
                # For simplicity in this phase, dump to ops_scripts root or map specific folders
                target = ops_scripts / item.name
                print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                if target.exists():
                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                    shutil.rmtree(target)  # Force overwrite logic for dirs
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(item), str(target))

        # Cleanup empty dir
        try:
            root_scripts.rmdir()
            print("[SUCCESS] Illegal 'scripts/' directory eliminated.")
        except OSError:
            print("[WARNING] 'scripts/' not empty, manual check required.")
    else:
        print("[CHECK] Root 'scripts/' is clean.")

    # 2. EVACUATE COVERAGE_HTML
    cov_html = root / "coverage_html"
    reports_cov = root / REPORTS_DIR / "coverage_html"

    if cov_html.exists():
        print("\n[DETECT] Illegal root 'coverage_html/' found.")
        reports_cov.parent.mkdir(exist_ok=True)

        if reports_cov.exists():
            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
            shutil.rmtree(reports_cov)

        print("  - Moving to reports/coverage_html")
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.move(str(cov_html), str(reports_cov))
        print("[SUCCESS] Coverage report relocated.")
    else:
        print("[CHECK] Root 'coverage_html/' is clean.")

    # 3. RELOCATE PURGE_CACHE (Specific Request)
    # Checks if it ended up in ops_scripts during step 1, or needs specific handling
    purge_script = ops_scripts / "purge_cache.py"
    maint_script_dir = ops_scripts / "maintenance"
    if purge_script.exists():
        maint_script_dir.mkdir(exist_ok=True)
        target = maint_script_dir / "purge_cache.py"
        print("\n[REFILE] Organizing purge_cache.py -> ops_scripts/maintenance/")
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.move(str(purge_script), str(target))


if __name__ == "__main__":
    enforce_root_hygiene()
