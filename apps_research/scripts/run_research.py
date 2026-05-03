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
        choices=[
            "brief",
            "comparison",
            "trend",
            "position",
            "thought_leadership",
            "company",
            "role_profile",
        ],
        help="Artifact mode",
    )
    parser.add_argument(
        "--jd-anchor",
        default="",
        help="Path to job_description.json for facet weighting (mode=company)",
    )
    parser.add_argument(
        "--depth",
        default="standard",
        choices=["shallow", "standard", "deep"],
        help="Research depth (mode=company)",
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
    parser.add_argument(
        "--reference-doc",
        default="",
        help="Path to a PDF / TXT / MD exemplar; chunks added to brief context (plan §P3.1)",
    )
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

    from agentic_core.runtime.contracts.otel_lifecycle_bridge import otel_lifecycle_capture

    if args.mode == "company":
        with otel_lifecycle_capture(
            mission="apps_research.run_research.company", app_id="apps_research"
        ):
            return _run_company_brief(args)

    if args.mode == "role_profile":
        with otel_lifecycle_capture(
            mission="apps_research.run_research.role_profile", app_id="apps_research"
        ):
            return _run_role_profile(args)

    from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
    from apps_research.types.research_types import ResearchRequest

    with otel_lifecycle_capture(mission="apps_research.run_research", app_id="apps_research"):
        return _run_research(args, ResearchOrchestrator, ResearchRequest)


def _run_company_brief(args) -> int:
    """Mode-company entrypoint.

    Persists a CompanyBrief JSON under <out>/company_research.json and
    validates it with the apps_rg pydantic schema before returning.
    """
    from datetime import datetime, timezone

    from apps_research.engines.company_brief_engine import CompanyBriefEngine

    try:
        output_dir = Path(_normalize_output_dir(args.out))
    except ValueError as exc:
        _log.error(str(exc))
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    engine = CompanyBriefEngine()
    payload = {
        "topic": args.topic,
        "jd_anchor": args.jd_anchor or None,
        "depth": args.depth,
    }
    try:
        brief = engine.execute(payload)
    except (ValueError, RuntimeError) as exc:
        _log.error("CompanyBriefEngine failed: %s", exc)
        return 1

    target = run_dir / "company_research.json"
    target.write_text(json.dumps(brief, indent=2, sort_keys=True), encoding="utf-8")

    # Optional pydantic validation — best-effort, surfaces shape errors early.
    try:
        from apps_rg.types.company_research import CompanyBrief

        CompanyBrief.model_validate(brief)
    except ImportError:
        pass
    except Exception as exc:  # guardian: allow-broad-exception -- pydantic v1/v2 raise heterogeneous; surface but do not abort write
        _log.warning("CompanyBrief schema validation warning: %s", exc)

    if args.json_output:
        print(json.dumps({"status": "complete", "artifact": str(target)}, indent=2))
    else:
        print(f"[apps_research] Wrote company brief to {target}")
    return 0


def _run_research(args, ResearchOrchestrator, ResearchRequest) -> int:
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


def _run_role_profile(args) -> int:
    """Mode-role_profile entrypoint (plan §P2.3).

    Persists a RoleProfile JSON under <out>/runs/<ts>/role_profile.json and
    validates it with the pydantic schema before returning.
    """
    from datetime import datetime, timezone

    from apps_research.engines.role_profile_engine import RoleProfileEngine

    try:
        output_dir = Path(_normalize_output_dir(args.out))
    except ValueError as exc:
        _log.error(str(exc))
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / "runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    engine = RoleProfileEngine()
    try:
        profile = engine.execute({"role": args.topic, "depth": args.depth})
    except (ValueError, RuntimeError) as exc:
        _log.error("RoleProfileEngine failed: %s", exc)
        return 1

    target = run_dir / "role_profile.json"
    target.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")

    try:
        from apps_research.types.role_profile import RoleProfile

        RoleProfile.model_validate(profile)
    except Exception as exc:  # guardian: allow-broad-exception -- pydantic v1/v2 raise heterogeneous; surface but do not abort write
        _log.warning("RoleProfile schema validation warning: %s", exc)

    if args.json_output:
        print(json.dumps({"status": "complete", "artifact": str(target)}, indent=2))
    else:
        print(f"[apps_research] Wrote role profile to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
