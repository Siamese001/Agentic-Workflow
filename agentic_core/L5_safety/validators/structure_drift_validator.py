"""Structure drift manifest generator for architectural integrity monitoring.

This module provides deterministic generation of structure manifests
that can be used to detect unauthorized changes to the codebase structure.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def generate_structure_manifest() -> dict[str, Any]:
    """Generate a deterministic structure manifest of the codebase.

    Returns:
        A dictionary containing the structure manifest with:
        - directories: List of all directories in the codebase
        - python_files: List of all Python files with their relative paths
        - hash: SHA256 hash of the manifest content for integrity checking
    """
    manifest = {'directories': [], 'python_files': []}
    for path in sorted(PROJECT_ROOT.rglob('*')):
        if path.is_dir():
            if any((part.startswith('.') for part in path.parts)):
                continue
            if any((part in ['__pycache__', '.pytest_cache', '.nox', 'node_modules'] for part in path.parts)):
                continue
            if '.git' in path.parts:
                continue
            relative_path = path.relative_to(PROJECT_ROOT).as_posix()
            manifest['directories'].append(relative_path)
    for py_file in sorted(PROJECT_ROOT.rglob('*.py')):
        if any((part.startswith('.') for part in py_file.parts)):
            continue
        if '.git' in py_file.parts:
            continue
        if '__pycache__' in py_file.parts:
            continue
        relative_path = py_file.relative_to(PROJECT_ROOT).as_posix()
        manifest['python_files'].append(relative_path)
    content_for_hash = json.dumps({k: v for k, v in manifest.items() if k != 'hash'}, sort_keys=True, separators=(',', ':'))
    manifest['hash'] = hashlib.sha256(content_for_hash.encode()).hexdigest()
    return manifest

def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    _wg.ensure_dir(output_path.parent)
    _wg.write_json(output_path, manifest, indent=2)

def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load a structure manifest from a file.

    Args:
        manifest_path: Path to the manifest file

    Returns:
        The loaded structure manifest
    """
    with open(manifest_path, encoding='utf-8') as f:
        return json.load(f)
if __name__ == '__main__':
    manifest = generate_structure_manifest()
    output_file = PROJECT_ROOT / 'artifacts' / 'structure' / 'structure_manifest.json'
    save_manifest(manifest, output_file)
    print(f'Structure manifest saved to: {output_file}')
    print(f"Manifest hash: {manifest['hash']}")
