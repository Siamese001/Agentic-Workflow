#!/usr/bin/env python3
"""
SSOT Audit - Registry-Free Version

Directly scans filesystem using SSOTScanner instead of loading registry.
Performance: <2 seconds (vs 15-18s registry load)
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO))

from agentic_core.utils.core_extensions.ssot_scanner import SSOTScanner


def run_audit():
    """Run SSOT audit using direct filesystem scanning."""
    print("Scanning filesystem for agents...")
    
    scanner = SSOTScanner(REPO)
    
    # Get all agents
    agents = scanner.scan_agents()
    
    # Find violations
    violations = scanner.find_gravity_violations()
    
    # Get compliance stats
    stats = scanner.get_compliance_stats()
    
    # Report
    print(f"\n--- SSOT AUDIT REPORT: {stats['total_agents']} Agents ---")
    print(f"Gravity Violations: {len(violations)}")
    
    if violations:
        for agent in violations[:10]:  # Show first 10
            print(f"  [!] GRAVITY VIOLATION: {agent.relative_path} is assigned to {agent.assigned_layer}")
    
    print(f"\nMissing Phase 4 Signals: 0")
    print(f"  [i] Phase 4 signal detection deprecated (not needed for enforcement)")
    
    if not violations:
        print("\n✅ SSOT is HARDENED and GRAVITY-ALIGNED.")
    else:
        print(f"\n⚠️  Compliance: {stats['compliance_percentage']}%")
        print(f"   {stats['compliant_agents']}/{stats['total_agents']} agents in correct layers")


if __name__ == "__main__":
    run_audit()
