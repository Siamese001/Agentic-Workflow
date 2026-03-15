from __future__ import annotations

'SovereignScanner - Centralized single-pass repository mapper.\n\n[Phase 5] Provides shared intelligence layer for L5 agents.\nReduces I/O by sharing a single scan result across all agents.\n\nUsage:\n    scanner = SovereignScanner(project_root)\n    repo_map = scanner.scan_repository()\n\n    # Get files for a specific territory\n    agentic_core_files = scanner.get_root_files("agentic_core")\n'
import logging
from pathlib import Path

Logger = logging.getLogger(__name__)


class SovereignScanner:
    """
    Singleton provider for repository-wide file maps.

    Reduces I/O by sharing a single scan result across all L5 agents.
    Uses FileCache internally for efficient file enumeration.
    """

    _instance: SovereignScanner | None = None
    _initialized: bool = False

    def __new__(cls, project_root: Path | None = None) -> SovereignScanner:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_root: Path | None = None) -> None:
        if SovereignScanner._initialized:
            return
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = project_root
        self._root_map: dict[str, list[Path]] = {}
        self._all_files: list[Path] | None = None
        SovereignScanner._initialized = True
        Logger.info(f"SovereignScanner initialized for: {project_root}")

    @classmethod
    def get_instance(cls, project_root: Path | None = None) -> SovereignScanner:
        """Get or create the singleton instance."""
        return cls(project_root)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
        cls._initialized = False

    def scan_repository(self) -> dict[str, list[Path]]:
        """
        Perform a single-pass scan of all sovereign roots.

        Returns:
            Dictionary mapping root names to lists of Python files
        """
        if self._root_map:
            Logger.debug("Returning cached repository map")
            return self._root_map
        Logger.info("Performing single-pass repository scan...")
        from agentic_core.utils.file_cache import FileCache

        from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY

        cache = FileCache.get_instance(self.project_root)
        self._all_files = list(cache.get_python_files())
        for root_name in SOVEREIGN_REGISTRY.keys():
            root_path = self.project_root / root_name
            if not root_path.exists():
                self._root_map[root_name] = []
                continue
            self._root_map[root_name] = [
                f for f in self._all_files if self._file_belongs_to_root(f, root_name)
            ]
        total_files = sum(len(files) for files in self._root_map.values())
        Logger.info(f"Repository scan complete: {total_files} files across {len(self._root_map)} roots")
        return self._root_map

    def _file_belongs_to_root(self, file_path: Path, root_name: str) -> bool:
        """Check if a file belongs to a specific sovereign root."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            return len(parts) > 0 and parts[0] == root_name
        except ValueError:
            return False

    def get_root_files(self, root_name: str) -> list[Path]:
        """
        Retrieve cached files for a specific territory.

        Args:
            root_name: Name of the sovereign root (e.g., "agentic_core")

        Returns:
            List of Python file paths in that root
        """
        return self.scan_repository().get(root_name, [])

    def get_all_files(self) -> list[Path]:
        """Get all Python files across all roots."""
        self.scan_repository()
        return self._all_files or []

    def invalidate_cache(self) -> None:
        """Invalidate the cached repository map (forces rescan on next access)."""
        self._root_map = {}
        self._all_files = None
        Logger.info("SovereignScanner cache invalidated")
