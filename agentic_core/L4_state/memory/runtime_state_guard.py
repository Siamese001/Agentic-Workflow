import json
import os
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint_config import RUNTIME_STATE_JSON


class RuntimeStateGuard:
    """
    Atomic guardian for runtime_state.json.
    Implements Write-Replace pattern and automatic backup recovery.
    """

    def __init__(self, project_root: Path):
        self.state_path = project_root / RUNTIME_STATE_JSON
        self.backup_path = project_root / f"{RUNTIME_STATE_JSON}.bak"
        self._state_cache: dict[str, Any] = {}
        self._batch_depth = 0  # [OPTIMIZATION] Track nesting level for batching
        self._dirty = False  # [OPTIMIZATION] Track if memory differs from disk
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
                shutil.copy(self.backup_path, self.state_path)
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
        metrics = self._state_cache.get("shared_alignment_metrics", {})
        current = metrics.get(key, 0)
        metrics[key] = current + value
        self._state_cache["shared_alignment_metrics"] = metrics

        if self._batch_depth > 0:
            self._dirty = True  # Defer write
        else:
            self._atomic_persist()

    def _atomic_persist(self):
        """
        Writes to a temp file then renames to ensure atomicity.
        Prevents half-written files during crashes.
        """
        temp_path = self.state_path.with_suffix(".tmp")
        try:
            # 1. Write to temp
            with open(temp_path, "w") as f:
                json.dump(self._state_cache, f, indent=4)

            # 2. Create backup of current valid state
            if self.state_path.exists():
                shutil.copy(self.state_path, self.backup_path)

            # 3. Atomic rename (replace)
            os.replace(temp_path, self.state_path)
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[StateGuard] PERSISTENCE FAILURE: {e}")
            if temp_path.exists():
                os.remove(temp_path)
