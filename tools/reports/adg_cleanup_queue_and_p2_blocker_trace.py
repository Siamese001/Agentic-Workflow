"""Emit the mandatory ADG cleanup queue and P2 blocker trace report.

The report combines two separate evidence streams into one BCG-style artifact:

* the latest dead-code control report, which drives the deprecation / deletion
  queue and shows why deletion is not approved yet
* the latest published ADG snapshot plus the P2 ratchet ceiling, which shows
  why the run is still blocked on MEDIUM hygiene debt

The module writes a markdown report for humans and a JSON companion for tools.
Both the stable file names and ``*_latest`` mirrors are updated on every emit.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.reports.adg_bcg_adapter import (
    build_bcg_brief,
    build_deprecation_deletion_plan,
    render_bcg_brief_md,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
REPORT_STEM = "adg_cleanup_queue_and_p2_blocker_trace"


def _repo_rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {"value": data}


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _latest_by_glob(root: Path, pattern: str) -> Path | None:
    candidates = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _resolve_existing_path(raw: Any, *bases: Path) -> Path | None:
    if not raw:
        return None
    candidate = Path(str(raw))
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None
    for base in bases:
        try:
            resolved = (base / candidate).resolve()
        except OSError:
            continue
        if resolved.is_file():
            return resolved
    return None


def _latest_snapshot_sqlite(
    adg_artifacts_dir: Path,
) -> tuple[Path | None, Path | None, dict[str, Any] | None]:
    manifests = []
    latest_manifest = adg_artifacts_dir / "adg_generation_manifest_latest.json"
    if latest_manifest.is_file():
        manifests.append(latest_manifest)
    manifests.extend(
        sorted(adg_artifacts_dir.glob("adg_generation_manifest_*.json"), key=lambda p: p.stat().st_mtime)
    )
    seen: set[Path] = set()
    for manifest_path in reversed(manifests):
        if manifest_path in seen:
            continue
        seen.add(manifest_path)
        manifest = _read_json(manifest_path)
        if not isinstance(manifest, dict):
            continue
        raw = manifest.get("sqlite_path") or manifest.get("snapshot_path")
        sqlite_path = _resolve_existing_path(raw, manifest_path.parent, adg_artifacts_dir, REPO_ROOT)
        if sqlite_path is not None:
            return sqlite_path, manifest_path, manifest
    fallback = _latest_by_glob(adg_artifacts_dir, "adg_indexed_*.sqlite")
    if fallback is not None:
        return fallback.resolve(), None, None
    return None, None, None


def _latest_gate_invocation_manifest(adg_artifacts_dir: Path) -> tuple[Path | None, dict[str, Any] | None]:
    path = _latest_by_glob(adg_artifacts_dir, "adg_gate_invocation_manifest_*.json")
    if path is None:
        return None, None
    return path.resolve(), _read_json(path)


def _latest_dead_code_report(adg_artifacts_dir: Path) -> tuple[Path | None, dict[str, Any] | None]:
    latest = adg_artifacts_dir / "dead_code_zone_control_report_latest.json"
    if latest.is_file():
        return latest.resolve(), _read_json(latest)
    path = _latest_by_glob(adg_artifacts_dir, "dead_code_zone_control_report_*.json")
    if path is None:
        return None, None
    return path.resolve(), _read_json(path)


def _latest_p2_ratchet(adg_artifacts_dir: Path) -> tuple[Path | None, dict[str, Any] | None]:
    path = adg_artifacts_dir / "p2_ratchet.json"
    if not path.is_file():
        return None, None
    return path.resolve(), _read_json(path)


def _query_medium_hygiene_rows(sqlite_path: Path | None) -> list[dict[str, Any]]:
    if sqlite_path is None or not sqlite_path.is_file():
        return []
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                select file_path, line_no, evidence, disposition, severity, violation_class
                from violations
                where severity='MEDIUM'
                  and violation_class='hygiene'
                  and disposition='untriaged'
                order by file_path, line_no
                """
            ).fetchall()
        except sqlite3.Error:
            return []
    return [dict(row) for row in rows]


