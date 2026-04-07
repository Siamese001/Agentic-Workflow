"""SSOT discovery validator utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class SSOTDiscoveryValidator:
    """Validator for Single Source of Truth discovery."""

    def __init__(self) -> None:
        self._sources: dict[str, Any] = {}

    def register_source(self, name: str, path: str, checksum: str) -> None:
        """Register a SSOT source."""
        self._sources[name] = {
            "path": path,
            "checksum": checksum,
        }

    def validate_source(self, name: str, checksum: str) -> bool:
        """Validate a source against registered checksum."""
        if name not in self._sources:
            return False
        return self._sources[name]["checksum"] == checksum

    def get_source_path(self, name: str) -> str | None:
        """Get registered source path."""
        source = self._sources.get(name)
        return source["path"] if source else None


def discover_ssot(name: str) -> dict[str, Any] | None:
    """Discover SSOT by name."""
    validator = SSOTDiscoveryValidator()
    return validator._sources.get(name)


def get_python_files(directory: str | Path, pattern: str = "*.py") -> list[str]:
    """Get Python files from directory matching pattern."""
    directory = Path(directory)
    if not directory.exists():
        return []
    return [str(f) for f in directory.rglob(pattern) if f.is_file()]


__all__ = ["SSOTDiscoveryValidator", "discover_ssot", "get_python_files"]
