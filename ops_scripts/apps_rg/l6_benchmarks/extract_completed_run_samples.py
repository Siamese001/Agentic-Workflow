#!/usr/bin/env python3
"""Extract completed-run apps_rg section outputs into L6 benchmark candidate samples (offline)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from glob import glob
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _common import iter_string_fields, load_json, scan_pii, write_json_report

SECTION_GROUP_MAP: dict[str, str] = {
    "headline": "positioning",
    "executive_summary": "executive_summary",
    "competencies": "competencies",
    "unify_bullets": "bullet",
    "ibm_bullets": "bullet",
    "unify_narrative": "narrative",
    "ibm_narrative": "narrative",
}

ROLE_ANCHOR_MAP: dict[str, str] = {
    "headline": "cross_resume",
    "executive_summary": "cross_resume",
    "competencies": "cross_resume",
    "unify_bullets": "unify",
    "unify_narrative": "unify",
    "ibm_bullets": "ibm",
    "ibm_narrative": "ibm",
}

ELIGIBLE_SECTIONS = frozenset(SECTION_GROUP_MAP)

_SPLIT_THRESHOLDS = (60, 80)


def _split_bucket(benchmark_id: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:{benchmark_id}".encode()).hexdigest()
    bucket = int(digest[:8], 16) % 100
    if bucket < _SPLIT_THRESHOLDS[0]:
        return "calibration"
    if bucket < _SPLIT_THRESHOLDS[1]:
        return "validation"
    return "drift_holdout"


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _discover_run_dirs(repo_root: Path, proofs_glob: str) -> list[Path]:
    pattern = str(repo_root / proofs_glob)
    seen: set[Path] = set()
    for hit in glob(pattern, recursive=True):
        p = Path(hit)
        if p.name == "x3_disposition.json":
            seen.add(p.parent)
        elif p.name == "run_manifest.json":
            seen.add(p.parent)
    return sorted(seen)


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = load_json(path)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def _extract_section_text(section_id: str, artifact_dir: Path, l2: dict[str, Any]) -> str | None:
    if section_id == "headline":
        line = l2.get("headline_line")
        if isinstance(line, str) and line.strip():
            return line.strip()
    if section_id == "executive_summary":
        text = l2.get("resume_display_text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    if section_id in ("unify_bullets", "ibm_bullets"):
        bullets = l2.get("bullets")
        if isinstance(bullets, list):
            lines = []
            for b in bullets:
                if isinstance(b, dict):
                    bt = b.get("bullet_text")
                    if isinstance(bt, str) and bt.strip():
                        lines.append(bt.strip())
            if lines:
                return "\n".join(f"- {ln}" for ln in lines)
        out_txt = artifact_dir / f"{section_id}_output.txt"
        if out_txt.is_file():
            return out_txt.read_text(encoding="utf-8").strip() or None
    if section_id in ("unify_narrative", "ibm_narrative"):
        sent = l2.get("narrative_sentence")
        if isinstance(sent, str) and sent.strip():
            return sent.strip()
        header = l2.get("unify_header") or l2.get("ibm_header")
        if isinstance(header, dict):
            rn = header.get("role_narrative")
            if isinstance(rn, str) and rn.strip():
                return rn.strip()
        out_txt = artifact_dir / f"{section_id}_output.txt"
        if out_txt.is_file():
            return out_txt.read_text(encoding="utf-8").strip() or None
    if section_id == "competencies":
        bundle = _load_optional(artifact_dir / "competencies_section_output.json")
        if bundle and isinstance(bundle.get("display_lines"), list):
            lines = [str(x) for x in bundle["display_lines"] if str(x).strip()]
            if lines:
                return "\n".join(lines)
        comps = l2.get("competencies")
        if isinstance(comps, list):
            parts: list[str] = []
            for c in comps:
                if isinstance(c, dict):
                    label = c.get("category_label", "")
                    terms = c.get("terms") or []
                    term_texts = []
                    for t in terms:
                        if isinstance(t, dict) and t.get("text"):
                            term_texts.append(str(t["text"]))
                    if label or term_texts:
                        parts.append(f"{label}: {', '.join(term_texts)}".strip(": "))
            if parts:
                return "\n".join(parts)
    return None


def _classify_quality(x3: dict[str, Any], manifest: dict[str, Any]) -> str:
    x3_code = str(x3.get("x3_code") or "")
    pq = str(x3.get("product_quality_status") or manifest.get("product_quality_status") or "")
    if x3_code == "X3_ALLOW" and pq == "PASS":
        return "x2_pass_x3_allow"
    if pq == "PASS" and ("REVIEW" in x3_code or x3_code.startswith("X3_REVIEW")):
        return "x2_pass_x3_review"
    if x3_code == "X3_BLOCK":
        return "x2_fail_x3_block"
    if not x3_code:
        return "incomplete_or_ineligible"
    return "incomplete_or_ineligible"


def _pii_status_for_sample(sample_fields: dict[str, Any], *, manifest: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    if manifest.get("pii_status_cleared") is True or manifest.get("pii_review_cleared") is True:
        return "cleared", []
    hits: list[dict[str, str]] = []
    for _fp, text in iter_string_fields(sample_fields):
        hits.extend(scan_pii(text))
    if hits:
        return "pending_review", hits
    return "pending_review", []


def _build_input_refs(ledger: dict[str, Any] | None, artifact_dir: Path, repo_root: Path) -> dict[str, str]:
    refs: dict[str, str] = {}
    if not ledger:
        return refs
    ir = ledger.get("input_refs")
    if not isinstance(ir, dict):
        return refs
    mapping = {
        "jd_ref": "jd_text_ref",
        "briefing_ref": "briefing_ref",
        "base_resume_ledger_ref": "base_resume_ref",
        "broad_skills_ledger_ref": "broad_skills_ledger_ref",
        "selected_role_fact_set_ref": "srfs_ref",
    }
    for out_key, in_key in mapping.items():
        val = ir.get(in_key)
        if isinstance(val, str) and val.strip():
            if val.endswith(".json") or "/" in val or "\\" in val:
                refs[out_key] = val.replace("\\", "/")
            else:
                refs[out_key] = _repo_rel(artifact_dir / val, repo_root) if (artifact_dir / val).exists() else val
    if not refs.get("selected_role_fact_set_ref"):
        sfp = artifact_dir / "selected_fact_plan.json"
        if sfp.is_file():
            refs["selected_role_fact_set_ref"] = _repo_rel(sfp, repo_root)
    return refs


def _stable_benchmark_id(run_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"apps_rg_benchmark:{run_id}"))


def _try_extract_run(
    artifact_dir: Path,
    repo_root: Path,
    *,
    seed: int,
) -> tuple[dict[str, Any] | None, str | None]:
    manifest = _load_optional(artifact_dir / "run_manifest.json")
    x3 = _load_optional(artifact_dir / "x3_disposition.json")
    l2 = _load_optional(artifact_dir / "l2_output.json")
    if not manifest or not x3 or not l2:
        return None, "incomplete_artifacts"

    section_id = str(manifest.get("section_id") or l2.get("section_id") or "")
    if section_id not in ELIGIBLE_SECTIONS:
        return None, f"ineligible_section:{section_id}"

    gen_status = str(
        manifest.get("runtime_generation_status")
        or x3.get("runtime_generation_status")
        or l2.get("runtime_generation_status")
        or ""
    )
    if gen_status != "REAL_LLM":
        return None, f"not_real_llm:{gen_status}"

    if manifest.get("test_only_mock_provider") or manifest.get("test_only_mock_judges"):
        return None, "mock_only_run"

    text = _extract_section_text(section_id, artifact_dir, l2)
    if not text:
        return None, "missing_section_text"

    run_id = str(manifest.get("run_id") or artifact_dir.name)
    benchmark_id = _stable_benchmark_id(run_id)
    split = _split_bucket(benchmark_id, seed)

    ledger = _load_optional(artifact_dir / "section_input_usage_ledger.json")
    x2_pool = _load_optional(artifact_dir / "x2_source_fact_pool_receipt.json")

    sample_core = {
        "generated_section_text": text,
        "section_id": section_id,
    }
    pii_status, pii_hits = _pii_status_for_sample(sample_core, manifest=manifest)

    rel_dir = _repo_rel(artifact_dir, repo_root)
    x3_code = str(x3.get("x3_code") or "")
    pq = str(x3.get("product_quality_status") or "")
    proof_eligible = bool(manifest.get("proof_eligible")) and x3_code == "X3_ALLOW" and pq == "PASS"

    unsupported: list[str] = []
    if x2_pool and isinstance(x2_pool.get("unsupported_source_fact_ids"), list):
        unsupported = [str(x) for x in x2_pool["unsupported_source_fact_ids"]]

    job_family = "live_real_llm"
    if ledger and isinstance(ledger.get("input_refs"), dict):
        tt = ledger["input_refs"].get("target_title")
        if isinstance(tt, str) and tt.strip():
            job_family = tt.strip()[:120]

    sample: dict[str, Any] = {
        "schema_version": "1.0.0",
        "benchmark_id": benchmark_id,
        "section_id": section_id,
        "section_group": SECTION_GROUP_MAP[section_id],
        "section_tier": "P0",
        "role_anchor": ROLE_ANCHOR_MAP[section_id],
        "job_family": job_family,
        "generated_section_text": text,
        "dataset_origin": "generated",
        "pii_status": pii_status,
        "created_at": manifest.get("generated_at_utc") or datetime.now(timezone.utc).isoformat(),
        "negative_control_type": None,
        "input_refs": _build_input_refs(ledger, artifact_dir, repo_root),
        "collection_metadata": {
            "extraction_wave": "w6",
            "source_runtime_proof_path": rel_dir,
            "artifact_dir": rel_dir,
            "run_id": run_id,
            "split_assignment": split,
            "candidate_quality_status": _classify_quality(x3, manifest),
            "x2_product_quality_status": pq,
            "x2_failed_gates": list(x3.get("x2_failed_gates") or []),
            "x3_disposition": x3_code,
            "proof_eligible": proof_eligible,
            "certification_proof_eligible": proof_eligible,
            "skills_authority_source_type": (
                (ledger or {}).get("skills_authority_source_type")
                or (x2_pool or {}).get("skills_authority_source_type")
            ),
            "claim_evidence_source_type": (
                (ledger or {}).get("claim_evidence_source_type")
                or (x2_pool or {}).get("claim_evidence_source_type")
            ),
            "unsupported_source_fact_ids": unsupported,
            "runtime_generation_status": gen_status,
            "pii_scan_hits": pii_hits,
            "c0_evidence_refs": [],
            "x2_receipt_refs": [
                p
                for p in (
                    _repo_rel(artifact_dir / "x2_gate_outputs.json", repo_root),
                    _repo_rel(artifact_dir / "x2_source_fact_pool_receipt.json", repo_root),
                )
                if (artifact_dir / Path(p).name).exists()
            ],
            "x1d_judge_refs": (
                [_repo_rel(artifact_dir / "x1d_llm_judge_outputs.json", repo_root)]
                if (artifact_dir / "x1d_llm_judge_outputs.json").is_file()
                else []
            ),
        },
    }
    if ledger:
        for key in ("skills_authority_source_type", "claim_evidence_source_type"):
            val = ledger.get(key)
            if isinstance(val, str) and val:
                sample["collection_metadata"][key] = val
    if x2_pool:
        for key in ("skills_authority_source_type", "claim_evidence_source_type"):
            if key not in sample["collection_metadata"]:
                val = x2_pool.get(key)
                if isinstance(val, str) and val:
                    sample["collection_metadata"][key] = val

    return sample, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract completed-run benchmark samples.")
    parser.add_argument("--runtime-proofs-glob", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--manifest-out", required=True)
    parser.add_argument("--max-samples", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--live-proof-index",
        default="docs/reports/apps_rg/apps_rg_live_section_proof_results.json",
        help="Optional index of known REAL_LLM artifact dirs",
    )
    parser.add_argument(
        "--index-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When index file exists, extract only indexed artifact dirs (default true)",
    )
    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    out_root = repo_root / args.out_root
    collected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    candidate_dirs: list[Path] = []
    index_path = repo_root / args.live_proof_index
    if index_path.is_file():
        index = load_json(index_path)
        for row in index.get("sections", []):
            ad = row.get("artifact_dir")
            if isinstance(ad, str):
                candidate_dirs.append((repo_root / ad).resolve())

    if not (args.index_only and index_path.is_file()):
        for d in _discover_run_dirs(repo_root, args.runtime_proofs_glob):
            if d not in candidate_dirs:
                candidate_dirs.append(d)

    seen_run: set[str] = set()
    for artifact_dir in candidate_dirs:
        if len(collected) >= args.max_samples:
            break
        if not artifact_dir.is_dir():
            skipped.append({"path": str(artifact_dir), "reason": "missing_dir"})
            continue
        manifest = _load_optional(artifact_dir / "run_manifest.json")
        run_id = str((manifest or {}).get("run_id") or artifact_dir.name)
        if run_id in seen_run:
            continue
        seen_run.add(run_id)

        sample, skip_reason = _try_extract_run(artifact_dir, repo_root, seed=args.seed)
        if sample is None:
            skipped.append({"path": _repo_rel(artifact_dir, repo_root), "reason": skip_reason or "unknown"})
            continue

        split = sample["collection_metadata"]["split_assignment"]
        group = sample["section_group"]
        dest = out_root / group / split / f"{sample['benchmark_id']}.json"
        collected.append(
            {
                "benchmark_id": sample["benchmark_id"],
                "section_id": sample["section_id"],
                "section_group": group,
                "split": split,
                "dest_path": _repo_rel(dest, repo_root),
                "candidate_quality_status": sample["collection_metadata"]["candidate_quality_status"],
                "pii_status": sample["pii_status"],
                "x3_disposition": sample["collection_metadata"]["x3_disposition"],
            }
        )
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    drift_ids = [c["benchmark_id"] for c in collected if c["split"] == "drift_holdout"]
    drift_manifest = {
        "manifest_kind": "drift_holdout_w6",
        "sealed": False,
        "dry_run": args.dry_run,
        "note": "Drift holdout IDs reserved at extraction; not used for first-pass calibration.",
        "drift_holdout_benchmark_ids": drift_ids,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    drift_path = out_root / "_manifests" / "drift_holdout_manifest_w6.json"
    if not args.dry_run:
        write_json_report(drift_path, drift_manifest)

    quality_counts: dict[str, int] = {}
    pii_counts: dict[str, int] = {}
    x2x3_counts: dict[str, int] = {}
    for c in collected:
        q = c["candidate_quality_status"]
        quality_counts[q] = quality_counts.get(q, 0) + 1
        p = c["pii_status"]
        pii_counts[p] = pii_counts.get(p, 0) + 1
        x3 = c["x3_disposition"]
        x2x3_counts[x3] = x2x3_counts.get(x3, 0) + 1

    manifest_doc = {
        "tool": "extract_completed_run_samples",
        "status": "PASS" if collected else "PARTIAL",
        "dry_run": args.dry_run,
        "proof_eligible": False,
        "datasets_collected": len(collected) > 0,
        "public_datasets_ingested": False,
        "human_labels_collected": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "samples_collected_count": len(collected),
        "samples_skipped_count": len(skipped),
        "candidate_quality_status_counts": quality_counts,
        "pii_status_counts": pii_counts,
        "x2_x3_status_counts": x2x3_counts,
        "collected": collected,
        "skipped": skipped[:50],
        "drift_holdout_manifest": _repo_rel(drift_path, repo_root),
    }
    if not args.dry_run:
        write_json_report(Path(args.manifest_out), manifest_doc)
    else:
        write_json_report(Path(args.manifest_out), manifest_doc)

    return 0 if collected else 1


if __name__ == "__main__":
    sys.exit(main())
