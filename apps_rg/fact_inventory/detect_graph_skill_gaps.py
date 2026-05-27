"""Post-run skill gap detector — closes the feedback loop between resume runs and the graph.

Reads three artifacts from a completed lane artifact directory:
  - graph_selection_rationale.json   (GSR) — JD admission checks, selected skills, allowed facts
  - native_c03_final_evidence.json   (C03) — facts that actually reached the LLM
  - master_skills_arsenal_ledger.json         — DRAFT skills with allowed_phrases for overlap detection

Optionally reads the resume display text to detect uncited fact IDs.

Output: candidate_skill_gap_report.json

Usage::

    python apps_rg/fact_inventory/detect_graph_skill_gaps.py \
        --artifact-dir artifacts/apps_rg/runtime_proofs/<run_id>/lanes/executive_summary \
        [--ledger apps_rg/fact_inventory/master_skills_arsenal_ledger.json] \
        [--resume-text artifacts/.../resume_display_text.txt] \
        [--output artifacts/.../candidate_skill_gap_report.json]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_gsr(artifact_dir: Path) -> dict[str, Any] | None:
    p = artifact_dir / "graph_selection_rationale.json"
    return _load_json(p) if p.exists() else None


def _load_c03(artifact_dir: Path) -> dict[str, Any] | None:
    p = artifact_dir / "native_c03_final_evidence.json"
    return _load_json(p) if p.exists() else None


def _load_ledger(ledger_path: Path) -> dict[str, Any]:
    return _load_json(ledger_path)


def _load_resume_text(path: Path | None) -> str:
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Gap detectors
# ---------------------------------------------------------------------------

def detect_jd_rejected_skills(gsr: dict[str, Any]) -> list[dict[str, Any]]:
    """Return skills that were evaluated against the JD but not admitted to the graph selection."""
    checks = gsr.get("jd_only_admission_checks", [])
    if not isinstance(checks, list):
        return []
    return [
        {
            "skill_id": c.get("skill_id"),
            "reason_code": c.get("reason_code"),
            "fact_id_links_count": c.get("fact_id_links_count", 0),
            "jd_text_present": c.get("jd_text_present", False),
        }
        for c in checks
        if isinstance(c, dict) and not c.get("admitted", True)
    ]


def detect_draft_skills_matching_jd(
    gsr: dict[str, Any],
    ledger: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return DRAFT skills whose allowed_phrases overlap with the JD keyword hits or section_id context."""
    jd_hits: list[str] = gsr.get("jd_keyword_hits", [])
    if not isinstance(jd_hits, list):
        jd_hits = []

    # Normalise JD text for phrase overlap
    jd_lower = " ".join(str(h).lower() for h in jd_hits)

    skill_rows = ledger.get("skill_rows", [])
    results: list[dict[str, Any]] = []
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        if row.get("activation_status") != "DRAFT":
            continue
        allowed = [str(p).lower() for p in (row.get("allowed_phrases") or [])]
        overlap = [p for p in allowed if p and p in jd_lower]
        if overlap or not row.get("fact_id_links"):
            results.append(
                {
                    "skill_id": row.get("skill_id"),
                    "pillar": row.get("pillar"),
                    "overlap_phrases": overlap,
                    "missing_fact_links": not bool(row.get("fact_id_links")),
                    "support_level": row.get("support_level"),
                }
            )
    return results


def detect_uncited_fact_ids(
    c03: dict[str, Any],
    resume_text: str,
) -> list[str]:
    """Return fact IDs that were selected by C03 but whose source snippets don't appear in the resume text."""
    selected = c03.get("selected_source_fact_ids", [])
    if not isinstance(selected, list) or not resume_text.strip():
        return []

    # A fact is "cited" if its ID appears anywhere in the resume text
    # (conservative check — the LLM may have used the content without the ID)
    uncited: list[str] = []
    for fid in selected:
        if str(fid).lower() not in resume_text.lower():
            uncited.append(str(fid))
    return uncited


