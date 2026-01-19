#!/usr/bin/env python3
"""
CRITICAL: Health Score Validation
Tests that Health scores are correctly calculated and within valid ranges.
This is a HARD BLOCKER for deployment.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent

def validate_health_score_calculation():
    """Validate Health scores match SSOT formula calculations."""
    print("\n" + "="*70)
    print("CRITICAL: Health Score Calculation Validation")
    print("="*70)
    
    # Import SSOT calculation functions
    sys.path.insert(0, str(project_root / "scripts"))
    from dashboard_ssot_definitions import (
        calc_health_score, is_l0_territory
    )
    
    # Load dashboard data
    data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    data = json.loads(content)
    
    failures = []
    tolerance = 0.2  # Allow 0.2% difference for floating point
    
    print(f"\n   Validating Health score calculations for {len(data)} territories...")
    
    for row in data:
        territory = row['Territory']
        
        # Get dashboard values
        dashboard_health = row.get('Health')
        heal_cap = row.get('Heal Cap %', 0)
        invocation = row.get('Invocation %', 0)
        test = row.get('Test %', 0)
        complexity_health = row.get('Complexity Health %', 0)
        
        if dashboard_health is None:
            failures.append(f"{territory}: Health field is None")
            continue
        
        # Recalculate expected health using SSOT formula
        is_l0 = is_l0_territory(territory)
        expected_health = calc_health_score(
            heal_cap, invocation, test,
            50.0,  # Observable % placeholder (same as generation)
            complexity_health,
            is_l0=is_l0
        )
        
        # Compare
        diff = abs(dashboard_health - expected_health)
        if diff > tolerance:
            failures.append(
                f"{territory}: Health mismatch (expected {expected_health:.1f}, got {dashboard_health:.1f}, diff {diff:.1f})"
            )
    
    if failures:
        print(f"\n❌ HEALTH CALCULATION FAILED: {len(failures)} mismatches")
        for f in failures[:10]:
            print(f"   {f}")
        if len(failures) > 10:
            print(f"   ... and {len(failures) - 10} more")
        return False
    else:
        print(f"\n✅ PASSED: All Health scores match SSOT calculations")
        return True

def validate_health_score_ranges():
    """Validate Health scores are within valid ranges (0-100)."""
    print("\n" + "="*70)
    print("CRITICAL: Health Score Range Validation")
    print("="*70)
    
    # Load dashboard data
    data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    data = json.loads(content)
    
    failures = []
    warnings = []
    
    for row in data:
        territory = row['Territory']
        health = row.get('Health')
        
        if health is None:
            failures.append(f"{territory}: Health is None")
        elif health < 0 or health > 100:
            failures.append(f"{territory}: Health={health:.1f} (out of range 0-100)")
        elif health < 50:
            warnings.append(f"⚠️  {territory}: Health={health:.1f}% (critically low, <50%)")
    
    if failures:
        print(f"\n❌ RANGE VALIDATION FAILED: {len(failures)} out-of-range values")
        for f in failures:
            print(f"   {f}")
        return False
    else:
        print(f"\n✅ PASSED: All Health scores in valid range (0-100)")
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} territories with critically low health (<50%):")
            for w in warnings[:5]:
                print(f"   {w}")
            if len(warnings) > 5:
                print(f"   ... and {len(warnings) - 5} more")
        
        return True

def validate_health_score_sanity():
    """Sanity checks: Health should correlate with component metrics."""
    print("\n" + "="*70)
    print("CRITICAL: Health Score Sanity Checks")
    print("="*70)
    
    # Load dashboard data
    data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    data = json.loads(content)
    
    warnings = []
    
    for row in data:
        if row['Territory'] == 'TOTAL':
            continue
        
        territory = row['Territory']
        health = row.get('Health', 0)
        heal_cap = row.get('Heal Cap %', 0)
        test = row.get('Test %', 0)
        complexity_health = row.get('Complexity Health %', 0)
        
        # Sanity check: If all component metrics are high, health should be high
        if heal_cap > 90 and test > 90 and complexity_health > 50:
            if health < 70:
                warnings.append(
                    f"⚠️  {territory}: High component metrics but low Health "
                    f"(Heal:{heal_cap:.0f}%, Test:{test:.0f}%, ComplexHealth:{complexity_health:.0f}%, Health:{health:.0f}%)"
                )
        
        # Sanity check: If all component metrics are low, health should be low
        if heal_cap < 50 and test < 50:
            if health > 70:
                warnings.append(
                    f"⚠️  {territory}: Low component metrics but high Health "
                    f"(Heal:{heal_cap:.0f}%, Test:{test:.0f}%, Health:{health:.0f}%)"
                )
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} sanity check warnings:")
        for w in warnings[:5]:
            print(f"   {w}")
        if len(warnings) > 5:
            print(f"   ... and {len(warnings) - 5} more")
    else:
        print(f"\n✅ PASSED: Health scores correlate with component metrics")
    
    # Warnings don't fail the test
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CRITICAL: HEALTH SCORE VALIDATION")
    print("="*70)
    print("\nHealth score is the PRIMARY METRIC for territory health.")
    print("Missing or incorrect Health scores are DEPLOYMENT BLOCKERS.")
    
    all_passed = True
    
    all_passed &= validate_health_score_calculation()
    all_passed &= validate_health_score_ranges()
    all_passed &= validate_health_score_sanity()
    
    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    
    if all_passed:
        print("\n✅ ALL HEALTH SCORE VALIDATIONS PASSED")
        print("   - Calculation accuracy ✅")
        print("   - Range validation ✅")
        print("   - Sanity checks ✅")
        print("\n✅ HEALTH SCORES CORRECT - DEPLOYMENT APPROVED")
        sys.exit(0)
    else:
        print("\n❌ HEALTH SCORE VALIDATION FAILED")
        print("\n❌ DEPLOYMENT BLOCKED - FIX HEALTH SCORE CALCULATION")
        sys.exit(1)
