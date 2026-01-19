from __future__ import annotations
"""
Modular Manifest Loader - Merges split manifest files on load.
Replaces monolithic active_manifest.json (482KB) with modular chunks.
"""
import json
from pathlib import Path
from typing import Dict, List, Any

MANIFEST_DIR = Path(__file__).parent


def load_manifest() -> Dict[str, Any]:
    """Load and merge all manifest chunks into single dict."""
    manifest = {
        'files': [],
        'duplicates_removed': [],
    }
    
    # Load metadata
    metadata_file = MANIFEST_DIR / '_metadata.json'
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
        manifest.update(metadata)
    
    # Load duplicates
    duplicates_file = MANIFEST_DIR / '_duplicates.json'
    if duplicates_file.exists():
        duplicates = json.loads(duplicates_file.read_text())
        manifest['duplicates_removed'] = duplicates.get('duplicates_removed', [])
    
    # Load all layer files
    for layer_file in MANIFEST_DIR.glob('*.json'):
        if layer_file.name.startswith('_'):
            continue  # Skip metadata files
        
        layer_data = json.loads(layer_file.read_text())
        manifest['files'].extend(layer_data.get('files', []))
    
    return manifest


def load_layer(layer_name: str) -> Dict[str, Any]:
    """Load a specific layer's manifest (lazy loading)."""
    layer_file = MANIFEST_DIR / f'{layer_name}.json'
    if layer_file.exists():
        return json.loads(layer_file.read_text())
    return {'layer': layer_name, 'files': [], 'file_count': 0}


def get_available_layers() -> List[str]:
    """Get list of available layer names."""
    return [
        f.stem for f in MANIFEST_DIR.glob('*.json')
        if not f.name.startswith('_')
    ]


# Backward compatibility - load full manifest on import
ACTIVE_MANIFEST = load_manifest()

__all__ = ['load_manifest', 'load_layer', 'get_available_layers', 'ACTIVE_MANIFEST']
