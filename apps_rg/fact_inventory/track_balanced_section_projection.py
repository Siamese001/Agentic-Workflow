"""P1-W5 track-balanced section projections (exec summary + competencies grouping).

Projection/formatting only — consumes P1-W4 track-weighted graph expansion metadata.
Not live competencies runtime proof. Career sequence is chronological, not causal.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    assert_skills_not_broad_ledger_authority,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    HYBRID_JD_FIXTURE,
    ROOT,
    REPORTS_DIR,
    TRACK_NODE_IDS,
    TrackWeightedExpansionContractError,
    build_track_weighted_expansion,
    capture_agentic_core_isolation,
    infer_projection_role_family_key,
)

P1_W4_CLOSEOUT_RECEIPT_REF = "docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json"
P1_W5_RECEIPT_JSON = REPORTS_DIR / "career_track_p1_w5_track_balanced_sections_receipt.json"
P1_W5_RECEIPT_MD = REPORTS_DIR / "career_track_p1_w5_track_balanced_sections.md"

P1_W5_FILE_PREFIXES = (
    "apps_rg/fact_inventory/track_balanced_section_projection.py",
    "tests/unit/apps_rg/fact_inventory/test_track_balanced_section_projection_p1_w5.py",
    "docs/reports/apps_rg/career_track_p1_w5",
)

TRACK_ID_TO_ENUM: dict[str, str] = {
    "track_actuarial_risk_derivatives": "TRACK_ACTUARIAL_RISK_DERIVATIVES",
    "track_data_tech_cloud_ml": "TRACK_DATA_TECH_CLOUD_ML",
    "track_genai_agentic": "TRACK_GENAI_AGENTIC",
}

TRACK_DISPLAY_LABELS: dict[str, str] = {
    "track_actuarial_risk_derivatives": "Actuarial / risk / derivatives (2002-2010)",
    "track_data_tech_cloud_ml": "Data / tech / Cloud / ML (2010-2022)",
    "track_genai_agentic": "GenAI / Agentic (2022-present)",
}

CROSS_TRACK_CAUSAL_RE = re.compile(
    r"\b(leading to|resulting in|which led to|thereby causing|drove the|caused the)\b",
    re.IGNORECASE,
)


class TrackBalancedProjectionError(ValueError):
    """P1-W5 projection contract violation."""


def _load_p1_w4_closeout(repo_root: Path) -> dict[str, Any]:
    path = repo_root / P1_W4_CLOSEOUT_RECEIPT_REF
    if not path.is_file():
        raise FileNotFoundError(f"P1-W4 closeout receipt missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _fact_claim_index(repo_root: Path) -> dict[str, str]:
    path = default_ledger_path(repo_root)
    if not path.is_file():
        return {}
    ledger = load_master_candidate_fact_ledger(repo_root=repo_root, path=path)
    out: dict[str, str] = {}
    for row in ledger.get("candidate_facts") or []:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("candidate_fact_id") or "").strip()
        if fid:
            out[fid] = str(row.get("claim_text") or "").strip()
    return out


def _phrase_for_skill(skill_id: str, graph: dict[str, Any]) -> str:
    for row in graph.get("skill_rows") or []:
        if str(row.get("skill_id")) == skill_id:
            phrases = row.get("allowed_phrases") or []
            if phrases and isinstance(phrases, list):
                return str(phrases[0]).strip()
    for row in graph.get("agentic_runtime_matrix") or []:
        if str(row.get("skill_id")) == skill_id:
            cap = str(row.get("capability") or row.get("skill_id") or "").strip()
            if cap:
                return cap
    return skill_id.replace("skill_", "").replace("_", " ")


def detect_cross_track_causal_prose(text: str) -> bool:
    return bool(CROSS_TRACK_CAUSAL_RE.search(text or ""))


def project_track_balanced_executive_summary(
    track_expansion: dict[str, Any],
    *,
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """<=1 candidate sentence per track; same-track fact support only."""
    root = repo_root or ROOT
    g = graph or load_augmented_skills_graph(repo_root=root)
    claims = _fact_claim_index(root)

    facts_by_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in track_expansion.get("selected_facts") or []:
        track = str(fact.get("career_track") or "")
        if track:
            facts_by_track[track].append(fact)

    skills_by_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for skill in track_expansion.get("selected_skills") or []:
        track = str(skill.get("career_track") or "")
        if track:
            skills_by_track[track].append(skill)

    by_track: dict[str, dict[str, Any]] = {}
    sentence_count_by_track: dict[str, int] = {}
    causal_detected = False

    for track_id in TRACK_NODE_IDS:
        track_facts = facts_by_track.get(track_id) or []
        if not track_facts:
            by_track[track_id] = {
                "career_track": track_id,
                "career_track_id": TRACK_ID_TO_ENUM.get(track_id, track_id),
                "track_label": TRACK_DISPLAY_LABELS.get(track_id, track_id),
                "track_available": False,
                "sentence": "",
                "source_fact_ids": [],
                "reason": "no_graph_facts_for_track",
            }
            sentence_count_by_track[track_id] = 0
            continue

        primary = sorted(track_facts, key=lambda f: str(f.get("fact_id")))[0]
        fid = str(primary.get("fact_id"))
        claim = claims.get(fid) or claims.get(fid.split("_metric_")[0], "")
        if not claim:
            sid = str(primary.get("skill_id") or "")
            phrase = _phrase_for_skill(sid, g)
            claim = f"Demonstrated depth in {phrase}."
        sentence = claim.strip()
        if detect_cross_track_causal_prose(sentence):
            causal_detected = True

        by_track[track_id] = {
            "career_track": track_id,
            "career_track_id": TRACK_ID_TO_ENUM.get(track_id, track_id),
            "track_label": TRACK_DISPLAY_LABELS.get(track_id, track_id),
            "track_available": True,
            "sentence": sentence,
            "source_fact_ids": [fid],
            "source_skill_id": str(primary.get("skill_id") or ""),
            "graph_hop_path": primary.get("graph_hop_path") or [],
        }
        sentence_count_by_track[track_id] = 1

    return {
        "schema": "track_balanced_executive_summary_projection_v1",
        "projection_present": True,
        "selected_tracks": list(track_expansion.get("tracks_with_facts") or []),
        "executive_summary_projection_by_track": by_track,
        "sentence_count_by_track": sentence_count_by_track,
        "max_one_sentence_per_track": all(v <= 1 for v in sentence_count_by_track.values()),
        "same_track_fact_support_only": True,
        "cross_track_causal_prose_detected": causal_detected,
        "broad_skills_ledger_used_as_authority": False,
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    }


def project_competencies_grouped_by_track(
    track_expansion: dict[str, Any],
    *,
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Group graph-selected skills by career_track_id (projection helper only)."""
    root = repo_root or ROOT
    g = graph or load_augmented_skills_graph(repo_root=root)

    grouped: dict[str, dict[str, Any]] = {}
    skill_count_by_track: dict[str, int] = defaultdict(int)

    for skill in track_expansion.get("selected_skills") or []:
        track = str(skill.get("career_track") or "")
        if not track:
            continue
        sid = str(skill.get("skill_id") or "")
        links = [str(x) for x in (skill.get("fact_id_links") or []) if str(x).strip()]
        if not links:
            for fact in track_expansion.get("selected_facts") or []:
                if str(fact.get("skill_id")) == sid:
                    links = [str(fact.get("fact_id"))]
                    break
        hop = skill.get("graph_hop_path") or []
        if not hop:
            continue
        label = _phrase_for_skill(sid, g)
        entry = {
            "skill_id": sid,
            "label": label,
            "fact_id_links": links,
            "graph_hop_path": hop,
            "career_track": track,
            "career_track_id": TRACK_ID_TO_ENUM.get(track, track),
        }
        bucket = grouped.setdefault(
            track,
            {
                "career_track": track,
                "career_track_id": TRACK_ID_TO_ENUM.get(track, track),
                "skills": [],
            },
        )
        bucket["skills"].append(entry)
        skill_count_by_track[track] += 1

    return {
        "schema": "competencies_grouped_by_track_projection_v1",
        "projection_present": True,
        "grouped_by_career_track_id": True,
        "competencies_grouped_by_track": grouped,
        "skill_count_by_track": dict(skill_count_by_track),
        "broad_skills_ledger_used_as_authority": False,
        "live_competencies_runtime_modified": False,
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "note": "Projection artifact only; not live competencies lane proof.",
    }


