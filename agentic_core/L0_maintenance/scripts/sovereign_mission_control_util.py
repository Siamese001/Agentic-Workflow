from __future__ import annotations

import asyncio

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import sys
from pathlib import Path

repo_root: Any = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.append(str(REPO_ROOT))
# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

from canon_validator_agentic_v2 import run_mission as run_healing

from agentic_core.L0_maintenance.P1_core.sovereign_auditor_v3 import main_util as run_audit


async def execute_unified_mission(target: Any = "agentic_core") -> Any:
    """
    [L6 MISSION CONTROL]
    Sequences Diagnosis (Auditor) and Surgery (Validator).
    """
    print(f"\n{'=' * 80}\n[MISSION CONTROL] INITIATING UNIFIED SOVEREIGN SWEEP\n{'=' * 80}")
    print("\n[*] PHASE 1: Executing Multi-Dimensional Audit...")
    report: Any = await run_audit()
    overall_health: Any = report.get_overall_score()
    print(f"\n[DIAGNOSIS COMPLETE] Current Health Score: {overall_health:.1f}%")
    if overall_health >= 98.0:
        print("\n[VERDICT] Sovereignty Intact. No surgery required. Perfection Sealed.")
        return
    print(f"\n[VERDICT] Health threshold breach ({overall_health}% < 98%). Unleashing Healers.")
    issues: Any = report.get_all_issues()
    target_files: Any = list({issue["file"] for issue in issues if issue.get("file")})
    print(f"[*] PHASE 2: Surgical Healing initiated for {len(target_files)} targeted files...")
    await run_healing(target_scope=target)
    print("\n[*] PHASE 3: Final Compliance Sealing...")
    final_report: Any = await run_audit()
    if final_report.get_overall_score() > overall_health:
        print(f"\n[SUCCESS] Mission Achieved. Health improved to {final_report.get_overall_score():.1f}%")
    else:
        print("\n[L6 ALERT] Mission Stalled. Structural drift persists. Manual review required.")


if __name__ == "__main__":
    asyncio.run(execute_unified_mission())
