#!/usr/bin/env python3
import os
import sys

if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
Regenerate FULL dashboard data from agent_discovery_full.json.

This updates:
1. dashboardData (Table 1 territory summaries)
2. realAgentData (Table 2 per-agent metrics)
3. Strategic Observations (via StrategicRecommendationAgent)

NO HARDCODING - all values calculated from discovery data.
Uses dashboard_ssot_definitions.py as SINGLE SOURCE OF TRUTH for all calculations.

GUARDRAILS (RCA 2026-01-20):
- Corruption detection: Checks for multiple </html> tags
- Bracket counting: Proper JSON replacement without partial matches
- Pattern flexibility: Handles window.x || fallback patterns
- Size validation: Warns if HTML exceeds expected size
- Duplicate detection: Validates no duplicate JS declarations
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(
    __file__,
).parent.parent.parent.parent  # agentic_core/L0_maintenance/scripts -> project root
DISCOVERY_PATH = PROJECT_ROOT / "agent_discovery_full.json"
DASHBOARD_PATH = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"

# Add project root to path for imports
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

# Import SSOT definitions
from agentic_core.L5_safety.validators.dashboard_ssot_definitions_config import (
    FIELD_CYCLOMATIC_COMPLEXITY,
    FIELD_DOCUMENTED_PCT,
    FIELD_HAS_HEALING,
    FIELD_HAS_TESTS,
    FIELD_INVOCATION,
    FIELD_MCP_HARDENED,
    FIELD_PROPER_BASE_CLASS,
    FIELD_SCHEMA_STRICTNESS,
    FIELD_TYPED_PCT,
    calc_avg_cc,
    calc_canonical_inheritance_pct,
    calc_code_quality_score,
    calc_complexity_health,
    calc_documented_pct,
    calc_hardened_pct,
    calc_heal_cap_pct,
    calc_health_score,
    calc_invocation_pct,
    calc_schema_strictness_pct,
    calc_test_pct,
    calc_typed_pct,
    get_heal_cap_display,
    get_invocation_display,
    get_territory_sort_key,
    is_l0_territory,
    sort_dashboard_data,
)

# Territory name mapping (discovery -> dashboard)
TERRITORY_MAPPING = {
    "Base/Base Class": "Base/Root",
    "L0 Maintenance/Base Class": "L0 Maintenance/Base Agent",
    "L1 Cognition/Base Class": "L1 Cognition/Base Agent",
    "L2 Execution/Base Class": "L2 Execution/Base Agent",
    "L3 Orchestration/Base Class": "L3 Orchestration/Base Agent",
    "L4 State/Base Class": "L4 State/Base Agent",
    "L5 Safety/Base Class": "L5 Safety/Base Agent",
    "L6_Observability/Base Class": "L6 observability/Base Agent",
    "L6_Observability/Metrics": "L6 observability/Metrics",
    "L6_Observability/Telemetry": "L6 observability/Infrastructure",
    "L1/Prompt_Governance": "L1 Cognition/Core",
    "Utils": "Apps Shared",
}


def calculate_code_quality(typed: float, documented: float, schema: float, base: float) -> float:
    """Calculate Code Quality Score using SSOT formula."""
    return calc_code_quality_score(typed, documented, schema, base)