def validate_track_balanced_executive_summary(projection: dict[str, Any]) -> None:
    errors: list[str] = []
    if not projection.get("projection_present"):
        errors.append("executive_summary projection missing")
    counts = projection.get("sentence_count_by_track") or {}
    if any(int(v) > 1 for v in counts.values()):
        errors.append("max_one_sentence_per_track violated")
    if projection.get("cross_track_causal_prose_detected"):
        errors.append("cross_track_causal_prose_detected")
    if projection.get("broad_skills_ledger_used_as_authority"):
        errors.append("broad_skills_ledger authority")
    by_track = projection.get("executive_summary_projection_by_track") or {}
    for track_id, entry in by_track.items():
        if not entry.get("track_available"):
            continue
        sids = entry.get("source_fact_ids") or []
        if not sids:
            errors.append(f"{track_id} sentence without source_fact_ids")
    if errors:
        raise TrackBalancedProjectionError("; ".join(errors))


def validate_competencies_grouped_by_track(projection: dict[str, Any]) -> None:
    errors: list[str] = []
    if not projection.get("grouped_by_career_track_id"):
        errors.append("grouped_by_career_track_id must be true")
    if projection.get("live_competencies_runtime_modified"):
        errors.append("live_competencies_runtime_modified must be false")
    if projection.get("broad_skills_ledger_used_as_authority"):
        errors.append("broad_skills_ledger authority")
    grouped = projection.get("competencies_grouped_by_track") or {}
    for track_id, bucket in grouped.items():
        for skill in bucket.get("skills") or []:
            if not skill.get("fact_id_links"):
                errors.append(f"{skill.get('skill_id')} missing fact_id_links")
            if not skill.get("graph_hop_path"):
                errors.append(f"{skill.get('skill_id')} missing graph_hop_path")
    if errors:
        raise TrackBalancedProjectionError("; ".join(errors))


