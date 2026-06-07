"""CLI runner: score the HITL ledger and emit UWG draft proposals.

Plan: `docs/archive/windsurf/legacy-tree/plans/system-learning-activation-path-a5e2f1.md`

Closes Gap 4 from the 2026-04-23 gap review. Before this runner,
`RuntimeHitlConsumer` had 477 lines of well-tested production code but
zero runtime importers — the meta-learning draft pipeline was
architecturally complete but inert.

Pipeline wired here
-------------------

    RuntimeHitlLedger (artifacts/runtime/hitl_ledger.db)
        → HitlDecisionQualityEngine.score_ledger()
            → HitlQualityReport
                → RuntimeHitlConsumer.consume_and_submit()
                    → DraftProposal[]
                        → FileDraftSink (artifacts/runtime/hitl_drafts/)

Usage
-----

    python -m tools.system_learning.run_hitl_consumer
    python tools/system_learning/run_hitl_consumer.py --ledger <path>
    python tools/system_learning/run_hitl_consumer.py --dry-run
    python tools/system_learning/run_hitl_consumer.py --run-id <id>

Exit codes
----------
    0: success (including success when zero drafts were produced)
    2: ledger not found / unreadable
    3: consumer failure (raised exception)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Activate the system-learning HITL draft consumer over the runtime ledger."
    )
    p.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="Path to runtime HITL ledger SQLite file (default: DEFAULT_LEDGER_PATH).",
    )
    p.add_argument(
        "--draft-dir",
        type=Path,
        default=None,
        help="Directory where draft proposals are written (default: DEFAULT_DRAFT_DIR).",
    )
    p.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Filter ledger to a single run_id. Default: score the full ledger.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Score and compute drafts, but do NOT write them to the sink.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON summary instead of human-readable output.",
    )
    return p


def run(
    ledger_path: Path | None = None,
    draft_dir: Path | None = None,
    run_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Invoke the HITL activation pipeline once and return a summary.

    Separated from `main()` so tests can call `run()` directly without
    argparse. Never writes to sys.argv, never prints — returns data only.
    """
    from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (  # noqa: PLC0415
        DEFAULT_LEDGER_PATH,
        RuntimeHitlLedger,
    )
    from apps_eval.engines.hitl_decision_quality_engine import (  # noqa: PLC0415
        HitlDecisionQualityEngine,
    )
    from agentic_core.L6_system_learning.runtime_hitl_consumer import (  # noqa: PLC0415
        DEFAULT_DRAFT_DIR,
        FileDraftSink,
        RuntimeHitlConsumer,
    )

    resolved_ledger = ledger_path if ledger_path is not None else DEFAULT_LEDGER_PATH
    if not resolved_ledger.exists():
        return {
            "ok": False,
            "reason": f"ledger_not_found: {resolved_ledger}",
            "drafts_produced": 0,
            "drafts_written": 0,
            "ledger_path": str(resolved_ledger),
        }

    ledger = RuntimeHitlLedger(path=resolved_ledger)
    engine = HitlDecisionQualityEngine()
    report = engine.score_ledger(ledger, run_id_filter=run_id)

    # Collect the same entries the engine scored so the consumer sees them.
    if run_id is not None:
        entries = ledger.list_by_run(run_id)
    else:
        # score_ledger with no filter scans list_pending() internally;
        # mirror that here for consistency of evidence shown to the consumer.
        entries = list(ledger.list_pending())

    resolved_draft_dir = draft_dir if draft_dir is not None else DEFAULT_DRAFT_DIR
    sink = FileDraftSink(root=resolved_draft_dir)
    consumer = RuntimeHitlConsumer(sink=sink)

    if dry_run:
        drafts = consumer.consume(report, entries=entries)
        written = 0
    else:
        receipts = consumer.consume_and_submit(report, entries=entries)
        drafts = [d for d, _receipt in receipts]
        written = len(receipts)

    return {
        "ok": True,
        "ledger_path": str(resolved_ledger),
        "draft_dir": str(resolved_draft_dir),
        "run_id_filter": run_id,
        "dry_run": dry_run,
        "total_ledger_entries": report.total_entries,
        "resolved_entries": report.resolved_entries,
        "pending_entries": report.pending_entries,
        "overall_quality_score": round(report.overall_score, 4),
        "bucket_count": len(report.buckets),
        "drafts_produced": len(drafts),
        "drafts_written": written,
        "draft_ids": [d.draft_id for d in drafts],
        "draft_kinds": sorted({d.kind.value for d in drafts}),
    }


def _format_human(summary: dict[str, Any]) -> str:
    if not summary.get("ok"):
        return f"FAIL: {summary.get('reason', 'unknown')}"
    lines = [
        f"HITL consumer run — {summary['ledger_path']}",
        f"  filter:             run_id={summary['run_id_filter'] or '(all)'}",
        f"  dry_run:            {summary['dry_run']}",
        f"  total entries:      {summary['total_ledger_entries']}",
        f"  resolved / pending: {summary['resolved_entries']} / {summary['pending_entries']}",
        f"  buckets scored:     {summary['bucket_count']}",
        f"  overall score:      {summary['overall_quality_score']}",
        f"  drafts produced:    {summary['drafts_produced']}",
        f"  drafts written:     {summary['drafts_written']}",
        f"  draft kinds:        {', '.join(summary['draft_kinds']) or '(none)'}",
        f"  draft dir:          {summary['draft_dir']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        summary = run(
            ledger_path=args.ledger,
            draft_dir=args.draft_dir,
            run_id=args.run_id,
            dry_run=args.dry_run,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"FAIL: consumer raised {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    if not summary.get("ok"):
        print(_format_human(summary), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(_format_human(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
