"""Structure drift manifest writer — stdlib only, no UWG dependency.

Write counterpart for structure_drift_validator.generate_structure_manifest().
Moved here from validators/ to preserve the pure read-only contract of that module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["save_manifest"]
