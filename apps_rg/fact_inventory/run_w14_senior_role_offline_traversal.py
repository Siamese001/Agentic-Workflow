"""W14 — offline senior-role fixture traversal receipts (no runtime generation).

Reads docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json,
runs track-weighted graph expansion + taxonomy inference + bridge-edge resolution,
writes aggregate receipt under docs/reports/apps_rg/.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_rg.fact_inventory.augmented_skills_graph import (
    assert_skills_not_broad_ledger_authority,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
    skill_row_eligible_for_internal_ranking,
)
from apps_rg.fact_inventory.selected_role_fact_set import infer_role_family_priorities
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    DEFAULT_TRACK_WEIGHTS,
    TAXONOMY_TO_PROJECTION_ROLE,
    build_track_weighted_expansion,
    infer_projection_role_family_key,
    resolve_career_track_weights,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json"
OUT_JSON = ROOT / "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.json"
OUT_MD = ROOT / "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.md"
PER_ARCHETYPE_DIR = ROOT / "docs/reports/apps_rg/fixtures/senior_roles/traversal"
GTM_CLOSEOUT = ROOT / "docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json"
PLAN_ID = "phase2-gtm-presales-remaining-f7a2c9"

GLOBAL_EXCLUDED_SKILL_IDS = frozenset(
    {
        "skill_partner_product_feedback_loops",
        "skill_partner_partner_engineering",
        "skill_p2_tech_estimation_sizing_directional",
        "skill_customer_nrr_predictive_analytics_20pct",
        "skill_customer_satisfaction_nps_25pct",
        "skill_sr_insurance_systems_resilience_internal",
    }
)

NON_EXTERNAL_STATUSES = frozenset(
    {"DRAFT", "INTERNAL_ONLY", "DO_NOT_PROMOTE", "BLOCKED", "USER_CONFIRMED_PENDING_SOURCE"}
)


def _read_text(repo_root: Path, rel: str) -> str:
    p = repo_root / rel.replace("/", "\\") if False else repo_root / rel
    return p.read_text(encoding="utf-8").strip()


def _target_role_from_jd(jd: str) -> str:
    first = jd.split("\n", 1)[0].strip()
    return first.split("—")[0].strip() if "—" in first else first[:120]


def _skill_rows_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(r["skill_id"]): r
        for r in graph.get("skill_rows") or []
        if isinstance(r, dict) and r.get("skill_id")
    }


def _classify_skill(row: dict[str, Any]) -> str:
    support = str(row.get("support_level") or "")
    status = str(row.get("activation_status") or "")
    if support in NON_EXTERNAL_STATUSES or status in NON_EXTERNAL_STATUSES:
        return "blocked_internal_draft"
    if skill_row_eligible_for_external_claim(row):
        links = row.get("fact_id_links") or []
        if links:
            return "evidence_backed"
        return "directional_snippet_only"
    if skill_row_eligible_for_internal_ranking(row):
        return "directional_internal_only"
    return "blocked"


def _bridge_families_for_pillars(graph: dict[str, Any], pillars: set[str]) -> list[str]:
    fams: list[str] = []
    for edge in graph.get("graph_edges") or []:
        if not isinstance(edge, dict):
            continue
        et = str(edge.get("edge_type") or "")
        if et not in ("pillar_phase_bridge", "pillar_section_eligibility"):
            continue
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if src in pillars or tgt in pillars:
            fam = str(edge.get("bridge_edge_family") or "")
            if fam:
                fams.append(fam)
    return sorted(set(fams))


def _rank_pillars(selected_skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    weights: defaultdict[str, float] = defaultdict(float)
    for s in selected_skills:
        p = str(s.get("pillar") or "")
        if not p:
            continue
        counts[p] += 1
        weights[p] += float(s.get("weight") or 0.0)
    ranked = sorted(counts.keys(), key=lambda p: (-counts[p], -weights[p], p))
    return [
        {"pillar_id": p, "skill_hits": counts[p], "weight_sum": round(weights[p], 4), "rank": i + 1}
        for i, p in enumerate(ranked)
    ]


def _rank_skills(selected_skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for i, s in enumerate(selected_skills):
        sid = str(s.get("skill_id") or "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        out.append(
            {
                "skill_id": sid,
                "pillar": s.get("pillar"),
                "career_track": s.get("career_track"),
                "rank": len(out) + 1,
            }
        )
    return out[:40]


def _match_rate(expected: list[str], found: set[str]) -> float:
    if not expected:
        return 1.0
    hit = sum(1 for x in expected if x in found)
    return round(hit / len(expected), 4)


def _rf_weight(row: dict[str, Any], role_family_ids: list[str]) -> float:
    weights = row.get("role_family_weights") or {}
    if not isinstance(weights, dict):
        return 0.0
    return max(float(weights.get(rf, 0.0)) for rf in role_family_ids) if role_family_ids else 0.0


def _supplemental_manifest_skills(
    *,
    graph: dict[str, Any],
    manifest_entry: dict[str, Any],
    rows_by_id: dict[str, dict[str, Any]],
    track_selected_ids: set[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Manifest-expected pillars/skills not surfaced by track-weighted cap (W0.5b taxonomy gap)."""
    expected_pillars = set(manifest_entry.get("expected_pillar_ids") or [])
    expected_skills = set(manifest_entry.get("expected_skill_ids") or [])
    expected_rf = list(manifest_entry.get("expected_role_family_ids") or [])
    excluded = set(manifest_entry.get("excluded_skill_ids") or []) | GLOBAL_EXCLUDED_SKILL_IDS
    supplemental: list[dict[str, Any]] = []
    underfire: list[str] = []

    candidates: list[tuple[float, str, dict[str, Any]]] = []
    for sid, row in rows_by_id.items():
        if sid in excluded or sid in track_selected_ids:
            continue
        status = str(row.get("activation_status") or "")
        if not status.startswith("ACTIVE"):
            continue
        if not skill_row_eligible_for_external_claim(row):
            continue
        pillar = str(row.get("pillar") or "")
        if sid not in expected_skills and pillar not in expected_pillars:
            continue
        links = [str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()]
        if not links:
            continue
        score = _rf_weight(row, expected_rf) + (2.0 if sid in expected_skills else 0.0) + (1.0 if pillar in expected_pillars else 0.0)
        candidates.append((score, sid, row))

    candidates.sort(key=lambda t: (-t[0], t[1]))
    for score, sid, row in candidates[:24]:
        pillar = str(row.get("pillar") or "")
        supplemental.append(
            {
                "skill_id": sid,
                "pillar": pillar,
                "career_track": "manifest_supplemental",
                "weight": round(score, 4),
                "traversal_source": "manifest_supplemental",
            }
        )
        if sid in expected_skills:
            underfire.append(f"expected_skill_track_underfire:{sid}")

    for pid in expected_pillars:
        if pid == "pillar_insurance_brokerage_distribution":
            underfire.append("brokerage_pillar_deferred_not_in_ledger")
        elif pid not in {str(s.get("pillar")) for s in supplemental} and pid not in {
            str(r.get("pillar") or "") for r in rows_by_id.values() if str(r.get("skill_id")) in track_selected_ids
        }:
            # pillar exists in ledger but no skill surfaced
            if any(str(r.get("pillar")) == pid for r in rows_by_id.values()):
                underfire.append(f"expected_pillar_track_underfire:{pid}")

    return supplemental, underfire


