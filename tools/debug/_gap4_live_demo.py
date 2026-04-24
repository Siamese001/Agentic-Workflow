"""Live demo: Gap 4 activation working end-to-end."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from tools.meta_learning.run_hitl_consumer import run


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        ledger_path = Path(td) / "live.db"
        draft_dir = Path(td) / "drafts"
        ledger = RuntimeHitlLedger(path=ledger_path)
        for i in range(12):
            entry = ledger.record_escalation(
                run_id="live-demo",
                trace_id=f"t{i:03d}",
                hitl_class=HitlClass.SAFETY,
                approver_pool="live_pool",
                timeout_s=1800,
                policy_snapshot="p1",
                envelope={"i": i},
            )
            ledger.record_timeout(entry.ledger_id, reason_code="DEMO_TIMEOUT")
        summary = run(
            ledger_path=ledger_path,
            draft_dir=draft_dir,
            run_id="live-demo",
        )
        print("LIVE DEMO - Gap 4 activation end-to-end")
        print(f"  total entries:    {summary['total_ledger_entries']}")
        print(f"  resolved:         {summary['resolved_entries']}")
        print(f"  bucket_count:     {summary['bucket_count']}")
        print(f"  overall_score:    {summary['overall_quality_score']}")
        print(f"  drafts produced:  {summary['drafts_produced']}")
        print(f"  drafts written:   {summary['drafts_written']}")
        print(f"  draft kinds:      {summary['draft_kinds']}")
        print(f"  draft files:      {len(list(draft_dir.glob('*.json')))}")


if __name__ == "__main__":
    main()
