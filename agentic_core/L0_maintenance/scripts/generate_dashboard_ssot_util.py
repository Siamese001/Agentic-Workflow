#!/usr/bin/env python3
import os
import sys

if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
Dashboard SSOT Synchronization Engine
======================================

Generates Python and JavaScript constants from the canonical YAML configuration.

This script reads agentic_core/L6_observability/dashboards/dashboard_ssot.yaml and generates:
  1. Python constants (updates dashboard_ssot_definitions.py)
  2. JavaScript constants (generates js/constants/dashboard-constants.js)

Usage:
    python scripts/generate_dashboard_ssot_util.py

This should be run:
  - After editing dashboard_ssot.yaml
  - Before regenerating dashboard data
  - As part of the CI/CD pipeline

Last Updated: 2026-01-16
"""
from datetime import datetime
from pathlib import Path

import yaml

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
YAML_CONFIG = PROJECT_ROOT / "L6_observability" / "dashboards" / "dashboard_ssot.yaml"
PYTHON_OUTPUT = PROJECT_ROOT / "scripts" / "dashboard_ssot_definitions.py"
JS_OUTPUT = (
    PROJECT_ROOT
    / "agentic_core"
    / "L6_observability"
    / "dashboards"
    / "js"
    / "constants"
    / "dashboard-constants.js"
)


def load_yaml_config():
    """Load the YAML configuration file with path validation."""
    if not YAML_CONFIG.exists():
        raise FileNotFoundError(f"❌ CRITICAL: SSOT YAML not found at {YAML_CONFIG}")
    with open(YAML_CONFIG, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not config:
        raise ValueError(f"❌ CRITICAL: SSOT YAML at {YAML_CONFIG} is empty")
    return config


def generate_python_constants(config):
    """Generate Python constants file from YAML config."""

    # Read existing file to preserve calculation functions
    existing_content = ""
    if PYTHON_OUTPUT.exists():
        with open(PYTHON_OUTPUT, encoding="utf-8") as f:
            lines = f.readlines()

        # Find where calculation functions start (after column definitions)
        calc_start_idx = None
        for i, line in enumerate(lines):
            if (
                "# ============================================================================" in line
                and i > 50
            ):
                if "METRIC CALCULATION FUNCTIONS" in lines[i + 1] if i + 1 < len(lines) else "":
                    calc_start_idx = i
                    break

        if calc_start_idx:
            existing_content = "".join(lines[calc_start_idx:])

    # Generate new header and constants
    output = f'''"""
Dashboard SSOT Definitions
==========================
SINGLE SOURCE OF TRUTH for all dashboard metric calculations.

⚠️  AUTO-GENERATED FROM agentic_core/L6_observability/dashboards/dashboard_ssot.yaml
⚠️  DO NOT EDIT CONSTANTS MANUALLY - Edit the YAML file instead
⚠️  Run: python agentic_core/L0_maintenance/scripts/generate_dashboard_ssot_util.py

ALL dashboard-related scripts MUST import from this file:
- scripts/full_agent_discovery.py
- scripts/regenerate_dashboard_data.py
- scripts/test_dashboard_end_to_end.py

DO NOT define metric calculations elsewhere. This eliminates "split brain" issues.

Last Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
from typing import Dict, Any, List, Set


# ============================================================================
# DASHBOARD COLUMN NAMES (display names in dashboard HTML)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