def _candidate_fact_phrase_overlap(
    rejected_skill: dict[str, Any],
    ledger: dict[str, Any],
    skill_rows_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find existing candidate facts (from skill rows) that could anchor a rejected skill."""
    sid = rejected_skill.get("skill_id", "")
    row = skill_rows_by_id.get(sid, {})
    allowed_phrases = [str(p).lower() for p in (row.get("allowed_phrases") or [])]
    if not allowed_phrases:
        return []

    suggestions: list[dict[str, Any]] = []
    # Look at all ACTIVE_CONFIRMED skill rows that have facts — their fact_id_links
    # may be appropriate anchors for the rejected skill's domain
    for other_row in ledger.get("skill_rows", []):
        if not isinstance(other_row, dict):
            continue
        if other_row.get("skill_id") == sid:
            continue
        if other_row.get("activation_status") not in ("ACTIVE_CONFIRMED", "ACTIVE"):
            continue
        other_phrases = [str(p).lower() for p in (other_row.get("allowed_phrases") or [])]
        overlap = [p for p in allowed_phrases if any(p in op or op in p for op in other_phrases)]
        if overlap:
            for fid in other_row.get("fact_id_links", []):
                suggestions.append(
                    {
                        "rejected_skill_id": sid,
                        "candidate_fact_id": str(fid),
                        "anchor_skill_id": other_row.get("skill_id"),
                        "match_reason": f"phrase overlap: {overlap[:2]}",
                    }
                )
    return suggestions[:5]  # cap to avoid noise


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_gap_report(
    *,
    artifact_dir: Path,
    ledger_path: Path = DEFAULT_LEDGER,
    resume_text_path: Path | None = None,
) -> dict[str, Any]:
    gsr = _load_gsr(artifact_dir)
    c03 = _load_c03(artifact_dir)
    ledger = _load_ledger(ledger_path)
    resume_text = _load_resume_text(resume_text_path)

    skill_rows_by_id: dict[str, dict[str, Any]] = {
        r.get("skill_id", ""): r
        for r in ledger.get("skill_rows", [])
        if isinstance(r, dict) and r.get("skill_id")
    }

    jd_rejected: list[dict[str, Any]] = detect_jd_rejected_skills(gsr) if gsr else []
    draft_matching: list[dict[str, Any]] = (
        detect_draft_skills_matching_jd(gsr, ledger) if gsr else []
    )
    uncited: list[str] = detect_uncited_fact_ids(c03, resume_text) if c03 else []

    suggested_links: list[dict[str, Any]] = []
    for rej in jd_rejected:
        suggested_links.extend(
            _candidate_fact_phrase_overlap(rej, ledger, skill_rows_by_id)
        )
    # Deduplicate
    seen = set()
    deduped_links: list[dict[str, Any]] = []
    for s in suggested_links:
        key = (s.get("rejected_skill_id"), s.get("candidate_fact_id"))
        if key not in seen:
            seen.add(key)
            deduped_links.append(s)

    section_id = (gsr or {}).get("section_id", artifact_dir.name)

    return {
        "schema": "candidate_skill_gap_report_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "section_id": section_id,
        "summary": {
            "jd_rejected_count": len(jd_rejected),
            "draft_skills_with_jd_overlap_or_no_facts": len(draft_matching),
            "uncited_fact_ids_count": len(uncited),
            "suggested_fact_links_count": len(deduped_links),
        },
        "jd_rejected_skills": jd_rejected,
        "draft_skills_matching_jd": draft_matching,
        "uncited_fact_ids": uncited,
        "suggested_fact_links": deduped_links,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Post-run skill gap detector for apps_rg resume pipelines."
    )
    parser.add_argument(
        "--artifact-dir",
        required=True,
        help="Path to the lane artifact directory (contains graph_selection_rationale.json etc.)",
    )
    parser.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER),
        help="Path to master_skills_arsenal_ledger.json",
    )
    parser.add_argument(
        "--resume-text",
        default=None,
        help="Optional path to resume_display_text.txt for uncited-fact detection",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for candidate_skill_gap_report.json (default: artifact_dir/candidate_skill_gap_report.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    artifact_dir = Path(args.artifact_dir).resolve()
    ledger_path = Path(args.ledger).resolve()
    resume_text_path = Path(args.resume_text).resolve() if args.resume_text else None
    output_path = (
        Path(args.output).resolve()
        if args.output
        else artifact_dir / "candidate_skill_gap_report.json"
    )

    if not artifact_dir.is_dir():
        raise FileNotFoundError(f"artifact_dir not found: {artifact_dir}")
    if not ledger_path.is_file():
        raise FileNotFoundError(f"ledger not found: {ledger_path}")

    report = build_gap_report(
        artifact_dir=artifact_dir,
        ledger_path=ledger_path,
        resume_text_path=resume_text_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"gap_report_written={output_path}")
    s = report["summary"]
    print(
        f"summary: jd_rejected={s['jd_rejected_count']} "
        f"draft_overlap={s['draft_skills_with_jd_overlap_or_no_facts']} "
        f"uncited={s['uncited_fact_ids_count']} "
        f"suggested_links={s['suggested_fact_links_count']}"
    )


if __name__ == "__main__":
    main()
