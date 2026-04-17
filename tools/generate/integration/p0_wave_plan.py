"""P0 remediation wave-plan emission for ADG generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.core.p0_wave_plan import (
    build_p0_remediation_wave_plan,
    render_p0_remediation_wave_plan,
    serialize_p0_remediation_wave_plan,
)


def _emit_p0_remediation_wave_plan(
    adg_artifacts_dir: Path,
    ts: str,
    sqlite_path: Path | None,
    limit: int = 200,
) -> dict[str, Any]:
    """Generate and persist a P0 remediation wave plan derived from ADG SQLite.

    Returns a metadata dict with emitted paths and whether the plan is actionable.
    The artifact is always emitted when a canonical SQLite file is available so
    failed runs still leave deterministic guidance behind.
    """
    if sqlite_path is None or not sqlite_path.exists():
        return {"plan_required": False, "json_path": None, "markdown_path": None}

    issues_dir = adg_artifacts_dir / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    plan = build_p0_remediation_wave_plan(sqlite_path, limit=limit)
    json_path = issues_dir / f"p0_remediation_wave_plan_{ts}.json"
    markdown_path = issues_dir / f"p0_remediation_wave_plan_{ts}.md"

    json_path.write_text(serialize_p0_remediation_wave_plan(plan), encoding="utf-8")
    markdown_path.write_text(render_p0_remediation_wave_plan(plan, ts), encoding="utf-8")

    summary = plan.get("summary", {})
    if plan.get("plan_required", False):
        print(
            "[ADG] P0 remediation wave plan emitted: "
            f"{markdown_path.name} "
            f"(issues={summary.get('total_p0_issues', 0)} "
            f"layers={summary.get('layer_violations', 0)} "
            f"cycles={summary.get('circular_imports', 0)} "
            f"dynamic_exec={summary.get('dynamic_exec', 0)})"
        )
    else:
        print(f"[ADG] P0 remediation wave plan emitted: {markdown_path.name} (clean snapshot)")

    return {
        "plan_required": bool(plan.get("plan_required", False)),
        "json_path": json_path,
        "markdown_path": markdown_path,
        "summary": summary,
    }
