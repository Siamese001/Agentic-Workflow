"""State management module for execute_ssot - extracted during Wave 1 modularization.

This module contains RuntimeStateManager for managing execution state and checkpoints.
"""

from typing import Any, Dict, List, Optional
import json
import time


class RuntimeStateManager:
    """Manages runtime state, checkpoints, and recovery for execute_ssot.

    This class handles:
    - State persistence across phases
    - Checkpoint creation and restoration
    - Recovery from failures
    - Progress tracking
    """

    def __init__(self, checkpoint_dir: Optional[str] = None):
        self.checkpoint_dir = checkpoint_dir
        self.state: Dict[str, Any] = {}
        self.checkpoints: List[Dict] = []
        self.current_phase: Optional[str] = None
        self.start_time: Optional[float] = None

    def initialize(self, initial_state: Dict[str, Any]) -> None:
        """Initialize state manager with initial state.

        Args:
            initial_state: Initial state dictionary
        """
        self.state = initial_state.copy()
        self.start_time = time.time()
        self.checkpoints = []

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set a value in state.

        Args:
            key: State key
            value: Value to set
        """
        self.state[key] = value

    def create_checkpoint(self, phase: str, metadata: Optional[Dict] = None) -> int:
        """Create a checkpoint for the current phase.

        Args:
            phase: Current phase name
            metadata: Additional checkpoint metadata

        Returns:
            Checkpoint index
        """
        self.current_phase = phase
        checkpoint = {
            "timestamp": time.time(),
            "phase": phase,
            "state": self.state.copy(),
            "metadata": metadata or {}
        }
        self.checkpoints.append(checkpoint)
        return len(self.checkpoints) - 1

    def restore_checkpoint(self, index: int) -> bool:
        """Restore state from a checkpoint.

        Args:
            index: Checkpoint index to restore

        Returns:
            True if restoration successful
        """
        if index < 0 or index >= len(self.checkpoints):
            return False

        checkpoint = self.checkpoints[index]
        self.state = checkpoint["state"].copy()
        self.current_phase = checkpoint["phase"]
        return True

    def get_latest_checkpoint(self) -> Optional[Dict]:
        """Get the latest checkpoint.

        Returns:
            Latest checkpoint or None if no checkpoints
        """
        if not self.checkpoints:
            return None
        return self.checkpoints[-1]

    def save_to_disk(self, filepath: str) -> tuple[bool, Optional[str]]:
        """Save current state to disk.

        Args:
            filepath: Path to save state

        Returns:
            Tuple of (success, error_message)
        """
        try:
            data = {
                "state": self.state,
                "checkpoints": self.checkpoints,
                "current_phase": self.current_phase,
                "start_time": self.start_time
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True, None
        except Exception as e:
            return False, str(e)

    def load_from_disk(self, filepath: str) -> tuple[bool, Optional[str]]:
        """Load state from disk.

        Args:
            filepath: Path to load state from

        Returns:
            Tuple of (success, error_message)
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.state = data.get("state", {})
            self.checkpoints = data.get("checkpoints", [])
            self.current_phase = data.get("current_phase")
            self.start_time = data.get("start_time")
            return True, None
        except Exception as e:
            return False, str(e)

    def get_elapsed_time(self) -> float:
        """Get elapsed time since initialization.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def reset(self) -> None:
        """Reset state manager to initial state."""
        self.state = {}
        self.checkpoints = []
        self.current_phase = None
        self.start_time = None
