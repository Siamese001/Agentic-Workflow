import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing: Any = {}
    repo_root: Any = Path('.')
    sovereign_roots: Any = {'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas', 'prompt_governance', 'observability', 'config', 'data', 'archives', 'docs'}
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            for file_path in root_path.rglob('*.py'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob('*.json'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob('*.md'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
    return existing
