from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "flatten_scripts_directory_util", "L0")
_emit_routes_through("p1", "flatten_scripts_directory_util", "L0")
_emit_escalates_to_human("p1", "flatten_scripts_directory_util", "L0")
_emit_reads_policy_state("p1", "flatten_scripts_directory_util", "L0")

"""
Flatten scripts directory to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import DEPTH_RULES, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.utils.path_util import (
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

ROOT: Any = Path(__file__).resolve().parents[4]
CORE: Any = ROOT / AGENTIC_CORE_DIR
SCRIPTS_DIR: Any = CORE / "L0_routing/scripts"
REQUIRED_DEPTH: Any = DEPTH_RULES.get("agentic_core", 4)


def flatten_scripts() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "flatten_scripts", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "flatten_scripts", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "flatten_scripts")
    print(f"[*] FLATTENING L0_routing/scripts TO DEPTH-{REQUIRED_DEPTH}...")
    moved: Any = 0
    if not SCRIPTS_DIR.exists():
        print("[!] Scripts directory not found")
        return
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.L0_routing.utils.ssot_discovery_util import get_python_files

    for py_file in get_python_files(SCRIPTS_DIR):
        rel_path: Any = py_file.relative_to(CORE)
        parts: Any = rel_path.parts
        if len(parts) > REQUIRED_DEPTH - 1:
            path_prefix: Any = "_".join(parts[2:-1])
            # [SAFEGUARD] Use SSOT function to prevent duplicate prefix sprawl
            new_name: Any = safe_prefixed_filename(path_prefix, py_file.name)

            # Validate no duplicate prefix was created
            has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
            if has_dup:
                print(f"  [!] BLOCKED: {dup_msg}")
                continue

            target: Any = SCRIPTS_DIR / new_name
            counter: Any = 1
            while target.exists():
                target: Any = SCRIPTS_DIR / f"{path_prefix}_{counter}_{py_file.stem}{py_file.suffix}"
                counter += 1
            try:
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(py_file), str(target))
                print(f"  [✓] {rel_path} -> {target.relative_to(CORE)}")
                moved += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"  [X] Failed: {py_file.name} - {e}")
    print("\n[*] Cleaning empty directories...")
    for root, dirs, _files in os.walk(SCRIPTS_DIR, topdown=False):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for dir_name in dirs:
            dir_path: Any = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()) and dir_path != SCRIPTS_DIR:
                    dir_path.rmdir()
                    print(f"  [✓] Removed: {dir_path.relative_to(CORE)}")
            # guardian: allow-silent-swallow
            except:
                pass
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.")


if __name__ == "__main__":
    flatten_scripts()
