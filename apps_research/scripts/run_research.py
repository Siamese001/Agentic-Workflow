"""
run_research.py — CLI entrypoint for apps_research.

Usage:
    python -m apps_research --topic "enterprise agentic AI governance" --mode comparison
    python -m apps_research.scripts.run_research --topic "..." --mode brief --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

_log = logging.getLogger("apps_research.run_research")


def _normalize_output_dir(raw_path: str) -> str:
    out = Path(raw_path).expanduser().resolve()
    if out.exists() and not out.is_dir():
        raise ValueError(f"--out must be a directory path, got existing file: {out}")
    return str(out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apps_research", description="Autonomous Research Engine")
    parser.add_argument("--topic", required=True, help="Research topic or question")
    parser.add_argument(
        "--mode",
        default="brief",
        choices=["brief", "comparison", "trend", "position", "thought_leadership"],
        help="Artifact mode",
    )
    parser.add_argument(
        "--audience",
        default="technical",
        choices=["technical", "executive", "market-facing"],
    )
    parser.add_argument(
        "--compare",
        default="",
        help="Comma-separated comparison subjects for comparison mode",
    )
    parser.add_argument("--horizon", default="", help="Time horizon e.g. '12 months'")
    parser.add_argument("--out", default="reports/research")
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

    from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
    from apps_research.types.research_types import ResearchRequest

    comparison_subjects = [s.strip() for s in args.compare.split(",") if s.strip()]

    request = ResearchRequest(
        topic=args.topic,
        mode=args.mode,
        audience_style=args.audience,
        comparison_subjects=comparison_subjects,
        time_horizon=args.horizon,
        dry_run=args.dry_run,
        trace_id=args.trace_id,
    )

    try:
        output_dir = _normalize_output_dir(args.out)
    except ValueError as exc:
        _log.error(str(exc))
        return 1

    orchestrator = ResearchOrchestrator(dry_run=args.dry_run, output_dir=output_dir)
    result = asyncio.run(orchestrator.run(request))
    status = str(result.status)

    if args.json_output:
        print(
            json.dumps(
                {
                    "trace_id": result.trace_id,
                    "status": status,
                    "quality_score": result.quality_score,
                    "sections": len(result.sections),
                    "sources": len(result.source_register),
                    "gate_violations": result.gate_violations,
                    "artifacts": result.artifact_paths,
                },
                indent=2,
                sort_keys=True,
            ),
        )

    return 0 if status in ("complete", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