def _is_archived_surface(scope: str) -> bool:
    lowered = scope.lower()
    return any(
        token in lowered
        for token in (
            "/_archived",
            "/_obsolete",
            "/archive/",
            "/legacy/",
            "generated/legacy",
        )
    )


def _cleanup_queue_rows(
    dead_code_report: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unresolved = (dead_code_report or {}).get("unresolved_imports") or {}
    hotspots = unresolved.get("unresolved_hotspots") or []
    live_rows: list[dict[str, Any]] = []
    archived_rows: list[dict[str, Any]] = []
    for rank, hotspot in enumerate(hotspots, start=1):
        if not isinstance(hotspot, (list, tuple)) or len(hotspot) < 2:
            continue
        scope = str(hotspot[0] or "").strip()
        if not scope:
            continue
        count = int(hotspot[1] or 0)
        archived = _is_archived_surface(scope)
        move = "Triage unresolved imports" if not archived else "Defer archived unresolved imports"
        why_it_matters = "This is where unresolved-import noise is concentrated, so fixing it will make the next scan more trustworthy."
        evidence = f"{count} unresolved import(s) on this surface."
        next_step = (
            "Trace the live imports, then rerun the scan."
            if not archived
            else "Leave archived noise deferred unless it affects live paths."
        )
        row = {
            "priority": rank,
            "scope": scope,
            "count": count,
            "surface": "archived" if archived else "live",
            "move": move,
            "why_it_matters": why_it_matters,
            "business_reason": why_it_matters,
            "evidence": evidence,
            "technical_reason": evidence,
            "next_step": next_step,
            "why_this_rank": next_step,
            "decision": "investigate" if not archived else "defer",
            "decision_options": [],
            "done_condition": "Rerun ADG and confirm the unresolved-import noise is lower or intentionally archived.",
        }
        if row["surface"] == "archived":
            archived_rows.append(row)
        else:
            live_rows.append(row)
    live_rows.sort(key=lambda r: (-int(r.get("count", 0) or 0), str(r.get("scope", ""))))
    archived_rows.sort(key=lambda r: (-int(r.get("count", 0) or 0), str(r.get("scope", ""))))
    for idx, row in enumerate(live_rows, start=1):
        row["priority"] = idx
    for idx, row in enumerate(archived_rows, start=len(live_rows) + 1):
        row["priority"] = idx
    return live_rows, archived_rows


def _evidence_interpretation(evidence: str) -> str:
    if evidence == "Exception":
        return "Broad exception catch or swallow on a live hygiene path."
    if evidence == "OSError":
        return "Filesystem / IO error handling needs to be narrowed."
    if evidence == "ImportError":
        return "Import fallback logic should be explicit and local."
    if evidence == "ValueError":
        return "Parsing or validation guard should be tightened."
    if "import *" in evidence:
        return "Star import hides dependencies and makes review harder."
    return "Hygiene debt on the current published snapshot."


def _p2_summary(
    sqlite_path: Path | None,
    ratchet_doc: dict[str, Any] | None,
    failed_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    rows = _query_medium_hygiene_rows(sqlite_path)
    evidence_counts = Counter(str(row.get("evidence") or "").strip() or "unknown" for row in rows)
    file_counts = Counter(str(row.get("file_path") or "").strip() or "unknown" for row in rows)
    current_count = len(rows)
    ceiling = int((ratchet_doc or {}).get("exception_swallow_ceiling") or 0)
    delta = current_count - ceiling
    baseline_snapshot = str((ratchet_doc or {}).get("snapshot") or "").strip()
    failed_timestamp = str((failed_manifest or {}).get("timestamp") or "").strip()
    failed_status = str((failed_manifest or {}).get("certification_status") or "").strip()

    evidence_rows = [
        {
            "evidence": evidence,
            "count": count,
            "interpretation": _evidence_interpretation(evidence),
        }
        for evidence, count in evidence_counts.most_common()
    ]
    file_rows = [
        {
            "scope": file_path,
            "count": count,
            "surface": "live runtime"
            if file_path.startswith("apps_rg/runtime/")
            else (
                "core"
                if file_path.startswith("agentic_core/")
                else ("apps" if file_path.startswith("apps_") else "other")
            ),
            "move": "Reduce MEDIUM hygiene debt",
            "why_it_matters": "This path concentrates MEDIUM hygiene debt on a visible runtime or core surface.",
            "business_reason": "This path concentrates MEDIUM hygiene debt on a visible runtime or core surface.",
            "evidence": f"{count} MEDIUM hygiene record(s) in the published snapshot.",
            "technical_reason": f"{count} MEDIUM hygiene record(s) in the published snapshot.",
            "next_step": "Burn down the highest-count files, then rerun ADG.",
            "why_this_rank": "Burn down the highest-count files, then rerun ADG.",
            "decision": "reduce",
            "decision_options": [],
            "done_condition": "The published MEDIUM hygiene count is at or below the ceiling.",
        }
        for file_path, count in file_counts.most_common()
    ]

    if sqlite_path is None:
        status = "missing"
        business_read = "No published sqlite snapshot was available, so the P2 trace could not be quantified."
    elif current_count > ceiling:
        status = "over_ceiling"
        business_read = (
            f"The published snapshot is still {delta} over the P2 ceiling, so the ratchet remains blocked."
        )
    else:
        status = "within_ceiling"
        business_read = "The published snapshot is at or below the P2 ceiling, so this blocker is cleared."

    priority_rows: list[dict[str, Any]] = []
    for row in file_rows[:4]:
        priority_rows.append(
            {
                "priority": len(priority_rows) + 1,
                "move": row["move"],
                "scope": row["scope"],
                "why_it_matters": "This is a live surface where removing hygiene debt improves trust in the next run.",
                "business_reason": "This is a live surface where removing hygiene debt improves trust in the next run.",
                "evidence": row["evidence"],
                "technical_reason": row["technical_reason"],
                "next_step": row["next_step"],
                "why_this_rank": row["why_this_rank"],
                "decision": row["decision"],
                "decision_options": [],
                "done_condition": row["done_condition"],
            }
        )
    star_import_rows = [row for row in rows if "import *" in str(row.get("evidence") or "")]
    if star_import_rows:
        priority_rows.append(
            {
                "priority": len(priority_rows) + 1,
                "move": "Remove star imports",
                "scope": "; ".join(
                    sorted(
                        {
                            str(row.get("file_path") or "")
                            for row in star_import_rows
                            if str(row.get("file_path") or "")
                        }
                    )
                ),
                "why_it_matters": "Star imports hide dependencies and make deprecation decisions harder to defend.",
                "business_reason": "Star imports hide dependencies and make deprecation decisions harder to defend.",
                "evidence": f"{len(star_import_rows)} MEDIUM hygiene record(s) are explicit star imports.",
                "technical_reason": f"{len(star_import_rows)} MEDIUM hygiene record(s) are explicit star imports.",
                "next_step": "Replace star imports with explicit imports.",
                "why_this_rank": "Easy wins should follow the largest live runtime hotspots.",
                "decision": "deprecate",
                "decision_options": [],
                "done_condition": "Star imports are gone from the published snapshot.",
            }
        )
    priority_rows.append(
        {
            "priority": len(priority_rows) + 1,
            "move": "Re-run ADG and keep the ceiling honest",
            "scope": str((ratchet_doc or {}).get("snapshot") or "p2_ratchet.json"),
            "why_it_matters": "Do not change the ceiling until the underlying hygiene debt is actually reduced or explicitly accepted.",
            "business_reason": "Do not change the ceiling until the underlying hygiene debt is actually reduced or explicitly accepted.",
            "evidence": f"Current count={current_count}; ceiling={ceiling}; delta={delta}.",
            "technical_reason": f"Current count={current_count}; ceiling={ceiling}; delta={delta}.",
            "next_step": "Re-baseline only after the evidence changes are intentional and approved.",
            "why_this_rank": "Re-baselining before cleanup only hides the blocker.",
            "decision": "rebaseline_if_intentional",
            "decision_options": [],
            "done_condition": "The published count is at or below the ceiling and the baseline reflects the current intent.",
        }
    )

    brief = build_bcg_brief(
        title="BCG P2 Ratchet Brief",
        status=status.upper(),
        status_label="P2 ratchet status",
        business_read=business_read,
        technical_read=[
            f"Published sqlite snapshot: {_repo_rel(sqlite_path)}"
            if sqlite_path
            else "Published sqlite snapshot: missing",
            f"P2 ceiling: {ceiling}",
            f"Current MEDIUM hygiene count: {current_count}",
            f"Delta vs ceiling: {delta:+d}",
            f"Baseline snapshot: {baseline_snapshot or 'missing'}",
            (
                "Latest failed run: "
                f"{failed_timestamp or 'missing'}" + (f" ({failed_status})" if failed_status else "")
            ),
        ],
        priority_rule=(
            "Fix the largest live runtime hygiene hotspots first, then remove star imports, "
            "then re-baseline only if the debt is intentional."
        ),
        priority_rows=priority_rows,
        why_this_order=[
            "The highest-count live runtime surfaces move the ceiling fastest.",
            "Star imports are low-ambiguity cleanup once the larger exception paths are underway.",
            "Re-baselining too early hides the blocker instead of paying it down.",
        ],
        next_step="Burn down the top runtime hotspots, then rerun ADG and confirm the count stays under the ceiling.",
        table_limit=6,
    )

    return {
        "status": status,
        "business_read": business_read,
        "summary": {
            "current_medium_hygiene_count": current_count,
            "ceiling": ceiling,
            "delta": delta,
            "baseline_snapshot": baseline_snapshot,
            "published_snapshot": _repo_rel(sqlite_path) if sqlite_path else "",
            "failed_run_timestamp": failed_timestamp,
            "failed_run_status": failed_status,
        },
        "brief": brief,
        "evidence_buckets": evidence_rows,
        "file_hotspots": file_rows,
        "priority_rows": priority_rows,
        "sample_rows": rows[:12],
    }


def _build_cleanup_payload(
    *,
    dead_code_report: dict[str, Any] | None,
    dead_code_path: Path | None,
) -> dict[str, Any]:
    plan = build_deprecation_deletion_plan(dead_code_report, None, None)
    live_rows, archived_rows = _cleanup_queue_rows(dead_code_report)
    summary = plan.get("summary") or {}
    brief = dict(plan.get("brief") or {})
    if dead_code_report is None:
        brief["status"] = "MISSING"
    elif summary.get("dead_code_candidates", 0) == 0:
        brief["status"] = "NO_DELETIONS_APPROVED"
    elif not brief.get("status"):
        brief["status"] = str((dead_code_report or {}).get("status") or "UNKNOWN")
    brief["status_label"] = "Deletion status"
    brief["title"] = "BCG Cleanup Brief"

    return {
        "status": str((dead_code_report or {}).get("status") or "missing"),
        "source": _repo_rel(dead_code_path) if dead_code_path else "",
        "summary": summary,
        "brief": brief,
        "priority_rows": plan.get("priority_rows") or [],
        "live_queue": live_rows[:9],
        "archived_queue": archived_rows[:9],
        "cleanup_candidates": plan.get("cleanup_candidates") or [],
    }


def build_adg_cleanup_queue_and_p2_blocker_trace(
    *,
    adg_artifacts_dir: Path = ARTIFACTS_ADG,
) -> dict[str, Any]:
    dead_code_path, dead_code_report = _latest_dead_code_report(adg_artifacts_dir)
    sqlite_path, sqlite_manifest_path, sqlite_manifest = _latest_snapshot_sqlite(adg_artifacts_dir)
    ratchet_path, ratchet_doc = _latest_p2_ratchet(adg_artifacts_dir)
    failed_manifest_path, failed_manifest = _latest_gate_invocation_manifest(adg_artifacts_dir)

    cleanup = _build_cleanup_payload(
        dead_code_report=dead_code_report,
        dead_code_path=dead_code_path,
    )
    p2 = _p2_summary(sqlite_path, ratchet_doc, failed_manifest)

    overall_status = "present"
    if dead_code_report is None or ratchet_doc is None or sqlite_path is None:
        overall_status = "degraded"
    if dead_code_report is None and sqlite_path is None and ratchet_doc is None:
        overall_status = "missing"

    cleanup_brief = (cleanup.get("brief") or {}) if isinstance(cleanup, dict) else {}
    p2_brief = (p2.get("brief") or {}) if isinstance(p2, dict) else {}
    priority_rows = list((cleanup.get("priority_rows") or [])[:3]) + list((p2.get("priority_rows") or [])[:3])
    bcg_findings = build_bcg_brief(
        title="BCG Cleanup + P2 Blocker Brief",
        status=overall_status.upper(),
        status_label="Trace status",
        secondary_statuses={
            "Cleanup status": str(cleanup.get("status") or "missing"),
            "P2 status": str(p2.get("status") or "missing"),
        },
        business_read=(
            "Use this report to choose between cleanup triage and P2 blocker burn-down; do not delete code unless the dead-code brief explicitly approves it."
        ),
        technical_read=[
            str(cleanup_brief.get("business_read") or "Cleanup brief unavailable."),
            str(p2_brief.get("business_read") or p2.get("business_read") or "P2 brief unavailable."),
            f"Live cleanup queue rows: {len(cleanup.get('live_queue') or [])}",
            f"Archived cleanup queue rows: {len(cleanup.get('archived_queue') or [])}",
            f"P2 delta: {(p2.get('summary') or {}).get('delta', 'unknown')}",
        ],
        priority_rule="Deletions require dead-code proof; live unresolved-import cleanup outranks archived noise; P2 ceiling work outranks broad cleanup when over ceiling.",
        priority_rows=priority_rows,
        why_this_order=[
            "Deletion is irreversible, so it requires the strongest proof.",
            "Live unresolved-import noise reduces trust in the next ADG scan.",
            "P2 over-ceiling hygiene debt blocks the ratchet until paid down or intentionally rebaselined.",
            "Archived or obsolete surfaces stay deferred unless they affect live paths.",
        ],
        next_step="Follow the first live cleanup or P2 blocker row, then rerun ADG.",
        table_limit=6,
    )

    return {
        "artifact_kind": "adg_cleanup_queue_and_p2_blocker_trace",
        "status": overall_status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": {
            "dead_code_report": _repo_rel(dead_code_path) if dead_code_path else "",
            "sqlite": _repo_rel(sqlite_path) if sqlite_path else "",
            "sqlite_manifest": _repo_rel(sqlite_manifest_path) if sqlite_manifest_path else "",
            "ratchet": _repo_rel(ratchet_path) if ratchet_path else "",
            "failed_run_manifest": _repo_rel(failed_manifest_path) if failed_manifest_path else "",
        },
        "cleanup": cleanup,
        "p2": p2,
        "bcg_findings": {
            "schema_version": "1.0",
            "report_kind": "adg_cleanup_queue_and_p2_blocker_trace",
            "brief": bcg_findings,
        },
        "source_snapshots": {
            "sqlite_manifest": sqlite_manifest or {},
            "p2_ratchet": ratchet_doc or {},
            "dead_code_report": dead_code_report or {},
            "failed_run_manifest": failed_manifest or {},
        },
    }


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    align = []
    for header in headers:
        lowered = header.lower()
        if lowered in {"priority", "count", "records", "delta"} or header.startswith("Rank"):
            align.append("---:")
        else:
            align.append("---")
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(align) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_md(value) for value in row) + " |")
    return "\n".join(lines)


