#!/usr/bin/env python3
"""
MISSION TELEMETRY DASHBOARD
---------------------------
Visualizes the post-mission state from runtime_state.json.
Provides architectural health metrics and circuit breaker status.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Setup
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from agentic_core.L5_safety.config.structure_blueprint_config import (
    HEALING_CONFIG,
    RUNTIME_STATE_JSON,
)


def generate_report():
    state_path = project_root / RUNTIME_STATE_JSON

    if not state_path.exists():
        print(f"❌ No runtime state found at {state_path}")
        return

    try:
        with open(state_path) as f:
            state = json.load(f)
    except json.JSONDecodeError:
        print("❌ Corrupted runtime state file.")
        return

    metrics = state.get("shared_alignment_metrics", {})
    upgrades = metrics.get("upgrade_count", 0)
    scanned = metrics.get("files_scanned", 0)
    last_upgrade = metrics.get("last_upgrade", "N/A")

    # Calculate Ratios
    intervention_ratio = (upgrades / scanned * 100) if scanned > 0 else 0
    cb_limit = HEALING_CONFIG.get("max_shared_upgrades_per_run", 10)

    print("\n" + "=" * 50)
    print(f"📡 SOVEREIGN MISSION TELEMETRY [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 50)

    print("\n📊 VOLUME METRICS")
    print(f"   • Total Files Scanned:   {scanned}")
    print(f"   • Shared Upgrades:       {upgrades}")
    print(f"   • Intervention Ratio:    {intervention_ratio:.2f}%")

    print("\n🛡️  CIRCUIT BREAKER STATUS")
    print(f"   • Limit:                 {cb_limit} upgrades/run")
    print(f"   • Status:                {'🔴 TRIPPED' if upgrades >= cb_limit else '🟢 ACTIVE'}")
    print(f"   • Capacity Used:         {min(100, (upgrades / cb_limit) * 100):.1f}%")

    print("\n📍 LATEST ACTIVITY")
    print(f"   • Last Upgrade:          {last_upgrade}")

    print("\n" + "=" * 50)

    # Recommendations
    if upgrades >= cb_limit:
        print("⚠️  ACTION REQUIRED: Circuit Breaker tripped. Review 'apps_shared' for quality.")
        print("   Run 'python ops_scripts/sovereign_healing_mission.py' again to continue healing.")
    elif scanned > 0 and intervention_ratio < 1.0:
        print("✅  HEALTHY: Low intervention ratio indicates strong architectural separation.")
    else:
        print("ℹ️  STATUS: Mission ready for execution.")


if __name__ == "__main__":
    generate_report()