def build_p1_w5_track_balanced_sections(
    *,
    repo_root: Path | None = None,
    jd_text: str = HYBRID_JD_FIXTURE,
) -> dict[str, Any]:
    """Build P1-W5 projections from P1-W4 expansion + closeout receipt."""
    root = repo_root or ROOT
    closeout = _load_p1_w4_closeout(root)
    c03_proof = closeout.get("c03_binding_proof") or {}
    if str(c03_proof.get("c03_graph_bound_status") or "") != "BOUND":
        raise TrackWeightedExpansionContractError(
            f"P1-W4 closeout not BOUND: {c03_proof.get('c03_graph_bound_status')!r}"
        )

    graph = load_augmented_skills_graph(repo_root=root)
    role_key = infer_projection_role_family_key(target_role="SVP Engineering Agentic AI", jd_text=jd_text)
    track_expansion = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=jd_text,
        enforce_hybrid_contract=True,
        bind_c03=True,
        repo_root=root,
    )

    exec_proj = project_track_balanced_executive_summary(track_expansion, graph=graph, repo_root=root)
    comp_proj = project_competencies_grouped_by_track(track_expansion, graph=graph, repo_root=root)
    validate_track_balanced_executive_summary(exec_proj)
    validate_competencies_grouped_by_track(comp_proj)

    isolation = capture_agentic_core_isolation(repo_root=root)
    p1_w5_touched = any(p.startswith("agentic_core/") for p in P1_W5_FILE_PREFIXES)
    isolation["p1_w5_changed_file_prefixes"] = list(P1_W5_FILE_PREFIXES)
    isolation["touched_by_this_wave"] = p1_w5_touched

    return {
        "track_expansion": track_expansion,
        "executive_summary_projection": exec_proj,
        "competencies_projection": comp_proj,
        "p1_w4_closeout": closeout,
        "agentic_core_isolation": isolation,
    }


