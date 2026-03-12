import sys
from pathlib import Path
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

project_root = get_validated_project_root()
baseline = project_root / "ops_scripts/hooks/landmine_baseline.txt"

lines = [l.strip() for l in baseline.read_text(encoding='utf-8').splitlines() if l.strip()]

for cat in ['silent_swallower', 'magic_configuration', 'global_mutation']:
    cat_lines = [l for l in lines if f':{cat}:' in l]
    print(f'\n{cat} ({len(cat_lines)} total):')
    for s in cat_lines[:5]:
        print(f'  {s}')
