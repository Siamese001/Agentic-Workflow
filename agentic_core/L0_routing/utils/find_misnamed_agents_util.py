"""
[DEPRECATED] Find files containing agent classes that don't follow *Agent.py naming.

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script performs its own AST scan which may conflict with the SSOT.
"""
import warnings
warnings.warn('find_misnamed_agents.py is DEPRECATED. Use full_agent_discovery.py instead.', DeprecationWarning, stacklevel=2)
import ast
from pathlib import Path
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, get_python_files
except ImportError:
    AGENTIC_CORE_DIR = Path(AGENTIC_CORE_DIR)
    APPS_LIC_DIR = Path(APPS_LIC_DIR)
    APPS_RG_DIR = Path(APPS_RG_DIR)
    APPS_SHARED_DIR = Path(APPS_SHARED_DIR)

    def get_python_files(directory):
        """Fallback implementation to get Python files."""
        return directory.rglob('*.py')
PROJECT_ROOT = Path(__file__).parent.parent
AGENT_SUFFIXES = {'Agent', 'Handler', 'Manager', 'Controller', 'Executor', 'Validator', 'Orchestrator', 'Governor', 'Enforcer', 'Analyzer', 'Sentinel'}
EXCLUDE = {'Mixin', 'Base', 'Abstract', 'Protocol'}

def has_agent_class(path: Path) -> list:
    """Return agent class names in file."""
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='ignore'))
    # guardian: allow-silent-swallow
    except:
        return []
    agents = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any((p in node.name for p in EXCLUDE)):
                continue
            if any((node.name.endswith(s) for s in AGENT_SUFFIXES)):
                agents.append(node.name)
    return agents
scan_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
misnamed = []
properly_named = 0
for d in scan_dirs:
    dir_path = PROJECT_ROOT / d
    if not dir_path.exists():
        continue
    for py_file in get_python_files(dir_path):
        if '__pycache__' in str(py_file):
            continue
        agents = has_agent_class(py_file)
        if agents:
            if 'Agent' in py_file.name:
                properly_named += 1
            else:
                misnamed.append((py_file.relative_to(PROJECT_ROOT), agents))
print(f'Properly named (*Agent.py with agent classes): {properly_named}')
print(f"Misnamed (contains agents but no 'Agent' in filename): {len(misnamed)}")
print(f"\n{'=' * 60}")
print('FILES NEEDING RENAME:')
print(f"{'=' * 60}\n")
for path, classes in sorted(misnamed)[:50]:
    print(f'{path}')
    print(f"  Classes: {', '.join(classes)}")
    print()
if len(misnamed) > 50:
    print(f'... and {len(misnamed) - 50} more files')
