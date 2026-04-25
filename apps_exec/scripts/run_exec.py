"""
run_exec.py — CLI entrypoint for apps_exec Executive Brief Generator.

Usage:
    python -m apps_exec --audience recruiter --source-dirs docs/architecture --out reports/executive
    python -m apps_exec.scripts.run_exec --audience cto --dry-run

Options:
    --audience      Target persona: recruiter | cto | svp_eng | board | head_of_ai
    --source-dirs   Comma-separated list of source directories to ingest
    --out           Output directory for generated artifacts
    --emphasis      Emphasis area: governance | orchestration | rag | safety | observability
    --tone          Override tone: board-ready | cto-ready | recruiter-friendly | technical
    --industry      Optional industry context string
    --dry-run       Parse and plan but do not emit artifacts
    --trace-id      Optional trace ID for correlation
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

_log = logging.getLogger("apps_exec.run_exec")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps_exec",
        description="Executive Brief Generator — agentic_core platform",
    )
    parser.add_argument(
        "--audience",
        default="recruiter",
        choices=["recruiter", "cto", "svp_eng", "board", "head_of_ai"],
        help="Target audience persona",
    )
    parser.add_argument(
        "--source-dirs",
        default="docs/architecture",
        help="Comma-separated source directories to ingest",
    )
    parser.add_argument(
        "--out",
        default="reports/executive",
        help="Output directory for generated artifacts",
    )
    parser.add_argument(
        "--emphasis",
        default="",
        help="Emphasis area: governance | orchestration | rag | safety | observability",
    )
    parser.add_argument(
        "--tone",
        default="",
        help="Override tone: board-ready | cto-ready | recruiter-friendly | technical",
    )
    parser.add_argument("--industry", default="", help="Optional industry context")
    parser.add_argument("--dry-run", action="store_true", help="Plan but do not emit artifacts")
    parser.add_argument("--trace-id", default="", help="Correlation trace ID")
    parser.add_argument("--json-output", action="store_true", help="Emit run summary JSON to stdout")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
    from apps_exec.types.exec_types import AudiencePersona, BriefTone, EmphasisArea, ExecBriefRequest

    source_dirs = [s.strip() for s in args.source_dirs.split(",") if s.strip()]
    _VALID_EMPHASIS = {"governance", "orchestration", "rag", "safety", "observability"}
    _VALID_TONE = {"board-ready", "cto-ready", "recruiter-friendly", "technical"}
    _VALID_AUDIENCE = {"recruiter", "cto", "svp_eng", "board", "head_of_ai"}

    emphasis_areas = []
    if args.emphasis:
        e = args.emphasis.strip()
        if e in _VALID_EMPHASIS:
            emphasis_areas = [e]
        else:
            _log.warning("Unknown emphasis '%s' — ignoring", args.emphasis)

    tone = "technical"
    if args.tone:
        t = args.tone.strip()
        if t in _VALID_TONE:
            tone = t
        else:
            _log.warning("Unknown tone '%s' — using default", args.tone)

    if args.audience not in _VALID_AUDIENCE:
        _log.error("Unknown audience '%s'", args.audience)
        return 1
    audience = args.audience

    request = ExecBriefRequest(
        audience=audience,
        source_dirs=source_dirs,
        emphasis_areas=emphasis_areas,
        tone=tone,
        industry=args.industry,
        dry_run=args.dry_run,
        trace_id=args.trace_id,
    )

    import asyncio

    orchestrator = ExecOrchestrator(dry_run=args.dry_run, output_dir=args.out)
    _maybe = orchestrator.run(request)
    if asyncio.iscoroutine(_maybe):
        result = asyncio.run(_maybe)
    else:
        result = _maybe

    if args.json_output:
        summary = {
            "trace_id": result.trace_id,
            "status": str(result.status),
            "audience": result.audience,
            "quality_score": result.quality_score,
            "sections_generated": len(result.sections),
            "gate_violations": result.gate_violations,
            "artifacts": result.artifact_paths,
        }
        print(json.dumps(summary, indent=2))

    if str(result.status) in ("complete", "dry_run"):
        _log.info(
            "[apps_exec] SUCCESS trace=%s status=%s artifacts=%d",
            result.trace_id,
            str(result.status),
            len(result.artifact_paths),
        )
        return 0
    else:
        _log.error(
            "[apps_exec] FAILED trace=%s status=%s violations=%s error=%s",
            result.trace_id,
            str(result.status),
            result.gate_violations,
            result.error,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
