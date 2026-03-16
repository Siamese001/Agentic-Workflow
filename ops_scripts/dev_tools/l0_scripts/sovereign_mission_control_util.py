from __future__ import annotations

import asyncio

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "sovereign_mission_control_util")
_emit_applies_guardrail("p0", "sovereign_mission_control_util", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_mission_control_util", "policy_binding")
_emit_snapshots_state("p0", "sovereign_mission_control_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

repo_root: Any = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.append(str(REPO_ROOT))
from typing import Any

from agentic_core.L0_routing.P1_core.sovereign_auditor_v3 import main_util as run_audit
from canon_validator_agentic_v2 import run_mission as run_healing


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
    _clk = get_clock()
    _clk.emit_replay_key(context=f"ops:mission_control:heal:{target}")
    _clk.emit_determinism_digest(inputs={"op": "run_healing", "target": str(target)})
    await run_healing(target_scope=target)
    print("\n[*] PHASE 3: Final Compliance Sealing...")
    final_report: Any = await run_audit()
    if final_report.get_overall_score() > overall_health:
        print(f"\n[SUCCESS] Mission Achieved. Health improved to {final_report.get_overall_score():.1f}%")
    else:
        print("\n[L6 ALERT] Mission Stalled. Structural drift persists. Manual review required.")


if __name__ == "__main__":
    asyncio.run(execute_unified_mission())
