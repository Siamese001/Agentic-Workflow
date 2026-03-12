"""
[DEPRECATED] This script is deprecated. Use regenerate_dashboard_full.py instead.

DEPRECATION REASON: This script does not use SSOT definitions and generates
incorrect data structure (15 rows instead of 43 territories).

CANONICAL SSOT: scripts/regenerate_dashboard_full.py
 - Uses dashboard_ssot_definitions.py for all calculations
 - Generates correct 43 territory rows with TOTAL first
 - Updates dashboardData, realAgentData, and recommendations

This file is kept for reference only. DO NOT USE.
"""
import sys
from collections import defaultdict
from pathlib import Path
print('[DEPRECATED] This script is deprecated. Use regenerate_dashboard_full.py instead.')
sys.exit(1)
'\nGenerate modular dashboard data files from agent_discovery_full.json\nCreates: dashboard_data.js, agent_data.js, recommendations.js, observations.js\n'
import json
import sys
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def load_discovery():
    discovery_path = Path('agent_discovery_full.json')
    if not discovery_path.exists():
        print(f'❌ {discovery_path} not found')
        sys.exit(1)
    with open(discovery_path) as f:
        data = json.load(f)
    if isinstance(data, list):
        agents = data
    else:
        agents = data.get('agents', [])
    print(f'✅ Loaded {len(agents)} agents from discovery')
    return agents

def map_territory(agent):
    """
    Get territory from agent discovery data (SSOT).

    Uses the 'territory' field from agent_discovery_full.json which is
    computed by territory_ssot_definitions.get_territory_from_path().
    This ensures consistency with regenerate_data.py.
    """
    territory = agent.get('territory', 'Unknown')
    if not territory or territory == 'Unknown':
        layer = agent.get('layer', '')
        if layer:
            return f'{layer}/Core'
        return 'Unknown'
    return territory

def calculate_metrics(agents_in_territory):
    """Calculate territory metrics from agent list"""
    total = len(agents_in_territory)
    if total == 0:
        return None
    heal_cap = sum((1 for a in agents_in_territory if a.get('has_healing', False)))
    heal_invocation = sum((1 for a in agents_in_territory if a.get('invocation') == 'Yes'))
    has_tests = sum((1 for a in agents_in_territory if a.get('has_tests', False)))
    heal_cap_pct = heal_cap / total * 100
    heal_inv_pct = heal_invocation / total * 100
    test_pct = has_tests / total * 100
    complexities = [a.get('cyclomatic_complexity', 0) for a in agents_in_territory if a.get('cyclomatic_complexity')]
    avg_cc = sum(complexities) / len(complexities) if complexities else 0
    complexity_health = max(0, 100 - avg_cc * 2) if avg_cc else 100
    observable_agents = sum((1 for a in agents_in_territory if a.get('observability', {}).get('logging') or a.get('observability', {}).get('metrics') or a.get('observability', {}).get('tracing')))
    observable_pct = observable_agents / total * 100 if total > 0 else 0
    typed_values = [a.get('typed_pct', 0) for a in agents_in_territory]
    typed_pct = sum(typed_values) / len(typed_values) if typed_values else 0
    doc_values = [a.get('documented_pct', 0) for a in agents_in_territory]
    documented_pct = sum(doc_values) / len(doc_values) if doc_values else 0
    hardened_count = sum((1 for a in agents_in_territory if a.get('mcp_hardened', False)))
    hardened_pct = hardened_count / total * 100 if total > 0 else 0
    health = heal_cap_pct * 0.3 + heal_inv_pct * 0.1 + test_pct * 0.25 + observable_pct * 0.2 + complexity_health * 0.15
    if health >= 85:
        risk = 'Low'
    elif health >= 70:
        risk = 'Medium'
    else:
        risk = 'High'
    code_quality = (typed_pct + documented_pct) / 2
    return {'Territory': None, 'Total': total, 'Compliant': heal_cap, 'Heal Cap %': round(heal_cap_pct, 1), 'Heal Invocation %': round(heal_inv_pct, 1), 'Invocation %': round(heal_inv_pct, 1), 'Test %': round(test_pct, 1), 'Observable %': round(observable_pct, 1), 'Avg CC': round(avg_cc, 1), 'Typed %': round(typed_pct, 1), 'Documented %': round(documented_pct, 1), 'Metadata %': 100.0, 'Canonical Inheritance %': 100.0, 'schema Strictness %': 100.0, 'Complexity Health': round(complexity_health, 1), 'Code Quality Score': round(code_quality, 1), 'Health': round(health, 1), 'Risk': risk, 'Hardened %': round(hardened_pct, 1), 'Criticality': 75}
