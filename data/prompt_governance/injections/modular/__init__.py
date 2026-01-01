"""
Modular Injections Loader - Merges split YAML files on load.
Replaces monolithic injection YAMLs with modular chunks for faster loading.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List

MODULAR_DIR = Path(__file__).parent


def load_injection(injection_type: str) -> Dict[str, Any]:
    """Load a specific injection type by merging its modular files."""
    injection_dir = MODULAR_DIR / injection_type
    if not injection_dir.exists():
        return {}
    
    result = {}
    
    # Load metadata
    meta_file = injection_dir / '_meta.yaml'
    if meta_file.exists():
        meta = yaml.safe_load(meta_file.read_text())
        result['version'] = meta.get('version', '1.0')
        result['last_updated'] = meta.get('last_updated', 'unknown')
    
    # Load all component files
    for yaml_file in injection_dir.glob('*.yaml'):
        if yaml_file.name.startswith('_'):
            continue
        data = yaml.safe_load(yaml_file.read_text())
        result.update(data)
    
    return result


def load_all_injections() -> Dict[str, Dict[str, Any]]:
    """Load all injection types."""
    injections = {}
    for injection_dir in MODULAR_DIR.iterdir():
        if injection_dir.is_dir() and not injection_dir.name.startswith('_'):
            injections[injection_dir.name] = load_injection(injection_dir.name)
    return injections


def get_available_injections() -> List[str]:
    """Get list of available injection types."""
    return [
        d.name for d in MODULAR_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ]


# Lazy-loaded injection accessors
def get_safety_injection() -> Dict[str, Any]:
    return load_injection('safety')

def get_reasoning_injection() -> Dict[str, Any]:
    return load_injection('reasoning')

def get_tool_use_injection() -> Dict[str, Any]:
    return load_injection('tool_use')

def get_framing_injection() -> Dict[str, Any]:
    return load_injection('framing')

def get_context_engineering_injection() -> Dict[str, Any]:
    return load_injection('context_engineering')

def get_output_governance_injection() -> Dict[str, Any]:
    return load_injection('output_governance')


__all__ = [
    'load_injection',
    'load_all_injections',
    'get_available_injections',
    'get_safety_injection',
    'get_reasoning_injection',
    'get_tool_use_injection',
    'get_framing_injection',
    'get_context_engineering_injection',
    'get_output_governance_injection',
]
