#!/usr/bin/env python3
"""
Recalculate Code Quality Scores in Dashboard

Updates the Code Quality Score formula from simple average (Typed + Documented) / 2
to weighted composite: (Typed × 0.30) + (Documented × 0.30) + (schema × 0.25) + (Canonical × 0.15)
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_PATH = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"


def calculate_code_quality_score(typed_pct, documented_pct, schema_pct, canonical_pct):
    """
    Calculate Code Quality Score using weighted formula.

    Formula: (Typed × 0.30) + (Documented × 0.30) + (schema × 0.25) + (Canonical × 0.15)

    Weights rationale:
    - Typed %: 30% - Critical for type safety and IDE support
    - Documented %: 30% - Essential for maintainability and onboarding
    - schema Strictness %: 25% - Important for data validation and contracts
    - Canonical Inheritance %: 15% - Architectural compliance, less critical than others
    """
    score = typed_pct * 0.30 + documented_pct * 0.30 + schema_pct * 0.25 + canonical_pct * 0.15
    return round(score, 1)


def extract_territory_data(content):
    """Extract all territory data blocks from dashboard."""
    # Find the dashboardData array
    match = re.search(r"const dashboardData = \[(.*?)\];", content, re.DOTALL)
    if not match:
        print("ERROR: Could not find dashboardData array")
        return None

    data_content = match.group(1)

    # Split into individual territory objects
    territories = []
    current_obj = ""
    brace_count = 0

    for char in data_content:
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1

        current_obj += char

        if brace_count == 0 and current_obj.strip():
            territories.append(current_obj.strip().rstrip(","))
            current_obj = ""

    return territories


def update_code_quality_score(territory_text):
    """Update Code Quality Score in a territory data block."""
    # Extract values
    typed_match = re.search(r'"Typed %":\s*([\d.]+)', territory_text)
    documented_match = re.search(r'"Documented %":\s*([\d.]+)', territory_text)
    schema_match = re.search(r'"schema Strictness %":\s*([\d.]+)', territory_text)
    canonical_match = re.search(r'"Canonical Inheritance %":\s*([\d.]+)', territory_text)

    if not all([typed_match, documented_match, schema_match, canonical_match]):
        return territory_text

    typed = float(typed_match.group(1))
    documented = float(documented_match.group(1))
    schema = float(schema_match.group(1))
    canonical = float(canonical_match.group(1))

    # Calculate new score
    new_score = calculate_code_quality_score(typed, documented, schema, canonical)

    # Replace old score
    updated = re.sub(r'"Code Quality Score":\s*[\d.]+', f'"Code Quality Score": {new_score}', territory_text)

    return updated


def main():
    """Main function to recalculate all Code Quality Scores."""
    print("=" * 70)
    print("Recalculating Code Quality Scores")
    print("=" * 70)

    if not DASHBOARD_PATH.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_PATH}")
        return 1

    # Read dashboard
    content = DASHBOARD_PATH.read_text(encoding="utf-8")

    # Extract territories
    territories = extract_territory_data(content)
    if not territories:
        return 1

    print(f"\nFound {len(territories)} territories to update")

    # Update each territory
    updated_territories = []
    changes = []

    for i, territory in enumerate(territories):
        # Extract territory name for logging
        name_match = re.search(r'"Territory":\s*"([^"]+)"', territory)
        territory_name = name_match.group(1) if name_match else f"Territory {i + 1}"

        # Extract old score
        old_score_match = re.search(r'"Code Quality Score":\s*([\d.]+)', territory)
        old_score = float(old_score_match.group(1)) if old_score_match else None

        # Update score
        updated = update_code_quality_score(territory)
        updated_territories.append(updated)

        # Extract new score
        new_score_match = re.search(r'"Code Quality Score":\s*([\d.]+)', updated)
        new_score = float(new_score_match.group(1)) if new_score_match else None

        if old_score != new_score:
            changes.append((territory_name, old_score, new_score))
            print(f"  ✓ {territory_name}: {old_score} → {new_score}")

    # Reconstruct dashboardData
    new_data_content = ",\n  ".join(updated_territories)
    new_dashboard_data = f"const dashboardData = [\n  {new_data_content}\n];"

    # Replace in content
    updated_content = re.sub(r"const dashboardData = \[.*?\];", new_dashboard_data, content, flags=re.DOTALL)

    # Write back
    DASHBOARD_PATH.write_text(updated_content, encoding="utf-8")

    print(f"\n✅ Updated {len(changes)} Code Quality Scores")
    print(f"Dashboard saved to: {DASHBOARD_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
