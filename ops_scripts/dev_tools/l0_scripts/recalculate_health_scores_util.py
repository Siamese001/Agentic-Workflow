"""
Recalculate Health Scores based on new Complexity Health values.

Uses the canonical health calculation formula:
Health = (Heal Cap × 0.30) + (Invocation × 0.10) + (Test × 0.25) + (Obs × 0.20) + (Complexity × 0.15)
"""
import json
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = get_validated_project_root()
DASHBOARD_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.L5_safety.validators.canonical_truth_validator import calculate_health_score

def main():
    print('=' * 70)
    print('Recalculating Health Scores with Complexity Health = 100%')
    print('=' * 70)
    if not DASHBOARD_PATH.exists():
        print(f'ERROR: Dashboard not found at {DASHBOARD_PATH}')
        return 1
    content = DASHBOARD_PATH.read_text(encoding='utf-8')
    start_marker = 'const dashboardData = ['
    end_marker = '];'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)
    json_str = content[start_idx + len(start_marker) - 1:end_idx - 1]
    territories = json.loads(json_str)
    print(f'\nFound {len(territories)} territories')
    changes = []
    for territory in territories:
        name = territory.get('Territory', 'Unknown')
        heal_cap = territory.get('Heal Cap %', 0)
        invoc = territory.get('Heal Invocation %', 0)
        test_cov = territory.get('Test %', 0)
        obs = territory.get('Observable %', 0)
        comp_health = territory.get('Complexity Health', 0)
        old_health = territory.get('Health', 0)
        new_health = round(calculate_health_score(heal_cap=heal_cap, invoc=invoc, test_cov=test_cov, obs=obs, comp_health=comp_health), 1)
        if abs(old_health - new_health) > 0.01:
            changes.append((name, old_health, new_health))
            territory['Health'] = new_health
            breakdown = f'Heal:{int(heal_cap)}+Inv:{int(invoc)}+Test:{int(test_cov)}+Obs:{int(obs)}+CC:{int(comp_health)}'
            territory['Health Breakdown'] = breakdown
    new_json = json.dumps(territories, indent=2)
    new_content = content[:start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1:]
    DASHBOARD_PATH.write_text(new_content, encoding='utf-8')
    print(f'\n✅ Updated {len(changes)} Health scores')
    print('\nChanges made:')
    for name, old, new in changes:
        print(f'  {name}: {old} -> {new}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
