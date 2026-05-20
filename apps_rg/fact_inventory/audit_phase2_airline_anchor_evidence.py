"""Evidence uplift audit for skill_p2_anchor_major_airline_devops_aws — read-only search + receipt."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CLOSEOUT_SSOT = ROOT / "docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json"
OUT_JSON = ROOT / "docs/reports/apps_rg/skills_graph_phase2_airline_anchor_evidence_uplift.json"
OUT_MD = ROOT / "docs/reports/apps_rg/skills_graph_phase2_airline_anchor_evidence_uplift.md"

TARGET_SKILL = "skill_p2_anchor_major_airline_devops_aws"

SEARCH_PATHS: tuple[Path, ...] = (
    ROOT / "apps_rg/resume",
    ROOT / "artifacts/apps_rg/fact_inventory",
    ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
    ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json",
    ROOT / "docs/reports/apps_rg/exec_summary_fact_ledger_expansion_audit.json",
)

AIRLINE_RE = re.compile(
    r"\b(airline|aviation|air\s*line|travel\s+carrier|major\s+carrier|"
    r"american\s+airlines|delta\s+air|united\s+airlines|southwest|jetblue)\b",
    re.I,
)
TCV_100M_RE = re.compile(
    r"(\$100\s*M|\$100M|100\s*million|~?\s*100M\s+engagement|TCV.*100)",
    re.I,
)
QUOTA_100M_RE = re.compile(r"(presales\s+quota|carried\s+\$100M|personally\s+carried\s+\$100M)", re.I)
DEVOPS_RE = re.compile(r"\b(DevOps|CI/?CD|pipeline\s+modern)", re.I)
AWS_MOD_RE = re.compile(r"\b(AWS|cloud\s+migration|modernization)\b", re.I)

CURATED_CANDIDATES: list[dict[str, Any]] = [
    {
        "support_item": "major_airline_aviation_travel_carrier_client_context",
        "linked_fact_id": None,
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Directed large-scale regulatory IT transformations and legacy-modernization programs "
            "for major financial institutions across risk, compliance, data, cloud, and architecture domains."
        ),
        "candidate_fact_id": "fact_consulting_001",
        "confidence": "LOW",
        "supports_airline_anchor": False,
        "rationale": "Says major financial institutions — not airline/aviation/travel; wrong vertical.",
    },
    {
        "support_item": "aws_modernization_program",
        "linked_fact_id": "fact_solutions_002",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Developed industry-specific AI, analytics, and cloud modernization solutions across "
            "financial-services risk, compliance, fraud, and regulatory use cases."
        ),
        "candidate_fact_id": "fact_solutions_002",
        "confidence": "MEDIUM",
        "supports_airline_anchor": False,
        "rationale": "AWS/cloud modernization exists but financial-services vertical only; no airline client.",
    },
    {
        "support_item": "aws_modernization_program",
        "linked_fact_id": None,
        "source_path": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_quote": (
            "Cloud Infrastructure Modernization: Led migration from legacy on-prem environments to scalable "
            "cloud-native architectures, reducing infrastructure overhead by 30%..."
        ),
        "candidate_fact_id": "bul_ibm_002 / exp_ibm_001",
        "confidence": "HIGH",
        "supports_airline_anchor": False,
        "rationale": "IBM Partner delivery evidence; not airline-specific; must not conflate with anchor.",
    },
    {
        "support_item": "devops_pipeline_modernization",
        "linked_fact_id": "fact_engineering_platform_003",
        "source_path": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_quote": (
            "Governed Runtime Reliability: Strengthened enterprise retrieval quality, context assembly, "
            "evaluation gates, telemetry instrumentation, rollback controls, and AI CI/CD standards..."
        ),
        "candidate_fact_id": "bul_unify_003 / fact_engineering_platform_003",
        "confidence": "HIGH",
        "supports_airline_anchor": False,
        "rationale": "Unify platform CI/CD — not client-named airline DevOps program.",
    },
    {
        "support_item": "technical_architecture_or_solutioning_contribution",
        "linked_fact_id": None,
        "source_path": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_quote": (
            "Led architecture and commercial ownership of a $30M cloud and AI transformation portfolio, "
            "serving as systems architect for Fortune 500 financial institutions..."
        ),
        "candidate_fact_id": "exp_ibm_001",
        "confidence": "HIGH",
        "supports_airline_anchor": False,
        "rationale": "IBM $30M portfolio — explicit non-claim vs airline ~$100M anchor.",
    },
    {
        "support_item": "presales_pursuit_solution_architecture",
        "linked_fact_id": "fact_solutions_001",
        "source_path": "docs/reports/apps_rg/exec_summary_fact_ledger_expansion_audit.json",
        "source_quote": (
            "Translated complex AI, data, and cloud architecture into executive value propositions "
            "and measurable ROI for senior stakeholders."
        ),
        "candidate_fact_id": "fact_solutions_001",
        "confidence": "MEDIUM",
        "supports_airline_anchor": False,
        "rationale": "Field CTO / solutioning — no airline client or engagement named.",
    },
    {
        "support_item": "approximate_100m_engagement_scope_or_tcv",
        "linked_fact_id": None,
        "source_path": "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json",
        "source_quote": "forbidden_phrases_without_stronger_support: carried $100M presales quota",
        "candidate_fact_id": None,
        "confidence": "LOW",
        "supports_airline_anchor": False,
        "rationale": "$100M appears only as forbidden quota language — not engagement TCV proof.",
    },
    {
        "support_item": "approximate_100m_engagement_scope_or_tcv",
        "linked_fact_id": "fact_sales_accounts_002",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Closed multi-year modernization deals exceeding $15M by demonstrating ROI on HPC simulations..."
        ),
        "candidate_fact_id": "fact_sales_accounts_002",
        "confidence": "MEDIUM",
        "supports_airline_anchor": False,
        "rationale": ">$15M deals — not ~$100M; Strategic Account Executive archive; no airline.",
    },
]


def _scan_file(path: Path) -> dict[str, Any]:
    rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    if not path.is_file():
        return {"path": rel, "exists": False, "airline_hits": [], "tcv_100m_hits": [], "quota_100m_hits": []}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": rel, "exists": True, "read_error": str(exc), "airline_hits": [], "tcv_100m_hits": []}
    airline_hits: list[str] = []
    tcv_hits: list[str] = []
    quota_hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        if AIRLINE_RE.search(line):
            airline_hits.append(f"L{i}:{line.strip()[:240]}")
        if TCV_100M_RE.search(line) and not QUOTA_100M_RE.search(line):
            tcv_hits.append(f"L{i}:{line.strip()[:240]}")
        if QUOTA_100M_RE.search(line):
            quota_hits.append(f"L{i}:{line.strip()[:240]}")
    return {
        "path": rel,
        "exists": True,
        "airline_hit_count": len(airline_hits),
        "airline_hits": airline_hits[:20],
        "tcv_100m_hit_count": len(tcv_hits),
        "tcv_100m_hits": tcv_hits[:20],
        "quota_100m_hit_count": len(quota_hits),
        "quota_100m_hits": quota_hits[:20],
    }


def _skill_row_snapshot() -> dict[str, Any]:
    ledger = json.loads((ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json").read_text(encoding="utf-8"))
    row = next(r for r in ledger.get("skill_rows") or [] if r.get("skill_id") == TARGET_SKILL)
    return {
        "skill_id": TARGET_SKILL,
        "support_level": row.get("support_level"),
        "visibility_rule": row.get("visibility_rule"),
        "fact_id_links": row.get("fact_id_links"),
        "source_snippets": row.get("source_snippets"),
        "external_claim_policy": row.get("external_claim_policy"),
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 airline anchor — evidence uplift audit",
        "",
        f"**Promotion decision:** {payload['promotion_decision']}",
        f"**Proof classification:** {payload['proof_classification']}",
        f"**Generated:** {payload['generated_at_utc']}",
        "",
        "## Target skill (unchanged)",
        "",
        f"- `{TARGET_SKILL}` — {payload['skill_row_after_audit']['support_level']}, "
        f"inference_only={payload['inference_only']}",
        "",
        "## Support-item manifest",
        "",
    ]
    for item in payload["support_item_manifest"]:
        lines.append(f"### {item['support_item']}")
        lines.append(f"- **Confidence recommendation:** {item['confidence_recommendation']}")
        lines.append(f"- **Supports airline anchor:** {item['supports_airline_anchor']}")
        if item.get("best_evidence"):
            ev = item["best_evidence"]
            lines.append(f"- **Source:** [{Path(ev['source_path']).name}]({ev['source_path']})")
            lines.append(f"- **Quote:** {ev.get('source_quote', '')[:500]}")
            if ev.get("linked_fact_id"):
                lines.append(f"- **linked_fact_id:** `{ev['linked_fact_id']}`")
        else:
            lines.append("- **Best evidence:** none in repo")
        lines.append(f"- **Rationale:** {item['rationale']}")
        lines.append("")
    lines.extend(["## Explicit non-claims", ""])
    for c in payload["explicit_non_claims"]:
        lines.append(f"- {c}")
    lines.extend(["", "## Remaining gaps", ""])
    for g in payload["evidence_gaps_remaining"]:
        lines.append(f"- **{g['gap_id']}**: {g['reason']}")
    lines.extend(["", "## Next blocker", "", payload["next_blocker"]])
    return "\n".join(lines) + "\n"


def _build_support_manifest() -> list[dict[str, Any]]:
    by_item: dict[str, list[dict[str, Any]]] = {}
    for row in CURATED_CANDIDATES:
        by_item.setdefault(row["support_item"], []).append(row)
    manifest: list[dict[str, Any]] = []
    for item_id, rows in by_item.items():
        supporting = [r for r in rows if r["supports_airline_anchor"]]
        best = supporting[0] if supporting else max(rows, key=lambda r: {"HIGH": 3, "MEDIUM": 2, "LOW": 1}[r["confidence"]])
        manifest.append(
            {
                "support_item": item_id,
                "confidence_recommendation": best["confidence"] if not supporting else best["confidence"],
                "supports_airline_anchor": bool(supporting),
                "best_evidence": (
                    {
                        "source_path": best["source_path"],
                        "source_quote": best["source_quote"],
                        "linked_fact_id": best.get("linked_fact_id"),
                        "candidate_fact_id": best.get("candidate_fact_id"),
                    }
                    if best.get("source_quote")
                    else None
                ),
                "alternate_evidence": [
                    {
                        "source_path": r["source_path"],
                        "source_quote": r["source_quote"],
                        "linked_fact_id": r.get("linked_fact_id"),
                        "confidence": r["confidence"],
                        "supports_airline_anchor": r["supports_airline_anchor"],
                        "rationale": r["rationale"],
                    }
                    for r in rows
                    if r is not best
                ],
                "rationale": (
                    "No repo evidence ties this support item to a major-airline ~$100M DevOps/AWS engagement."
                    if not supporting
                    else best["rationale"]
                ),
            }
        )
    return manifest


def main() -> int:
    closeout = json.loads(CLOSEOUT_SSOT.read_text(encoding="utf-8"))
    anchor_closeout = next(
        s for s in closeout.get("new_skills") or [] if s.get("skill_id") == TARGET_SKILL
    )
    scan_results = [_scan_file(p) for p in SEARCH_PATHS]
    archive_files_on_disk = list((ROOT / "apps_rg/resume").rglob("*"))
    archive_note = (
        "Phase I resume archive filenames appear in design/candidate ledger metadata only; "
        f"no .txt/.docx Amit Ayer resume variants on disk under apps_rg/resume "
        f"({len(archive_files_on_disk)} files present — base resume JSON only)."
    )

    promotion_decision = "DO_NOT_PROMOTE"
    proof_classification = "NO_PROMOTION_INSUFFICIENT_EVIDENCE"
    next_blocker = (
        "Ingest operator-approved source naming the airline client, engagement TCV (~$100M if claimed), "
        "DevOps/AWS scope, and Amit's role (solutioning vs delivery vs portfolio owner) — then re-run this audit."
    )

    payload: dict[str, Any] = {
        "schema": "skills_graph_phase2_airline_anchor_evidence_uplift_v1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS",
        "scope": "phase2_airline_anchor_evidence_uplift_readonly",
        "closeout_ssot": str(CLOSEOUT_SSOT.relative_to(ROOT)).replace("\\", "/"),
        "target_skill_id": TARGET_SKILL,
        "skill_row_closeout_ssot": anchor_closeout,
        "skill_row_after_audit": _skill_row_snapshot(),
        "inference_only": True,
        "promotion_decision": promotion_decision,
        "proof_classification": proof_classification,
        "repo_scan": {
            "search_paths": [str(p.relative_to(ROOT)).replace("\\", "/") for p in SEARCH_PATHS],
            "file_results": scan_results,
            "archive_on_disk_note": archive_note,
            "total_airline_hits_in_scan": sum(r.get("airline_hit_count", 0) for r in scan_results),
            "total_tcv_100m_hits_excl_quota": sum(r.get("tcv_100m_hit_count", 0) for r in scan_results),
        },
        "support_item_manifest": _build_support_manifest(),
        "explicit_non_claims": [
            "No major-airline / aviation / travel-carrier client named in searchable repo sources.",
            "No ~$100M engagement TCV or program scope tied to an airline client.",
            "Do not claim personal ownership of full ~$100M engagement.",
            "IBM $30M cloud/AI transformation portfolio (exp_ibm_001) is financial-institutions scope — not airline.",
            "$100M presales quota phrases are forbidden unsupported claims — not engagement proof.",
            "Generic AWS modernization, DevOps/CI-CD, and solution-architecture evidence does not lift airline anchor.",
            "No customer-success claims added.",
        ],
        "evidence_gaps_remaining": closeout.get("evidence_gaps") or [],
        "next_blocker": next_blocker,
        "ledger_mutation": False,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    print(f"AUDIT promotion_decision={promotion_decision} airline_hits={payload['repo_scan']['total_airline_hits_in_scan']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
