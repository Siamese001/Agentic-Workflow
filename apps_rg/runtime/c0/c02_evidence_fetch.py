"""C0.2 — retrieve candidate fact atoms (metadata only; no graph inference)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.runtime.c0.constants import (
    CLAIM_ELIGIBLE,
    CONFIDENCE_PENDING,
    FORBIDDEN_PROOF_SOURCE_TYPES,
    NOT_PROOF,
    PROOF_ELIGIBLE,
    REPO_ROOT,
    SOURCE_LEDGER,
    SOURCE_PRIOR_VARIANT,
    SOURCE_PROOF_POOL,
    SOURCE_SRFS,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool

C02Atom = dict[str, Any]


def _manifest_path(repo_root: Path) -> Path:
    return repo_root / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json"


def _load_manifest_rows(repo_root: Path) -> list[dict[str, Any]]:
    path = _manifest_path(repo_root)
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("rows") or [])


def _ledger_by_id(repo_root: Path) -> dict[str, dict[str, Any]]:
    ledger = load_master_candidate_fact_ledger(repo_root=repo_root, path=default_ledger_path(repo_root))
    out: dict[str, dict[str, Any]] = {}
    for row in ledger.get("candidate_facts") or []:
        if isinstance(row, dict):
            fid = str(row.get("candidate_fact_id") or "").strip()
            if fid:
                out[fid] = row
    return out


def _atom_from_ledger_row(row: dict[str, Any], *, section_id: str) -> C02Atom:
    fid = str(row.get("candidate_fact_id") or "").strip()
    conf = str(row.get("confidence") or "MEDIUM").upper()
    proof = PROOF_ELIGIBLE if conf == "HIGH" else CLAIM_ELIGIBLE
    return {
        "fact_id": fid,
        "text_to_embed": str(row.get("claim_text") or "")[:2000],
        "source_type": SOURCE_LEDGER,
        "source_ref": default_ledger_path(REPO_ROOT).as_posix(),
        "source_span_ref": f"ledger:{fid}",
        "confidence": conf if conf in {"HIGH", "MEDIUM", "LOW"} else CONFIDENCE_PENDING,
        "domain_tags": [str(row.get("domain_family") or "")] if row.get("domain_family") else [],
        "skill_tags": list(row.get("capability_tags") or []),
        "metric_refs": [str(m) for m in (row.get("metric_values") or [])],
        "career_phase_refs": [],
        "graph_node_refs": [],
        "allowed_sections": [section_id],
        "blocked_sections": [],
        "proof_status": proof,
        "requires_trace_audit": conf != "HIGH",
        "retrieval_score": 1.0,
        "rejected_reason": "",
    }


def _atom_from_manifest_row(row: dict[str, Any], *, section_id: str) -> C02Atom | None:
    if not row.get("embed_allowed"):
        return None
    atom_text = str(row.get("candidate_fact_atom") or "").strip()
    if not atom_text:
        return None
    matched = row.get("matched_existing_fact_id")
    fid = str(matched) if matched else f"prior_variant:{hashlib.sha256(atom_text.encode()).hexdigest()[:16]}"
    conf = str(row.get("confidence") or CONFIDENCE_PENDING)
    return {
        "fact_id": fid,
        "text_to_embed": atom_text,
        "source_type": SOURCE_PRIOR_VARIANT,
        "source_ref": str(row.get("source_resume_variant") or ""),
        "source_span_ref": str(row.get("source_span_ref") or ""),
        "confidence": conf,
        "domain_tags": [str(row.get("variant_family") or "")],
        "skill_tags": [],
        "metric_refs": [],
        "career_phase_refs": [],
        "graph_node_refs": [],
        "allowed_sections": [section_id],
        "blocked_sections": [],
        "proof_status": str(row.get("proof_status") or CLAIM_ELIGIBLE),
        "requires_trace_audit": bool(row.get("requires_trace_audit")),
        "retrieval_score": 0.5,
        "rejected_reason": "",
    }


def _atoms_from_proof_pool(pool: SectionProofPool, *, section_id: str, ledger: dict[str, dict[str, Any]]) -> list[C02Atom]:
    atoms: list[C02Atom] = []
    plan_facts = list((pool.selected_fact_plan or {}).get("facts") or [])
    for pf in plan_facts:
        if not isinstance(pf, dict):
            continue
        fid = str(pf.get("candidate_fact_id") or pf.get("fact_id") or "").strip()
        if not fid or fid not in pool.allowed_fact_ids:
            continue
        row = ledger.get(fid) or pf
        atom = _atom_from_ledger_row(row if isinstance(row, dict) else pf, section_id=section_id)
        atom["source_type"] = SOURCE_PROOF_POOL
        atom["source_ref"] = pool.proof_pool_ref
        atoms.append(atom)
    return atoms


def fetch_c02_evidence_atoms(
    *,
    section_id: str,
    pool: SectionProofPool,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """C0.2 fetch bundle — atoms + rejected JD/generic candidates."""
    root = repo_root or REPO_ROOT
    ledger = _ledger_by_id(root)
    atoms = _atoms_from_proof_pool(pool, section_id=section_id, ledger=ledger)
    seen = {a["fact_id"] for a in atoms}
    for mrow in _load_manifest_rows(root):
        atom = _atom_from_manifest_row(mrow, section_id=section_id)
        if atom and atom["fact_id"] not in seen:
            atoms.append(atom)
            seen.add(atom["fact_id"])
    rejected: list[dict[str, str]] = []
    for st in FORBIDDEN_PROOF_SOURCE_TYPES:
        rejected.append({"source_type": st, "reason": "forbidden_as_candidate_proof"})
    return {
        "schema_version": "c02_evidence_fetch_v1",
        "section_id": section_id,
        "atoms": atoms,
        "rejected_candidates": rejected,
        "graph_inference_performed": False,
        "jd_used_as_proof": False,
        "srfs_ref": pool.srfs_ref if pool.srfs_present else "",
        "proof_pool_ref": pool.proof_pool_ref,
    }


def c02_atom_to_evidence_item(atom: C02Atom, *, timestamp_iso: str) -> Any:
    """Convert C0.2 atom to agentic_core EvidenceItem (data-only)."""
    from agentic_core.runtime.contracts.final_evidence_contract import (
        ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        EvidenceItem,
    )

    content = str(atom.get("text_to_embed") or "")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]
    return EvidenceItem(
        source=f"fact:{atom['fact_id']}",
        content=content,
        content_type="text",
        retrieval_timestamp=timestamp_iso,
        source_type=str(atom.get("source_type") or SOURCE_LEDGER),
        source_id=str(atom.get("fact_id") or ""),
        source_uri_or_ref=str(atom.get("source_span_ref") or ""),
        chunk_digest=digest,
        allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        retrieval_method="metadata",
        stratum=str(atom.get("proof_status") or ""),
        metadata_score=float(atom.get("retrieval_score") or 0.0),
    )


__all__ = [
    "C02Atom",
    "c02_atom_to_evidence_item",
    "fetch_c02_evidence_atoms",
]
