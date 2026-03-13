"""
Manifest Manager.

Handles persistence of workflow state to disk/storage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        pass
except ImportError:

    class MCPHardenedMixin:
        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        pass


@dataclass
class ManifestManager(MCPHardenedMixin, HealerMixin):
    """
    Manages loading and saving of workflow manifests (checkpoints).
    """

    base_path: str | Path = field(default_factory=lambda: Path("./manifests"))

    def __post_init__(self) -> None:
        super().__init__()
        self.base_path = Path(self.base_path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    def save_manifest(self, manifest_id: str, data: dict[str, Any]) -> Path:
        """
        Saves data to a JSON manifest file.

        Args:
            manifest_id: Unique identifier for the file.
            data: Dictionary data to save.

        Returns:
            Path object of the saved file.
        """
        try:
            target_file = self.base_path / f"{manifest_id}.json"
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return target_file
        except (OSError, TypeError) as e:
            raise

    def load_manifest(self, manifest_id: str) -> dict[str, Any]:
        """
        Loads data from a JSON manifest file.

        Args:
            manifest_id: Unique identifier for the file.

        Returns:
            Dictionary containing the manifest data.

        Raises:
            FileNotFoundError: If the manifest does not exist.
        """
        target_file = self.base_path / f"{manifest_id}.json"
        if not target_file.exists():
            raise FileNotFoundError(f"Manifest not found: {target_file}")
        with open(target_file, encoding="utf-8") as f:
            return json.load(f)
