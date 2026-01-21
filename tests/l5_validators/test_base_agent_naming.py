#!/usr/bin/env python3
"""
CRITICAL: Base Agent Naming Convention Validation
Ensures correct naming for Base Agents in each layer.
This is a HARD BLOCKER for deployment.

Naming Rules:
1. "Sovereign Base Agent" (not "Base/Base Class")
2. Each layer L0-L6 must have "Base Agent" (not "Base Class")
3. Base Agent must be FIRST row for each layer
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def validate_base_agent_naming():
    """Validate Base Agent naming convention in dashboard data."""
    print("\n" + "="*70)
    print("CRITICAL: Base Agent Naming Convention Validation")
    print("="*70)

    # Load dashboard data
    data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    data = json.loads(content)

    failures = []

    # Required Base Agent names
    REQUIRED_BASE_AGENTS = [
        'Sovereign Base Agent',
        'L6_Observability/Base Agent',
        'L5 Safety/Base Agent',
        'L4 State/Base Agent',
        'L3 Orchestration/Base Agent',
        'L2 Execution/Base Agent',
        'L1 Cognition/Base Agent',
        'L0 Maintenance/Base Agent'
    ]

    # Check all required Base Agents exist
    territories = [row['Territory'] for row in data]

    for required in REQUIRED_BASE_AGENTS:
        if required not in territories:
            failures.append(f"Missing required Base Agent: '{required}'")

    # Check for incorrect "Base Class" naming
    FORBIDDEN_NAMES = [
        'Base/Base Class',
        'L6_Observability/Base Class',
        'L5 Safety/Base Class',
        'L4 State/Base Class',
        'L3 Orchestration/Base Class',
        'L2 Execution/Base Class',
        'L1 Cognition/Base Class',
        'L0 Maintenance/Base Class'
    ]

    for forbidden in FORBIDDEN_NAMES:
        if forbidden in territories:
            failures.append(f"Forbidden 'Base Class' naming found: '{forbidden}' (should be 'Base Agent')")

    if failures:
        print(f"\n❌ NAMING VALIDATION FAILED: {len(failures)} issues")
        for f in failures:
            print(f"   {f}")
        return False
    else:
        print(f"\n✅ PASSED: All Base Agent names correct")
        print(f"   - Sovereign Base Agent ✅")
        print(f"   - L6_Observability/Base Agent ✅")
        print(f"   - L5 Safety/Base Agent ✅")
        print(f"   - L4 State/Base Agent ✅")
        print(f"   - L3 Orchestration/Base Agent ✅")
        print(f"   - L2 Execution/Base Agent ✅")
        print(f"   - L1 Cognition/Base Agent ✅")
        print(f"   - L0 Maintenance/Base Agent ✅")
        return True

def validate_base_agent_order():
    """Validate Base Agent is first for each layer."""
    print("\n" + "="*70)
    print("CRITICAL: Base Agent Position Validation")
    print("="*70)

    # Load dashboard data
    data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    data = json.loads(content)

    territories = [row['Territory'] for row in data]

    # Expected order: TOTAL, Sovereign Base Agent, then each layer with Base Agent first
    expected_positions = {
        'TOTAL': 0,
        'Sovereign Base Agent': 1,
        'L6_Observability/Base Agent': 2,
        'L5 Safety/Base Agent': 5,  # After L6 territories
        'L4 State/Base Agent': 10,  # After L5 territories
        'L3 Orchestration/Base Agent': 13,  # After L4 territories
        'L2 Execution/Base Agent': 15,  # After L3 territories
        'L1 Cognition/Base Agent': 17,  # After L2 territories
        'L0 Maintenance/Base Agent': 19,  # After L1 territories
    }

    failures = []

    for base_agent, expected_pos in expected_positions.items():
        if base_agent in territories:
            actual_pos = territories.index(base_agent)
            if actual_pos != expected_pos:
                failures.append(
                    f"{base_agent}: Expected position {expected_pos}, found at {actual_pos}"
                )
        else:
            failures.append(f"{base_agent}: Not found in dashboard data")

    # Validate Base Agent is first for each layer
    layer_checks = [
        ('L6_Observability/Base Agent', ['L6_Observability/Metrics', 'L6_Observability/Telemetry']),
        ('L5 Safety/Base Agent', ['L5 Safety/Validators', 'L5 Safety/Guardrails', 'L5 Safety/Red Teaming', 'L5 Safety/Gravity']),
        ('L4 State/Base Agent', ['L4 State/Infrastructure', 'L4 State/Core']),
        ('L3 Orchestration/Base Agent', ['L3 Orchestration/Core']),
        ('L2 Execution/Base Agent', ['L2 Execution/Core']),
        ('L1 Cognition/Base Agent', ['L1 Cognition/Core']),
        ('L0 Maintenance/Base Agent', ['L0 Maintenance/Core']),
    ]

    for base_agent, layer_territories in layer_checks:
        if base_agent in territories:
            base_pos = territories.index(base_agent)
            for territory in layer_territories:
                if territory in territories:
                    territory_pos = territories.index(territory)
                    if territory_pos < base_pos:
                        failures.append(
                            f"{base_agent} must come BEFORE {territory} (Base Agent at {base_pos}, {territory} at {territory_pos})"
                        )

    if failures:
        print(f"\n❌ POSITION VALIDATION FAILED: {len(failures)} issues")
        for f in failures:
            print(f"   {f}")
        return False
    else:
        print(f"\n✅ PASSED: All Base Agents in correct positions")
        print(f"   - Sovereign Base Agent at position 1 (after TOTAL) ✅")
        print(f"   - Each layer's Base Agent comes FIRST ✅")
        return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CRITICAL: BASE AGENT NAMING & ORDERING VALIDATION")
    print("="*70)
    print("\nNaming Convention:")
    print("  - 'Sovereign Base Agent' (NOT 'Base/Base Class')")
    print("  - 'L6_Observability/Base Agent' (NOT 'L6_Observability/Base Class')")
    print("  - Same pattern for L5, L4, L3, L2, L1, L0")
    print("\nOrdering Rule:")
    print("  - Base Agent must be FIRST row for each layer")

    all_passed = True

    all_passed &= validate_base_agent_naming()
    all_passed &= validate_base_agent_order()

    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)

    if all_passed:
        print("\n✅ ALL BASE AGENT VALIDATIONS PASSED")
        print("   - Naming convention ✅")
        print("   - Position ordering ✅")
        print("\n✅ DEPLOYMENT APPROVED")
        sys.exit(0)
    else:
        print("\n❌ BASE AGENT VALIDATION FAILED")
        print("\n❌ DEPLOYMENT BLOCKED - FIX BASE AGENT NAMING/ORDERING")
        sys.exit(1)