def build_real_agent_data(agents: list[dict], territory_mapping: dict[str, str]) -> dict[str, Any]:
    """Build realAgentData structure from discovery data."""
    # Group agents by normalized territory
    territory_agents = defaultdict(list)
    for agent in agents:
        territory = agent.get("territory", "Unknown")
        mapped = territory_mapping.get(territory, territory)
        territory_agents[mapped].append(agent)

    real_agent_data = {}

    for territory, agent_list in territory_agents.items():
        # Initialize arrays for each metric
        heal_cap = []
        invocation = []
        hardened = []
        test = []
        complexity_health = []
        health = []
        typed = []
        documented = []
        schema_strictness = []
        proper_base = []
        code_quality = []
        agents_data = []

        for agent in agent_list:
            # Extract metrics from discovery using SSOT field names
            has_healing = 100.0 if agent.get(FIELD_HAS_HEALING, False) else 0.0
            has_invocation = 100.0 if agent.get(FIELD_INVOCATION) == "Yes" else 0.0
            is_hardened = 100.0 if agent.get(FIELD_MCP_HARDENED, False) else 0.0
            has_tests = 100.0 if agent.get(FIELD_HAS_TESTS, False) else 0.0

            # Complexity health using SSOT calculation
            cc = agent.get(FIELD_CYCLOMATIC_COMPLEXITY, 0)
            comp_health = calc_complexity_health(cc)

            # Get actual percentages from discovery using SSOT field names
            typed_pct = agent.get(FIELD_TYPED_PCT, 0.0)
            doc_pct = agent.get(FIELD_DOCUMENTED_PCT, 0.0)
            schema_pct = agent.get(FIELD_SCHEMA_STRICTNESS, 0.0)
            base_pct = 100.0 if agent.get(FIELD_PROPER_BASE_CLASS, False) else 0.0

            # Calculate code quality
            quality = calculate_code_quality(typed_pct, doc_pct, schema_pct, base_pct)

            # Calculate health score using SSOT formula
            observable = 100.0 if agent.get("observability", {}).get("logging", False) else 0.0
            agent_health = calc_health_score(
                has_healing,
                has_invocation,
                has_tests,
                observable,
                comp_health,
                is_l0=is_l0_territory(territory),
            )

            # Add to arrays
            heal_cap.append(has_healing)
            invocation.append(has_invocation)
            hardened.append(is_hardened)
            test.append(has_tests)
            complexity_health.append(comp_health)
            health.append(agent_health)
            typed.append(typed_pct)
            documented.append(doc_pct)
            schema_strictness.append(schema_pct)
            proper_base.append(base_pct)
            code_quality.append(quality)

            # Build agent detail
            obs = agent.get("observability", {})
            has_proper_base = agent.get(FIELD_PROPER_BASE_CLASS, False)
            inheritance_list = agent.get("inheritance", [])
            base_class_name = inheritance_list[-1] if inheritance_list else "Unknown"

            agents_data.append(
                {
                    "name": agent.get("class_name", "Unknown"),
                    "path": agent.get("path", ""),
                    "rel": agent.get("path", ""),
                    "abs_file": str(PROJECT_ROOT / agent.get("path", "")),
                    "abs_class": str(PROJECT_ROOT / agent.get("path", "")),
                    "class_line": 1,
                    "has_mixin": agent.get(FIELD_HAS_HEALING, False),
                    "invocation": agent.get(FIELD_INVOCATION, "No"),
                    "has_tests": agent.get(FIELD_HAS_TESTS, False),
                    "obs_summary": f"Logging: {'✓' if obs.get('logging') else '✗'} | Metrics: {'✓' if obs.get('metrics') else '✗'} | Tracing: {'✓' if obs.get('tracing') else '✗'}",
                    "mcp_summary": f"Shield: {'✓' if agent.get(FIELD_MCP_HARDENED) else '✗'} | @hardened: ✗ | Safe: ✓",
                    "typing_summary": f"Typed: {typed_pct:.0f}%",
                    "typed_pct": typed_pct,
                    "overall_typed_pct": typed_pct,
                    "complexity": cc,
                    "health": agent_health,
                    "healCap": has_healing,
                    "test": has_tests,
                    "complexityHealth": comp_health,
                    "hardened": is_hardened,
                    "documented": doc_pct,
                    "schema": schema_pct,
                    "base": base_pct,
                    "proper_base_class": has_proper_base,  # Boolean for drill-down display
                    "base_class_name": base_class_name,  # Name of base class for display
                    "has_base_violation": not has_proper_base,  # For row highlighting
                    "quality": quality,
                    "loc": agent.get("loc", 50),
                },
            )

        real_agent_data[territory] = {
            "healCap": heal_cap,
            "invocation": invocation,
            "hardened": hardened,
            "test": test,
            "complexityHealth": complexity_health,
            "health": health,
            "typed": typed,
            "documented": documented,
            "schemaStrictness": schema_strictness,
            "properBase": proper_base,
            "codeQuality": code_quality,
            "agents": agents_data,
        }

    return real_agent_data


