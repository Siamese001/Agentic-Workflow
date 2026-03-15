import json
import os
from pathlib import Path
from typing import Any

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.L0_routing.config import RUNTIME_STATE_JSON
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


class RuntimeStateGuard:
    """
    Atomic guardian for runtime_state.json.
    Implements Write-Replace pattern and automatic backup recovery.
    """

    def __init__(self, project_root: Path):
        self.state_path = project_root / RUNTIME_STATE_JSON
        self.backup_path = project_root / f"{RUNTIME_STATE_JSON}.bak"
        self._state_cache: dict[str, Any] = {}
        self._batch_depth = 0
        self._dirty = False
        self._load_state()

    def __enter__(self):
        """Enter batch mode: suspend disk writes."""
        self._batch_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit batch mode: flush if at top level and dirty."""
        self._batch_depth = max(0, self._batch_depth - 1)
        if self._batch_depth == 0 and self._dirty:
            self._atomic_persist()
            self._dirty = False

    def _load_state(self):
        """Loads state with failover to backup if corruption is detected."""
        if not self.state_path.exists():
            self._state_cache = {}
            return
        try:
            with open(self.state_path) as f:
                self._state_cache = json.load(f)
        except json.JSONDecodeError:
            print(f"[StateGuard] CORRUPTION DETECTED in {self.state_path}. Attempting restore...")
            if self.backup_path.exists():
                _get_write_gateway().copy_file(self.backup_path, self.state_path)
                with open(self.state_path) as f:
                    self._state_cache = json.load(f)
            else:
                print("[StateGuard] No backup found. Resetting state.")
                self._state_cache = {}

    def get_metric(self, key: str, default: Any = 0) -> Any:
        return self._state_cache.get("shared_alignment_metrics", {}).get(key, default)

    def increment_metric(self, key: str, value: int = 1):
        """
        Updates metric.
        Persists immediately UNLESS inside a batch context.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RuntimeStateGuard.increment_metric")

        metrics = self._state_cache.get("shared_alignment_metrics", {})
        current = metrics.get(key, 0)
        metrics[key] = current + value
        self._state_cache["shared_alignment_metrics"] = metrics
        if self._batch_depth > 0:
            self._dirty = True
        else:
            self._atomic_persist()

    def _atomic_persist(self):
        """
        Writes to a temp file then renames to ensure atomicity.
        Prevents half-written files during crashes.
        """
        temp_path = self.state_path.with_suffix(".tmp")
        try:
            assert_no_persistent_write("L4", "json.dump")
            _get_write_gateway().write_json(temp_path, self._state_cache, indent=4)
            if self.state_path.exists():
                _get_write_gateway().copy_file(self.state_path, self.backup_path)
            os.replace(temp_path, self.state_path)
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[StateGuard] PERSISTENCE FAILURE: {e}")
            if temp_path.exists():
                assert_no_persistent_write("L4", "os.mutate")
                _get_write_gateway().remove_file(temp_path)