TERRITORY_ORDER = ['Sovereign Base Agent', 'L6 observability/Base Agent', 'L6 observability/Core', 'L6 observability/Infrastructure', 'L6 observability/Metrics', 'L5 Safety/Base Agent', 'L5 Safety/Core', 'L5 Safety/Gravity', 'L5 Safety/Guardrails', 'L5 Safety/Red Teaming', 'L5 Safety/Validators', 'L4 State/Base Agent', 'L4 State/Core', 'L4 State/Infrastructure', 'L4 State/Specialized', 'L3 Orchestration/Base Agent', 'L3 Orchestration/Core', 'L3 Orchestration/Infrastructure', 'L3 Orchestration/Specialized', 'L2 Execution/Base Agent', 'L2 Execution/Core', 'L2 Execution/Specialized', 'L1 Cognition/Base Agent', 'L1 Cognition/Core', 'L1 Cognition/Specialized', 'L0 Maintenance/Base Agent', 'L0 Maintenance/Core', 'L0 Maintenance/Infrastructure', 'Apps Rg', 'Apps Lic', 'Apps Shared']

def generate_dashboard_data(agents):
    """Generate dashboard_data.js with territory rollups"""
    territories = defaultdict(list)
    for agent in agents:
        territory = map_territory(agent)
        if territory != 'Unknown':
            territories[territory].append(agent)
    print(f'📊 Found {len(territories)} territories')
    dashboard_data = []
    for territory_name in TERRITORY_ORDER:
        if territory_name not in territories:
            continue
        agents_list = territories[territory_name]
        metrics = calculate_metrics(agents_list)
        if metrics:
            metrics['Territory'] = territory_name
            dashboard_data.append(metrics)
    len(agents)
    total_metrics = calculate_metrics(agents)
    if total_metrics:
        total_metrics['Territory'] = 'TOTAL'
        dashboard_data.append(total_metrics)
    output_path = Path('agentic_core/L6_observability/dashboards/data/dashboard_data.js')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('/**\n')
        f.write(' * Strategic Dashboard Metrics\n')
        f.write(' * Loaded as global variable for file:// protocol compatibility\n')
        f.write(' */\n')
        f.write('window.dashboardData = ')
        f.write(json.dumps(dashboard_data, indent=2))
        f.write(';\n')
    print(f'✅ Generated {output_path} with {len(dashboard_data)} rows')
    return dashboard_data