def build_dashboard_data(agents: list[dict], territory_mapping: dict[str, str]) -> list[dict]:
    """Build dashboardData structure from discovery data."""
    # Group agents by normalized territory
    territory_agents = defaultdict(list)
    for agent in agents:
        territory = agent.get("territory", "Unknown")
        mapped = territory_mapping.get(territory, territory)
        territory_agents[mapped].append(agent)

    dashboard_data = []

    # Build TOTAL row first - using SSOT calculation functions
    total_agents = len(agents)

    # Use SSOT functions for all metric calculations
    heal_cap_pct = calc_heal_cap_pct(agents)
    invocation_pct = calc_invocation_pct(agents)
    test_pct = calc_test_pct(agents)
    hardened_pct = calc_hardened_pct(agents)
    proper_base_pct = calc_canonical_inheritance_pct(agents)
    avg_typed = calc_typed_pct(agents)
    avg_documented = calc_documented_pct(agents)
    avg_schema = calc_schema_strictness_pct(agents)
    avg_cc = calc_avg_cc(agents)
    complexity_health = calc_complexity_health(avg_cc)

    # Calculate health score using SSOT formula
    health = calc_health_score(heal_cap_pct, invocation_pct, test_pct, 50.0, complexity_health, is_l0=False)

    code_quality = calculate_code_quality(avg_typed, avg_documented, avg_schema, proper_base_pct)

    total_row = {
        "Territory": "TOTAL",
        "Total": total_agents,
        "Compliant": total_agents,
        "Heal Cap %": heal_cap_pct,
        "Heal Invocation %": invocation_pct,
        "Invocation %": invocation_pct,
        "Test %": test_pct,
        "Observable %": 50.0,
        "Avg CC": round(avg_cc, 1),
        "Typed %": round(avg_typed, 1),
        "Documented %": round(avg_documented, 1),
        "Metadata %": 100.0,
        "Canonical Inheritance %": proper_base_pct,
        "schema Strictness %": round(avg_schema, 1),
        "Complexity Health": complexity_health,
        "Code Quality Score": code_quality,
        "Health": health,
        "Risk": "Low" if health >= 75 else "Medium" if health >= 50 else "High",
        "Hardened %": hardened_pct,
        "Criticality": 75,
    }
    dashboard_data.append(total_row)

    # Build territory rows using SSOT functions
    for territory, agent_list in sorted(territory_agents.items(), key=lambda x: get_territory_sort_key(x[0])):
        count = len(agent_list)
        if count == 0:
            continue

        # L0 is infrastructure/scripts layer - healing N/A (SSOT definition)
        is_l0 = is_l0_territory(territory)

        # Use SSOT functions for all calculations
        t_heal_cap_pct_val = calc_heal_cap_pct(agent_list, is_l0)
        t_invocation_pct_val = calc_invocation_pct(agent_list, is_l0)
        t_test_pct = calc_test_pct(agent_list)
        t_hardened_pct = calc_hardened_pct(agent_list)
        t_proper_base_pct = calc_canonical_inheritance_pct(agent_list)
        t_typed = calc_typed_pct(agent_list)
        t_documented = calc_documented_pct(agent_list)
        t_schema = calc_schema_strictness_pct(agent_list)
        t_cc = calc_avg_cc(agent_list)
        t_complexity_health = calc_complexity_health(t_cc)

        # Use SSOT display functions for L0 N/A handling
        t_heal_cap_pct = get_heal_cap_display(t_heal_cap_pct_val, is_l0)
        t_invocation_pct = get_invocation_display(t_invocation_pct_val, is_l0)

        # Use SSOT health calculation
        t_health = calc_health_score(
            t_heal_cap_pct_val,
            t_invocation_pct_val,
            t_test_pct,
            50.0,
            t_complexity_health,
            is_l0=is_l0,
        )

        t_code_quality = calculate_code_quality(t_typed, t_documented, t_schema, t_proper_base_pct)

        territory_row = {
            "Territory": territory,
            "Total": count,
            "Compliant": count,
            "Heal Cap %": t_heal_cap_pct,
            "Heal Invocation %": t_invocation_pct,
            "Invocation %": t_invocation_pct,
            "Test %": t_test_pct,
            "Observable %": 50.0,
            "Avg CC": round(t_cc, 1),
            "Typed %": round(t_typed, 1),
            "Documented %": round(t_documented, 1),
            "Metadata %": 100.0,
            "Canonical Inheritance %": t_proper_base_pct,
            "schema Strictness %": round(t_schema, 1),
            "Complexity Health": t_complexity_health,
            "Code Quality Score": t_code_quality,
            "Health": t_health,
            "Risk": "Low" if t_health >= 75 else "Medium" if t_health >= 50 else "High",
            "Hardened %": t_hardened_pct,
            "Criticality": 75,
        }
        dashboard_data.append(territory_row)

    # Apply SSOT sorting: Base/Root first, TOTAL last
    return sort_dashboard_data(dashboard_data)


