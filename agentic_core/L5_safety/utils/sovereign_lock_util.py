from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_lock_util")
emit_determinism_digest("p0", "sovereign_lock_util")

_emit_dispatches_healing_run("p1", "sovereign_lock_util", "L5")
_emit_routes_through("p1", "sovereign_lock_util", "L5")
_emit_escalates_to_human("p1", "sovereign_lock_util", "L5")
_emit_reads_policy_state("p1", "sovereign_lock_util", "L5")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

root: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR


def enforce_gravity() -> Any:
    """Ensures no file in agentic_core reaches 'down' into apps."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "enforce_gravity", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "enforce_gravity", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "enforce_gravity")
    print("[*] ENFORCING GRAVITY...")
    violations: Any = 0
    forbidden: Any = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(CORE):
        if py_file.name == "__init__.py":
            continue
        content: Any = py_file.read_text(encoding="utf-8")
        for f in forbidden:
            if f in content:
                if re.search(f"^(import\\s+{f}|from\\s+{f})", content, re.M):
                    print(f"  [X] GRAVITY BREACH: {py_file.relative_to(ROOT)} imports {f}!")
                    violations += 1
    return violations


def enforce_depth() -> Any:
    """Ensures every file is EXACTLY at Depth 4. No shallower, no deeper."""
    print("[*] ENFORCING ABSOLUTE DEPTH-4 MANDATE...")
    violations: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(CORE):
        if py_file.name == "__init__.py":
            continue
        parts: Any = py_file.relative_to(CORE).parts
        if len(parts) != 3:
            depth_status: Any = "SHALLOW" if len(parts) < 3 else "TUNNEL"
            print(f"  [X] {depth_status} VIOLATION: {py_file.relative_to(ROOT)}")
            print(f"      Actual: {len(parts) + 1} | Required: 4")
            violations += 1
    return violations


def check_airlocks() -> Any:
    """Ensures __init__.py files are minimal (under 50 lines)."""
    print("[*] CHECKING AIRLOCK HYGIENE...")
    violations: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for init_file in [f for f in get_python_files(CORE) if f.name == "__init__.py"]:
        lines: Any = init_file.read_text(encoding="utf-8").splitlines()
        if len(lines) > 50:
            print(f"  [X] HEAVY AIRLOCK: {init_file.relative_to(ROOT)} has {len(lines)} lines. Keep it lean!")
            violations += 1
    return violations


if __name__ == "__main__":
    v1: Any = enforce_gravity()
    v2: Any = enforce_depth()
    v3: Any = check_airlocks()
    total: Any = v1 + v2 + v3
    if total > 0:
        print(f"\n[BLOCK] {total} Sovereignty Violations detected. Fix these before committing.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Sovereign Core is locked and compliant. Move forward.")
        sys.exit(0)