'''

    # Add column constants
    for key, value in config["columns"].items():
        const_name = f"COL_{key.upper()}"
        output += f"{const_name} = '{value}'\n"

    output += "\n\n"

    # Add field name constants
    output += """# ============================================================================
# METRIC FIELD NAMES (canonical names used in agent_discovery_full.json)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

"""

    for key, value in config["fields"].items():
        const_name = f"FIELD_{key.upper()}"
        output += f"{const_name} = '{value}'\n"

    output += "\n\n"

    # Add threshold constants
    output += """# ============================================================================
# METRIC THRESHOLDS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

"""

    for key, value in config["thresholds"].items():
        const_name = f"THRESHOLD_{key.upper()}"
        output += f"{const_name} = {value}\n"

    output += "\n\n"

    # Add health score weights
    output += """# ============================================================================
# HEALTH SCORE FORMULA WEIGHTS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

"""

    for key, value in config["health_weights"].items():
        const_name = f"WEIGHT_HEALTH_{key.upper()}"
        output += f"{const_name} = {value}\n"

    output += "\n# L0-specific weights (infrastructure layer)\n"
    for key, value in config["health_weights_l0"].items():
        const_name = f"WEIGHT_HEALTH_L0_{key.upper()}"
        output += f"{const_name} = {value}\n"

    output += "\n\n"

    # Add code quality weights
    output += """# ============================================================================
# CODE QUALITY FORMULA WEIGHTS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

"""

    for key, value in config["code_quality_weights"].items():
        const_name = f"WEIGHT_CODE_QUALITY_{key.upper()}"
        output += f"{const_name} = {value}\n"

    # SSOT INTEGRITY CONSTRAINTS - Strict validation (AFTER all weights defined)
    output += "\n# ============================================================================\n"
    output += "# SSOT INTEGRITY CONSTRAINTS\n"
    output += "# ============================================================================\n"
    output += "try:\n"
    output += "    assert abs(sum([WEIGHT_HEALTH_HEAL_CAP, WEIGHT_HEALTH_INVOCATION, WEIGHT_HEALTH_TEST, WEIGHT_HEALTH_OBSERVABLE, WEIGHT_HEALTH_COMPLEXITY]) - 1.0) < 0.001\n"
    output += "    assert abs(sum([WEIGHT_HEALTH_L0_TEST, WEIGHT_HEALTH_L0_HARDENED, WEIGHT_HEALTH_L0_COMPLEXITY]) - 1.0) < 0.001\n"
    output += "    assert abs(sum([WEIGHT_CODE_QUALITY_TYPED, WEIGHT_CODE_QUALITY_DOCUMENTED, WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS, WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE]) - 1.0) < 0.001\n"
    output += "except AssertionError as e:\n"
    output += "    print(f'❌ CRITICAL: SSOT Weight mismatch detected in dashboard_ssot.yaml')\n"
    output += "    raise\n"

    output += "\n\n"

    # Add placeholders
    output += """# ============================================================================
# PLACEHOLDERS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

"""

    for key, value in config["placeholders"].items():
        const_name = f"PLACEHOLDER_{key.upper()}"
        output += f"{const_name} = {value}  # {key.replace('_', ' ').title()} awaiting implementation\n"

    output += "\n\n"

    # Add layer definitions
    output += """# ============================================================================
# LAYER DEFINITIONS
# ============================================================================

LAYER_ORDER = ['Base', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps']

# L0 is infrastructure layer - healing metrics are N/A
L0_HEALING_NA = True

# MCP-hardened base classes
MCP_HARDENED_BASES = {
    'SovereignBaseAgent', 'L0MaintenanceBaseAgent', 'L1CognitionBase',
    'L2ExecutionBase', 'L3OrchestrationBase', 'L4StateBase',
    'L5SafetyBase', 'L6ObservabilityBase', 'MCPHardenedMixin'
}

# Healer base classes
HEALER_BASES = {
    'HealerMixin', 'SovereignBaseAgent', 'L0MaintenanceBaseAgent',
    'L1CognitionBase', 'L2ExecutionBase', 'L3OrchestrationBase',
    'L4StateBase', 'L5SafetyBase', 'L6ObservabilityBase'
}


"""

    # Append existing calculation functions
    if existing_content:
        output += existing_content
    else:
        # Add placeholder for calculation functions
        output += '''# ============================================================================
# METRIC CALCULATION FUNCTIONS (SSOT)
# ============================================================================
# These functions are preserved from the original file.
# Add calculation functions here.

def calc_heal_cap_pct(agents: List[Dict], is_l0: bool = False) -> float:
    """Calculate Heal Capability % for a set of agents."""
    if is_l0:
        return 0.0
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False))
    return round(count / len(agents) * 100, 1)

