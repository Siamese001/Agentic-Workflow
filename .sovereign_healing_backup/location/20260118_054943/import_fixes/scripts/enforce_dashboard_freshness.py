#!/usr/bin/env python3
"""
Dashboard Freshness Enforcement Script

Ensures the dashboard is always up-to-date before commits.
Called by pre-commit hook to enforce SSOT compliance.

Features:
- Detects if discovery JSON is stale
- Auto-regenerates discovery and dashboard if needed
- Validates dashboard sources from SSOT JSON
- Blocks commits if dashboard is out of sync

Usage:
    python scripts/enforce_dashboard_freshness.py [--check-only]
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.smart_discovery import is_discovery_stale, get_json_mtime, get_latest_source_mtime

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dashboard_enforcer")


def check_dashboard_freshness() -> tuple[bool, str]:
    """
    Check if dashboard is fresh and sourced from SSOT.
    
    Returns:
        (is_fresh, reason)
    """
    dashboard_path = PROJECT_ROOT / REPORTS_DIR / "autonomy_dashboard.html"
    discovery_json = PROJECT_ROOT / AGENT_DISCOVERY_JSON
    
    # Check if dashboard exists
    if not dashboard_path.exists():
        return False, "Dashboard HTML does not exist"
    
    # Check if discovery JSON exists
    if not discovery_json.exists():
        return False, "Discovery JSON does not exist"
    
    # Check if discovery is stale
    is_stale, stale_reason = is_discovery_stale()
    if is_stale:
        return False, f"Discovery JSON is stale: {stale_reason}"
    
    # Check if dashboard is older than discovery JSON
    try:
        dashboard_mtime = datetime.fromtimestamp(dashboard_path.stat().st_mtime)
        json_mtime = get_json_mtime()
        
        if json_mtime and dashboard_mtime < json_mtime:
            return False, f"Dashboard ({dashboard_mtime}) is older than discovery JSON ({json_mtime})"
    except Exception as e:
        return False, f"Failed to check dashboard mtime: {e}"
    
    return True, "Dashboard is fresh"


def regenerate_dashboard() -> bool:
    """
    Regenerate discovery and dashboard.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        log.info("🔄 Regenerating discovery JSON...")
        from scripts.smart_discovery import ensure_fresh_discovery
        ensure_fresh_discovery()
        
        log.info("🔄 Regenerating dashboard...")
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        agent.generate_compliance_report(markdown=True)
        
        log.info("✅ Dashboard regenerated successfully")
        return True
    except Exception as e:
        log.error(f"❌ Failed to regenerate dashboard: {e}")
        return False


def main():
    """Main enforcement logic."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enforce dashboard freshness")
    parser.add_argument("--check-only", action="store_true", help="Only check, don't regenerate")
    args = parser.parse_args()
    
    log.info("=" * 80)
    log.info("DASHBOARD FRESHNESS ENFORCEMENT")
    log.info("=" * 80)
    
    # Check freshness
    is_fresh, reason = check_dashboard_freshness()
    
    if is_fresh:
        log.info("✅ Dashboard is fresh and up-to-date")
        log.info(f"   Reason: {reason}")
        return 0
    
    log.warning(f"⚠️  Dashboard is stale: {reason}")
    
    if args.check_only:
        log.error("❌ Dashboard freshness check failed (check-only mode)")
        return 1
    
    # Auto-regenerate
    log.info("")
    log.info("🔧 Auto-regenerating dashboard to ensure freshness...")
    log.info("")
    
    if regenerate_dashboard():
        log.info("")
        log.info("=" * 80)
        log.info("✅ DASHBOARD UPDATED SUCCESSFULLY")
        log.info("=" * 80)
        log.info("")
        log.info("📝 IMPORTANT: The following files have been updated:")
        log.info("   - agent_discovery_full.json")
        log.info("   - agent_discovery_full.manifest.json")
        log.info("   - reports/autonomy_dashboard.html")
        log.info("   - reports/autonomy_compliance_report.md")
        log.info("   - reports/autonomy_compliance_data.csv")
        log.info("")
        log.info("🔄 Please stage these files and commit again:")
        log.info("   git add agent_discovery_full.json agent_discovery_full.manifest.json reports/")
        log.info("   git commit")
        log.info("")
        return 1  # Block commit to force user to stage updated files
    else:
        log.error("")
        log.error("=" * 80)
        log.error("❌ DASHBOARD REGENERATION FAILED")
        log.error("=" * 80)
        log.error("")
        log.error("Please fix the errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
