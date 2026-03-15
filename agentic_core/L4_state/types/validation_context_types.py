from __future__ import annotations

import hashlib

from agentic_core.interfaces.write_gateway import get_write_gateway


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"Brief description of functionality and purpose."
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

LOGGER = logging.getLogger(__name__)


class IValidationContextProtocol(Protocol):
    """Brief description of functionality and purpose."""

    cycle_id: int | None
    status: str
    start_time: datetime
    end_time: datetime | None
    files_scanned: int
    files_skipped: int
    violations_found: int
    flapping_files: dict[str, int]

    def update_file_hash(self, file_path: str, file_hash: str): ...

    def mark_flapping(self, file_path: str): ...


class IValidationContextManager(Protocol):
    """Brief description of functionality and purpose."""

    current_context: IValidationContextProtocol | None

    def get_last_file_hashes(self) -> dict[str, str]: ...

    def get_flapping_files(self) -> dict[str, int]: ...

    def start_new_cycle(self, cycle_id: int = None) -> IValidationContextProtocol: ...

    def complete_cycle(self, status: str = "COMPLETED"): ...

    def load_memory(self) -> bool: ...


Logger = logging.getLogger(__name__)


class Historian:
    """
    Tracks validation history and optimizes file scanning.

    Features:
    - MD5 hash-based change detection
    - Skip logic for unchanged files
    - Flapping detection for unstable files
    - Cycle history tracking
    """

    def __init__(self, context_manager: IValidationContextManager, memory_dir: Path = None):
        """
        Initialize the Historian.

        Args:
            context_manager: An instance conforming to IValidationContextManager protocol.
            memory_dir: Directory to store historical data
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "Historian.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "Historian.__init__", "p0_governance")
        self.memory_dir = memory_dir or Path("observability/memory")
        _get_write_gateway().ensure_dir(self.memory_dir)
        self.context_manager = context_manager
        self.cycle_history_file = self.memory_dir / "cycle_history.json"
        self.file_history_file = self.memory_dir / "file_history.json"
        self.last_hashes: dict[str, str] = {}
        self.file_history: dict[str, list[dict]] = {}
        self._load_memory()

    def _load_memory(self):
        self.last_hashes = self.context_manager.get_last_file_hashes()
        if self.file_history_file.exists():
            try:
                with open(self.file_history_file) as f:
                    self.file_history = json.load(f)
                LOGGER.info(f"Loaded history for {len(self.file_history)} files")
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                LOGGER.error(f"Failed to load file history: {e}")
                self.file_history = {}

    def _save_memory(self):
        """Save historical data to memory files."""
        try:
            _get_write_gateway().write_json(self.file_history_file, self.file_history, indent=2)
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            LOGGER.error(f"Failed to save file history: {e}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of file contents.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash as hex string
        """
        try:
            with open(file_path, "rb") as f:
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                return hash_md5.hexdigest()
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Failed to hash {file_path}: {e}")
            return ""

    def should_skip_file(self, file_path: Path) -> bool:
        """
        Check if a file should be skipped based on hash comparison.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be skipped (unchanged)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "Historian.should_skip_file")

        rel_path = str(file_path.relative_to(Path.cwd()))
        current_hash = self.calculate_file_hash(file_path)
        if not current_hash:
            return False
        last_hash = self.last_hashes.get(rel_path)
        if last_hash and last_hash == current_hash:
            if self._is_flapping(rel_path):
                LOGGER.debug(f"File {rel_path} is flapping, not skipping")
                return False
            LOGGER.debug(f"Skipping unchanged file: {rel_path}")
            return True
        return False

    def _is_flapping(self, file_path: str) -> bool:
        """
        Check if a file is flapping (toggling status frequently).

        Args:
            file_path: Relative file path

        Returns:
            True if file is flapping
        """
        flapping_files = self.context_manager.get_flapping_files()
        return flapping_files.get(file_path, 0) >= 3

    def record_file_result(self, file_path: Path, status: str, violations: list = None):
        """
        Record validation result for a file.

        Args:
            file_path: Path to the file
            status: Validation status (PASS/FAIL)
            violations: List of violations found
        """
        rel_path = str(file_path.relative_to(Path.cwd()))
        current_hash = self.calculate_file_hash(file_path)
        context = self.context_manager.current_context
        if context:
            context.update_file_hash(rel_path, current_hash)
            if rel_path in self.file_history:
                last_status = self.file_history[rel_path][-1].get("status")
                if last_status != status:
                    context.mark_flapping(rel_path)
                    LOGGER.debug(f"File {rel_path} status changed: {last_status} -> {status}")
        if rel_path not in self.file_history:
            self.file_history[rel_path] = []
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "hash": current_hash,
            "status": status,
            "violations_count": len(violations) if violations else 0,
        }
        self.file_history[rel_path].append(record)
        if len(self.file_history[rel_path]) > 10:
            self.file_history[rel_path] = self.file_history[rel_path][-10:]

    def get_unchanged_files(self, file_list: list[Path]) -> tuple[set[Path], set[Path]]:
        """
        Separate files into unchanged and modified sets.

        Args:
            file_list: List of files to check

        Returns:
            Tuple of (unchanged_files, modified_files)
        """
        unchanged = set()
        modified = set()
        for file_path in file_list:
            if self.should_skip_file(file_path):
                unchanged.add(file_path)
            else:
                modified.add(file_path)
        return (unchanged, modified)

    def start_cycle(self, cycle_id: int = None) -> IValidationContextProtocol:
        """
        Start a new validation cycle.

        Args:
            cycle_id: Optional cycle ID

        Returns:
            New ValidationContext
        """
        return self.context_manager.start_new_cycle(cycle_id)

    def complete_cycle(self, status: str = "COMPLETED"):
        """
        Complete the current cycle and save history.

        Args:
            status: Cycle completion status
        """
        context = self.context_manager.current_context
        if context:
            LOGGER.info(f"[Historian] Cycle {context.cycle_id} complete:")
            LOGGER.info(f"  Files scanned: {context.files_scanned}")
            LOGGER.info(f"  Files skipped: {context.files_skipped}")
            LOGGER.info(f"  Violations found: {context.violations_found}")
            total_files = context.files_scanned + context.files_skipped
            if total_files > 0:
                skip_percent = context.files_skipped / total_files * 100
                LOGGER.info(f"  Skip efficiency: {skip_percent:.1f}%")
        self.context_manager.complete_cycle(status)
        self._save_memory()

    def get_file_statistics(self, file_path: Path) -> dict:
        """
        Get validation statistics for a file.

        Args:
            file_path: Path to the file

        Returns:
            Statistics dictionary
        """
        rel_path = str(file_path.relative_to(Path.cwd()))
        if rel_path not in self.file_history:
            return {"validations": 0}
        history = self.file_history[rel_path]
        total_validations = len(history)
        failures = sum(1 for record in history if record.get("status") == "FAIL")
        last_validation = history[-1] if history else None
        return {
            "validations": total_validations,
            "failures": failures,
            "success_rate": (total_validations - failures) / total_validations * 100
            if total_validations > 0
            else 0,
            "last_status": last_validation.get("status") if last_validation else None,
            "last_validated": last_validation.get("timestamp") if last_validation else None,
            "is_flapping": self._is_flapping(rel_path),
        }

    def get_cycle_summary(self) -> dict:
        """
        Get summary of the current cycle.

        Returns:
            Cycle summary dictionary
        """
        context = self.context_manager.current_context
        if not context:
            return {"status": "No active cycle"}
        duration = None
        if context.end_time:
            duration = (context.end_time - context.start_time).total_seconds()
        elif context.start_time:
            duration = (datetime.utcnow() - context.start_time).total_seconds()
        return {
            "cycle_id": context.cycle_id,
            "status": context.status,
            "duration_seconds": duration,
            "files_scanned": context.files_scanned,
            "files_skipped": context.files_skipped,
            "violations_found": context.violations_found,
            "flapping_files": len(context.flapping_files),
        }


_historian: Historian | None = None


def get_historian() -> Historian:
    """Get the global Historian instance. Must be initialized first."""
    global _historian
    if _historian is None:
        raise RuntimeError("Historian has not been initialized. Call initialize_historian first.")
    return _historian


def initialize_historian(context_manager: IValidationContextManager, memory_dir: Path = None):
    """
    Initialize the Historian system.

    Args:
        context_manager: An instance conforming to IValidationContextManager protocol.
        memory_dir: Directory for storing historical data
    """
    global _historian
    _historian = Historian(context_manager, memory_dir)
    if _historian.context_manager.load_memory():
        LOGGER.info("Historian initialized with existing memory")
    else:
        LOGGER.info("Historian initialized (fresh start)")


def should_skip_file(file_path: Path) -> bool:
    """Check if a file should be skipped."""
    Historian = get_historian()
    return Historian.should_skip_file(file_path)


def record_validation_result(file_path: Path, status: str, violations: list = None):
    """Record validation result for a file."""
    Historian = get_historian()
    Historian.record_file_result(file_path, status, violations)