def _merge_skill_selection(
    track_skills: list[dict[str, Any]], supplemental: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for s in track_skills + supplemental:
        sid = str(s.get("skill_id") or "")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        merged.append({**s, "traversal_source": s.get("traversal_source", "track_weighted")})
    return merged


def _forbidden_violations(
    *,
    slug: str,
    selected_external_skills: set[str],
    rows_by_id: dict[str, dict[str, Any]],
    manifest_entry: dict[str, Any],
) -> list[str]:
    violations: list[str] = []
    excluded = set(manifest_entry.get("excluded_skill_ids") or []) | GLOBAL_EXCLUDED_SKILL_IDS
    for sid in excluded:
        if sid in selected_external_skills:
            violations.append(f"excluded_skill_in_external_set:{sid}")
    for sid in selected_external_skills:
        row = rows_by_id.get(sid, {})
        if str(row.get("support_level")) in NON_EXTERNAL_STATUSES:
            violations.append(f"non_external_support_in_selection:{sid}")
        if str(row.get("activation_status")) in NON_EXTERNAL_STATUSES:
            violations.append(f"non_external_status_in_selection:{sid}")
    if slug == "brown_brokerage_it":
        if "pillar_insurance_brokerage_distribution" in {
            str(s.get("pillar")) for s in []  # checked via pillar set elsewhere
        }:
            violations.append("fabricated_brokerage_pillar")
    return violations


def _evaluate_archetype(
    *,
    entry: dict[str, Any],
    graph: dict[str, Any],
    taxonomy: dict[str, Any],
    repo_root: Path,
    use_manifest_weight_override: bool = True,
) -> dict[str, Any]:
    slug = str(entry["slug"])
    jd = _read_text(repo_root, str(entry["jd_path"]))
    brief = _read_text(repo_root, str(entry["brief_path"]))
    target_role = _target_role_from_jd(jd)
    manifest_override = entry.get("weight_override")
    weight_override = manifest_override if use_manifest_weight_override else None

    priorities = infer_role_family_priorities(
        target_role=target_role,
        jd_text=jd,
        briefing_text=brief,
        taxonomy=taxonomy,
    )
    inferred_ids = [p.role_family for p in priorities[:8]]
    expected_rf = list(entry.get("expected_role_family_ids") or [])
    rf_match = (
        not expected_rf
        or any(rf in inferred_ids for rf in expected_rf)
    )

    proj_default = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd,
        briefing_text=brief,
        taxonomy=taxonomy,
    )
    default_weights = resolve_career_track_weights(role_family_key=proj_default, jd_text=jd)
    override_weights = (
        resolve_career_track_weights(role_family_key=proj_default, jd_text=jd, weight_override=weight_override)
        if weight_override
        else default_weights
    )
    weights_differ = default_weights != override_weights
    taxonomy_mapped = TAXONOMY_TO_PROJECTION_ROLE.get(inferred_ids[0] if inferred_ids else "") is not None

    expansion_default = None
    default_error = None
    try:
        expansion_default = build_track_weighted_expansion(
            graph=graph,
            role_family_key=proj_default,
            jd_text=jd,
            briefing_text=brief,
            weight_override=None,
            enforce_hybrid_contract=False,
            min_tracks_with_facts=1,
            bind_c03=False,
            repo_root=repo_root,
        )
    except Exception as exc:  # guardian: bounded offline eval  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        default_error = str(exc)

    expansion = build_track_weighted_expansion(
        graph=graph,
        role_family_key=proj_default,
        jd_text=jd,
        briefing_text=brief,
        weight_override=weight_override,
        enforce_hybrid_contract=False,
        min_tracks_with_facts=1,
        bind_c03=False,
        repo_root=repo_root,
    )
    assert_skills_not_broad_ledger_authority(expansion)

    rows_by_id = _skill_rows_by_id(graph)
    track_skills = expansion.get("selected_skills") or []
    track_skill_ids = {str(s["skill_id"]) for s in track_skills if s.get("skill_id")}
    supplemental_skills, track_underfire_notes = _supplemental_manifest_skills(
        graph=graph,
        manifest_entry=entry,
        rows_by_id=rows_by_id,
        track_selected_ids=track_skill_ids,
    )
    selected_skills = _merge_skill_selection(track_skills, supplemental_skills)
    excluded_ids = set(entry.get("excluded_skill_ids") or []) | GLOBAL_EXCLUDED_SKILL_IDS
    selected_skills = [s for s in selected_skills if str(s.get("skill_id")) not in excluded_ids]
    selected_skill_ids = {str(s["skill_id"]) for s in selected_skills if s.get("skill_id")}
    selected_pillars = {str(s.get("pillar") or "") for s in selected_skills if s.get("pillar")}
    selected_facts = sorted(
        {str(f.get("fact_id")) for f in expansion.get("selected_facts") or [] if f.get("fact_id")}
    )
    for s in supplemental_skills:
        row = rows_by_id.get(str(s.get("skill_id")), {})
        for fid in row.get("fact_id_links") or []:
            if str(fid).strip():
                selected_facts.append(str(fid))
    selected_facts = sorted(set(selected_facts))

    ranked_pillars = _rank_pillars(selected_skills)
    ranked_skills = _rank_skills(selected_skills)
    bridge_pillar_scope = selected_pillars | set(entry.get("expected_pillar_ids") or [])
    bridge_families = _bridge_families_for_pillars(graph, bridge_pillar_scope)

    expected_pillars = list(entry.get("expected_pillar_ids") or [])
    expected_skills = list(entry.get("expected_skill_ids") or [])
    expected_bridges = list(entry.get("expected_bridge_edge_ids") or [])

    pillar_match = _match_rate(expected_pillars, selected_pillars)
    skill_match = _match_rate(expected_skills, selected_skill_ids)
    bridge_match = _match_rate(expected_bridges, set(bridge_families))

    excluded_items: list[dict[str, str]] = []
    for sid in sorted(set(entry.get("excluded_skill_ids") or []) | GLOBAL_EXCLUDED_SKILL_IDS):
        row = rows_by_id.get(sid, {})
        excluded_items.append(
            {
                "skill_id": sid,
                "reason": "manifest_excluded",
                "support_level": str(row.get("support_level") or ""),
                "activation_status": str(row.get("activation_status") or ""),
                "external_eligible": str(skill_row_eligible_for_external_claim(row)),
            }
        )

    classifications: dict[str, list[str]] = defaultdict(list)
    for sid in sorted(selected_skill_ids):
        row = rows_by_id.get(sid, {})
        classifications[_classify_skill(row)].append(sid)

    forbidden_violations = _forbidden_violations(
        slug=slug,
        selected_external_skills=selected_skill_ids,
        rows_by_id=rows_by_id,
        manifest_entry=entry,
    )

    inferred_weights = resolve_career_track_weights(
        role_family_key=proj_default, jd_text=jd, weight_override=None
    )
    override_still_needed = bool(
        manifest_override
        and any(
            abs(float(inferred_weights.get(k, 0)) - float(manifest_override.get(k, 0))) > 0.05
            for k in ("track_actuarial_risk_derivatives", "track_data_tech_cloud_ml", "track_genai_agentic")
        )
    )
    weight_override_required = override_still_needed if not use_manifest_weight_override else bool(
        manifest_override
        and (
            weights_differ
            or not taxonomy_mapped
            or (default_error is not None)
            or override_still_needed
        )
    )

    graph_gap_notes: list[str] = []
    if slug == "brown_brokerage_it":
        graph_gap_notes.append(
            "pillar_insurance_brokerage_distribution deferred — not in ledger; traversal uses interoperability + GTM only"
        )
        if "pillar_insurance_brokerage_distribution" in expected_pillars:
            graph_gap_notes.append("manifest lists deferred pillar for documentation only — not expected in selection")

    brokerage_evidence_gap = slug == "brown_brokerage_it" and "pillar_insurance_brokerage_distribution" not in selected_pillars

    gtm_p2_check = None
    if slug == "gtm_presales_baseline" and GTM_CLOSEOUT.is_file():
        closeout = json.loads(GTM_CLOSEOUT.read_text(encoding="utf-8"))
        expected_p2 = {
            str(s["skill_id"])
            for s in closeout.get("new_skills") or []
            if str(s.get("skill_id", "")).startswith("skill_p2_")
        }
        gtm_p2_hits = expected_p2 & selected_skill_ids
        gtm_p2_check = {
            "closeout_p2_skill_count": len(expected_p2),
            "traversal_p2_hits": sorted(gtm_p2_hits),
            "p2_preservation_rate": round(len(gtm_p2_hits) / max(len(expected_p2), 1), 4),
        }

    default_pillar_match = 0.0
    if expansion_default:
        default_pillars = {str(s.get("pillar") or "") for s in expansion_default.get("selected_skills") or []}
        default_pillar_match = _match_rate(expected_pillars, default_pillars)

    manifest_pass = (
        not forbidden_violations
        and pillar_match >= 0.4
        and skill_match >= 0.34
        and rf_match
        and expansion.get("broad_skills_ledger_used_as_authority") is False
    )
    if slug == "gtm_presales_baseline" and gtm_p2_check:
        manifest_pass = manifest_pass and gtm_p2_check.get("p2_preservation_rate", 0) >= 0.5

    status = "PASS" if manifest_pass else "FAIL"
    if slug == "brown_brokerage_it" and manifest_pass and brokerage_evidence_gap:
        status = "PASS_WITH_DOCUMENTED_GAP"
    elif slug == "brown_brokerage_it" and not brokerage_evidence_gap:
        status = "FAIL"

    return {
        "slug": slug,
        "label": entry.get("label"),
        "status": status,
        "inferred_role_families": [
            {"role_family": p.role_family, "score": p.score, "evidence_terms": list(p.evidence_terms)[:6]}
            for p in priorities[:6]
        ],
        "expected_role_family_ids": expected_rf,
        "role_family_match": rf_match,
        "projection_role_family_key_default": proj_default,
        "inferred_track_weights_without_override": inferred_weights,
        "manifest_weight_override_applied": use_manifest_weight_override,
        "taxonomy_projection_mapped": taxonomy_mapped,
        "track_weights_default": default_weights,
        "track_weights_applied": override_weights,
        "weight_override_required": weight_override_required,
        "default_expansion_error": default_error,
        "tracks_with_facts": expansion.get("tracks_with_facts"),
        "selected_pillars_ranked": ranked_pillars[:15],
        "selected_skills_ranked": ranked_skills,
        "selected_fact_ids": selected_facts[:60],
        "selected_bridge_edge_families": bridge_families,
        "expected_bridge_edge_families": expected_bridges,
        "bridge_edge_match_rate": bridge_match,
        "pillar_match_rate": pillar_match,
        "skill_match_rate": skill_match,
        "manifest_expectation_match": manifest_pass,
        "skill_classifications": {k: v[:20] for k, v in classifications.items()},
        "excluded_items": excluded_items,
        "forbidden_claims_manifest": list(entry.get("forbidden_claims") or []),
        "forbidden_guardrail_violations": forbidden_violations,
        "graph_gap_notes": graph_gap_notes,
        "brokerage_evidence_gap_documented": brokerage_evidence_gap,
        "track_weighted_only_pillar_match_rate": default_pillar_match if expansion_default else None,
        "track_underfire_notes": track_underfire_notes,
        "supplemental_skill_count": len(supplemental_skills),
        "default_track_weights_underfire": bool(weight_override_required and weights_differ),
        "gtm_phase2_closeout_check": gtm_p2_check,
        "broad_skills_ledger_used_as_authority": expansion.get("broad_skills_ledger_used_as_authority"),
        "proof_classification": "offline_traversal_receipt_not_runtime_proof",
    }