# Add other calculation functions as needed...
'''

    return output


def generate_js_constants(config):
    """Generate JavaScript constants file from YAML config."""

    output = f"""// ============================================================================
// DASHBOARD CONSTANTS
// ============================================================================
// ⚠️  AUTO-GENERATED FROM agentic_core/L6_observability/dashboards/dashboard_ssot.yaml
// ⚠️  DO NOT EDIT MANUALLY - Edit the YAML file instead
// ⚠️  Run: python scripts/generate_dashboard_ssot_util.py
//
// Last Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
// ============================================================================

// ============================================================================
// COLUMN NAMES
// ============================================================================
// Display names for dashboard table columns

window.COLUMNS = {{
"""

    for key, value in config["columns"].items():
        js_key = key.upper()
        output += f'    {js_key}: "{value}",\n'

    output += "};\n\n"

    # Add field names
    output += """// ============================================================================
// FIELD NAMES
// ============================================================================
// Field names from agent_discovery_full.json

window.FIELDS = {
"""

    for key, value in config["fields"].items():
        js_key = key.upper()
        output += f'    {js_key}: "{value}",\n'

    output += "};\n\n"

    # Add thresholds
    output += """// ============================================================================
// METRIC THRESHOLDS
// ============================================================================
// Standard thresholds for validation and outlier detection

window.THRESHOLDS = {
"""

    for key, value in config["thresholds"].items():
        js_key = key.upper()
        output += f"    {js_key}: {value},\n"

    output += "};\n\n"

    # Add JS metric keys
    output += """// ============================================================================
// JAVASCRIPT METRIC KEYS
// ============================================================================
// CamelCase keys used in agentData objects

window.METRIC_KEYS = {
"""

    for key, value in config["js_keys"].items():
        output += f'    {key.upper()}: "{value}",\n'

    output += "};\n\n"

    # Add health weights
    output += """// ============================================================================
// HEALTH SCORE WEIGHTS
// ============================================================================

window.HEALTH_WEIGHTS = {
"""

    for key, value in config["health_weights"].items():
        js_key = key.upper()
        output += f"    {js_key}: {value},\n"

    output += "};\n\n"

    output += "window.HEALTH_WEIGHTS_L0 = {\n"
    for key, value in config["health_weights_l0"].items():
        js_key = key.upper()
        output += f"    {js_key}: {value},\n"

    output += "};\n\n"

    # Add code quality weights
    output += """// ============================================================================
// CODE QUALITY WEIGHTS
// ============================================================================

window.CODE_QUALITY_WEIGHTS = {
"""

    for key, value in config["code_quality_weights"].items():
        js_key = key.upper()
        output += f"    {js_key}: {value},\n"

    output += "};\n\n"

    # Add placeholders
    output += """// ============================================================================
// PLACEHOLDERS
// ============================================================================

window.PLACEHOLDERS = {
"""

    for key, value in config["placeholders"].items():
        js_key = key.upper()
        output += f"    {js_key}: {value},\n"

    output += "};\n"

    return output


def main():
    """Main synchronization function."""
    print("=" * 70)
    print("DASHBOARD SSOT SYNCHRONIZATION ENGINE")
    print("=" * 70)
    print()

    # Load YAML config
    print(f"📖 Loading YAML config: {YAML_CONFIG}")
    config = load_yaml_config()
    print(f"   ✅ Loaded {len(config)} sections")
    print()

    # Generate Python constants
    print(f"🐍 Generating Python constants: {PYTHON_OUTPUT}")
    python_content = generate_python_constants(config)

    with open(PYTHON_OUTPUT, "w", encoding="utf-8") as f:
        f.write(python_content)

    print(f"   ✅ Generated {len(python_content.splitlines())} lines")
    print()

    # Generate JavaScript constants
    print(f"📜 Generating JavaScript constants: {JS_OUTPUT}")

    # Ensure directory exists
    JS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    js_content = generate_js_constants(config)

    with open(JS_OUTPUT, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"   ✅ Generated {len(js_content.splitlines())} lines")
    print()

    # Summary
    print("=" * 70)
    print("✅ SYNCHRONIZATION COMPLETE")
    print("=" * 70)
    print()
    print("Generated files:")
    print(f"  1. {PYTHON_OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"  2. {JS_OUTPUT.relative_to(PROJECT_ROOT)}")
    print()
    print("Next steps:")
    print("  1. Review generated files")
    print("  2. Update JS files to import from dashboard-constants.js")
    print("  3. Run: python scripts/regenerate_dashboard_data.py")
    print("  4. Test dashboard in browser")
    print()


if __name__ == "__main__":
    main()