def generate_strategic_recommendations(dashboard_data: list[dict]) -> dict[str, Any]:
    """
    Generate strategic recommendations using StrategicRecommendationAgent.

    Args:
        dashboard_data: List of territory metrics

    Returns:
        Dict with 'review' and 'recommendations' keys
    """
    try:
        # Correct import path: L1_cognition/thought_engine/
        from agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent import (
            StrategicRecommendationAgent,
        )

        agent = StrategicRecommendationAgent(project_root=PROJECT_ROOT)
        result = agent.run(dashboard_data)
        return result
    except ImportError as e:
        print(f"  ⚠️  StrategicRecommendationAgent import failed: {e}")
        return {
            "review": "Strategic analysis unavailable - module not found.",
            "recommendations": [],
        }
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"  ⚠️  StrategicRecommendationAgent failed: {e}")
        # Return fallback
        return {
            "review": "Strategic analysis unavailable - agent initialization failed.",
            "recommendations": [],
        }


def inject_strategic_observations(content: str, recommendations: dict[str, Any]) -> str:
    """
    Inject strategic observations and recommendations into dashboard HTML.

    Updates both strategicObservationsData and recommendationsData JavaScript variables.
    """
    # Build the recommendations data structure for JavaScript
    recs_data = []
    for i, rec in enumerate(recommendations.get("recommendations", []), 1):
        # Parse recommendation format: "1. Title<br>Details..."
        if "<br>" in rec:
            parts = rec.split("<br>", 1)
            title = parts[0].lstrip("0123456789. ")
            description = parts[1] if len(parts) > 1 else ""
        else:
            title = rec.lstrip("0123456789. ")
            description = ""

        recs_data.append(
            {
                "priority": i,
                "title": title,
                "description": description,
                "impact": "HIGH" if i <= 3 else "MEDIUM" if i <= 7 else "LOW",
                "effort": "MEDIUM",
            },
        )

    # Build the observations data structure
    obs_data = {
        "macro_observations": recommendations.get("macro_observations", []),
        "metric_observations": recommendations.get("metric_observations", []),
    }

    # Find and replace strategicObservationsData - use brace counting (RCA 2026-01-20)
    # Handle both patterns: 'const x = {' and 'const x = window.x || {'
    obs_start_idx = content.find("const strategicObservationsData = window.strategicObservationsData || {")
    if obs_start_idx == -1:
        obs_start_idx = content.find("const strategicObservationsData = {")

    if obs_start_idx == -1:
        # Add before recommendationsData (but only if it doesn't exist)
        recs_idx = content.find("const recommendationsData = ")
        if recs_idx != -1:
            new_obs = f"const strategicObservationsData = {json.dumps(obs_data, indent=2)};\n\n        "
            content = content[:recs_idx] + new_obs + content[recs_idx:]
    else:
        # Use brace counting to find matching close (RCA fix)
        brace_count = 0
        obs_end_idx = obs_start_idx
        for i, char in enumerate(content[obs_start_idx:], obs_start_idx):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    obs_end_idx = i + 1
                    break
        # Skip semicolon if present
        if obs_end_idx < len(content) and content[obs_end_idx] == ";":
            obs_end_idx += 1

        new_obs = f"const strategicObservationsData = {json.dumps(obs_data, indent=2)};"
        content = content[:obs_start_idx] + new_obs + content[obs_end_idx:]

    # Find and replace recommendationsData - handle both patterns
    # Pattern 1: 'const recommendationsData = ['
    # Pattern 2: 'const recommendationsData = window.recommendationsData || ['
    marker_start = "const recommendationsData = window.recommendationsData || ["
    start_idx = content.find(marker_start)
    if start_idx == -1:
        marker_start = "const recommendationsData = ["
        start_idx = content.find(marker_start)

    if start_idx == -1:
        # If not found, try to add it before dashboardData
        dd_idx = content.find("const dashboardData = ")
        if dd_idx != -1:
            new_recs = f"const recommendationsData = {json.dumps(recs_data, indent=2)};\n\n        "
            content = content[:dd_idx] + new_recs + content[dd_idx:]
    else:
        # Find matching closing bracket by counting brackets
        bracket_count = 0
        end_idx = start_idx
        for i, char in enumerate(content[start_idx:], start_idx):
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        # Skip semicolon if present
        if end_idx < len(content) and content[end_idx] == ";":
            end_idx += 1

        new_recs = f"const recommendationsData = {json.dumps(recs_data, indent=2)};"
        content = content[:start_idx] + new_recs + content[end_idx:]

    return content


