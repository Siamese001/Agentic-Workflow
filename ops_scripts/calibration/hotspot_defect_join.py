"""hotspot_defect_join.py — Weekly join of mv_hotspot_centrality top-N vs
30-day defect additions and git churn.

**W3.1 STATUS: STUB** — full implementation deferred to wave W3.1 of
`.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`. The stub exists so
`check_ledger_writer_contract.py` can verify the registered writer_hook
path resolves on disk.

When implemented, this module will:
    1. Load the latest adg_indexed_<ts>.sqlite snapshot
    2. Read top-N rows from mv_hotspot_centrality
    3. Query Notion SC/AP Violation Backlog for rows created in last 30 days
    4. Query git log for churn per predicted hotspot file over 30 days
    5. Write prediction rows (at snapshot time) and outcome rows (30 days later)
       via tools.ledgers.writer_for("hotspot_defect")
    6. Emit a ranked drift report under docs/reports/calibration/hotspot_defect/

Run as:
    python ops_scripts/calibration/hotspot_defect_join.py --top-n 100 --window-days 30
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-n", type=int, default=100)
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(
        f"[hotspot_defect_join] STUB — implementation deferred to W3.1. "
        f"top_n={args.top_n} window_days={args.window_days} dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
