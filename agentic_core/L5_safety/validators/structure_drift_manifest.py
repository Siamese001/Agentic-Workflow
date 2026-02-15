"""Structure drift manifest generator for architectural integrity monitoring.

This module provides deterministic generation of structure manifests
that can be used to detect unauthorized changes to the codebase structure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def generate_structure_manifest() -> dict[str, Any]:
    """Generate a deterministic structure manifest of the codebase.

    Returns:
        A dictionary containing the structure manifest with:
        - directories: List of all directories in the codebase
        - python_files: List of all Python files with their relative paths
        - hash: SHA256 hash of the manifest content for integrity checking
    """
    manifest = {
        "directories": [],
        "python_files": [],
    }

    # Collect all directories (excluding hidden and common ignore patterns)
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if path.is_dir():
            # Skip hidden directories and common ignore patterns
            if any(part.startswith(".") for part in path.parts):
                continue
            if any(part in ["__pycache__", ".pytest_cache", ".nox", "node_modules"] for part in path.parts):
                continue
            if ".git" in path.parts:
                continue

            relative_path = path.relative_to(PROJECT_ROOT).as_posix()
            manifest["directories"].append(relative_path)

    # Collect all Python files
    for py_file in sorted(PROJECT_ROOT.rglob("*.py")):
        # Skip hidden files and common ignore patterns
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if ".git" in py_file.parts:
            continue
        if "__pycache__" in py_file.parts:
            continue

        relative_path = py_file.relative_to(PROJECT_ROOT).as_posix()
        manifest["python_files"].append(relative_path)

    # Generate hash of the manifest content (excluding the hash field itself)
    content_for_hash = json.dumps(
        {k: v for k, v in manifest.items() if k != "hash"}, sort_keys=True, separators=(",", ":")
    )
    manifest["hash"] = hashlib.sha256(content_for_hash.encode()).hexdigest()

    return manifest


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load a structure manifest from a file.

    Args:
        manifest_path: Path to the manifest file

    Returns:
        The loaded structure manifest
    """
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # Generate and save manifest when run directly
    manifest = generate_structure_manifest()
    output_file = PROJECT_ROOT / "artifacts" / "structure" / "structure_manifest.json"
    save_manifest(manifest, output_file)
    print(f"Structure manifest saved to: {output_file}")
    print(f"Manifest hash: {manifest['hash']}")