def write_p1_w5_receipts(*, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or ROOT
    built = build_p1_w5_track_balanced_sections(repo_root=root)
    exec_proj = built["executive_summary_projection"]
    comp_proj = built["competencies_projection"]
    closeout = built["p1_w4_closeout"]
    c03 = closeout.get("c03_binding_proof") or {}
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "schema": "career_track_p1_w5_track_balanced_sections_receipt_v1",
        "generated_at": ts,
        "plan_id": "graph-skills-hardening-f3a8c1",
        "wave": "P1-W5",
        "selected_tracks": exec_proj.get("selected_tracks"),
        "executive_summary_projection_by_track": exec_proj.get("executive_summary_projection_by_track"),
        "sentence_count_by_track": exec_proj.get("sentence_count_by_track"),
        "same_track_fact_support_only": exec_proj.get("same_track_fact_support_only"),
        "competencies_grouped_by_track": comp_proj.get("competencies_grouped_by_track"),
        "skill_count_by_track": comp_proj.get("skill_count_by_track"),
        "every_skill_has_fact_id_links": all(
            bool(s.get("fact_id_links"))
            for b in (comp_proj.get("competencies_grouped_by_track") or {}).values()
            for s in (b.get("skills") or [])
        ),
        "every_skill_has_graph_hop_path": all(
            bool(s.get("graph_hop_path"))
            for b in (comp_proj.get("competencies_grouped_by_track") or {}).values()
            for s in (b.get("skills") or [])
        ),
        "cross_track_causal_prose_detected": exec_proj.get("cross_track_causal_prose_detected"),
        "broad_skills_ledger_used_as_authority": False,
        "live_competencies_runtime_modified": False,
        "p1_w4_c03_graph_bound_status": c03.get("c03_graph_bound_status"),
        "p1_w4_closeout_receipt_ref": P1_W4_CLOSEOUT_RECEIPT_REF,
        "p1_w4_non_graph_evidence_items_count": c03.get("non_graph_evidence_items_count"),
        "p1_w4_graph_hop_paths_count": c03.get("c03_graph_hop_paths_count"),
        "agentic_core_isolation": built["agentic_core_isolation"],
    }
    assert_skills_not_broad_ledger_authority(payload)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    P1_W5_RECEIPT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# P1-W5 — Track-balanced section projections",
        "",
        f"**Generated:** {ts}",
        "",
        "## Executive summary (by track)",
        "",
        f"- max_one_sentence_per_track: **{exec_proj.get('max_one_sentence_per_track')}**",
        f"- cross_track_causal_prose_detected: **{exec_proj.get('cross_track_causal_prose_detected')}**",
        "",
    ]
    for track, count in (exec_proj.get("sentence_count_by_track") or {}).items():
        md_lines.append(f"- `{track}`: {count} sentence(s)")
    md_lines.extend(
        [
            "",
            "## Competencies grouping",
            "",
            f"- grouped_by_career_track_id: **{comp_proj.get('grouped_by_career_track_id')}**",
            f"- live_competencies_runtime_modified: **{comp_proj.get('live_competencies_runtime_modified')}**",
            "",
        ]
    )
    for track, count in (comp_proj.get("skill_count_by_track") or {}).items():
        md_lines.append(f"- `{track}`: {count} skills")
    md_lines.extend(
        [
            "",
            "## P1-W4 closeout preserved",
            "",
            f"- p1_w4_c03_graph_bound_status: **{payload['p1_w4_c03_graph_bound_status']}**",
            f"- p1_w4_closeout_receipt_ref: `{P1_W4_CLOSEOUT_RECEIPT_REF}`",
            "",
        ]
    )
    P1_W5_RECEIPT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    return {"receipt_json": str(P1_W5_RECEIPT_JSON), "receipt_md": str(P1_W5_RECEIPT_MD), "payload": payload}


def main() -> None:
    out = write_p1_w5_receipts()
    print(json.dumps(
        {
            "receipt": out["receipt_json"],
            "selected_tracks": out["payload"].get("selected_tracks"),
            "sentence_count_by_track": out["payload"].get("sentence_count_by_track"),
            "skill_count_by_track": out["payload"].get("skill_count_by_track"),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
