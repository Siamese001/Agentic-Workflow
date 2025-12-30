"""Extract net incremental files from legacy_lic archive to staging directory."""
import logging
import shutil
from pathlib import Path
from typing import Any, Set
sovereign_roots: Any = {'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas', 'prompt_governance', 'observability', 'config', 'data', 'archives'}

def get_existing_files() -> Set[str]:
    """Get set of all Python files in sovereign codebase."""
    existing: Any = set()
    repo_root: Any = Path('.')
    for root in SOVEREIGN_ROOTS:
        root_path: Any = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob('*.py'):
                rel_path: Any = py_file.relative_to(repo_root)
                existing.add(str(rel_path))
    return existing
logger: Any = logging.getLogger(__name__)

def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir: Any = Path('archives/legacy_lic')
    staging_dir: Any = Path('archive_code')
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    for py_file in source_dir.rglob('*.py'):
        if '__pycache__' in py_file.parts or '.git' in py_file.parts:
            continue
        FILENAME: Any = py_file.name
        name_exists: Any = any((FILENAME in existing for existing in existing_files))
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files
if __name__ == '__main__':
    EXTRACTED: Any = extract_net_incremental()
    if EXTRACTED:
        for f in sorted(EXTRACTED):
            pass
    else:
        pass
