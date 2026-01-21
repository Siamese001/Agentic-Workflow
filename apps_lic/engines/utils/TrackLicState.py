"""
LIC State coordinator - HOP-based state management with atomic writes.

Ported from: archives/legacy_lic/Agentic LIC/state_manager_LIC.py
"""

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class StateCheckpoint:
    """Checkpoint for a HOP state."""

    hop_id: str
    mission_id: str
    timestamp: str
    checksum: str
    filepath: str


@dataclass
class StateValidationResult:
    """Result of state validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class LICStateManager:
    """
    State management for HOP-based architecture.

    Each HOP (single-responsibility agent) reads from and writes to the
    state/ directory. This creates an auditable trail and enables:
    - Debugging: Inspect state at any HOP
    - Resumability: Re-run from any HOP
    - Auditability: Complete record of workflow decisions
    """

    SCHEMA_VERSION = "13.0"

    def __init__(
        self,
        mission_id: str,
        state_directory: str = "state",
        create_if_missing: bool = True,
    ) -> None:
        """
        Initialize state coordinator for a mission.

        Args:
            mission_id: Unique mission identifier
            state_directory: foundation directory for state files
            create_if_missing: Create directory if it doesn't exist
        """
        self.mission_id = mission_id
        self.base_dir = Path(state_directory)
        self.mission_dir = self.base_dir / mission_id
        self._checkpoints: dict[str, StateCheckpoint] = {}

        if create_if_missing:
            self.mission_dir.mkdir(parents=True, exist_ok=True)

    def write_state(
        self,
        hop_id: str,
        data: dict[str, object],
        atomic: bool = True,
    ) -> str:
        """
        Write state file for a HOP.

        Args:
            hop_id: HOP identifier (e.g., "HOP-1", "1_profile_analysis")
            data: State data to write
            atomic: Use atomic write (write to staging file, then rename)

        Returns:
            Path to written file
        """
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.mission_dir / filename

        # Add metadata
        data_with_metadata = {
            "hop_id": hop_id,
            "mission_id": self.mission_id,
            "timestamp": datetime.now().isoformat(),
            "schema_version": self.SCHEMA_VERSION,
            **data,
        }

        if atomic:
            # Atomic write: write to staging file, then rename
            staging_path = filepath.with_suffix(".staging")

            with open(staging_path, "w", encoding="utf-8") as f:
                json.dump(data_with_metadata, f, indent=2, default=str)

            # Atomic rename
            staging_path.replace(filepath)
        else:
            # Direct write
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_with_metadata, f, indent=2, default=str)

        # Calculate and store checksum
        checksum = self._calculate_checksum(filepath)
        self._checkpoints[hop_id] = StateCheckpoint(
            hop_id=hop_id,
            mission_id=self.mission_id,
            timestamp=data_with_metadata["timestamp"],
            checksum=checksum,
            filepath=str(filepath),
        )

        return str(filepath)

    def read_state(
        self,
        hop_id: str,
        validate_checksum: bool = False,
    ) -> dict[str, object]:
        """
        Read state file for a HOP.

        Args:
            hop_id: HOP identifier
            validate_checksum: Verify file integrity

        Returns:
            State data dictionary

        Raises:
            FileNotFoundError: If state file doesn't exist
            ValueError: If checksum validation fails
        """
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.mission_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"State file not found: {filepath}")

        # Validate checksum if requested
        if validate_checksum:
            stored_checkpoint = self._checkpoints.get(hop_id)
            if stored_checkpoint:
                current_checksum = self._calculate_checksum(filepath)
                if stored_checkpoint.checksum != current_checksum:
                    raise ValueError(f"Checksum mismatch for {filename}: file may be corrupted")

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        return data

    def state_exists(self, hop_id: str) -> bool:
        """Check if state file exists for a HOP."""
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.mission_dir / filename
        return filepath.exists()

    def list_states(self) -> list[str]:
        """List all state files for this mission."""
        if not self.mission_dir.exists():
            return []

        states = []
        for filepath in self.mission_dir.glob("*.json"):
            states.append(filepath.stem)
        return sorted(states)

    def delete_state(self, hop_id: str) -> bool:
        """Delete a state file."""
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = self.mission_dir / filename

        if filepath.exists():
            filepath.unlink()
            self._checkpoints.pop(hop_id, None)
            return True
        return False

    def clear_all_states(self) -> int:
        """Clear all state files for this mission."""
        if not self.mission_dir.exists():
            return 0

        count = 0
        for filepath in self.mission_dir.glob("*.json"):
            filepath.unlink()
            count += 1

        self._checkpoints.clear()
        return count

    def get_checkpoint(self, hop_id: str) -> StateCheckpoint | None:
        """Get Checkpoint for a HOP."""
        return self._checkpoints.get(hop_id)

    def get_all_checkpoints(self) -> dict[str, StateCheckpoint]:
        """Get all checkpoints."""
        return self._checkpoints.copy()

    def validate_state(self, hop_id: str) -> StateValidationResult:
        """Validate a state file."""
        result = StateValidationResult(is_valid=True)

        if not self.state_exists(hop_id):
            result.is_valid = False
            result.errors.append(f"State file not found for {hop_id}")
            return result

        try:
            data = self.read_state(hop_id)

            # Check required fields
            required_fields = ["hop_id", "mission_id", "timestamp", "schema_version"]
            for field_name in required_fields:
                if field_name not in data:
                    result.warnings.append(f"Missing field: {field_name}")

            # Check schema version
            if data.get("schema_version") != self.SCHEMA_VERSION:
                result.warnings.append(
                    f"Schema version mismatch: expected {self.SCHEMA_VERSION}, "
                    f"got {data.get('schema_version')}"
                )

        except json.JSONDecodeError as e:
            result.is_valid = False
            result.errors.append(f"Invalid JSON: {e}")
        except (ValueError, TypeError, KeyError, OSError) as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {e}")

        return result

    def export_mission(self, output_path: str) -> str:
        """Export all mission state to a single archive."""
        output_file = Path(output_path)
        if output_file.suffix != ".zip":
            output_file = output_file.with_suffix(".zip")

        shutil.make_archive(
            str(output_file.with_suffix("")),
            "zip",
            self.mission_dir,
        )

        return str(output_file)

    def _sanitize_filename(self, hop_id: str) -> str:
        """Sanitize hop_id for use as filename."""
        # Replace spaces and special characters
        sanitized = hop_id.replace(" ", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "_-.")
        return sanitized

    def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class StateValidator:
    """Validator for state consistency across HOPs."""

    def __init__(self, state_manager: LICStateManager) -> None:
        """Initialize with a state coordinator."""
        self.state_manager = state_manager

    def validate_hop_chain(self, hop_ids: list[str]) -> StateValidationResult:
        """Validate a chain of HOPs for consistency."""
        result = StateValidationResult(is_valid=True)

        for hop_id in hop_ids:
            hop_result = self.state_manager.validate_state(hop_id)
            if not hop_result.is_valid:
                result.is_valid = False
                result.errors.extend(hop_result.errors)
            result.warnings.extend(hop_result.warnings)

        return result

    def validate_dependencies(
        self,
        hop_id: str,
        required_hops: list[str],
    ) -> StateValidationResult:
        """Validate that required HOPs have completed before this HOP."""
        result = StateValidationResult(is_valid=True)

        for required_hop in required_hops:
            if not self.state_manager.state_exists(required_hop):
                result.is_valid = False
                result.errors.append(f"Required HOP {required_hop} not completed before {hop_id}")

        return result


def create_state_manager(
    mission_id: str,
    state_directory: str = "state",
) -> LICStateManager:
    """builder function to create a state coordinator."""
    return LICStateManager(mission_id, state_directory)


def create_state_validator(state_manager: LICStateManager) -> StateValidator:
    """builder function to create a state validator."""
    return StateValidator(state_manager)
