import os
import sys
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
'\nDashboard SSOT Synchronization Engine\n======================================\n\nGenerates Python and JavaScript constants from the canonical YAML configuration.\n\nThis script reads agentic_core/L6_observability/dashboards/dashboard_ssot.yaml and generates:\n  1. Python constants (updates dashboard_ssot_definitions.py)\n  2. JavaScript constants (generates js/constants/dashboard-constants.js)\n\nUsage:\n    python scripts/generate_dashboard_ssot_util.py\n\nThis should be run:\n  - After editing dashboard_ssot.yaml\n  - Before regenerating dashboard data\n  - As part of the CI/CD pipeline\n\nLast Updated: 2026-01-16\n'
from datetime import datetime
from pathlib import Path
import yaml
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
YAML_CONFIG = PROJECT_ROOT / 'L6_observability' / 'dashboards' / 'dashboard_ssot.yaml'
PYTHON_OUTPUT = PROJECT_ROOT / 'scripts' / 'dashboard_ssot_definitions.py'
JS_OUTPUT = PROJECT_ROOT / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards' / 'js' / 'constants' / 'dashboard-constants.js'

def load_yaml_config():
    """Load the YAML configuration file with path validation."""
    # guardian: allow-config-with-logic
    if not YAML_CONFIG.exists():
        raise FileNotFoundError(f'❌ CRITICAL: SSOT YAML not found at {YAML_CONFIG}')
    with open(YAML_CONFIG, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # guardian: allow-config-with-logic
    if not config:
        raise ValueError(f'❌ CRITICAL: SSOT YAML at {YAML_CONFIG} is empty')
    return config

def generate_python_constants(config):
    """Generate Python constants file from YAML config."""
    existing_content = ''
    if PYTHON_OUTPUT.exists():
        with open(PYTHON_OUTPUT, encoding='utf-8') as f:
            lines = f.readlines()
        calc_start_idx = None
        for i, line in enumerate(lines):
            if '# ============================================================================' in line and i > 50:
                if 'METRIC CALCULATION FUNCTIONS' in lines[i + 1] if i + 1 < len(lines) else '':
                    calc_start_idx = i
                    break
        if calc_start_idx:
            existing_content = ''.join(lines[calc_start_idx:])
    output = f'''"""\nDashboard SSOT Definitions\n==========================\nSINGLE SOURCE OF TRUTH for all dashboard metric calculations.\n\n⚠️  AUTO-GENERATED FROM agentic_core/L6_observability/dashboards/dashboard_ssot.yaml\n⚠️  DO NOT EDIT CONSTANTS MANUALLY - Edit the YAML file instead\n⚠️  Run: python agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py\n\nALL dashboard-related scripts MUST import from this file:\n- scripts/full_agent_discovery.py\n- scripts/regenerate_dashboard_data.py\n- scripts/test_dashboard_end_to_end.py\n\nDO NOT define metric calculations elsewhere. This eliminates "split brain" issues.\n\nLast Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"""\nfrom typing import Dict, Any, List, Set\n\n\n# ============================================================================\n# DASHBOARD COLUMN NAMES (display names in dashboard HTML)\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'''
    for key, value in config['columns'].items():
        const_name = f'COL_{key.upper()}'
        output += f"{const_name} = '{value}'\n"
    output += '\n\n'
    output += '# ============================================================================\n# METRIC FIELD NAMES (canonical names used in agent_discovery_full.json)\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'
    for key, value in config['fields'].items():
        const_name = f'FIELD_{key.upper()}'
        output += f"{const_name} = '{value}'\n"
    output += '\n\n'
    output += '# ============================================================================\n# METRIC THRESHOLDS\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'
    for key, value in config['thresholds'].items():
        const_name = f'THRESHOLD_{key.upper()}'
        output += f'{const_name} = {value}\n'
    output += '\n\n'
    output += '# ============================================================================\n# HEALTH SCORE FORMULA WEIGHTS\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'
    for key, value in config['health_weights'].items():
        const_name = f'WEIGHT_HEALTH_{key.upper()}'
        output += f'{const_name} = {value}\n'
    output += '\n# L0-specific weights (infrastructure layer)\n'
    for key, value in config['health_weights_l0'].items():
        const_name = f'WEIGHT_HEALTH_L0_{key.upper()}'
        output += f'{const_name} = {value}\n'
    output += '\n\n'
    output += '# ============================================================================\n# CODE QUALITY FORMULA WEIGHTS\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'
    for key, value in config['code_quality_weights'].items():
        const_name = f'WEIGHT_CODE_QUALITY_{key.upper()}'
        output += f'{const_name} = {value}\n'
    output += '\n# ============================================================================\n'
    output += '# SSOT INTEGRITY CONSTRAINTS\n'
    output += '# ============================================================================\n'
    output += 'try:\n'
    output += '    assert abs(sum([WEIGHT_HEALTH_HEAL_CAP, WEIGHT_HEALTH_INVOCATION, WEIGHT_HEALTH_TEST, WEIGHT_HEALTH_OBSERVABLE, WEIGHT_HEALTH_COMPLEXITY]) - 1.0) < 0.001\n'
    output += '    assert abs(sum([WEIGHT_HEALTH_L0_TEST, WEIGHT_HEALTH_L0_HARDENED, WEIGHT_HEALTH_L0_COMPLEXITY]) - 1.0) < 0.001\n'
    output += '    assert abs(sum([WEIGHT_CODE_QUALITY_TYPED, WEIGHT_CODE_QUALITY_DOCUMENTED, WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS, WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE]) - 1.0) < 0.001\n'
    output += 'except AssertionError as e:\n'
    output += "    print(f'❌ CRITICAL: SSOT Weight mismatch detected in dashboard_ssot.yaml')\n"
    output += '    raise\n'
    output += '\n\n'
    output += '# ============================================================================\n# PLACEHOLDERS\n# ============================================================================\n# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY\n\n'
    for key, value in config['placeholders'].items():
        const_name = f'PLACEHOLDER_{key.upper()}'
        output += f"{const_name} = {value}  # {key.replace('_', ' ').title()} awaiting implementation\n"
    output += '\n\n'
    output += "# ============================================================================\n# LAYER DEFINITIONS\n# ============================================================================\n\nLAYER_ORDER = ['Base', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps']\n\n# L0 is infrastructure layer - healing metrics are N/A\nL0_HEALING_NA = True\n\n# MCP-hardened base classes\nMCP_HARDENED_BASES = {\n    'SovereignBaseAgent', 'L0RoutingBaseAgent', 'L1CognitionBase',\n    'L2ExecutionBase', 'L3OrchestrationBase', 'L4StateBase',\n    'L5SafetyBase', 'L6ObservabilityBase', 'MCPHardenedMixin'\n}\n\n# Healer base classes\nHEALER_BASES = {\n    'HealerMixin', 'SovereignBaseAgent', 'L0RoutingBaseAgent',\n    'L1CognitionBase', 'L2ExecutionBase', 'L3OrchestrationBase',\n    'L4StateBase', 'L5SafetyBase', 'L6ObservabilityBase'\n}\n\n\n"
    if existing_content:
        output += existing_content
    else:
        output += '# ============================================================================\n# METRIC CALCULATION FUNCTIONS (SSOT)\n# ============================================================================\n# These functions are preserved from the original file.\n# Add calculation functions here.\n\ndef calc_heal_cap_pct(agents: List[Dict], is_l0: bool = False) -> float:\n    """Calculate Heal Capability % for a set of agents."""\n    if is_l0:\n        return 0.0\n    if not agents:\n        return 0.0\n    count = sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False))\n    return round(count / len(agents) * 100, 1)\n\n# Add other calculation functions as needed...\n'
    return output

def generate_js_constants(config):
    """Generate JavaScript constants file from YAML config."""
    output = f"// ============================================================================\n// DASHBOARD CONSTANTS\n// ============================================================================\n// ⚠️  AUTO-GENERATED FROM agentic_core/L6_observability/dashboards/dashboard_ssot.yaml\n// ⚠️  DO NOT EDIT MANUALLY - Edit the YAML file instead\n// ⚠️  Run: python scripts/generate_dashboard_ssot_util.py\n//\n// Last Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n// ============================================================================\n\n// ============================================================================\n// COLUMN NAMES\n// ============================================================================\n// Display names for dashboard table columns\n\nwindow.COLUMNS = {{\n"
    for key, value in config['columns'].items():
        js_key = key.upper()
        output += f'    {js_key}: "{value}",\n'
    output += '};\n\n'
    output += '// ============================================================================\n// FIELD NAMES\n// ============================================================================\n// Field names from agent_discovery_full.json\n\nwindow.FIELDS = {\n'
    for key, value in config['fields'].items():
        js_key = key.upper()
        output += f'    {js_key}: "{value}",\n'
    output += '};\n\n'
    output += '// ============================================================================\n// METRIC THRESHOLDS\n// ============================================================================\n// Standard thresholds for validation and outlier detection\n\nwindow.THRESHOLDS = {\n'
    for key, value in config['thresholds'].items():
        js_key = key.upper()
        output += f'    {js_key}: {value},\n'
    output += '};\n\n'
    output += '// ============================================================================\n// JAVASCRIPT METRIC KEYS\n// ============================================================================\n// CamelCase keys used in agentData objects\n\nwindow.METRIC_KEYS = {\n'
    for key, value in config['js_keys'].items():
        output += f'    {key.upper()}: "{value}",\n'
    output += '};\n\n'
    output += '// ============================================================================\n// HEALTH SCORE WEIGHTS\n// ============================================================================\n\nwindow.HEALTH_WEIGHTS = {\n'
    for key, value in config['health_weights'].items():
        js_key = key.upper()
        output += f'    {js_key}: {value},\n'
    output += '};\n\n'
    output += 'window.HEALTH_WEIGHTS_L0 = {\n'
    for key, value in config['health_weights_l0'].items():
        js_key = key.upper()
        output += f'    {js_key}: {value},\n'
    output += '};\n\n'
    output += '// ============================================================================\n// CODE QUALITY WEIGHTS\n// ============================================================================\n\nwindow.CODE_QUALITY_WEIGHTS = {\n'
    for key, value in config['code_quality_weights'].items():
        js_key = key.upper()
        output += f'    {js_key}: {value},\n'
    output += '};\n\n'
    output += '// ============================================================================\n// PLACEHOLDERS\n// ============================================================================\n\nwindow.PLACEHOLDERS = {\n'
    for key, value in config['placeholders'].items():
        js_key = key.upper()
        output += f'    {js_key}: {value},\n'
    output += '};\n'
    return output

def main():
    """Main synchronization function."""
    print('=' * 70)
    print('DASHBOARD SSOT SYNCHRONIZATION ENGINE')
    print('=' * 70)
    print()
    print(f'📖 Loading YAML config: {YAML_CONFIG}')
    config = load_yaml_config()
    print(f'   ✅ Loaded {len(config)} sections')
    print()
    print(f'🐍 Generating Python constants: {PYTHON_OUTPUT}')
    python_content = generate_python_constants(config)
    with open(PYTHON_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(python_content)
    print(f'   ✅ Generated {len(python_content.splitlines())} lines')
    print()
    print(f'📜 Generating JavaScript constants: {JS_OUTPUT}')
    JS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    js_content = generate_js_constants(config)
    with open(JS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f'   ✅ Generated {len(js_content.splitlines())} lines')
    print()
    print('=' * 70)
    print('✅ SYNCHRONIZATION COMPLETE')
    print('=' * 70)
    print()
    print('Generated files:')
    print(f'  1. {PYTHON_OUTPUT.relative_to(PROJECT_ROOT)}')
    print(f'  2. {JS_OUTPUT.relative_to(PROJECT_ROOT)}')
    print()
    print('Next steps:')
    print('  1. Review generated files')
    print('  2. Update JS files to import from dashboard-constants.js')
    print('  3. Run: python scripts/regenerate_dashboard_data.py')
    print('  4. Test dashboard in browser')
    print()
if __name__ == '__main__':
    main()