def _md(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def _render_cleanup_section(cleanup: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.append("## Cleanup Queue")
    lines.append("")
    lines.append(
        "The dead-code report found no confirmed deletions, so this queue prioritizes signal cleanup and unresolved-import noise reduction."
    )
    lines.append("")
    live_rows = cleanup.get("live_queue") or []
    archived_rows = cleanup.get("archived_queue") or []
    if live_rows:
        lines.append("### Live unresolved-import queue")
        lines.append("")
        lines.append(
            _table(
                ["Priority", "Move", "Why it matters", "Evidence", "Next step"],
                [
                    [
                        row.get("priority"),
                        row.get("move"),
                        row.get("why_it_matters"),
                        row.get("evidence"),
                        row.get("next_step"),
                    ]
                    for row in live_rows
                ],
            )
        )
        lines.append("")
    if archived_rows:
        lines.append("### Archived or obsolete surfaces")
        lines.append("")
        lines.append(
            _table(
                ["Priority", "Move", "Why it matters", "Evidence", "Next step"],
                [
                    [
                        row.get("priority"),
                        row.get("move"),
                        row.get("why_it_matters"),
                        row.get("evidence"),
                        row.get("next_step"),
                    ]
                    for row in archived_rows
                ],
            )
        )
        lines.append("")
    return lines


def _render_p2_section(p2: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.append("## P2 Ratchet Trace")
    lines.append("")
    lines.append(
        "This section explains the current MEDIUM hygiene count, the ceiling in `p2_ratchet.json`, and why the latest run is still blocked."
    )
    lines.append("")
    p2_brief = p2.get("brief") or build_bcg_brief(
        title="BCG P2 Ratchet Brief",
        business_read="P2 trace unavailable.",
        technical_read=["No P2 data could be loaded."],
        status="MISSING",
        status_label="P2 ratchet status",
    )
    lines.extend(render_bcg_brief_md(p2_brief).splitlines())
    lines.append("")
    summary = p2.get("summary") or {}
    lines.append("### Trace Summary")
    lines.append("")
    lines.append(f"- **Current MEDIUM hygiene count:** {_md(summary.get('current_medium_hygiene_count'))}")
    lines.append(f"- **Ceiling:** {_md(summary.get('ceiling'))}")
    delta = int(summary.get("delta") or 0)
    lines.append(f"- **Delta:** {_md(f'{delta:+d}')}")
    lines.append(f"- **Baseline snapshot:** {_md(summary.get('baseline_snapshot') or 'missing')}")
    lines.append(f"- **Published snapshot:** {_md(summary.get('published_snapshot') or 'missing')}")
    if summary.get("failed_run_timestamp"):
        failed_line = f"- **Latest failed run:** {_md(summary.get('failed_run_timestamp'))}"
        if summary.get("failed_run_status"):
            failed_line += f" ({_md(summary.get('failed_run_status'))})"
        lines.append(failed_line)
    lines.append("")

    evidence_buckets = p2.get("evidence_buckets") or []
    if evidence_buckets:
        lines.append("### Evidence Buckets")
        lines.append("")
        lines.append(
            _table(
                ["Evidence", "Count", "Interpretation"],
                [
                    [row.get("evidence"), row.get("count"), row.get("interpretation")]
                    for row in evidence_buckets
                ],
            )
        )
        lines.append("")

    file_hotspots = p2.get("file_hotspots") or []
    if file_hotspots:
        lines.append("### File Hotspots")
        lines.append("")
        lines.append(
            _table(
                ["Priority", "Move", "Why it matters", "Evidence", "Next step"],
                [
                    [
                        idx,
                        row.get("move"),
                        row.get("why_it_matters"),
                        row.get("evidence"),
                        row.get("next_step"),
                    ]
                    for idx, row in enumerate(file_hotspots[:8], start=1)
                ],
            )
        )
        lines.append("")
    return lines


def render_adg_cleanup_queue_and_p2_blocker_trace(doc: dict[str, Any]) -> str:
    lines: list[str] = []
    a = lines.append
    a("# ADG Cleanup Queue and P2 Ratchet Trace")
    a("")
    a(f"- **Generated:** {_md(doc.get('generated_at_utc') or '')}")
    a(f"- **Report status:** {_md(doc.get('status') or '')}")
    sources = doc.get("sources") or {}
    if sources:
        a(f"- **Dead-code source:** `{_md(sources.get('dead_code_report') or 'missing')}`")
        a(f"- **Published sqlite:** `{_md(sources.get('sqlite') or 'missing')}`")
        a(f"- **P2 ratchet:** `{_md(sources.get('ratchet') or 'missing')}`")
        a(f"- **Failed-run manifest:** `{_md(sources.get('failed_run_manifest') or 'missing')}`")
    a("")
    cleanup = doc.get("cleanup") or {}
    p2 = doc.get("p2") or {}
    cleanup_brief = cleanup.get("brief") or build_bcg_brief(
        title="BCG Cleanup Brief",
        business_read="Cleanup report unavailable.",
        technical_read=["No dead-code report could be loaded."],
        status="MISSING",
        status_label="Deletion status",
    )
    lines.extend(render_bcg_brief_md(cleanup_brief).splitlines())
    a("")
    lines.extend(_render_cleanup_section(cleanup))
    lines.extend(_render_p2_section(p2))
    a("### What This Means")
    a("")
    a(
        "- There are no confirmed dead-code deletions in the latest dead-code report, so deletion stays deferred."
    )
    a(
        "- The published snapshot still carries MEDIUM hygiene debt against the P2 ceiling, so the ratchet remains open."
    )
    a("- Reduce the live runtime hotspots first, then rerun ADG and confirm the ceiling stays honest.")
    a("")
    return "\n".join(lines)


def _artifact_paths(
    *,
    adg_artifacts_dir: Path,
    docs_dir: Path,
    ts: str | None,
) -> dict[str, Path]:
    run_id = ts or "latest"
    base = f"{REPORT_STEM}_{run_id}"
    return {
        "json": adg_artifacts_dir / f"{base}.json",
        "md": adg_artifacts_dir / f"{base}.md",
        "json_latest": adg_artifacts_dir / f"{REPORT_STEM}_latest.json",
        "md_latest": adg_artifacts_dir / f"{REPORT_STEM}_latest.md",
        "json_alias": adg_artifacts_dir / f"{REPORT_STEM}.json",
        "md_alias": adg_artifacts_dir / f"{REPORT_STEM}.md",
        "docs_json": docs_dir / f"{REPORT_STEM}.json",
        "docs_md": docs_dir / f"{REPORT_STEM}.md",
        "docs_json_latest": docs_dir / f"{REPORT_STEM}_latest.json",
        "docs_md_latest": docs_dir / f"{REPORT_STEM}_latest.md",
    }


def emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace(
    *,
    adg_artifacts_dir: Path = ARTIFACTS_ADG,
    ts: str | None = None,
    fail_closed: bool = True,
    print_inline: bool = False,
    docs_dir: Path | None = None,
    write_latest: bool = True,
) -> tuple[int, Path | None]:
    docs_target = docs_dir if docs_dir is not None else DOCS_ADG
    try:
        doc = build_adg_cleanup_queue_and_p2_blocker_trace(adg_artifacts_dir=adg_artifacts_dir)
        md = render_adg_cleanup_queue_and_p2_blocker_trace(doc)
        paths = _artifact_paths(adg_artifacts_dir=adg_artifacts_dir, docs_dir=docs_target, ts=ts)
        _write_json(paths["json"], doc)
        _write_text(paths["md"], md)
        if write_latest:
            _write_json(paths["json_alias"], doc)
            _write_text(paths["md_alias"], md)
            _write_json(paths["json_latest"], doc)
            _write_text(paths["md_latest"], md)
            _write_json(paths["docs_json"], doc)
            _write_text(paths["docs_md"], md)
            _write_json(paths["docs_json_latest"], doc)
            _write_text(paths["docs_md_latest"], md)
        if print_inline:
            sys.stdout.write("\n" + md + ("\n" if md.endswith("\n") else "\n"))
        print(f"[adg_cleanup_queue_and_p2_blocker_trace] SUMMARY={_repo_rel(paths['json'])}", file=sys.stderr)
        return 0, paths["json"]
    except (OSError, sqlite3.Error, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"[adg_cleanup_queue_and_p2_blocker_trace] ERROR={exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--adg-artifacts-dir", type=Path, default=ARTIFACTS_ADG)
    parser.add_argument("--docs-dir", type=Path, default=DOCS_ADG)
    parser.add_argument("--ts", default=None)
    parser.add_argument("--no-inline", action="store_true")
    args = parser.parse_args(argv)

    rc, _path = emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace(
        adg_artifacts_dir=args.adg_artifacts_dir,
        ts=args.ts,
        fail_closed=True,
        print_inline=not args.no_inline,
        docs_dir=args.docs_dir,
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
