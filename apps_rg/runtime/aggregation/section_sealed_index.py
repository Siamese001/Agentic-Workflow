"""Derive sealed section pointers and extended proof artifact refs from rollup lanes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS
from apps_rg.runtime.aggregation._digest_utils import (
    canonical_json_sorted,
    rel_posix,
    sha256_file,
    sha256_utf8,
)
from apps_rg.runtime.spine.section_x3_finalize import FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT

GENERATED_LANE_PROOF_FILES: tuple[str, ...] = (
    "section_input_usage_ledger.json",
    "x2_source_fact_pool_receipt.json",
    "canonical_claim_ledger_v2.json",
    "claim_ledger.json",
    "section_metric_receipt.json",
    "x2_gate_outputs.json",
    "x3_disposition.json",
    FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
    "role_episode_final_materialized_selection_contract.json",
    "l2_output.json",
)


@dataclass(frozen=True)
class SectionSealedPointer:
    lane: str
    run_id: str
    artifact_dir: str
    l2_output_ref: str
    l2_output_digest: str
    section_hash: str
    section_digest: str
    x2_gate_outputs_ref: str | None
    x3_disposition_ref: str | None
    x3_code: str
    final_materialized_acceptance_contract_ref: str | None
    final_materialized_acceptance_contract_digest: str | None
    final_materialized_acceptance_ok: bool | None
    x2_failed: int
    x2_passed: int
    pool_receipt_status: str | None
    proof_pool_ref: str | None
    proof_pool_digest: str | None
    usage_ledger_ref: str | None
    claim_ledger_ref: str | None
    canonical_claim_ledger_ref: str | None
    section_metric_receipt_ref: str | None
    jd_digest: str | None
    briefing_digest: str | None
    base_resume_digest: str | None
    prompt_hash: str | None
    generated_at_utc: str | None
    runtime_generation_status: str | None
    product_quality_status: str | None
    source_fact_id_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane,
            "run_id": self.run_id,
            "artifact_dir": self.artifact_dir,
            "l2_output_ref": self.l2_output_ref,
            "l2_output_digest": self.l2_output_digest,
            "section_hash": self.section_hash,
            "section_digest": self.section_digest,
            "x2_gate_outputs_ref": self.x2_gate_outputs_ref,
            "x3_disposition_ref": self.x3_disposition_ref,
            "x3_code": self.x3_code,
            "final_materialized_acceptance_contract_ref": self.final_materialized_acceptance_contract_ref,
            "final_materialized_acceptance_contract_digest": self.final_materialized_acceptance_contract_digest,
            "final_materialized_acceptance_ok": self.final_materialized_acceptance_ok,
            "x2_failed": self.x2_failed,
            "x2_passed": self.x2_passed,
            "pool_receipt_status": self.pool_receipt_status,
            "proof_pool_ref": self.proof_pool_ref,
            "proof_pool_digest": self.proof_pool_digest,
            "usage_ledger_ref": self.usage_ledger_ref,
            "claim_ledger_ref": self.claim_ledger_ref,
            "canonical_claim_ledger_ref": self.canonical_claim_ledger_ref,
            "section_metric_receipt_ref": self.section_metric_receipt_ref,
            "jd_digest": self.jd_digest,
            "briefing_digest": self.briefing_digest,
            "base_resume_digest": self.base_resume_digest,
            "prompt_hash": self.prompt_hash,
            "generated_at_utc": self.generated_at_utc,
            "runtime_generation_status": self.runtime_generation_status,
            "product_quality_status": self.product_quality_status,
            "source_fact_id_count": self.source_fact_id_count,
        }


def _resolved_run_dir(repo: Path, rel: str) -> Path:
    rel_norm = rel.replace("\\", "/")
    while rel_norm.startswith("./"):
        rel_norm = rel_norm[2:]
    return (repo / rel_norm).resolve()


def _optional_ref(repo: Path, run_dir: Path, name: str) -> str | None:
    p = run_dir / name
    return rel_posix(repo, p) if p.is_file() else None


def _load_json(path: Path) -> dict[str, Any]:
    blob = json.loads(path.read_text(encoding="utf-8"))
    return blob if isinstance(blob, dict) else {}


def _count_source_fact_ids(l2: dict[str, Any], claim_ledger: list[Any]) -> int:
    ids: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            if fid:
                ids.add(str(fid))
    plan = l2.get("selected_fact_plan")
    if isinstance(plan, dict):
        for k in plan:
            if str(k).startswith(("bul_", "fact_")):
                ids.add(str(k))
    return len(ids)


def build_extended_source_artifact_refs(
    repo: Path,
    *,
    run_dir: Path,
    rollup_refs: dict[str, str],
    rollup_json_rel: str,
) -> dict[str, str]:
    """Top-level proof refs for a generated lane section (W2)."""
    out: dict[str, str] = {}
    for k, v in rollup_refs.items():
        if v:
            out[str(k)] = v.replace("\\", "/")
    for name in GENERATED_LANE_PROOF_FILES:
        ref = _optional_ref(repo, run_dir, name)
        if ref:
            out[name] = ref
    usage_path = run_dir / "section_input_usage_ledger.json"
    if usage_path.is_file():
        usage = _load_json(usage_path)
        refs = usage.get("input_refs") if isinstance(usage.get("input_refs"), dict) else {}
        pp_ref = refs.get("proof_pool_ref")
        if isinstance(pp_ref, str) and pp_ref.strip():
            out["proof_pool_ref"] = pp_ref.replace("\\", "/")
        pp_dig = refs.get("proof_pool_digest")
        if isinstance(pp_dig, str) and pp_dig.strip():
            out["proof_pool_digest"] = str(pp_dig)
    out["generated_lane_rollup_json"] = rollup_json_rel.replace("\\", "/")
    return out


def build_section_sealed_index(
    *,
    repo: Path,
    rollup_blob: dict[str, Any],
    base_resume_digest: str,
) -> dict[str, Any]:
    lanes = rollup_blob.get("lanes") or {}
    pointers: list[SectionSealedPointer] = []
    index_by_lane: dict[str, dict[str, Any]] = {}

    for lane in GENERATED_LANE_IDS:
        row = lanes.get(lane)
        if not isinstance(row, dict):
            continue
        rd = row.get("latest_successful_real_artifact_path") or row.get("rollup_source_run_dir")
        if not isinstance(rd, str) or not rd.strip():
            continue
        run_dir = _resolved_run_dir(repo, rd)
        l2_path = run_dir / "l2_output.json"
        l2 = _load_json(l2_path) if l2_path.is_file() else {}
        claim_ledger = list(l2.get("claim_ledger") or [])
        section_hash = sha256_utf8(canonical_json_sorted(l2))
        section_digest = sha256_file(l2_path) if l2_path.is_file() else section_hash

        x3_path = run_dir / "x3_disposition.json"
        x3 = _load_json(x3_path) if x3_path.is_file() else {}
        x3_code = str(x3.get("x3_code") or row.get("x3_code") or "")
        final_contract_path = run_dir / FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT
        final_contract = _load_json(final_contract_path) if final_contract_path.is_file() else {}

        pool_status: str | None = None
        proof_pool_ref: str | None = None
        proof_pool_digest: str | None = None
        pool_path = run_dir / "x2_source_fact_pool_receipt.json"
        if pool_path.is_file():
            pool = _load_json(pool_path)
            pool_status = str(pool.get("x2_source_fact_pool_status") or "")
            proof_pool_ref = str(pool.get("proof_pool_ref") or "").replace("\\", "/") or None
            proof_pool_digest = str(pool.get("proof_pool_digest") or "") or None

        jd_digest: str | None = None
        briefing_digest: str | None = None
        usage_path = run_dir / "section_input_usage_ledger.json"
        if usage_path.is_file():
            usage = _load_json(usage_path)
            irefs = usage.get("input_refs") if isinstance(usage.get("input_refs"), dict) else {}
            jd_h = irefs.get("jd_text_hash")
            br_h = irefs.get("briefing_hash")
            jd_digest = str(jd_h) if jd_h else None
            briefing_digest = str(br_h) if br_h else None
            if not proof_pool_digest and irefs.get("proof_pool_digest"):
                proof_pool_digest = str(irefs.get("proof_pool_digest"))

        fr = row.get("freshness") if isinstance(row.get("freshness"), dict) else {}
        ptr = SectionSealedPointer(
            lane=lane,
            run_id=str(l2.get("run_id") or row.get("latest_successful_real_run_id") or ""),
            artifact_dir=rel_posix(repo, run_dir),
            l2_output_ref=rel_posix(repo, l2_path),
            l2_output_digest=section_digest,
            section_hash=section_hash,
            section_digest=section_digest,
            x2_gate_outputs_ref=_optional_ref(repo, run_dir, "x2_gate_outputs.json"),
            x3_disposition_ref=_optional_ref(repo, run_dir, "x3_disposition.json"),
            x3_code=x3_code,
            final_materialized_acceptance_contract_ref=_optional_ref(
                repo,
                run_dir,
                FINAL_MATERIALIZED_ACCEPTANCE_CONTRACT,
            ),
            final_materialized_acceptance_contract_digest=(
                sha256_file(final_contract_path) if final_contract_path.is_file() else None
            ),
            final_materialized_acceptance_ok=(
                final_contract.get("pass") if isinstance(final_contract, dict) else None
            ),
            x2_failed=int(row.get("x2_failed") or 0),
            x2_passed=int(row.get("x2_passed") or 0),
            pool_receipt_status=pool_status,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
            usage_ledger_ref=_optional_ref(repo, run_dir, "section_input_usage_ledger.json"),
            claim_ledger_ref=_optional_ref(repo, run_dir, "claim_ledger.json"),
            canonical_claim_ledger_ref=_optional_ref(repo, run_dir, "canonical_claim_ledger_v2.json"),
            section_metric_receipt_ref=_optional_ref(repo, run_dir, "section_metric_receipt.json"),
            jd_digest=jd_digest,
            briefing_digest=briefing_digest,
            base_resume_digest=base_resume_digest,
            prompt_hash=str(l2.get("prompt_hash") or "") or None,
            generated_at_utc=str(fr.get("generated_at_utc") or row.get("latest_successful_real_generated_at_utc") or "")
            or None,
            runtime_generation_status=str(l2.get("runtime_generation_status") or row.get("runtime_generation_status") or "")
            or None,
            product_quality_status=str(l2.get("product_quality_status") or x3.get("product_quality_status") or "")
            or None,
            source_fact_id_count=_count_source_fact_ids(l2, claim_ledger),
        )
        pointers.append(ptr)
        index_by_lane[lane] = ptr.to_dict()

    return {
        "schema": "apps_rg.section_sealed_index.v1",
        "pointers": [p.to_dict() for p in pointers],
        "index_by_lane": index_by_lane,
    }
