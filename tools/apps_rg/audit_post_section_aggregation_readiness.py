#!/usr/bin/env python3
"""Read-only post-section aggregation readiness audit (apps_rg)."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SECTIONS = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)

METRIC_RE = re.compile(
    r"\b\d+(?:\.\d+)?%|\$\d+[\d,.]*[kmb]?|\b\d+\+?\s*(?:users|engineers|teams)\b",
    re.I,
)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"_parse_error": str(exc)}


def resolve_run_dir(section: str) -> tuple[Path | None, str | None, dict[str, Any]]:
    for bucket in ("mock", "real"):
        ptr = REPO / "artifacts/apps_rg/runtime_proofs" / section / f"latest_{bucket}_run.json"
        if not ptr.is_file():
            continue
        doc = load_json(ptr) or {}
        rel = doc.get("run_dir_repo_relative") or doc.get("run_dir")
        if not rel:
            continue
        rd = (REPO / str(rel).replace("\\", "/")).resolve()
        rel_posix = rd.relative_to(REPO).as_posix() if rd.is_relative_to(REPO) else rd.as_posix()
        if f"runtime_proofs/{section}/" not in rel_posix:
            continue
        if (rd / "l2_output.json").is_file():
            return rd, bucket, doc
    legacy = REPO / "artifacts/apps_rg/runtime_proofs" / section
    if (legacy / "l2_output.json").is_file():
        return legacy, "legacy", {}
    return None, None, {}


def x2_status(x2: dict[str, Any] | None) -> str:
    if not x2 or x2.get("_parse_error"):
        return "MISSING"
    gates = x2.get("gates")
    if isinstance(gates, list):
        return "PASS" if not [g for g in gates if not g.get("pass")] else "FAIL"
    failed = int(x2.get("x2_failed") or 0)
    if x2.get("total_x2_gates", 0) and failed == 0:
        return "PASS"
    return "FAIL" if failed else "UNKNOWN"


def collect_source_ids(l2: dict[str, Any], section: str) -> list[str]:
    ids: list[str] = []
    if section in ("headline", "executive_summary", "unify_narrative", "ibm_narrative"):
        for claim in l2.get("claim_ledger") or []:
            if isinstance(claim, dict):
                ids.extend(claim.get("source_fact_ids") or [])
    elif section in ("unify_bullets", "ibm_bullets"):
        for bullet in l2.get("bullets") or []:
            if isinstance(bullet, dict):
                ids.extend(bullet.get("source_fact_ids") or [])
        for claim in l2.get("claim_ledger") or []:
            if isinstance(claim, dict):
                ids.extend(claim.get("source_fact_ids") or [])
    elif section == "competencies":
        for claim in l2.get("claim_ledger") or []:
            if isinstance(claim, dict):
                ids.extend(claim.get("source_fact_ids") or [])
        comp = l2.get("competencies") or {}
        if isinstance(comp, dict):
            for group in comp.get("skill_groups") or []:
                if not isinstance(group, dict):
                    continue
                for item in group.get("items") or []:
                    if isinstance(item, dict):
                        ids.extend(item.get("source_fact_ids") or [])
    return [str(x).strip() for x in ids if str(x).strip()]


def primary_text(l2: dict[str, Any], section: str) -> str:
    if section == "headline":
        return str(l2.get("headline_line") or "")
    if section == "executive_summary":
        return str(l2.get("resume_display_text") or "")
    if section in ("unify_narrative", "ibm_narrative"):
        return str(l2.get("narrative_sentence") or "")
    if section in ("unify_bullets", "ibm_bullets"):
        return " | ".join(
            str(b.get("bullet_text") or "") for b in (l2.get("bullets") or []) if isinstance(b, dict)
        )
    if section == "competencies":
        parts: list[str] = []
        comp = l2.get("competencies") or {}
        if isinstance(comp, dict):
            for group in comp.get("skill_groups") or []:
                if not isinstance(group, dict):
                    continue
                for item in group.get("items") or []:
                    if isinstance(item, dict):
                        parts.append(str(item.get("text") or item.get("claim_text") or ""))
        return " | ".join(parts)
    return ""


def norm_phrase(sentence: str, n: int = 10) -> str:
    words = re.findall(r"[a-z0-9]+", sentence.lower())
    if len(words) < n:
        return ""
    return " ".join(words[:n])


def run_audit() -> dict[str, Any]:
    sections_checked: dict[str, Any] = {}
    section_artifacts: dict[str, Any] = {}
    x2_receipts: dict[str, Any] = {}
    proof_pool_digest_matrix: dict[str, Any] = {}
    all_ids_by_section: dict[str, list[str]] = {}
    texts_by_section: dict[str, str] = {}
    blockers: list[dict[str, Any]] = []
    major_gaps: list[dict[str, Any]] = []
    minor_gaps: list[dict[str, Any]] = []

    output_map = {
        "headline": "headline_output.txt",
        "executive_summary": "l2_output.resume_display_text",
        "unify_bullets": "l2_output.bullets",
        "unify_narrative": "l2_output.narrative_sentence",
        "ibm_bullets": "l2_output.bullets",
        "ibm_narrative": "l2_output.narrative_sentence",
        "competencies": "l2_output.competencies + competencies_section_output.json",
    }

    for sec in SECTIONS:
        rd, bucket, ptr = resolve_run_dir(sec)
        base_entry = {
            "run_dir": str(rd) if rd else None,
            "bucket": bucket,
            "run_id": ptr.get("run_id"),
        }
        if rd is None:
            blockers.append(
                {"code": "MISSING_RUN_DIR", "section": sec, "evidence": "no latest mock/real l2_output"}
            )
            sections_checked[sec] = base_entry
            continue

        l2_path = rd / "l2_output.json"
        usage_path = rd / "section_input_usage_ledger.json"
        receipt_path = rd / "x2_source_fact_pool_receipt.json"
        x2_path = rd / "x2_gate_outputs.json"

        usage = load_json(usage_path)
        receipt = load_json(receipt_path)
        x2 = load_json(x2_path)
        l2 = load_json(l2_path) or {}

        extra_files = [n for n in ("headline_output.txt", "executive_summary.txt", "competencies_section_output.json") if (rd / n).is_file()]

        section_artifacts[sec] = {
            "run_dir": base_entry["run_dir"],
            "bucket": bucket,
            "l2_output": l2_path.relative_to(REPO).as_posix(),
            "section_input_usage_ledger": usage_path.relative_to(REPO).as_posix() if usage_path.is_file() else None,
            "x2_source_fact_pool_receipt": receipt_path.relative_to(REPO).as_posix() if receipt_path.is_file() else None,
            "x2_gate_outputs": x2_path.relative_to(REPO).as_posix() if x2_path.is_file() else None,
            "output_artifact": output_map[sec],
            "output_files_present": extra_files,
        }

        if not usage_path.is_file():
            blockers.append({"code": "MISSING_USAGE_LEDGER", "section": sec, "path": str(usage_path)})
        if not receipt_path.is_file():
            blockers.append({"code": "MISSING_X2_RECEIPT", "section": sec, "path": str(receipt_path)})
        if not l2_path.is_file():
            blockers.append({"code": "MISSING_L2_OUTPUT", "section": sec, "path": str(l2_path)})

        digest_usage = (usage or {}).get("proof_pool_digest")
        digest_receipt = (receipt or {}).get("proof_pool_digest")
        digest_match = bool(digest_usage and digest_receipt and digest_usage == digest_receipt)
        proof_src = (usage or {}).get("proof_source")

        proof_pool_digest_matrix[sec] = {
            "proof_source_usage": proof_src,
            "proof_source_receipt": (receipt or {}).get("proof_source"),
            "proof_pool_digest_usage": digest_usage,
            "proof_pool_digest_receipt": digest_receipt,
            "digest_match": digest_match,
            "base_resume_fallback_used": (usage or {}).get("base_resume_fallback_used"),
        }
        if usage and receipt and digest_usage and digest_receipt and not digest_match:
            blockers.append(
                {
                    "code": "PROOF_POOL_DIGEST_MISMATCH",
                    "section": sec,
                    "usage_digest": digest_usage,
                    "receipt_digest": digest_receipt,
                }
            )

        receipt_stat = (receipt or {}).get("x2_source_fact_pool_status")
        if receipt_path.is_file() and receipt_stat != "PASS":
            blockers.append(
                {
                    "code": "X2_RECEIPT_FAIL",
                    "section": sec,
                    "status": receipt_stat,
                    "decisive_reason": (receipt or {}).get("decisive_reason"),
                }
            )

        gate_stat = x2_status(x2)
        if gate_stat == "FAIL":
            blockers.append({"code": "X2_GATES_FAIL", "section": sec, "path": str(x2_path)})

        non_proof = (usage or {}).get("non_proof_inputs")
        if non_proof and non_proof != ["jd_title_company", "briefing"]:
            minor_gaps.append({"code": "NON_PROOF_INPUTS_VARIANT", "section": sec, "observed": non_proof})

        ids = collect_source_ids(l2, sec)
        all_ids_by_section[sec] = ids
        texts_by_section[sec] = primary_text(l2, sec)

        if (l2.get("claim_ledger") or []) and not ids and sec != "competencies":
            blockers.append({"code": "EMPTY_SOURCE_FACT_IDS", "section": sec})

        if proof_src == "base_resume_fallback":
            minor_gaps.append(
                {
                    "code": "BASE_RESUME_FALLBACK_ACTIVE",
                    "section": sec,
                    "bucket": bucket,
                    "note": "expected only when broad_skills_ledger unavailable",
                }
            )

        x2_receipts[sec] = {
            "path": section_artifacts[sec].get("x2_source_fact_pool_receipt"),
            "x2_source_fact_pool_status": receipt_stat,
            "proof_source": (receipt or {}).get("proof_source"),
            "proof_pool_digest": digest_receipt,
            "allowed_source_fact_ids_count": (receipt or {}).get("allowed_source_fact_ids_count"),
        }

        sections_checked[sec] = {
            **base_entry,
            "proof_source": proof_src,
            "proof_pool_digest": digest_usage,
            "digest_match": digest_match,
            "x2_gate_status": gate_stat,
            "x2_receipt_status": receipt_stat,
            "source_fact_id_count": len(set(ids)),
            "runtime_generation_status": l2.get("runtime_generation_status") or ptr.get("runtime_generation_status"),
        }

    id_sections: dict[str, list[str]] = defaultdict(list)
    for sec, ids in all_ids_by_section.items():
        for fid in set(ids):
            id_sections[fid].append(sec)
    source_fact_reuse_matrix = {
        fid: {"sections": sorted(set(secs)), "section_count": len(set(secs))}
        for fid, secs in sorted(id_sections.items(), key=lambda kv: (-len(set(kv[1])), kv[0]))
    }
    overused = {fid: meta for fid, meta in source_fact_reuse_matrix.items() if meta["section_count"] >= 4}
    if overused:
        major_gaps.append(
            {
                "code": "SOURCE_FACT_ID_OVERUSE",
                "threshold": "same id in >=4 sections",
                "ids": overused,
            }
        )

    metric_hits: dict[str, list[str]] = defaultdict(list)
    for sec, text in texts_by_section.items():
        for m in set(METRIC_RE.findall(text)):
            metric_hits[m].append(sec)
    duplicate_metrics = [
        {"metric": m, "sections": sorted(set(secs))}
        for m, secs in metric_hits.items()
        if len(set(secs)) >= 3
    ]
    if duplicate_metrics:
        major_gaps.append({"code": "DUPLICATE_METRICS_CROSS_SECTION", "items": duplicate_metrics[:15]})

    phrase_hits: dict[str, list[str]] = defaultdict(list)
    for sec, text in texts_by_section.items():
        for sent in re.split(r"[.!?]+", text):
            prefix = norm_phrase(sent, 10)
            if len(prefix) > 40:
                phrase_hits[prefix].append(sec)
    phrase_overlap = [
        {"phrase_prefix": p, "sections": sorted(set(secs))}
        for p, secs in phrase_hits.items()
        if len(set(secs)) >= 3
    ][:25]
    if phrase_overlap:
        minor_gaps.append({"code": "PHRASE_OVERLAP", "items": phrase_overlap})

    def norm_ws(s: str) -> str:
        return re.sub(r"\s+", " ", s.lower().strip())

    for narr in ("unify_narrative", "ibm_narrative"):
        bullets_key = narr.replace("narrative", "bullets")
        nt = norm_ws(texts_by_section.get(narr, ""))
        bt = norm_ws(texts_by_section.get(bullets_key, ""))
        if not nt or not bt:
            continue
        for chunk in re.split(r"[.!?]+", bt):
            c = chunk.strip()
            if len(c) > 60 and c in nt:
                major_gaps.append(
                    {
                        "code": "NARRATIVE_REPEATS_BULLET_VERBATIM",
                        "narrative": narr,
                        "bullet_section": bullets_key,
                        "snippet": c[:140],
                    }
                )

    es = norm_ws(texts_by_section.get("executive_summary", ""))
    for bs in ("unify_bullets", "ibm_bullets"):
        bt = norm_ws(texts_by_section.get(bs, ""))
        if not es or not bt:
            continue
        for chunk in re.split(r"[.!?|]+", bt):
            c = chunk.strip()
            if len(c) > 55 and c in es:
                major_gaps.append(
                    {
                        "code": "EXEC_SUMMARY_OVERLAPS_BULLET",
                        "sections": ["executive_summary", bs],
                        "snippet": c[:120],
                    }
                )

    comp_t = norm_ws(texts_by_section.get("competencies", ""))
    for bs in ("unify_bullets", "ibm_bullets"):
        bt = norm_ws(texts_by_section.get(bs, ""))
        if not comp_t or not bt:
            continue
        for chunk in re.split(r"[|]+", comp_t):
            c = chunk.strip()
            if len(c) > 50 and c in bt:
                major_gaps.append(
                    {
                        "code": "COMPETENCIES_DUPLICATES_BULLET_LANGUAGE",
                        "sections": ["competencies", bs],
                        "snippet": c[:120],
                    }
                )

    rollup_path = REPO / "artifacts/apps_rg/reports/generated_lane_rollup.json"
    if not rollup_path.is_file():
        major_gaps.append(
            {
                "code": "MISSING_GENERATED_LANE_ROLLUP",
                "path": str(rollup_path.relative_to(REPO)),
                "note": "final_resume_assembler requires rollup pointers",
            }
        )

    digests = {
        sec: (proof_pool_digest_matrix.get(sec) or {}).get("proof_pool_digest_usage")
        for sec in SECTIONS
        if (proof_pool_digest_matrix.get(sec) or {}).get("proof_pool_digest_usage")
    }
    unique_digests = set(digests.values())
    if len(unique_digests) > 1:
        major_gaps.append(
            {
                "code": "CROSS_SECTION_PROOF_POOL_DIGEST_HETEROGENEITY",
                "unique_digest_count": len(unique_digests),
                "per_section_digests": digests,
                "note": (
                    "Each section resolves its own ledger slice; assembler embeds l2 snapshots "
                    "without verifying a single orchestration-scoped proof pool."
                ),
            }
        )

    l2_pool_mismatch: list[dict[str, Any]] = []
    for sec in ("unify_bullets", "ibm_bullets"):
        receipt = load_json(
            (Path(section_artifacts[sec]["run_dir"]) if section_artifacts.get(sec) else REPO)
            / "x2_source_fact_pool_receipt.json"
        )
        if receipt and receipt.get("x2_source_fact_pool_status") == "FAIL":
            l2_pool_mismatch.append(
                {
                    "section": sec,
                    "decisive_reason": receipt.get("decisive_reason"),
                    "unsupported_source_fact_ids": receipt.get("unsupported_source_fact_ids"),
                }
            )
    if l2_pool_mismatch:
        major_gaps.append(
            {
                "code": "L2_OUTPUT_IDS_OUTSIDE_ACTIVE_LEDGER_POOL",
                "sections": l2_pool_mismatch,
                "note": "Mock/stub L2 still cites legacy bul_* ids not in broad_skills_ledger allowlist",
            }
        )

    status = "PASS"
    if blockers:
        status = "FAIL"
    elif major_gaps:
        status = "PARTIAL"

    return {
        "status": status,
        "product_claim": False,
        "audit_evidence": "latest_mock_run or latest_real_run per section (artifacts/apps_rg/runtime_proofs)",
        "aggregation_code": {
            "final_resume_assembler": "apps_rg/runtime/internal/final_resume_assembler.py",
            "final_resume_x2": "apps_rg/runtime/assembly/final_resume_x2.py",
            "final_resume_manifest": "apps_rg/runtime/assembly/final_resume_manifest.py",
            "generated_lane_rollup": "apps_rg/runtime/internal/generated_lane_rollup.py",
            "orchestrate_full_resume": "apps_rg/runtime/internal/lane_batch.py",
            "resume_package_x3": "apps_rg/runtime/internal/resume_package_disposition.py",
            "modular_rg_output_builder": "apps_rg/l2_recipe/modular_rg_output_builder.py",
            "srfs_receipt_aggregator": "apps_rg/audit/srfs_receipt_aggregator.py",
        },
        "sections_checked": sections_checked,
        "section_artifacts": section_artifacts,
        "x2_receipts": x2_receipts,
        "proof_pool_digest_matrix": proof_pool_digest_matrix,
        "source_fact_reuse_matrix": dict(list(source_fact_reuse_matrix.items())[:50]),
        "duplicate_claims": [],
        "duplicate_metrics": duplicate_metrics,
        "phrase_overlap": phrase_overlap,
        "blockers": blockers,
        "major_gaps": major_gaps,
        "minor_gaps": minor_gaps,
        "recommended_next_wave": (
            "Wire final_resume_assembler preflight: require x2_source_fact_pool_receipt PASS + "
            "usage/receipt digest match per lane; add aggregate X2 gates for cross-section "
            "source_fact_id budget, narrative-vs-bullet substring anti-repeat, and metric dedup."
        ),
        "non_claims": [
            "Does not claim product ALLOW",
            "Does not rewrite outputs",
            "Does not weaken X2",
        ],
    }


def main() -> int:
    audit = run_audit()
    out_json = REPO / "docs/reports/apps_rg/apps_rg_post_section_aggregation_readiness_audit.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(audit["status"])
    print(f"blockers={len(audit['blockers'])} major={len(audit['major_gaps'])}")
    return 0 if audit["status"] == "PASS" else (1 if audit["status"] == "FAIL" else 2)


if __name__ == "__main__":
    sys.exit(main())
