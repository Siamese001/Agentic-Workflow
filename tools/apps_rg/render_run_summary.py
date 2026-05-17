"""Render a markdown summary of an apps_rg run for inline Cursor Agent chat display.

Reads the JSON evidence emitted by ``apps_rg`` into ``artifacts/apps_rg/runs/<run_id>/``
and prints a structured markdown summary covering:

  * Run identity (run_id, route, commit, replay_key, started_at)
  * L2 sub-stages (E1..E5) with PASS/FAIL/BYPASSED status and timing
  * HOP checkpoints (HOP-0.5 .. HOP-5) reached during the run
  * Per-section narrative verdicts (headline, exec_summary, ENGINEERING & PLATFORM COMPETENCIES, role bullets)
    with composite score, accepted status, and first failed gate
  * Gate failures with reason text
  * L7 route family certification matrix (1/9 certified for R4 path is the norm)
  * ATS / overfit / provenance reports
  * Final artifact paths (DOCX, JSON, run manifest)

Invocation:
    python tools/apps_rg/render_run_summary.py [<run_dir>]

If ``<run_dir>`` is omitted, the most recently modified directory under
``artifacts/apps_rg/runs/`` is selected.

Cursor Agent integration: per ``.windsurf/rules/apps-rg-post-run-summary.md``,
Cursor Agent MUST invoke this script after every apps_rg run and surface the
markdown output inline in chat.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runs"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.section_display_labels import summary_section_label

# ----------------------------------------------------------------- read helpers


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _latest_run_dir() -> Optional[Path]:
    if not RUNS_ROOT.is_dir():
        return None
    candidates = [
        p for p in RUNS_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _fmt_dur_ms(ms: float) -> str:
    if ms is None:
        return "—"
    if ms < 1.0:
        return f"{ms:.3f}ms"
    if ms < 1000:
        return f"{ms:.1f}ms"
    return f"{ms / 1000:.2f}s"


def _truncate_sha(s: str, head: int = 12) -> str:
    if not s:
        return "—"
    if s.startswith("sha256:"):
        return s[: 7 + head] + "…"
    return s[:head] + ("…" if len(s) > head else "")


def _yes_no(v: Any) -> str:
    if v is True:
        return "✅"
    if v is False:
        return "❌"
    return "—"


# ------------------------------------------------------------------- renderers


def _render_identity(run_dir: Path, identity: Optional[Dict[str, Any]],
                     manifest: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Run Identity", ""]
    payload = (identity or {}).get("payload", {}) if identity else {}
    rows: List[Tuple[str, str]] = [
        ("Run dir", str(run_dir.relative_to(REPO_ROOT)) if run_dir.is_relative_to(REPO_ROOT) else str(run_dir)),
        ("Run ID", payload.get("run_id") or (manifest or {}).get("run_id") or "—"),
        ("Request ID", payload.get("request_id") or (manifest or {}).get("request_id") or "—"),
        ("Route", payload.get("route_id") or (manifest or {}).get("route_id") or "—"),
        ("Chain kind", (manifest or {}).get("chain_kind") or "—"),
        ("Started at (UTC)", payload.get("started_at_utc") or "—"),
        ("Git commit", _truncate_sha(payload.get("git_commit") or "")),
        ("Git dirty", _yes_no(payload.get("git_dirty"))),
        ("Deterministic digest", _truncate_sha(payload.get("deterministic_digest") or "")),
        ("Replay key", payload.get("replay_key") or "—"),
        ("X3 disposition", (manifest or {}).get("x3_disposition") or "—"),
    ]
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for k, v in rows:
        lines.append(f"| **{k}** | `{v}` |")
    lines.append("")
    return lines


def _render_l2_substages(terminal_packet: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## L2 Sub-Stages (Steps)", ""]
    if not terminal_packet:
        lines.append("_terminal_ret_packet.json not found — substages unavailable._")
        lines.append("")
        return lines
    stages = (terminal_packet.get("payload", {}) or {}).get("l2_sub_stages", []) or []
    if not stages:
        lines.append("_No L2 sub-stages recorded._")
        lines.append("")
        return lines
    lines.append("| Step | Stage | Status | Duration |")
    lines.append("|---|---|---|---|")
    for st in stages:
        sid = st.get("sub_stage_id", "?")
        sname = st.get("sub_stage_name", "?")
        status = st.get("status", "—")
        dur = st.get("duration_ms", 0.0)
        icon = {"PASS": "✅", "FAIL": "❌", "BYPASSED": "⏭️"}.get(status, "•")
        lines.append(f"| **{sid}** | {sname} | {icon} {status} | {_fmt_dur_ms(dur)} |")
    lines.append("")
    return lines


def _render_hop_checkpoints(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Narrative HOP Checkpoints (Sub-steps)", ""]
    if not run_report:
        lines.append("_run_report.json not found — narrative HOPs unavailable._")
        lines.append("")
        return lines
    checkpoints = run_report.get("checkpoints", []) or []
    if not checkpoints:
        lines.append("_No HOP checkpoints recorded._")
        lines.append("")
        return lines
    # All checkpoints listed reached PASS by virtue of being recorded.
    lines.append("Reached: " + ", ".join(f"`{c}`" for c in checkpoints))
    lines.append("")
    completed = run_report.get("narrative_completed_at")
    if completed:
        lines.append(f"Narrative pass completed at: `{completed}`")
        lines.append("")
    return lines


def _render_section_verdicts(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Per-Section Narrative Verdicts", ""]
    if not run_report:
        lines.append("_run_report.json not found — verdicts unavailable._")
        lines.append("")
        return lines
    narrative = run_report.get("narrative", {}) or {}
    verdicts = narrative.get("per_section_verdicts", []) or []
    if not verdicts:
        lines.append("_No per-section verdicts recorded._")
        lines.append("")
        return lines
    lines.append("| Section | Tier | Source | Composite | Accepted | First failed gate |")
    lines.append("|---|---|---|---|---|---|")
    for v in verdicts:
        section = summary_section_label(str(v.get("section_id", "?")))
        tier = v.get("tier", "?")
        source = v.get("chosen_source", "?")
        comp = v.get("composite", 0.0)
        accepted = v.get("accepted")
        gate = v.get("failed_gate") or "—"
        icon = "✅" if accepted else "❌"
        lines.append(
            f"| `{section}` | {tier} | {source} | {comp:.4f} | {icon} | `{gate}` |"
        )
    lines.append("")
    return lines


def _render_gate_failures(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Gate Failures", ""]
    if not run_report:
        return []
    failures = (run_report.get("narrative", {}) or {}).get("gate_failures", []) or []
    if not failures:
        lines.append("_None — all gates passed._")
        lines.append("")
        return lines
    for i, f in enumerate(failures, 1):
        section_raw = str(f.get("section_id", "—"))
        section = summary_section_label(section_raw)
        gate = f.get("failed_gate") or f.get("reason") or "—"
        detail = f.get("detail") or ""
        if section != section_raw:
            lines.append(f"**{i}.** section=`{section}` (id=`{section_raw}`) gate=`{gate}`")
        else:
            lines.append(f"**{i}.** section=`{section}` gate=`{gate}`")
        if detail:
            lines.append(f"   - detail: {detail}")
    lines.append("")
    return lines


def _render_quality_reports(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Quality Reports", ""]
    if not run_report:
        return []
    rows: List[Tuple[str, str]] = []
    rows.append(("Final quality score", f"{run_report.get('final_quality_score', '—')}"))
    rows.append(("Status", str(run_report.get("status", "—"))))
    rows.append(("ATS valid", _yes_no(run_report.get("ats_valid"))))
    rows.append(("Retry iterations", str(run_report.get("retry_iterations", "—"))))

    overfit = run_report.get("overfit_report") or {}
    rows.append((
        "Overfit detector",
        f"score={overfit.get('score', '—')} escalate={_yes_no(overfit.get('escalate'))} flags={len(overfit.get('flags', []))}",
    ))
    prov = run_report.get("provenance_report") or {}
    rows.append((
        "Provenance",
        f"valid={_yes_no(prov.get('valid'))} reason=`{prov.get('reason', '—')}`",
    ))
    coverage = (run_report.get("narrative", {}) or {}).get("jd_keyword_coverage") or {}
    if coverage:
        cr = coverage.get("coverage_result") or {}
        rows.append((
            "JD keyword coverage",
            f"coverage={cr.get('coverage', '—')} missing={cr.get('missing', [])}",
        ))
    else:
        rows.append(("JD keyword coverage", "_not run / null_"))

    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k, v in rows:
        lines.append(f"| **{k}** | {v} |")
    lines.append("")
    return lines


def _render_l7_certification(l7: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## L7 Route Family Certification", ""]
    if not l7:
        lines.append("_agentic_core_l7_route_family_coverage.json not found._")
        lines.append("")
        return lines
    summary = l7.get("summary") or {}
    lines.append(
        f"Certified: **{summary.get('certified', 0)} / {summary.get('total_families', 0)}** · "
        f"fixture-only: {summary.get('fixture_only', 0)} · "
        f"not certified: {summary.get('not_certified', 0)}"
    )
    lines.append("")
    families = l7.get("route_families") or []
    if families:
        lines.append("| Family | Status | Proof class | Exercised |")
        lines.append("|---|---|---|---|")
        for f in families:
            fam = f.get("route_family", "?")
            stat = f.get("certification_status", "—")
            proof = f.get("proof_class", "—")
            exer = _yes_no(f.get("exercised_in_current_run"))
            icon = {"CERTIFIED": "✅", "NOT_CERTIFIED": "❌"}.get(stat, "•")
            lines.append(f"| `{fam}` | {icon} {stat} | `{proof}` | {exer} |")
        lines.append("")
    return lines


def _render_artifacts(run_dir: Path, run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Output Artifacts", ""]
    docx = run_dir / "Amit_Ayer_Resume.docx"
    json_resume = run_dir / "generated_resume.json"
    rows: List[Tuple[str, str, str]] = []
    for label, path in [
        ("Resume DOCX", docx),
        ("Resume JSON", json_resume),
        ("Run manifest", run_dir / "r4_run_manifest.json"),
        ("Run report", run_dir / "run_report.json"),
        ("How-trace", run_dir / "agentic_core_how_trace.json"),
        ("L7 coverage", run_dir / "agentic_core_l7_route_family_coverage.json"),
        ("Spine proof", run_dir / "agentic_core_spine_proof.json"),
    ]:
        exists = path.is_file()
        size = f"{path.stat().st_size:,} bytes" if exists else "missing"
        icon = "✅" if exists else "❌"
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        rows.append((label, str(rel), f"{icon} {size}"))
    lines.append("| Artifact | Path | Status |")
    lines.append("|---|---|---|")
    for label, path, stat in rows:
        lines.append(f"| **{label}** | `{path}` | {stat} |")
    lines.append("")

    # Surface key narrative anchors when available.
    if run_report:
        company = (run_report.get("narrative", {}) or {}).get("company_brief_provenance", {}).get("company")
        if company:
            lines.append(f"Company: **{company}**")
            lines.append("")
    return lines


# ------------------------------------------------------------------- main


def render(run_dir: Path) -> str:
    """Render the full markdown summary for ``run_dir``."""
    run_report = _load_json(run_dir / "run_report.json")
    manifest = _load_json(run_dir / "r4_run_manifest.json")
    identity = _load_json(run_dir / "runtime_identity_envelope.json")
    terminal = _load_json(run_dir / "terminal_ret_packet.json")
    l7 = _load_json(run_dir / "agentic_core_l7_route_family_coverage.json")

    title = f"# apps_rg Run Summary — `{run_dir.name}`"
    rendered_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts: List[str] = [title, "", f"_Rendered at {rendered_at}_", ""]
    parts += _render_identity(run_dir, identity, manifest)
    parts += _render_l2_substages(terminal)
    parts += _render_hop_checkpoints(run_report)
    parts += _render_section_verdicts(run_report)
    parts += _render_gate_failures(run_report)
    parts += _render_quality_reports(run_report)
    parts += _render_l7_certification(l7)
    parts += _render_artifacts(run_dir, run_report)
    return "\n".join(parts).rstrip() + "\n"


def main(argv: List[str]) -> int:
    if len(argv) > 1 and argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0
    if len(argv) > 1:
        run_dir = Path(argv[1]).resolve()
    else:
        latest = _latest_run_dir()
        if latest is None:
            print(
                f"No run directories found under {RUNS_ROOT}. "
                "Run `python -m apps_rg ...` first.",
                file=sys.stderr,
            )
            return 2
        run_dir = latest
    if not run_dir.is_dir():
        print(f"Run dir not found: {run_dir}", file=sys.stderr)
        return 2
    sys.stdout.write(render(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
