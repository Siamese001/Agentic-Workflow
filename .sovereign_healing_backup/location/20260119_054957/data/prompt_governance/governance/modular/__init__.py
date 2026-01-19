"""
Modular Governance Loader - Merges split YAML files on load.
Replaces monolithic governance YAMLs with modular chunks for faster loading.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List

MODULAR_DIR = Path(__file__).parent


def load_governance(governance_type: str) -> Dict[str, Any]:
    """Load a specific governance type by merging its modular files."""
    gov_dir = MODULAR_DIR / governance_type
    if not gov_dir.exists():
        return {}
    
    result = {}
    
    # Load metadata
    meta_file = gov_dir / '_meta.yaml'
    if meta_file.exists():
        meta = yaml.safe_load(meta_file.read_text())
        result['version'] = meta.get('version', '1.0')
        result['last_updated'] = meta.get('last_updated', 'unknown')
    
    # Load all component files
    for yaml_file in gov_dir.glob('*.yaml'):
        if yaml_file.name.startswith('_'):
            continue
        data = yaml.safe_load(yaml_file.read_text())
        result.update(data)
    
    return result


def load_all_governance() -> Dict[str, Dict[str, Any]]:
    """Load all governance types."""
    governance = {}
    for gov_dir in MODULAR_DIR.iterdir():
        if gov_dir.is_dir() and not gov_dir.name.startswith('_'):
            governance[gov_dir.name] = load_governance(gov_dir.name)
    return governance


def get_available_governance() -> List[str]:
    """Get list of available governance types."""
    return [
        d.name for d in MODULAR_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ]


__all__ = [
    'load_governance',
    'load_all_governance',
    'get_available_governance',
]
