"""
run_rfp.py — CLI entrypoint for apps_rfp AI Proposal / RFP Generator.

Usage:
    python -m apps_rfp --brief "problem statement" --industry financial_services --out rfp/
    python -m apps_rfp.scripts.run_rfp --brief-file input/brief.md --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_log = logging.getLogger("apps_rfp.run_rfp")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_rfp", description="AI Proposal / RFP Generator")
    parser.add_argument("--brief", default="", help="Problem statement text")
    parser.add_argument("--brief-file", default="", help="Path to a markdown file with the problem statement")
    parser.add_argument(
        "--industry",
        default="technology",
        choices=["financial_services", "healthcare", "technology", "government"],
        help="Target industry",
    )
    parser.add_argument(
        "--posture",
        default="cloud-first",
        choices=["cloud-first", "hybrid", "sovereign", "regulated"],
        help="Architecture posture",
    )
    parser.add_argument("--timeline-weeks", type=int, default=0, help="Delivery timeline in weeks")
    parser.add_argument("--out", default="rfp", help="Output directory")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--trace-id", default="")
    parser.add_argument("--json-output", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    problem = args.brief
    if not problem and args.brief_file:
        brief_path = Path(args.brief_file)
        if not brief_path.exists():
            _log.error("Brief file not found: %s", brief_path)
            return 1
        problem = brief_path.read_text(encoding="utf-8").strip()

    if not problem:
        _log.error("No problem statement provided. Use --brief or --brief-file.")
        return 1

    from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
    from apps_rfp.types.rfp_types import ArchitecturePosture, RfpRequest

    try:
        posture = ArchitecturePosture(args.posture)
    except ValueError:
        _log.warning("Unknown posture '%s' — using cloud-first", args.posture)
        posture = ArchitecturePosture.CLOUD_FIRST

    request = RfpRequest(
        problem_statement=problem,
        industry=args.industry,
        architecture_posture=posture,
        delivery_timeline_weeks=args.timeline_weeks,
        dry_run=args.dry_run,
        trace_id=args.trace_id,
    )

    orchestrator = RfpOrchestrator(dry_run=args.dry_run, output_dir=args.out)
    result = orchestrator.run(request)

    if args.json_output:
        print(
            json.dumps(
                {
                    "trace_id": result.trace_id,
                    "status": result.status.value,
                    "quality_score": result.quality_score,
                    "sections": len(result.sections),
                    "gate_violations": result.gate_violations,
                    "artifacts": result.artifact_paths,
                },
                indent=2,
            ),
        )

    return 0 if result.status.value in ("complete", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
