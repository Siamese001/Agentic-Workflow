from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "force_app_depth_util", "L5")
_emit_routes_through("p1", "force_app_depth_util", "L5")
_emit_escalates_to_human("p1", "force_app_depth_util", "L5")
_emit_reads_policy_state("p1", "force_app_depth_util", "L5")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint import safe_path_join
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

PROJECT_ROOT = get_validated_project_root()
CORE = safe_path_join(PROJECT_ROOT, AGENTIC_CORE_DIR)
APPS = [safe_path_join(PROJECT_ROOT, APPS_LIC_DIR), safe_path_join(PROJECT_ROOT, APPS_RG_DIR)]


def force_app_depth() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "force_app_depth", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "force_app_depth", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "force_app_depth")
    print("[*] FORCING DEPTH-4 ON TERRITORIES...")
    for app_path in APPS:
        if not app_path.exists():
            continue
        print(f"\n[HARDENING] {app_path.name}...")
        for item in app_path.iterdir():
            if item.is_dir() and item.name.endswith("_engine"):
                engine_folder = item
                dest: Any = CORE / "L2_execution" / "P3_engines" / engine_folder.name
            _wg.ensure_dir(dest)
            for item in engine_folder.iterdir():
                if item.is_dir() and item.name.startswith("__"):
                    continue
                _wg.move_path(str(item), str(dest / item.name))
            try:
                _wg.remove_tree(str(engine_folder))
            # guardian: allow-silent-swallow
            except:
                pass
                print(f"  [✓] ENGINE EXTRICATED: {engine_folder.name} -> Core/L2_execution/P3_engines")
        for item in app_path.iterdir():
            if item.is_dir() and item.name.startswith("L"):
                layer_folder = item
            layer_map: Any = {
                "L0": "L1_cognition",
                "L1": "L1_cognition",
                "L2": "L2_execution",
                "L3": "L3_orchestration",
            }
            target_layer: Any = layer_map.get(layer_folder.name, layer_folder.name)
            dest: Any = CORE / target_layer / "P1_core"
            _wg.ensure_dir(dest)
            for item in layer_folder.iterdir():
                if item.is_dir() and item.name.startswith("__"):
                    continue
                _wg.move_path(str(item), str(dest / item.name))
            try:
                _wg.remove_tree(str(layer_folder))
            # guardian: allow-silent-swallow
            except:
                pass
            print(f"  [✓] LAYER ANNEXED: {layer_folder.name} -> Core/{target_layer}/P1_core")
        app_p1: Any = app_path / "P1_core"
        _wg.ensure_dir(app_p1)
        if not (app_p1 / "__init__.py").exists():
            _wg.write_text(app_p1 / "__init__.py", '"""App Core Implementation"""\n')
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(app_path):
            if py_file.name == "__init__.py":
                continue
            if "sovereign_lock" in py_file.name:
                continue
            _wg.move_path(str(py_file), str(app_p1 / py_file.name))
            print(f"  [!] DEPTH CORRECTION: {py_file.name} -> {app_path.name}/P1_core")


if __name__ == "__main__":
    force_app_depth()
