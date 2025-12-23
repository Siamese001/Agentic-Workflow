"""
ValidationContext - State management for validation cycles

Tracks modified files, signals, and file hashes across cycles
to optimize performance and prevent unnecessary re-scanning.
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
import time


import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

LOGGER = logging.getLogger(__name__)


@dataclass
class ValidationContext:
    """
    Context for a validation cycle.

    Tracks:
    - Modified files in this cycle
    - Signals generated during validation
    - File hashes for change detection
    - Cycle metadata
    """
    # Core tracking
    modified_files: Set[Path] = field(default_factory=set)
    signals: List[str] = field(default_factory=list)
    file_hashes: Dict[str, str] = field(default_factory=dict)

    # Cycle metadata
    cycle_id: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED

    # Statistics
    files_scanned: int = 0
    files_skipped: int = 0
    violations_found: int = 0

    # Flapping detection
    flapping_files: Dict[str, int] = field(default_factory=dict)
    recent_cycles: List[Dict[str, Any]] = field(default_factory=list)

    def add_modified_file(self, file_path: Path):
        """Add a file to the modified set."""
        self.modified_files.add(file_path)

    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.signals.append(signal)

    def update_file_hash(self, file_path: str, file_hash: str):
        """Update the hash for a file."""
        self.file_hashes[file_path] = file_hash

    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Get the hash for a file."""
        return self.file_hashes.get(file_path)

    def mark_flapping(self, file_path: str):
        """Mark a file as flapping (toggling status)."""
        self.flapping_files[file_path] = self.flapping_files.get(file_path, 0) + 1

    def is_flapping(self, file_path: str, threshold: int = 3) -> bool:
        """Check if a file is flapping."""
        return self.flapping_files.get(file_path, 0) >= threshold

    def signal_healing_cycle(self, cycle_number: int, max_cycles: int = 5):
        """Signal the start of a healing cycle."""
        print(f"   [~] Healing Cycle {cycle_number}/{max_cycles}")

    def signal_convergence(self):
        """Signal that the validation has converged (no more changes)."""
        print("   [OK] Convergence achieved - no modifications in this cycle")
        self.add_signal("CONVERGENCE")

    def complete(self, status: str = "COMPLETED"):
        """Mark the cycle as complete."""
        self.end_time = datetime.utcnow()
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data["modified_files"] = [str(p) for p in self.modified_files]
        # Convert datetime objects to ISO strings
        data["start_time"] = self.start_time.isoformat()
        data["end_time"] = self.end_time.isoformat() if self.end_time else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationContext":
        """Create from dictionary."""
        # Convert string paths back to Path objects
        if "modified_files" in data:
            data["modified_files"] = {Path(p) for p in data["modified_files"]}
        # Convert ISO strings back to datetime
        if "start_time" in data and data["start_time"]:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if "end_time" in data and data["end_time"]:
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        return cls(**data)

    def save_to_file(self, file_path: Path):
        """Save context to file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            LOGGER.debug(f"Saved ValidationContext to {file_path}")
        except Exception as e:
            LOGGER.error(f"Failed to save ValidationContext: {e}")

    @classmethod
    def load_from_file(cls, file_path: Path) -> Optional["ValidationContext"]:
        """Load context from file."""
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r') as f:
                data = json.load(f)
            LOGGER.debug(f"Loaded ValidationContext from {file_path}")
            return cls.from_dict(data)
        except Exception as e:
            LOGGER.error(f"Failed to load ValidationContext: {e}")
            return None


class ValidationContextManager:
    """
    Manages ValidationContext persistence and history.
    """

    def __init__(self, memory_dir: Path = None):
        """
        Initialize the manager.

        Args:
            memory_dir: Directory to store context files
        """
        self.memory_dir = memory_dir or Path("observability/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.current_context: Optional[ValidationContext] = None
        self.context_history: List[ValidationContext] = []

        # Memory files
        self.canon_memory_file = self.memory_dir / "canon_memory.json"
        self.current_context_file = self.memory_dir / "current_context.json"

    def start_new_cycle(self, cycle_id: int = None) -> ValidationContext:
        """
        Start a new validation cycle.

        Args:
            cycle_id: Optional cycle ID, auto-incremented if not provided

        Returns:
            New ValidationContext
        """
        if cycle_id is None:
            # Get last cycle ID from history
            last_id = 0
            if self.context_history:
                last_id = max(ctx.cycle_id for ctx in self.context_history)
            cycle_id = last_id + 1

        self.current_context = ValidationContext(cycle_id=cycle_id)
        LOGGER.info(f"Started validation cycle {cycle_id}")
        return self.current_context

    def complete_cycle(self, status: str = "COMPLETED"):
        """Complete the current cycle and save to history."""
        if not self.current_context:
            LOGGER.warning("No active cycle to complete")
            return

        self.current_context.complete(status)
        self.context_history.append(self.current_context)

        # Save to memory
        self._save_memory()

        LOGGER.info(f"Completed cycle {self.current_context.cycle_id} with status {status}")

    def _save_memory(self):
        """Save context memory to files."""
        # Save current context
        if self.current_context:
            self.current_context.save_to_file(self.current_context_file)

        # Save canon memory (last cycle data)
        if self.context_history:
            last_context = self.context_history[-1]
            memory_data = {
                "last_cycle_id": last_context.cycle_id,
                "file_hashes": last_context.file_hashes,
                "flapping_files": last_context.flapping_files,
                "timestamp": last_context.end_time.isoformat() if last_context.end_time else None
            }

            with open(self.canon_memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)

    def load_memory(self) -> bool:
        """
        Load saved memory from files.

        Returns:
            True if memory was loaded successfully
        """
        # Load canon memory
        if self.canon_memory_file.exists():
            try:
                with open(self.canon_memory_file, 'r') as f:
                    memory_data = json.load(f)

                LOGGER.info(f"Loaded memory from cycle {memory_data.get('last_cycle_id')}")
                return True
            except Exception as e:
                LOGGER.error(f"Failed to load canon memory: {e}")

        return False

    def get_last_file_hashes(self) -> Dict[str, str]:
        """Get file hashes from the last cycle."""
        if self.canon_memory_file.exists():
            try:
                with open(self.canon_memory_file, 'r') as f:
                    memory_data = json.load(f)
                return memory_data.get("file_hashes", {})
            except Exception as e:
                LOGGER.error(f"Failed to load file hashes: {e}")

        return {}

    def get_flapping_files(self) -> Dict[str, int]:
        """Get flapping files from history."""
        if self.canon_memory_file.exists():
            try:
                with open(self.canon_memory_file, 'r') as f:
                    memory_data = json.load(f)
                return memory_data.get("flapping_files", {})
            except Exception as e:
                LOGGER.error(f"Failed to load flapping files: {e}")

        return {}


# Global instance
_context_manager: Optional[ValidationContextManager] = None


def get_context_manager() -> ValidationContextManager:
    """Get or create the global context manager."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ValidationContextManager()
    return _context_manager


def get_current_context() -> Optional[ValidationContext]:
    """Get the current validation context."""
    manager = get_context_manager()
    return manager.current_context