def generate_agent_data(agents, territories):
    """Generate agent_data.js with per-agent distributions and metric arrays for tooltips"""
    territory_agents = defaultdict(list)
    for agent in agents:
        territory = map_territory(agent)
        territory_agents[territory].append(agent)
    agent_data = {}
    for territory, agents_list in territory_agents.items():
        heal_cap_values = []
        invocation_values = []
        hardened_values = []
        test_values = []
        complexity_health_values = []
        health_values = []
        typed_values = []
        documented_values = []
        schema_values = []
        proper_base_values = []
        code_quality_values = []
        agent_objects = []
        for a in agents_list:
            has_healing = a.get('has_healing', False)
            heal_cap = 100.0 if has_healing else 0.0
            invocation = a.get('invocation', 'No')
            invocation_pct = 100.0 if invocation == 'Yes' else 50.0 if invocation == 'Inherited' else 0.0
            mcp_hardened = a.get('mcp_hardened', False)
            hardened_pct = 100.0 if mcp_hardened else 0.0
            has_tests = a.get('has_tests', False)
            test_pct = 100.0 if has_tests else 0.0
            cc = a.get('cyclomatic_complexity', 0) or 0
            complexity_health = max(0, 100 - cc * 2)
            typed_pct = a.get('typed_pct', 0) or 0
            documented_pct = a.get('documented_pct', 0) or 0
            schema_pct = 100.0
            proper_base_pct = 100.0
            health = heal_cap * 0.3 + invocation_pct * 0.1 + test_pct * 0.25 + hardened_pct * 0.2 + complexity_health * 0.15
            code_quality = typed_pct * 0.3 + documented_pct * 0.3 + schema_pct * 0.25 + proper_base_pct * 0.15
            heal_cap_values.append(heal_cap)
            invocation_values.append(invocation_pct)
            hardened_values.append(hardened_pct)
            test_values.append(test_pct)
            complexity_health_values.append(complexity_health)
            health_values.append(health)
            typed_values.append(typed_pct)
            documented_values.append(documented_pct)
            schema_values.append(schema_pct)
            proper_base_values.append(proper_base_pct)
            code_quality_values.append(code_quality)
            rel_path = a.get('rel_file', '') or a.get('path', '')
            abs_path = a.get('abs_file', '') or a.get('file_path', '')
            if not abs_path and rel_path:
                abs_path = f'C:/Git/Agentic-Workflow/{rel_path}'
            agent_objects.append({'name': a.get('class_name', '') or a.get('name', 'Unknown'), 'path': rel_path, 'abs_file': abs_path, 'file_path': abs_path, 'class_line': a.get('class_line', 1), 'has_healing': has_healing, 'has_mixin': has_healing, 'invocation': invocation, 'invocation_pct': invocation_pct, 'mcp_hardened': mcp_hardened, 'hardened_pct': hardened_pct, 'has_tests': has_tests, 'test_pct': test_pct, 'cyclomatic_complexity': cc, 'complexity_health': complexity_health, 'health': round(health, 1), 'typed_pct': typed_pct, 'documented_pct': documented_pct, 'schema_pct': schema_pct, 'proper_base_pct': proper_base_pct, 'code_quality': round(code_quality, 1), 'obs_summary': f"Logging: {('✓' if a.get('observability', {}).get('logging') else '✗')} | Metrics: {('✓' if a.get('observability', {}).get('metrics') else '✗')} | Tracing: {('✓' if a.get('observability', {}).get('tracing') else '✗')}", 'mcp_summary': f"Shield: {('✓' if mcp_hardened else '✗')} | @hardened: {('✓' if hardened_pct > 40 else '✗')} | Safe: {('✓' if hardened_pct > 20 else '✗')}", 'typing_summary': f"Init: {('✓' if typed_pct > 70 else '✗')} | Methods: {int(typed_pct)}% | Returns: {('✓' if typed_pct > 50 else '✗')}"})
        agent_data[territory] = {'agents': agent_objects, 'healCap': heal_cap_values, 'invocation': invocation_values, 'hardened': hardened_values, 'test': test_values, 'complexityHealth': complexity_health_values, 'health': health_values, 'typed': typed_values, 'documented': documented_values, 'schemaStrictness': schema_values, 'properBase': proper_base_values, 'codeQuality': code_quality_values}
    output_path = Path('agentic_core/L6_observability/dashboards/data/agent_data.js')
    with open(output_path, 'w') as f:
        f.write('/**\n')
        f.write(' * Per-Agent Distribution Data\n')
        f.write(' * Loaded as global variable for file:// protocol compatibility\n')
        f.write(' * Structure matches monolithic globalAgentData for full tooltip/drill-down support\n')
        f.write(' */\n')
        f.write('window.realAgentData = ')
        f.write(json.dumps(agent_data, indent=2))
        f.write(';\n')
    print(f'✅ Generated {output_path} with {len(agent_data)} territories (full metric arrays)')

def main():
    print('=' * 70)
    print('MODULAR DASHBOARD DATA GENERATOR')
    print('=' * 70)
    print()
    agents = load_discovery()
    dashboard_data = generate_dashboard_data(agents)
    generate_agent_data(agents, dashboard_data)
    print()
    print('=' * 70)
    print('✅ COMPLETE - Dashboard data files generated')
    print('=' * 70)
    print()
    print('Next steps:')
    print('1. Refresh browser at http://localhost:8765/autonomy_dashboard.html')
    print('2. Verify metrics show real values (not all 100%)')
    print('3. Run: python scripts/test_dashboard_end_to_end.py')
if __name__ == '__main__':
    main()
