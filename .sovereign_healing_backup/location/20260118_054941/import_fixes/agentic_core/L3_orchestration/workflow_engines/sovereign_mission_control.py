from __future__ import annotations
import asyncio
import sys
from pathlib import Path

# 1. Resolve Gravity Anchor
REPO_ROOT = Path(__file__).parent.parent
sys.path.append(str(REPO_ROOT))

from canon_validator_agentic_v2 import run_mission as run_healing

# 2. Sequential Import Link
from agentic_core.L5_safety.validators.sovereign_auditor_v3 import main as run_audit

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


async def execute_unified_mission(target=AGENTIC_CORE_DIR):
    """
    [L6 MISSION CONTROL]
    Sequences Diagnosis (Auditor) and Surgery (Validator).
    """
    print(f"\n{'='*80}\n[MISSION CONTROL] INITIATING UNIFIED SOVEREIGN SWEEP\n{'='*80}")

    # PHASE 1: DIAGNOSIS (The Supreme Court)
    print("\n[*] PHASE 1: Executing Multi-Dimensional Audit...")
    report = await run_audit() # Auditor generates SovereignReport
    
    overall_health = report.get_overall_score()
    print(f"\n[DIAGNOSIS COMPLETE] Current Health Score: {overall_health:.1f}%")

    # PHASE 2: DECISION LOGIC
    if overall_health >= 98.0:
        print("\n[VERDICT] Sovereignty Intact. No surgery required. Perfection Sealed.")
        return

    print(f"\n[VERDICT] Health threshold breach ({overall_health}% < 98%). Unleashing Healers.")

    # PHASE 3: SURGERY (The Surgeon)
    # Filter only the files the Auditor identified as problematic to save budget
    issues = report.get_all_issues()
    target_files = list(set([issue['file'] for issue in issues if issue.get('file')]))
    
    print(f"[*] PHASE 2: Surgical Healing initiated for {len(target_files)} targeted files...")
    
    # Run the Validator Mission exclusively on identified targets
    await run_healing(target_scope=target)

    # PHASE 4: FINAL VERIFICATION
    print("\n[*] PHASE 3: Final Compliance Sealing...")
    final_report = await run_audit()
    
    if final_report.get_overall_score() > overall_health:
        print(f"\n[SUCCESS] Mission Achieved. Health improved to {final_report.get_overall_score():.1f}%")
    else:
        print("\n[L6 ALERT] Mission Stalled. Structural drift persists. Manual review required.")

if __name__ == "__main__":
    asyncio.run(execute_unified_mission())