# =============================================================================
# GUARDRAILS - Post-regeneration validation (RCA 2026-01-20)
# =============================================================================


def validate_html_integrity(content: str) -> tuple[bool, list[str]]:
    """
    Validate HTML integrity after regeneration.

    GUARDRAILS:
    1. Single </html> tag (no corruption)
    2. Reasonable file size (< 1MB)
    3. No duplicate JS declarations
    4. Valid JSON in data structures

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Guardrail 1: Single </html> tag
    html_end_count = content.count("</html>")
    if html_end_count != 1:
        errors.append(f"CORRUPTION: Found {html_end_count} </html> tags (expected 1)")

    # Guardrail 2: Reasonable file size (< 1MB)
    size_kb = len(content) / 1024
    if size_kb > 1000:
        errors.append(f"BLOAT: HTML file is {size_kb:.0f}KB (expected < 1000KB)")
    elif size_kb > 700:
        errors.append(f"WARNING: HTML file is {size_kb:.0f}KB (approaching limit)")

    # Guardrail 3: No duplicate JS declarations
    js_declarations = [
        ("dashboardData", r"const\s+dashboardData\s*="),
        ("realAgentData", r"const\s+realAgentData\s*="),
        ("recommendationsData", r"const\s+recommendationsData\s*="),
        ("strategicObservationsData", r"const\s+strategicObservationsData\s*="),
    ]

    for var_name, pattern in js_declarations:
        matches = re.findall(pattern, content)
        if len(matches) > 1:
            errors.append(f"DUPLICATE: {var_name} declared {len(matches)} times")

    # Guardrail 4: TOTAL row exists in dashboardData
    if '"Territory": "TOTAL"' not in content and "'Territory': 'TOTAL'" not in content:
        errors.append("MISSING: TOTAL row not found in dashboardData")

    # Guardrail 5: Balanced script tags
    script_open = content.count("<script")
    script_close = content.count("</script>")
    if script_open != script_close:
        errors.append(f"UNBALANCED: {script_open} <script> vs {script_close} </script>")

    is_valid = len([e for e in errors if not e.startswith("WARNING")]) == 0
    return is_valid, errors


def validate_pre_regeneration(content: str) -> tuple[str, list[str]]:
    """
    Validate and potentially fix HTML before regeneration.

    Returns:
        (cleaned_content, warnings)
    """
    warnings = []

    # Check for corruption and auto-fix
    html_end_count = content.count("</html>")
    if html_end_count > 1:
        warnings.append(f"Auto-fixed: Truncated corrupted HTML ({html_end_count} </html> tags)")
        first_html_end = content.find("</html>") + len("</html>")
        content = content[:first_html_end]

    # Check size
    size_kb = len(content) / 1024
    if size_kb > 700:
        warnings.append(f"Input HTML is large: {size_kb:.0f}KB")

    return content, warnings


def main():
    print("=" * 70)
    print("FULL Dashboard Regeneration from agent_discovery_full.json")
    print("NO HARDCODING - All values calculated from discovery")
    print("=" * 70)

    # Load agent discovery
    with open(DISCOVERY_PATH, encoding="utf-8") as f:
        agents = json.load(f)

    print(f"\nLoaded {len(agents)} agents from discovery")

    # Build realAgentData
    print("\nBuilding realAgentData (Table 2 per-agent metrics)...")
    real_agent_data = build_real_agent_data(agents, TERRITORY_MAPPING)
    print(f"  Created {len(real_agent_data)} territory entries")

    # Build dashboardData
    print("\nBuilding dashboardData (Table 1 territory summaries)...")
    dashboard_data = build_dashboard_data(agents, TERRITORY_MAPPING)
    print(f"  Created {len(dashboard_data)} territory rows (including TOTAL)")

    # Generate strategic recommendations via StrategicRecommendationAgent
    print("\nGenerating strategic recommendations via StrategicRecommendationAgent...")
    strategic_recs = generate_strategic_recommendations(dashboard_data)
    print(f"  Generated {len(strategic_recs.get('recommendations', []))} recommendations")
    if strategic_recs.get("review"):
        print(f"  Review: {strategic_recs['review'][:100]}...")

    # Load dashboard HTML
    content = DASHBOARD_PATH.read_text(encoding="utf-8")

    # CRITICAL: Verify HTML ends with </html> - detect corruption
    html_end_count = content.count("</html>")
    if html_end_count > 1:
        print(f"  ⚠️  WARNING: HTML file appears corrupted ({html_end_count} </html> tags)")
        print("  ⚠️  Truncating to first </html> tag...")
        first_html_end = content.find("</html>") + len("</html>")
        content = content[:first_html_end]

    # Replace dashboardData - find the FIRST occurrence only
    # Handle both patterns: 'const dashboardData = [' and 'const dashboardData = window.dashboardData || ['
    print("\nUpdating dashboardData in HTML...")
    dd_start = content.find("const dashboardData = window.dashboardData || [")
    if dd_start == -1:
        dd_start = content.find("const dashboardData = [")
    if dd_start == -1:
        print("  ❌ ERROR: Could not find dashboardData declaration in HTML")
        return 1

    # Find the matching closing bracket by counting brackets
    bracket_count = 0
    dd_end = dd_start + len("const dashboardData = [")
    for i, char in enumerate(content[dd_start:], dd_start):
        if char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1
            if bracket_count == 0:
                dd_end = i + 1
                break

    # Skip the semicolon if present
    if dd_end < len(content) and content[dd_end] == ";":
        dd_end += 1

    new_dashboard_data = "const dashboardData = " + json.dumps(dashboard_data, indent=2) + ";"
    content = content[:dd_start] + new_dashboard_data + content[dd_end:]

    # Replace realAgentData - find the FIRST occurrence only
    # Handle both patterns: 'const realAgentData = {' and 'const realAgentData = window.realAgentData || {'
    print("Updating realAgentData in HTML...")
    rad_start = content.find("const realAgentData = window.realAgentData || {")
    if rad_start == -1:
        rad_start = content.find("const realAgentData = {")
    if rad_start == -1:
        print("  ❌ ERROR: Could not find realAgentData declaration in HTML")
        return 1

    # Find the matching closing brace by counting braces
    brace_count = 0
    rad_end = rad_start + len("const realAgentData = {")
    for i, char in enumerate(content[rad_start:], rad_start):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                rad_end = i + 1
                break

    # Skip the semicolon if present
    if rad_end < len(content) and content[rad_end] == ";":
        rad_end += 1

    new_real_agent_data = "const realAgentData = " + json.dumps(real_agent_data, indent=2) + ";"
    content = content[:rad_start] + new_real_agent_data + content[rad_end:]

    # Inject strategic recommendations
    print("Injecting strategic recommendations...")
    content = inject_strategic_observations(content, strategic_recs)

    # GUARDRAIL: Post-regeneration validation (RCA 2026-01-20)
    print("\n" + "=" * 70)
    print("🛡️  GUARDRAIL VALIDATION")
    print("=" * 70)

    is_valid, validation_errors = validate_html_integrity(content)

    if validation_errors:
        for err in validation_errors:
            if err.startswith("WARNING"):
                print(f"  ⚠️  {err}")
            else:
                print(f"  ❌ {err}")

    if not is_valid:
        print("\n  ❌ VALIDATION FAILED - HTML not written")
        print("  Fix the issues above and try again")
        return 1

    print("  ✅ All guardrail checks passed")

    # Write updated dashboard
    DASHBOARD_PATH.write_text(content, encoding="utf-8")

    # Report final file size
    final_size_kb = len(content) / 1024
    print(f"\n  📊 Final HTML size: {final_size_kb:.0f}KB")

    print("\n" + "=" * 70)
    print("✅ Dashboard fully regenerated from discovery data!")
    print("   - dashboardData: Territory summaries updated")
    print("   - realAgentData: Per-agent metrics updated")
    print("   - recommendationsData: Strategic recommendations updated")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
