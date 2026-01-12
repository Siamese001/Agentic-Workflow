#!/usr/bin/env python3
"""Debug which template is actually being loaded during generation."""
from pathlib import Path
import sys

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

sys.path.insert(0, str(Path.cwd()))

project_root = Path.cwd()

# Simulate the template loading logic from AutonomyGuardianAgent
template_path = project_root / AGENTIC_CORE_DIR / "config" / "validators" / "dashboard_template.html"

print("=" * 80)
print("TEMPLATE LOADING DEBUG")
print("=" * 80)
print(f"\nPrimary template path: {template_path}")
print(f"Primary template exists: {template_path.exists()}")

if not template_path.exists():
    # Fallback logic
    fallback_path = Path(__file__).parent / "dashboard_template.html"
    print(f"\nFallback to: {fallback_path}")
    print(f"Fallback exists: {fallback_path.exists()}")
    template_path = fallback_path

if template_path.exists():
    content = template_path.read_text(encoding='utf-8')
    print(f"\nTemplate being used: {template_path}")
    print(f"Template size: {len(content):,} bytes")
    print(f"Has 'Strategic Recommendations': {'Strategic Recommendations' in content}")
    print(f"Has 'STRATEGIC_REVIEW_INSERT': {'STRATEGIC_REVIEW_INSERT' in content}")
    
    # Show the section around Strategic Recommendations
    if 'Strategic Recommendations' in content:
        idx = content.find('Strategic Recommendations')
        snippet = content[max(0, idx-100):idx+200]
        print(f"\nContext around 'Strategic Recommendations':")
        print(snippet)
else:
    print("\nERROR: No template found!")

print("\n" + "=" * 80)
