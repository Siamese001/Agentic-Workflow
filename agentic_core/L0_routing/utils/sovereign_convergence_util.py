from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_convergence_util")
emit_determinism_digest("p0", "sovereign_convergence_util")

_emit_dispatches_healing_run("p1", "sovereign_convergence_util", "L0")
_emit_routes_through("p1", "sovereign_convergence_util", "L0")
_emit_escalates_to_human("p1", "sovereign_convergence_util", "L0")
_emit_reads_policy_state("p1", "sovereign_convergence_util", "L0")

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
migration_map: Any = {}


def align_territory() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "align_territory", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "align_territory", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "align_territory")
    print("[*] STARTING SOVEREIGN CONVERGENCE...")
    for source, target in MIGRATION_MAP.items():
        src_path: Any = ROOT / source
        dest_path: Any = ROOT / target
        if src_path.exists():
            print(f"  [>] Migrating Drift: {source} -> {target}")
            dest_path.mkdir(parents=True, exist_ok=True)
            for item in src_path.iterdir():
                if item.is_file():
                    assert_no_persistent_write("L0", "shutil.mutate")
                    shutil.move(str(item), str(dest_path / item.name))
                elif item.is_dir():
                    assert_no_persistent_write("L0", "shutil.mutate")
                    shutil.move(str(item), str(dest_path / item.name))
            try:
                src_path.rmdir()
                print(f"      [x] Removed legacy shell: {source}")
            except OSError:
                print(f"      [!] Warning: Could not remove {source} (not empty?)")
        else:
            print(f"  [-] Skipped: {source} (Not found)")
    print("\n[*] REWIRING IMPORTS...")
    replacements: Any = []
    count: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(ROOT):
        if "legacy_code" in str(py_file):
            continue
        try:
            with open(py_file, encoding="utf-8") as f:
                content: Any = f.read()
            original_content: Any = content
            for old, new in replacements:
                content: Any = re.sub(old, new, content)
            if content != original_content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  [✓] Rewired: {py_file.relative_to(ROOT)}")
                count += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  [!] Failed to process {py_file}: {e}")
    print(f"\n[OK] CONVERGENCE COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")


if __name__ == "__main__":
    align_territory()