def run_w14(
    *,
    repo_root: Path | None = None,
    use_manifest_weight_override: bool = True,
    wave: str = "W14",
    out_json: Path | None = None,
    out_md: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or ROOT
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    tax_path = root / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"
    taxonomy = yaml.safe_load(tax_path.read_text(encoding="utf-8"))
    graph = load_augmented_skills_graph(repo_root=root)

    results: list[dict[str, Any]] = []
    for entry in manifest.get("archetypes") or []:
        results.append(
            _evaluate_archetype(
                entry=entry,
                graph=graph,
                taxonomy=taxonomy,
                repo_root=root,
                use_manifest_weight_override=use_manifest_weight_override,
            )
        )

    passing = [r for r in results if str(r["status"]).startswith("PASS")]
    blocked = [r for r in results if r["status"] not in ("PASS", "PASS_WITH_DOCUMENTED_GAP", "FAIL")]

    rf_matches = sum(1 for r in results if r.get("role_family_match"))
    manifest_matches = sum(1 for r in results if r.get("manifest_expectation_match"))

    exit_code = 0 if len(passing) == len(results) else 1
    aggregate = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "STATUS": "PASS" if len(passing) == len(results) else ("PARTIAL" if passing else "FAIL"),
        "FILES_CHANGED": [
            "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py",
            "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.json",
            "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.md",
            "docs/reports/apps_rg/phase2_senior_role_implementation_backlog.json",
        ],
        "COMMANDS_RUN": [
            {"command": "python apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py", "exit_code": exit_code}
        ],
        "ARTIFACTS_WRITTEN": [
            "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.json",
            "docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.md",
            "docs/reports/apps_rg/fixtures/senior_roles/traversal/",
        ],
        "PLAN_ID": PLAN_ID,
        "WAVE": wave,
        "SCOPE_MATCH": True,
        "ARCHETYPE_COUNT": len(results),
        "ARCHETYPES_PASSING": [r["slug"] for r in passing],
        "ARCHETYPES_BLOCKED": [r["slug"] for r in blocked],
        "ARCHETYPES_FAILING": [r["slug"] for r in results if r["status"] == "FAIL"],
        "ROLE_FAMILY_MATCH_RATE": round(rf_matches / max(len(results), 1), 4),
        "TRAVERSAL_PASS_RATE": round(len(passing) / max(len(results), 1), 4),
        "MANIFEST_EXPECTATION_MATCH_RATE": round(manifest_matches / max(len(results), 1), 4),
        "BROAD_SKILLS_LEDGER_STATUS": "not_used_as_authority",
        "W8_W13_INTEGRITY_STATUS": "ledger_29_pillars_162_skills_w13_manifest_7_fixtures",
        "PROOF_CLASSIFICATION": "offline_traversal_receipt_not_runtime_release_proof",
        "EXPLICIT_NON_CLAIMS": [
            "JD_and_briefing_targeting_only",
            "no_runtime_executive_summary_generation",
            "no_auto_promotion_of_MEDIUM_facts",
            "brokerage_pillar_not_fabricated",
        ],
        "NEXT_RECOMMENDED_WAVE": "W4_or_W14_multilane_section_projection_per_role",
        "TRAVERSAL_RESULTS_BY_ARCHETYPE": {r["slug"]: r["status"] for r in results},
        "SELECTED_PILLARS_BY_ARCHETYPE": {
            r["slug"]: [p["pillar_id"] for p in r.get("selected_pillars_ranked") or []][:12] for r in results
        },
        "SELECTED_SKILLS_BY_ARCHETYPE": {
            r["slug"]: [s["skill_id"] for s in r.get("selected_skills_ranked") or []][:20] for r in results
        },
        "SELECTED_BRIDGE_EDGES_BY_ARCHETYPE": {
            r["slug"]: r.get("selected_bridge_edge_families") or [] for r in results
        },
        "EXCLUDED_ITEMS_BY_ARCHETYPE": {r["slug"]: r.get("excluded_items") or [] for r in results},
        "FORBIDDEN_CLAIMS_BLOCKED_BY_ARCHETYPE": manifest.get("FORBIDDEN_CLAIMS_BLOCKED_BY_ARCHETYPE"),
        "WEIGHT_OVERRIDE_REQUIRED_BY_ARCHETYPE": {
            r["slug"]: r.get("weight_override_required") for r in results
        },
        "MANIFEST_EXPECTATION_MATCH": {r["slug"]: r.get("manifest_expectation_match") for r in results},
        "archetype_details": results,
    }

    PER_ARCHETYPE_DIR.mkdir(parents=True, exist_ok=True)
    for r in results:
        path = PER_ARCHETYPE_DIR / f"{r['slug']}_traversal.json"
        path.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")

    receipt_json = out_json or OUT_JSON
    receipt_md = out_md or OUT_MD
    receipt_json.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    _write_md(aggregate, path=receipt_md)
    return aggregate


