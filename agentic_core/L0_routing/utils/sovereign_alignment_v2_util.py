from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_alignment_v2_util")
emit_determinism_digest("p0", "sovereign_alignment_v2_util")

_emit_dispatches_healing_run("p1", "sovereign_alignment_v2_util", "L0")
_emit_routes_through("p1", "sovereign_alignment_v2_util", "L0")
_emit_escalates_to_human("p1", "sovereign_alignment_v2_util", "L0")
_emit_reads_policy_state("p1", "sovereign_alignment_v2_util", "L0")
_emit_authorize_and_execute("p2", "sovereign_alignment_v2_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_alignment_v2_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_alignment_v2_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_alignment_v2_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_alignment_v2_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_alignment_v2_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_alignment_v2_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_alignment_v2_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_alignment_v2_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_alignment_v2_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_alignment_v2_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_alignment_v2_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_alignment_v2_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_alignment_v2_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_alignment_v2_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_alignment_v2_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_alignment_v2_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_alignment_v2_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_alignment_v2_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_alignment_v2_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

root: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR
migration_map: Any = {
    "agentic_core/engines": "agentic_core/L2_execution/P3_engines",
    "agentic_core/interfaces": "agentic_core/L1_cognition/P1_interfaces",
    "agentic_core/security": "agentic_core/L5_safety/P4_security",
    "agentic_core/agentic_workflow": "agentic_core/L3_orchestration/P5_workflow",
}


def flush_and_align() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "flush_and_align", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "flush_and_align", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "flush_and_align")
    print("[*] STARTING SOVEREIGN ALIGNMENT V2 & CIRCULAR FLUSH...")
    for source, target in MIGRATION_MAP.items():
        src_path: Any = ROOT / source
        dest_path: Any = ROOT / target
        if src_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            for item in src_path.iterdir():
                dest_item: Any = dest_path / item.name
                if dest_item.exists():
                    print(f"      [!] Skipping {item.name} (already exists at destination)")
                    continue
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.move(str(item), str(dest_item))
            try:
                src_path.rmdir()
                print(f"  [>] Migrated Drift: {source} -> {target}")
            except OSError:
                print(f"  [!] Could not remove {source} (not empty)")
        else:
            print(f"  [-] Skipped: {source} (not found)")
    print("\n[*] FLUSHING __init__.py FILES...")
    flush_count: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for init_file in [f for f in get_python_files(CORE) if f.name == "__init__.py"]:
        print(f"  [!] Flushing: {init_file.relative_to(ROOT)}")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(f'"""Sovereign Layer: {init_file.parent.name}"""\n')
        flush_count += 1
    print(f"  [OK] Flushed {flush_count} __init__.py files")
    print("\n[*] REWIRING IMPORTS...")
    rewire: Any = [
        ("agentic_core\\.L5_safety\\.P1_red_team\\.analysis", "agentic_core.L2_execution.reasoning.analysis")
    ]
    count: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(ROOT):
        if "legacy_code" in str(py_file) or "data" in str(py_file):
            continue
        try:
            with open(py_file, encoding="utf-8") as f:
                content: Any = f.read()
            new_content: Any = content
            for old, new in rewire:
                new_content: Any = re.sub(old, new, new_content)
            if new_content != content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  [✓] Rewired: {py_file.name}")
                count += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  [!] Failed to process {py_file}: {e}")
    print(f"\n[OK] CONVERGENCE V2 COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")


if __name__ == "__main__":
    flush_and_align()
