"""Report-only graph-skill utilization for an apps_rg run (non-blocking).

Wires the existing D8 anti-gaming scorer
(``apps_rg.runtime.graph_skills_utilization_scorer.score_graph_skills_utilization``)
against a real run's artifacts and surfaces GENUINE graph-skill materialization
per lane. It NEVER blocks, mutates the run, or stamps provenance — it only
measures what materialized, respecting the D8 rule that a skill counts as "used"
only when its allowed phrase appears in the display text AND a linked fact is
cited.

Two signals are emitted:
  * competencies — full D8 utilization (eligible / used / score) reconstructed
    from ``proof_pool_metadata.competency_capability_bundles`` (the only lane that
    carries allowed_phrases on disk).
  * competencies — derived evidence-strength score from existing graph metadata
    (report-only; never proof authority).
  * every lane — a lighter "graph skills referenced in the selection plan" count
    from each section's ``l2_output_snapshot.selected_fact_plan`` (reflection
    breadth, not D8-proven use).

Usage:
    python tools/apps_rg/graph_skill_utilization_report.py [<run_dir>] [--json-only]

With no run dir, the most recently modified run under artifacts/apps_rg/runs/ and
artifacts/apps_rg/e2e_aig_verify/ is auto-selected.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.graph_skills_utilization_scorer import score_graph_skills_utilization

_SKILL_ID_RE = re.compile(r"skill_[a-z0-9_]+")
# Tokens that are JSON *key* fragments, not real skill ids — the regex would
# otherwise count the keys "skill_id" / "source_skill_ids" as skill references.
_SKILL_ID_KEY_NOISE = frozenset({"skill_id", "skill_ids"})


def _latest_run_dir() -> Path | None:
    roots = [
        REPO_ROOT / "artifacts" / "apps_rg" / "runs",
        REPO_ROOT / "artifacts" / "apps_rg" / "e2e_aig_verify",
    ]
    candidates: list[Path] = []
    for root in roots:
        if root.is_dir():
            candidates.extend(p.parent for p in root.rglob("final_resume.json"))
    if not candidates:
        return None
    # Walk up to the modular root (the dir that holds both final_resume_assembly/
    # and sections/) so resolution works regardless of which final_resume.json hit.
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _find_spine_final_resume(run_dir: Path) -> Path | None:
    spine = sorted(run_dir.rglob("final_resume_assembly/final_resume.json"))
    return spine[-1] if spine else None


def _find_competencies_runtime_payload(run_dir: Path) -> Path | None:
    hits = sorted(run_dir.rglob("sections/competencies/real/*/runtime_payload.json"))
    return hits[-1] if hits else None


def _competencies_display_and_coverage(spine: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    by_id = {s.get("section_id"): s for s in spine.get("sections", []) if isinstance(s, dict)}
    snap = (by_id.get("competencies") or {}).get("l2_output_snapshot") or {}
    terms: list[str] = []
    for cat in snap.get("competencies") or []:
        if not isinstance(cat, dict):
            continue
        for term in cat.get("terms") or []:
            text = term.get("text") if isinstance(term, dict) else term
            if str(text or "").strip():
                terms.append(str(text).strip())
    display_text = " . ".join(terms)
    coverage = {
        "sentences": [
            {"cited_fact_ids": row.get("source_fact_ids") or []}
            for row in (snap.get("claim_ledger") or [])
            if isinstance(row, dict)
        ]
    }
    return display_text, coverage


def _competencies_skill_rows(runtime_payload: dict[str, Any]) -> list[dict[str, Any]]:
    bundles = (runtime_payload.get("proof_pool_metadata") or {}).get(
        "competency_capability_bundles"
    ) or []
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        links = [str(x) for x in (bundle.get("linked_source_fact_ids") or []) if str(x).strip()]
        for skill in bundle.get("bound_skills") or []:
            if not isinstance(skill, dict) or not str(skill.get("skill_id") or "").strip():
                continue
            metric_ids = [
                str(x)
                for x in (
                    skill.get("linked_metric_outcome_ids")
                    or bundle.get("linked_metric_outcome_ids")
                    or bundle.get("metric_outcome_ids")
                    or []
                )
                if str(x).strip()
            ]
            rows.append(
                {
                    "skill_id": str(skill["skill_id"]),
                    "allowed_phrases": [str(p) for p in (skill.get("allowed_phrases") or [])],
                    "fact_id_links": list(links),
                    "linked_source_fact_ids": list(links),
                    "linked_metric_outcome_ids": metric_ids,
                    "support_level": str(skill.get("support_level") or bundle.get("support_level") or ""),
                    "confidence_grade": str(
                        skill.get("confidence_grade")
                        or bundle.get("confidence_grade")
                        or bundle.get("evidence_confidence")
                        or bundle.get("confidence")
                        or ""
                    ),
                    "external_claim_policy": str(
                        skill.get("external_claim_policy") or bundle.get("external_claim_policy") or ""
                    ),
                    "human_confirmed": bool(skill.get("human_confirmed") or bundle.get("human_confirmed")),
                    "source_trace": bundle.get("source_trace") or bundle.get("source_trace_archive_relpaths") or [],
                    "forbidden_phrases": [],
                }
            )
    return rows


def _per_lane_selection_plan_skill_refs(spine: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sec in spine.get("sections", []):
        if not isinstance(sec, dict):
            continue
        snap = sec.get("l2_output_snapshot") or {}
        blob = json.dumps(snap.get("selected_fact_plan"))
        ids = sorted(set(_SKILL_ID_RE.findall(blob)) - _SKILL_ID_KEY_NOISE)
        out.append({"section_id": sec.get("section_id"), "selection_plan_skill_ref_count": len(ids), "skill_ids": ids})
    return out


def build_report(run_dir: Path) -> dict[str, Any]:
    spine_path = _find_spine_final_resume(run_dir)
    if spine_path is None:
        raise FileNotFoundError(f"No final_resume_assembly/final_resume.json under {run_dir}")
    spine = json.loads(spine_path.read_text(encoding="utf-8"))

    competencies: dict[str, Any] = {"available": False}
    rp_path = _find_competencies_runtime_payload(run_dir)
    if rp_path is not None:
        rp = json.loads(rp_path.read_text(encoding="utf-8"))
        rows = _competencies_skill_rows(rp)
        if rows:
            display_text, coverage = _competencies_display_and_coverage(spine)
            receipt = score_graph_skills_utilization(
                section_id="competencies",
                skill_rows=rows,
                resume_display_text=display_text,
                text_claim_coverage=coverage,
                allowed_fact_ids=[str(x) for x in (rp.get("allowed_fact_ids") or [])],
            )
            strength = receipt.get("evidence_strength") or {}
            competencies = {
                "available": True,
                "eligible_skill_count": receipt["eligible_skill_count"],
                "used_skill_count": len(receipt["used_skill_ids"]),
                "utilization_score": receipt["utilization_score"],
                "average_evidence_strength_score": strength.get("average_score", 0.0),
                "evidence_strength_band_counts": strength.get("band_counts", {}),
                "top_evidence_strength_skill_ids": [
                    row.get("skill_id") for row in (strength.get("top_skill_strength") or [])[:8]
                ],
                "top_evidence_strength": (strength.get("top_skill_strength") or [])[:8],
                "pass": receipt["pass"],
                "used_skill_ids": receipt["used_skill_ids"],
                "semantic_variants_matched": len(receipt["semantic_variants_matched"]),
                "forbidden_phrase_violations": len(receipt["forbidden_phrase_violations"]),
            }

    return {
        "schema": "apps_rg_graph_skill_utilization_report_v1",
        "report_class": "REPORT_ONLY_NON_BLOCKING",
        "run_dir": str(run_dir).replace("\\", "/"),
        "spine_final_resume": str(spine_path).replace("\\", "/"),
        "competencies_d8_utilization": competencies,
        "per_lane_selection_plan_skill_refs": _per_lane_selection_plan_skill_refs(spine),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# apps_rg Graph-Skill Utilization (report-only, non-blocking)", ""]
    comp = report.get("competencies_d8_utilization") or {}
    if comp.get("available"):
        lines += [
            "## Competencies — D8 genuine utilization",
            "",
            "| eligible skills | D8-used | utilization | avg evidence strength | semantic-variant matches | pass |",
            "|---|---|---|---|---|---|",
            f"| {comp['eligible_skill_count']} | {comp['used_skill_count']} | "
            f"{comp['utilization_score']} | {comp.get('average_evidence_strength_score', 0.0)} | "
            f"{comp['semantic_variants_matched']} | {comp['pass']} |",
            "",
            f"D8-used skill ids: {', '.join(comp['used_skill_ids']) or '_none_'}",
            "",
            "Top evidence-strength skill ids: "
            f"{', '.join(comp.get('top_evidence_strength_skill_ids') or []) or '_none_'}",
            "",
        ]
    else:
        lines += ["## Competencies — D8 genuine utilization", "", "_competencies skill rows not found in run_", ""]
    lines += [
        "## Per-lane graph-skill references (selection plan — reflection breadth)",
        "",
        "| lane | skill refs in selection plan |",
        "|---|---|",
    ]
    for row in report.get("per_lane_selection_plan_skill_refs") or []:
        lines.append(f"| {row['section_id']} | {row['selection_plan_skill_ref_count']} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--json-only"]
    json_only = "--json-only" in argv
    if args:
        run_dir = Path(args[0])
        if not run_dir.is_dir():
            print(f"not a directory: {run_dir}", file=sys.stderr)
            return 2
    else:
        resolved = _latest_run_dir()
        if resolved is None:
            print("no run dir found under artifacts/apps_rg/", file=sys.stderr)
            return 2
        run_dir = resolved
        # climb to the modular root holding final_resume_assembly/
        while run_dir != run_dir.parent and not (run_dir / "final_resume_assembly").is_dir():
            up = run_dir.parent
            if (up / "final_resume_assembly").is_dir():
                run_dir = up
                break
            run_dir = up

    report = build_report(run_dir)
    out_path = run_dir / "graph_skill_utilization_report.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if json_only:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report))
        print(f"\n_report: {out_path}_".replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
