import asyncio
import sys
from pathlib import Path

# 1. Resolve Gravity Anchor
REPO_ROOT = Path(__file__).parent.parent
sys.path.append(str(REPO_ROOT))

from canon_validator_agentic_v2 import run_mission as run_healing

# 2. Sequential Import Link
from AgenticCore.L0_maintenance.scripts.sovereign_auditor_v3 import main as run_audit


async def execute_unified_mission(target="AgenticCore"):
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
