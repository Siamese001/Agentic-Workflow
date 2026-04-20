"""Canonical Store.

Persistent storage for canonical raw units with version comparison,
conflict resolution, and graph lineage preservation for Pipeline B Phase B2.
"""

import json
import logging
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

from .canonical_types import (
    CanonicalDiff,
    CanonicalRawUnit,
)

log = logging.getLogger(__name__)


class CanonicalStore:
    """Persistent storage for canonical raw units.

    The CanonicalStore implements the storage layer for Pipeline B Phase B2.
    It provides persistent storage, version comparison, conflict resolution,
    and graph lineage preservation for canonical raw units.
    """

    def __init__(self, storage_path: Path | None = None):
        """Initialize the canonical store.

        Args:
            storage_path: Path to storage directory (defaults to knowledge/canonical_store)
        """
        if storage_path is None:
            from agentic_core.L0_routing.config import AGENTIC_CORE_DIR

            storage_path = AGENTIC_CORE_DIR / "knowledge" / "canonical_store"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage subdirectories
        self.units_path = self.storage_path / "units"
        self.units_path.mkdir(exist_ok=True)

        self.index_path = self.storage_path / "index"
        self.index_path.mkdir(exist_ok=True)

        self.lineage_path = self.storage_path / "lineage"
        self.lineage_path.mkdir(exist_ok=True)

        # In-memory caches
        self._unit_cache: dict[str, CanonicalRawUnit] = {}
        self._index_cache: dict[str, list[str]] = {}  # unit_id -> list of versions
        self._lineage_cache: dict[str, set[str]] = {}  # parent_id -> set of child_ids

        # Load existing data
        self._load_indices()

    def store_unit(self, unit: CanonicalRawUnit) -> bool:
        """Store a canonical unit in persistent storage.

        Args:
            unit: The canonical unit to store

        Returns:
            True if stored successfully, False otherwise
        """
        trace_id = f"store_{unit.identifier.unit_id}_{unit.identifier.version}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L4_STATE,
            "CanonicalStore.store_unit",
        )

        try:
            # Store unit file
            unit_file = self.units_path / f"{unit.identifier.unit_id}_v{unit.identifier.version}.json"
            with open(unit_file, "w", encoding="utf-8") as f:
                json.dump(unit.to_dict(), f, indent=2, default=str)

            # Update caches
            self._unit_cache[f"{unit.identifier.unit_id}:v{unit.identifier.version}"] = unit

            # Update index
            if unit.identifier.unit_id not in self._index_cache:
                self._index_cache[unit.identifier.unit_id] = []
            self._index_cache[unit.identifier.unit_id].append(f"v{unit.identifier.version}")
            self._save_index(unit.identifier.unit_id)

            # Update lineage
            if unit.lineage.parent_id:
                if unit.lineage.parent_id not in self._lineage_cache:
                    self._lineage_cache[unit.lineage.parent_id] = set()
                self._lineage_cache[unit.lineage.parent_id].add(unit.identifier.unit_id)
                self._save_lineage(unit.lineage.parent_id)

            log.debug(f"Stored canonical unit: {unit.identifier.unit_id}:v{unit.identifier.version}")
            return True

        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            log.error(f"Failed to store unit {unit.identifier.unit_id}: {e}")
            return False

    def get_unit(self, unit_id: str, version: int | None = None) -> CanonicalRawUnit | None:
        """Retrieve a canonical unit from storage.

        Args:
            unit_id: The unit ID to retrieve
            version: Specific version (latest if None)

        Returns:
            CanonicalRawUnit if found, None otherwise
        """
        if version is None:
            version = self._get_latest_version(unit_id)
            if version is None:
                return None

        cache_key = f"{unit_id}:v{version}"

        # Check cache first
        if cache_key in self._unit_cache:
            return self._unit_cache[cache_key]

        # Load from storage
        unit_file = self.units_path / f"{unit_id}_v{version}.json"
        if not unit_file.exists():
            return None

        try:
            with open(unit_file, encoding="utf-8") as f:
                data = json.load(f)

            unit = CanonicalRawUnit.from_dict(data)
            self._unit_cache[cache_key] = unit
            return unit

        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-return-none-swallow -- unit load: non-fatal, caller handles None as missing unit
            log.error(f"Failed to load unit {unit_id}:v{version}: {e}")
            return None

    def get_latest_unit(self, unit_id: str) -> CanonicalRawUnit | None:
        """Get the latest version of a unit.

        Args:
            unit_id: The unit ID to retrieve

        Returns:
            Latest CanonicalRawUnit if found, None otherwise
        """
        latest_version = self._get_latest_version(unit_id)
        if latest_version is None:
            return None
        return self.get_unit(unit_id, latest_version)

    def get_unit_versions(self, unit_id: str) -> list[int]:
        """Get all available versions for a unit.

        Args:
            unit_id: The unit ID

        Returns:
            List of version numbers
        """
        if unit_id in self._index_cache:
            version_strings = self._index_cache[unit_id]
            return [int(v[1:]) for v in version_strings if v.startswith("v")]
        return []

    def get_children(self, parent_id: str) -> list[CanonicalRawUnit]:
        """Get all child units of a parent.

        Args:
            parent_id: The parent unit ID

        Returns:
            List of child CanonicalRawUnit objects
        """
        if parent_id not in self._lineage_cache:
            return []

        child_ids = self._lineage_cache[parent_id]
        children = []

        for child_id in child_ids:
            child = self.get_latest_unit(child_id)
            if child:
                children.append(child)

        return children

    def find_by_checksum(self, checksum: str) -> list[CanonicalRawUnit]:
        """Find units by content checksum.

        Args:
            checksum: The checksum to search for

        Returns:
            List of matching CanonicalRawUnit objects
        """
        matches = []

        for unit_id in self._index_cache:
            latest_unit = self.get_latest_unit(unit_id)
            if latest_unit and latest_unit.identifier.checksum == checksum:
                matches.append(latest_unit)

        return matches

    def find_by_content_type(self, content_type: str) -> list[CanonicalRawUnit]:
        """Find units by content type.

        Args:
            content_type: The content type to search for

        Returns:
            List of matching CanonicalRawUnit objects
        """
        matches = []

        for unit_id in self._index_cache:
            latest_unit = self.get_latest_unit(unit_id)
            if latest_unit and latest_unit.metadata.content_type == content_type:
                matches.append(latest_unit)

        return matches

    def find_active_units(self) -> list[CanonicalRawUnit]:
        """Get all active (non-tombstoned, non-superseded) units.

        Returns:
            List of active CanonicalRawUnit objects
        """
        active_units = []

        for unit_id in self._index_cache:
            latest_unit = self.get_latest_unit(unit_id)
            if latest_unit and latest_unit.is_active():
                active_units.append(latest_unit)

        return active_units

    def compare_versions(self, unit_id: str, version1: int, version2: int) -> CanonicalDiff:
        """Compare two versions of a unit.

        Args:
            unit_id: The unit ID
            version1: First version number
            version2: Second version number

        Returns:
            CanonicalDiff showing the differences
        """
        unit1 = self.get_unit(unit_id, version1)
        unit2 = self.get_unit(unit_id, version2)

        if not unit1 or not unit2:
            raise ValueError(f"Cannot compare versions for unit {unit_id}")

        changes = []

        # Content changes
        if unit1.content != unit2.content:
            changes.append("Content changed")

        # Metadata changes
        if unit1.metadata.size_bytes != unit2.metadata.size_bytes:
            changes.append(f"Size changed: {unit1.metadata.size_bytes} -> {unit2.metadata.size_bytes}")

        if unit1.metadata.token_count != unit2.metadata.token_count:
            changes.append(
                f"Token count changed: {unit1.metadata.token_count} -> {unit2.metadata.token_count}"
            )

        # Status changes
        if unit1.status != unit2.status:
            changes.append(f"Status changed: {unit1.status.value} -> {unit2.status.value}")

        # Determine change type
        if version1 < version2:
            change_type = "updated"
        elif version1 > version2:
            change_type = "reverted"
        else:
            change_type = "unchanged"

        return CanonicalDiff(
            old_unit=unit1,
            new_unit=unit2,
            change_type=change_type,
            changes=changes,
        )

    def resolve_conflicts(self, unit_id: str) -> list[CanonicalDiff]:
        """Resolve conflicts for a unit by finding all versions and creating diffs.

        Args:
            unit_id: The unit ID to resolve conflicts for

        Returns:
            List of CanonicalDiff objects showing the evolution
        """
        versions = self.get_unit_versions(unit_id)
        if len(versions) < 2:
            return []

        diffs = []
        for i in range(len(versions) - 1):
            diff = self.compare_versions(unit_id, versions[i], versions[i + 1])
            diffs.append(diff)

        return diffs

    def get_lineage_graph(self, unit_id: str, max_depth: int = 3) -> dict[str, list[str]]:
        """Get the lineage graph for a unit.

        Args:
            unit_id: The unit ID to get lineage for
            max_depth: Maximum depth to traverse

        Returns:
            Dictionary mapping parent_id to list of child_ids
        """
        graph = {}
        visited = set()

        def traverse(current_id: str, depth: int):
            if depth >= max_depth or current_id in visited:
                return

            visited.add(current_id)
            children = self._lineage_cache.get(current_id, set())

            if children:
                graph[current_id] = list(children)
                for child_id in children:
                    traverse(child_id, depth + 1)

        traverse(unit_id, 0)
        return graph

    def cleanup_old_versions(self, unit_id: str, keep_latest: int = 5) -> int:
        """Clean up old versions of a unit, keeping only the latest N versions.

        Args:
            unit_id: The unit ID to clean up
            keep_latest: Number of latest versions to keep

        Returns:
            Number of versions removed
        """
        versions = self.get_unit_versions(unit_id)
        if len(versions) <= keep_latest:
            return 0

        # Sort versions and keep only the latest
        versions.sort()
        versions_to_remove = versions[:-keep_latest]

        removed_count = 0
        for version in versions_to_remove:
            unit_file = self.units_path / f"{unit_id}_v{version}.json"
            if unit_file.exists():
                unit_file.unlink()
                removed_count += 1

                # Remove from cache
                cache_key = f"{unit_id}:v{version}"
                self._unit_cache.pop(cache_key, None)

        # Update index
        self._index_cache[unit_id] = [f"v{v}" for v in versions[-keep_latest:]]
        self._save_index(unit_id)

        log.info(f"Cleaned up {removed_count} old versions for unit {unit_id}")
        return removed_count

    def get_storage_stats(self) -> dict[str, int]:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics
        """
        total_units = len(self._index_cache)
        active_units = len(self.find_active_units())
        total_versions = sum(len(versions) for versions in self._index_cache.values())

        # Calculate storage size
        storage_size = 0
        for unit_file in self.units_path.glob("*.json"):
            storage_size += unit_file.stat().st_size

        return {
            "total_units": total_units,
            "active_units": active_units,
            "total_versions": total_versions,
            "storage_size_bytes": storage_size,
            "avg_versions_per_unit": total_versions / total_units if total_units > 0 else 0,
        }

    def _get_latest_version(self, unit_id: str) -> int | None:
        """Get the latest version number for a unit."""
        versions = self.get_unit_versions(unit_id)
        return max(versions) if versions else None

    def _load_indices(self):
        """Load index and lineage data from storage."""
        # Load unit index
        for index_file in self.index_path.glob("*.json"):
            unit_id = index_file.stem
            try:
                with open(index_file, encoding="utf-8") as f:
                    self._index_cache[unit_id] = json.load(f)
            except (
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- index load: non-fatal, unit skipped from cache
                log.warning(f"Failed to load index for {unit_id}: {e}")

        # Load lineage data
        for lineage_file in self.lineage_path.glob("*.json"):
            parent_id = lineage_file.stem
            try:
                with open(lineage_file, encoding="utf-8") as f:
                    child_set = set(json.load(f))
                    self._lineage_cache[parent_id] = child_set
            except (
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- lineage load: non-fatal, lineage entry skipped
                log.warning(f"Failed to load lineage for {parent_id}: {e}")

    def _save_index(self, unit_id: str):
        """Save index data for a unit."""
        index_file = self.index_path / f"{unit_id}.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self._index_cache[unit_id], f, indent=2)

    def _save_lineage(self, parent_id: str):
        """Save lineage data for a parent."""
        lineage_file = self.lineage_path / f"{parent_id}.json"
        with open(lineage_file, "w", encoding="utf-8") as f:
            json.dump(list(self._lineage_cache[parent_id]), f, indent=2)


# Global store instance
_global_store: CanonicalStore | None = None


def get_canonical_store(storage_path: Path | None = None) -> CanonicalStore:
    """Get or create the global canonical store."""
    global _global_store
    if _global_store is None:
        _global_store = CanonicalStore(storage_path)
    return _global_store


def store_unit(unit: CanonicalRawUnit) -> bool:
    """Convenience function to store a canonical unit."""
    return get_canonical_store().store_unit(unit)


def get_unit(unit_id: str, version: int | None = None) -> CanonicalRawUnit | None:
    """Convenience function to retrieve a canonical unit."""
    return get_canonical_store().get_unit(unit_id, version)