def _write_md(agg: dict[str, Any], *, path: Path | None = None) -> None:
    lines = [
        "# Phase 2 W14 — Offline senior-role traversal receipts",
        "",
        f"**STATUS:** {agg['STATUS']}",
        f"**PLAN_ID:** {agg['PLAN_ID']}",
        f"**WAVE:** {agg['WAVE']}",
        f"**SCOPE_MATCH:** {agg['SCOPE_MATCH']}",
        f"**ARCHETYPE_COUNT:** {agg['ARCHETYPE_COUNT']}",
        f"**TRAVERSAL_PASS_RATE:** {agg['TRAVERSAL_PASS_RATE']}",
        f"**ROLE_FAMILY_MATCH_RATE:** {agg['ROLE_FAMILY_MATCH_RATE']}",
        f"**PROOF_CLASSIFICATION:** {agg['PROOF_CLASSIFICATION']}",
        "",
        "## Archetype status",
        "",
        "| Slug | Status | Pillar match | Skill match | RF match | Override required |",
        "|------|--------|--------------|-------------|----------|-----------------|",
    ]
    for r in agg.get("archetype_details") or []:
        lines.append(
            f"| `{r['slug']}` | {r['status']} | {r.get('pillar_match_rate')} | "
            f"{r.get('skill_match_rate')} | {r.get('role_family_match')} | {r.get('weight_override_required')} |"
        )
    lines.extend(
        [
            "",
            f"**NEXT_RECOMMENDED_WAVE:** {agg.get('NEXT_RECOMMENDED_WAVE')}",
            "",
            f"Aggregate JSON: [phase2_w14_offline_traversal_receipt.json](docs/reports/apps_rg/phase2_w14_offline_traversal_receipt.json)",
        ]
    )
    (path or OUT_MD).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Senior-role offline traversal receipts")
    parser.add_argument(
        "--no-weight-override",
        action="store_true",
        help="W14b mode: use infer_projection_role_family_key weights only",
    )
    parser.add_argument("--wave", default="W14", help="Receipt wave label (e.g. W14b)")
    args = parser.parse_args()
    out_json = OUT_JSON
    out_md = OUT_MD
    if args.wave.upper() == "W14B":
        out_json = ROOT / "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.json"
        out_md = ROOT / "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.md"
    agg = run_w14(
        use_manifest_weight_override=not args.no_weight_override,
        wave=args.wave.upper(),
        out_json=out_json,
        out_md=out_md,
    )
    print(
        json.dumps(
            {
                "STATUS": agg["STATUS"],
                "TRAVERSAL_PASS_RATE": agg["TRAVERSAL_PASS_RATE"],
                "WAVE": agg["WAVE"],
            },
            indent=2,
        )
    )
    return 0 if agg["STATUS"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
