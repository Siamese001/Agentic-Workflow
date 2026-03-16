from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "align_tests_structure_util")
emit_determinism_digest("p0", "align_tests_structure_util")

_emit_dispatches_healing_run("p1", "align_tests_structure_util", "L0")
_emit_routes_through("p1", "align_tests_structure_util", "L0")
_emit_escalates_to_human("p1", "align_tests_structure_util", "L0")
_emit_reads_policy_state("p1", "align_tests_structure_util", "L0")

"\nTEST STRUCTURE ALIGNMENT\nEnsures all test directories have __init__.py for Python package recognition.\n"
import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def align_tests_structure(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "align_tests_structure", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "align_tests_structure", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "align_tests_structure")
    from agentic_core.L5_safety.config.structure_blueprint import TESTS_L2_SUBFOLDER_MAP

    print("--- ALIGNING TESTS WITH SOVEREIGN LAW ---")
    tests_root: Any = Path(root_path) / TESTS_DIR
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        l1_path: Any = Path(tests_root) / l1
        ensure_dir_structure(l1_path)
        for l2 in l2_list:
            l2_path: Any = Path(l1_path) / l2
            ensure_dir_structure(l2_path)


def ensure_dir_structure(path: Any) -> Any:
    """Brief description of functionality and purpose."""
    # guardian: allow-path-string
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"✅ CREATED: {path}")
    init_file: Any = Path(path) / "__init__.py"
    # guardian: allow-path-string
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Sovereign Test Module\n")
        print(f"✅ ADDED __init__.py: {path}")
    gitkeep: Any = Path(path) / ".gitkeep"
    # guardian: allow-path-string
    if not os.path.exists(gitkeep):
        with open(gitkeep, "w") as f:
            f.write("")


if __name__ == "__main__":
    PROJECT_ROOT: Any = "C:/Git/Agentic-Workflow"
    align_tests_structure(PROJECT_ROOT)
    print("\n✅ TEST ALIGNMENT COMPLETE. Run your Gatekeeper to confirm.")
