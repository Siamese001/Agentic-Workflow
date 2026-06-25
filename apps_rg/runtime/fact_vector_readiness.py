"""Import-light fact-vector readiness gates for apps_rg generation.

This module is deliberately separate from C0 runtime imports. It proves the
first-principles ``fact_vectors`` index is ready before U0/C0 can consume it,
using direct Chroma SQLite metadata inspection and the bootstrap manifest.
It never embeds text and never writes Chroma rows.
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.section_authority_profile import (
    c0_authority_manifest,
    c0_section_authority_profile,
    direct_vector_section_ids,
)

BGE_M3_MODEL_ID = "BAAI/bge-m3"
EXPECTED_BGE_DIMENSION = 1024
COLLECTION_NAME = "fact_vectors"
MANIFEST_REL = "artifacts/apps_rg/c0/fact_vectors_bootstrap_manifest.json"
SPARSE_SIDE_CAR_REL = "data/cache/sparse/fact_vectors.db"

GENERATED_LANES: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)
DIRECT_VECTOR_LANES: tuple[str, ...] = direct_vector_section_ids()

SECTION_SOURCE_SLOT_MIN_COUNTS: dict[str, tuple[str, int]] = {
    "unify_bullets": ("bul_unify_", 6),
    "unify_narrative": ("bul_unify_", 6),
    "ibm_bullets": ("bul_ibm_", 5),
    "ibm_narrative": ("bul_ibm_", 5),
    "insurtech_bullets": ("bul_insurtech_", 3),
    "insurtech_narrative": ("bul_insurtech_", 3),
    "ey_bullets": ("bul_ey_", 3),
    "ey_narrative": ("bul_ey_", 3),
}

SOURCE_CLASS_ALLOWLIST = frozenset({"candidate_profile", "project_evidence"})

STATUS_PASS = "PASS"
STATUS_BLOCKED = "BLOCKED"
FALLBACK_DECISION_NOT_NEEDED = "NOT_NEEDED_STRICT_PASS"
FALLBACK_DECISION_USED_EXISTING_INDEX = "USED_EXISTING_FACT_VECTOR_INDEX"
FALLBACK_DECISION_BLOCKED = "BLOCKED_NO_SUFFICIENT_FALLBACK"

BLOCKED_PRE_U0_FACT_VECTOR_READINESS = "BLOCKED_PRE_U0_FACT_VECTOR_READINESS"
BLOCKED_POST_U0_SECTION_SUFFICIENCY = "BLOCKED_POST_U0_SECTION_SUFFICIENCY"

PRE_U0_GATE_ID = "pre_u0_fact_vector_readiness"
POST_U0_GATE_ID = "post_u0_section_sufficiency_preview"
PRE_U0_RECEIPT = "pre_u0_fact_vector_readiness.json"
POST_U0_RECEIPT = "post_u0_section_sufficiency_preview.json"

_SCHEMA = "apps_rg.fact_vector_readiness_gate.v1"


class FactVectorReadinessError(RuntimeError):
    """Raised when fact-vector readiness blocks before generation starts."""

    def __init__(self, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        block_code = str(receipt.get("block_code") or "BLOCKED_FACT_VECTOR_READINESS")
        reasons = ", ".join(str(r) for r in receipt.get("reasons") or []) or "unknown"
        super().__init__(f"{block_code}: {reasons}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return doc if isinstance(doc, dict) else {}


def _sqlite_path(*, repo_root: Path, chroma_path: str | None = None) -> Path:
    raw = str(chroma_path or "").strip()
    path = Path(raw) if raw else repo_root / "data" / "cache" / "chromadb"
    if not path.is_absolute():
        path = repo_root / path
    if path.suffix.lower() != ".sqlite3":
        path = path / "chroma.sqlite3"
    return path


def _metadata_value(row: sqlite3.Row) -> Any:
    for key in ("string_value", "int_value", "float_value", "bool_value"):
        value = row[key]
        if value is not None:
            return value
    return None


def _section_targets(meta: dict[str, Any]) -> set[str]:
    raw = str(meta.get("section_targets") or meta.get("section_type") or "")
    return {part.strip() for part in raw.split(",") if part.strip()}


def _counter_dict(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(v if v not in (None, "") else "<missing>") for v in values).items()))


def _inspect_chroma_sqlite(sqlite_path: Path) -> dict[str, Any]:
    if not sqlite_path.is_file():
        return {
            "available": False,
            "error": "chroma_sqlite_missing",
            "path": str(sqlite_path),
        }
    con = sqlite3.connect(str(sqlite_path))
    con.row_factory = sqlite3.Row
    try:
        collection = con.execute(
            "select id, name, dimension from collections where name = ?",
            (COLLECTION_NAME,),
        ).fetchone()
        if collection is None:
            return {
                "available": False,
                "error": "fact_vectors_collection_missing",
                "path": str(sqlite_path),
            }
        metadata_segment = con.execute(
            "select id from segments where collection = ? and scope = 'METADATA'",
            (collection["id"],),
        ).fetchone()
        if metadata_segment is None:
            return {
                "available": False,
                "error": "fact_vectors_metadata_segment_missing",
                "path": str(sqlite_path),
                "collection_dimension": collection["dimension"],
            }

        rows = con.execute(
            """
            select e.id as row_id,
                   e.embedding_id as embedding_id,
                   em.key as metadata_key,
                   em.string_value,
                   em.int_value,
                   em.float_value,
                   em.bool_value
              from embeddings e
              join embedding_metadata em on em.id = e.id
             where e.segment_id = ?
             order by e.id, em.key
            """,
            (metadata_segment["id"],),
        ).fetchall()
    finally:
        con.close()

    by_row: dict[int, dict[str, Any]] = {}
    embedding_ids: dict[int, str] = {}
    for row in rows:
        row_id = int(row["row_id"])
        by_row.setdefault(row_id, {})
        embedding_ids[row_id] = str(row["embedding_id"])
        by_row[row_id][str(row["metadata_key"])] = _metadata_value(row)

    metas = list(by_row.values())
    section_counts: Counter[str] = Counter()
    section_source_ids: dict[str, set[str]] = {lane: set() for lane in GENERATED_LANES}
    section_source_classes: dict[str, Counter[str]] = {lane: Counter() for lane in GENERATED_LANES}
    section_tiers: dict[str, Counter[str]] = {lane: Counter() for lane in GENERATED_LANES}
    for meta in metas:
        source_id = str(meta.get("source_document_id") or meta.get("candidate_fact_id") or "").strip()
        source_class = str(meta.get("source_class") or "<missing>")
        tier = str(meta.get("tier") or "<missing>")
        for lane in _section_targets(meta):
            if lane not in GENERATED_LANES:
                continue
            section_counts[lane] += 1
            if source_id:
                section_source_ids[lane].add(source_id)
            section_source_classes[lane][source_class] += 1
            section_tiers[lane][tier] += 1

    source_classes = [meta.get("source_class") for meta in metas]
    models = [meta.get("embedding_model_id") or meta.get("embedding_model") for meta in metas]
    dims = [meta.get("embedding_dim") or meta.get("embedding_dimension") for meta in metas]
    return {
        "available": True,
        "path": str(sqlite_path),
        "collection_name": COLLECTION_NAME,
        "collection_dimension": collection["dimension"],
        "collection_doc_count": len(by_row),
        "embedding_id_sample": [embedding_ids[k] for k in sorted(embedding_ids)[:8]],
        "model_counts": _counter_dict(models),
        "dim_counts": _counter_dict(dims),
        "source_class_counts": _counter_dict(source_classes),
        "section_counts": dict(sorted(section_counts.items())),
        "section_source_ids": {
            lane: sorted(section_source_ids[lane]) for lane in GENERATED_LANES
        },
        "section_source_class_counts": {
            lane: dict(sorted(section_source_classes[lane].items())) for lane in GENERATED_LANES
        },
        "section_tier_counts": {
            lane: dict(sorted(section_tiers[lane].items())) for lane in GENERATED_LANES
        },
    }


def _manifest_summary(*, repo_root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    path = manifest_path or repo_root / MANIFEST_REL
    doc = _read_json(path)
    required_lanes = [str(x) for x in (doc.get("required_lanes") or [])]
    missing_required = [str(x) for x in (doc.get("missing_required_lane_targets") or [])]
    per_section = doc.get("per_section_target_counts") if isinstance(doc, dict) else {}
    per_section = per_section if isinstance(per_section, dict) else {}
    locked = [str(x) for x in (doc.get("locked_deterministic_lanes") or [])]
    return {
        "path": str(path),
        "present": bool(doc),
        "schema_version": str(doc.get("schema_version") or "") if doc else "",
        "generated_at_utc": str(doc.get("generated_at_utc") or "") if doc else "",
        "source": str(doc.get("source") or "") if doc else "",
        "dry_run": bool(doc.get("dry_run")) if doc else False,
        "manifest_checksum": str(doc.get("manifest_checksum") or "") if doc else "",
        "required_lanes": required_lanes,
        "missing_required_lane_targets": missing_required,
        "locked_deterministic_lanes": locked,
        "per_section_target_counts": {str(k): int(v or 0) for k, v in per_section.items()},
        "upserted_count": int(doc.get("upserted_count") or 0) if doc else 0,
        "collection_count_after": int(doc.get("collection_count_after") or 0) if doc else 0,
        "sparse_sidecar_built": bool(doc.get("sparse_sidecar_built")) if doc else False,
    }


def _sparse_sidecar_summary(*, repo_root: Path) -> dict[str, Any]:
    path = repo_root / SPARSE_SIDE_CAR_REL
    if not path.is_file():
        return {
            "path": str(path),
            "available": False,
            "doc_count": 0,
            "error": "sparse_sidecar_missing",
        }
    try:
        con = sqlite3.connect(str(path))
        try:
            row = con.execute("select count(*) from docs").fetchone()
        finally:
            con.close()
    except sqlite3.Error as exc:
        return {
            "path": str(path),
            "available": False,
            "doc_count": 0,
            "error": f"sparse_sidecar_unreadable:{type(exc).__name__}",
        }
    doc_count = int(row[0] or 0) if row else 0
    return {
        "path": str(path),
        "available": doc_count > 0,
        "doc_count": doc_count,
        "error": "" if doc_count > 0 else "sparse_sidecar_empty",
    }


def _sections_in_scope(sections_in_scope: Any = None) -> tuple[str, ...]:
    if sections_in_scope is None:
        return GENERATED_LANES
    if isinstance(sections_in_scope, str):
        raw_sections = [sections_in_scope]
    else:
        try:
            raw_sections = list(sections_in_scope)
        except TypeError:
            raw_sections = []
    normalized = []
    for section in raw_sections:
        sid = str(section or "").strip().lower().replace("-", "_")
        if sid and sid in GENERATED_LANES and sid not in normalized:
            normalized.append(sid)
    return tuple(normalized) or GENERATED_LANES


def _row_for_section(
    *,
    section_id: str,
    chroma: dict[str, Any],
    manifest: dict[str, Any],
    model_dim_pass: bool,
    require_manifest_alignment: bool,
) -> dict[str, Any]:
    authority = c0_section_authority_profile(section_id)
    section_counts = chroma.get("section_counts") if isinstance(chroma.get("section_counts"), dict) else {}
    source_ids_by_section = (
        chroma.get("section_source_ids") if isinstance(chroma.get("section_source_ids"), dict) else {}
    )
    source_class_by_section = (
        chroma.get("section_source_class_counts")
        if isinstance(chroma.get("section_source_class_counts"), dict)
        else {}
    )
    tier_by_section = (
        chroma.get("section_tier_counts") if isinstance(chroma.get("section_tier_counts"), dict) else {}
    )
    manifest_counts = (
        manifest.get("per_section_target_counts")
        if isinstance(manifest.get("per_section_target_counts"), dict)
        else {}
    )
    source_ids = [
        str(x)
        for x in (source_ids_by_section.get(section_id) or [])
        if str(x).strip()
    ]
    source_class_counts = source_class_by_section.get(section_id) or {}
    reasons: list[str] = []
    live_count = int(section_counts.get(section_id) or 0)
    manifest_count = int(manifest_counts.get(section_id) or 0)
    unexpected_sources = sorted(
        source for source in source_class_counts if source not in SOURCE_CLASS_ALLOWLIST
    )
    direct_vector_required = bool(authority.direct_vector_proof)
    if direct_vector_required:
        if live_count <= 0:
            reasons.append("section_pre_run_fact_vector_hydration_missing")
        if require_manifest_alignment and manifest_count <= 0:
            reasons.append("section_bootstrap_manifest_coverage_missing")
        if not model_dim_pass:
            reasons.append("section_fact_vector_model_dim_not_sufficient")
        if unexpected_sources:
            reasons.append("section_source_class_not_authoritative")

    prefix, min_slots = (
        SECTION_SOURCE_SLOT_MIN_COUNTS.get(section_id, ("", 0))
        if direct_vector_required
        else ("", 0)
    )
    slot_ids = sorted({sid for sid in source_ids if prefix and sid.startswith(prefix)})
    if direct_vector_required and min_slots and len(slot_ids) < min_slots:
        reasons.append("section_expected_source_slot_coverage_missing")

    return {
        "section_id": section_id,
        "status": STATUS_PASS if not reasons else STATUS_BLOCKED,
        "reasons": reasons,
        "authority_mode": authority.authority_mode,
        "direct_vector_proof": authority.direct_vector_proof,
        "inherited_bullet_proof": authority.inherited_bullet_proof,
        "aggregate_section_proof": authority.aggregate_section_proof,
        "positioning_only": authority.positioning_only,
        "upstream_sections": list(authority.upstream_sections),
        "direct_fact_vector_required": direct_vector_required,
        "live_section_target_count": live_count,
        "manifest_section_target_count": manifest_count,
        "unique_source_document_count": len(set(source_ids)),
        "source_document_ids": source_ids,
        "section_source_class_counts": source_class_counts,
        "section_tier_counts": tier_by_section.get(section_id) or {},
        "expected_source_slot_prefix": prefix,
        "expected_source_slot_min_count": min_slots,
        "source_slot_count": len(slot_ids),
        "source_slot_ids": slot_ids,
        "model_dim_pass": model_dim_pass,
        "pre_run_hydration_present": live_count > 0,
        "source_authority_pass": not unexpected_sources,
        "delayed_loop_policy_pass": True,
        "write_authority": False,
        "comparison_authority": True,
        "same_run_write_policy": (
            "forbidden_for_product_retrieval"
            if direct_vector_required
            else "not_applicable_inherited_upstream_proof"
        ),
    }


def build_fact_vector_readiness_receipt(
    *,
    repo_root: Path | None = None,
    chroma_path: str | None = None,
    manifest_path: Path | None = None,
    gate_id: str = PRE_U0_GATE_ID,
    block_code: str = BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
    target_context: dict[str, Any] | None = None,
    require_manifest_alignment: bool = True,
    sections_in_scope: Any = None,
) -> dict[str, Any]:
    """Return a read-only readiness receipt for the pre-U0/post-U0 gates."""
    root = repo_root or _repo_root()
    section_ids = _sections_in_scope(sections_in_scope)
    direct_vector_sections = tuple(
        section_id
        for section_id in section_ids
        if c0_section_authority_profile(section_id).direct_vector_proof
    )
    direct_vector_in_scope = bool(direct_vector_sections)
    sqlite_path = _sqlite_path(repo_root=root, chroma_path=chroma_path)
    chroma = (
        _inspect_chroma_sqlite(sqlite_path)
        if direct_vector_in_scope
        else {
            "available": True,
            "skipped": True,
            "path": str(sqlite_path),
            "reason": "no_direct_fact_vector_sections_in_scope",
        }
    )
    manifest = _manifest_summary(repo_root=root, manifest_path=manifest_path)
    sparse = (
        _sparse_sidecar_summary(repo_root=root)
        if direct_vector_in_scope
        else {
            "path": str(root / SPARSE_SIDE_CAR_REL),
            "available": True,
            "skipped": True,
            "doc_count": 0,
            "reason": "no_direct_fact_vector_sections_in_scope",
        }
    )
    reasons: list[str] = []

    if direct_vector_in_scope and not chroma.get("available"):
        reasons.append(str(chroma.get("error") or "fact_vectors_unavailable"))

    collection_count = int(chroma.get("collection_doc_count") or 0)
    collection_dim = chroma.get("collection_dimension")
    model_counts = chroma.get("model_counts") if isinstance(chroma.get("model_counts"), dict) else {}
    dim_counts = chroma.get("dim_counts") if isinstance(chroma.get("dim_counts"), dict) else {}
    model_dim_pass = (
        not direct_vector_in_scope
        or (
            collection_count > 0
            and int(collection_dim or 0) == EXPECTED_BGE_DIMENSION
            and model_counts == {BGE_M3_MODEL_ID: collection_count}
            and dim_counts == {str(EXPECTED_BGE_DIMENSION): collection_count}
        )
    )
    if direct_vector_in_scope and collection_count <= 0:
        reasons.append("fact_vectors_collection_empty")
    if direct_vector_in_scope and int(collection_dim or 0) != EXPECTED_BGE_DIMENSION:
        reasons.append("fact_vectors_collection_dimension_not_1024")
    if direct_vector_in_scope and model_counts != {BGE_M3_MODEL_ID: collection_count}:
        reasons.append("fact_vectors_embedding_model_not_fully_bge_m3")
    if direct_vector_in_scope and dim_counts != {str(EXPECTED_BGE_DIMENSION): collection_count}:
        reasons.append("fact_vectors_embedding_dim_not_fully_1024")
    if direct_vector_in_scope and not sparse.get("available"):
        reasons.append(str(sparse.get("error") or "sparse_sidecar_unavailable"))

    if require_manifest_alignment and direct_vector_in_scope:
        required_lanes = set(str(x) for x in (manifest.get("required_lanes") or []))
        expected_lanes = set(direct_vector_sections)
        if not manifest.get("present"):
            reasons.append("bootstrap_manifest_missing")
        if manifest.get("dry_run"):
            reasons.append("bootstrap_manifest_is_dry_run")
        if not expected_lanes.issubset(required_lanes):
            reasons.append("bootstrap_manifest_required_lanes_not_current")
        if manifest.get("missing_required_lane_targets"):
            reasons.append("bootstrap_manifest_missing_required_lane_targets")
        locked_direct_lanes = set(str(x) for x in manifest.get("locked_deterministic_lanes") or [])
        if locked_direct_lanes & expected_lanes:
            reasons.append("bootstrap_manifest_has_locked_deterministic_lanes")

    rows = [
        _row_for_section(
            section_id=section_id,
            chroma=chroma,
            manifest=manifest,
            model_dim_pass=model_dim_pass,
            require_manifest_alignment=require_manifest_alignment,
        )
        for section_id in section_ids
    ]
    failed_sections = [
        row["section_id"] for row in rows if row.get("status") != STATUS_PASS
    ]
    if failed_sections:
        reasons.append("section_sufficiency_failed")

    status = STATUS_PASS if not reasons else STATUS_BLOCKED
    return {
        "schema_version": _SCHEMA,
        "gate_id": gate_id,
        "block_code": block_code,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "recorded_at": time.time(),
        "status": status,
        "allowed": status == STATUS_PASS,
        "reasons": reasons,
        "repo_root": str(root),
        "target_context": dict(target_context or {}),
        "policy": {
            "fact_hydration_pipeline": "source_ingestion_or_bootstrap_before_u0",
            "u0_write_authority": False,
            "c0_write_authority": False,
            "c0_comparison_authority": True,
            "generated_output_route": "staging_or_delayed_promotion_only",
            "live_write_during_c0": False,
        },
        "collection": chroma,
        "sparse_sidecar": sparse,
        "bootstrap_manifest": manifest,
        "authority_manifest": c0_authority_manifest(),
        "generated_lanes": list(GENERATED_LANES),
        "direct_vector_lanes": list(DIRECT_VECTOR_LANES),
        "sections_in_scope": list(section_ids),
        "direct_vector_lanes_in_scope": list(direct_vector_sections),
        "section_count": len(section_ids),
        "direct_vector_section_count": len(DIRECT_VECTOR_LANES),
        "direct_vector_section_count_in_scope": len(direct_vector_sections),
        "rows": rows,
        "failed_sections": failed_sections,
        "summary": {
            "collection_doc_count": collection_count,
            "collection_dimension": collection_dim,
            "model": BGE_M3_MODEL_ID,
            "expected_dim": EXPECTED_BGE_DIMENSION,
            "manifest_present": bool(manifest.get("present")),
            "sparse_sidecar_doc_count": int(sparse.get("doc_count") or 0),
            "failed_section_count": len(failed_sections),
            "direct_vector_failed_section_count": len(
                [
                    row
                    for row in rows
                    if row.get("status") != STATUS_PASS
                    and row.get("direct_fact_vector_required")
                ]
            ),
        },
    }


def build_fact_vector_readiness_with_fallback_receipt(
    *,
    repo_root: Path | None = None,
    chroma_path: str | None = None,
    manifest_path: Path | None = None,
    gate_id: str = PRE_U0_GATE_ID,
    block_code: str = BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
    target_context: dict[str, Any] | None = None,
    allow_existing_index_fallback: bool = True,
    sections_in_scope: Any = None,
) -> dict[str, Any]:
    """Build a strict receipt, then fall back to live-index sufficiency if allowed.

    Strict mode requires the canonical non-dry bootstrap manifest. The fallback
    path deliberately ignores manifest alignment but still requires the existing
    dense Chroma collection, sparse sidecar, BGE/1024 metadata, section coverage,
    and source-authority checks to pass.
    """
    strict = build_fact_vector_readiness_receipt(
        repo_root=repo_root,
        chroma_path=chroma_path,
        manifest_path=manifest_path,
        gate_id=gate_id,
        block_code=block_code,
        target_context=target_context,
        require_manifest_alignment=True,
        sections_in_scope=sections_in_scope,
    )
    if strict.get("status") == STATUS_PASS:
        strict["fallback"] = {
            "decision": FALLBACK_DECISION_NOT_NEEDED,
            "allow_existing_index_fallback": bool(allow_existing_index_fallback),
        }
        return strict
    if not allow_existing_index_fallback:
        strict["fallback"] = {
            "decision": FALLBACK_DECISION_BLOCKED,
            "allow_existing_index_fallback": False,
            "reason": "fallback_disabled",
        }
        return strict

    fallback = build_fact_vector_readiness_receipt(
        repo_root=repo_root,
        chroma_path=chroma_path,
        manifest_path=manifest_path,
        gate_id=gate_id,
        block_code=block_code,
        target_context={
            **dict(target_context or {}),
            "fallback_probe": "existing_fact_vectors_index_without_manifest_alignment",
        },
        require_manifest_alignment=False,
        sections_in_scope=sections_in_scope,
    )
    if fallback.get("status") == STATUS_PASS:
        fallback["fallback"] = {
            "decision": FALLBACK_DECISION_USED_EXISTING_INDEX,
            "allow_existing_index_fallback": True,
            "strict_status": strict.get("status"),
            "strict_reasons": list(strict.get("reasons") or []),
            "strict_failed_sections": list(strict.get("failed_sections") or []),
            "fallback_policy": (
                "live hydration/bootstrap proof is preferred; existing dense+sparse "
                "fact_vectors may be consumed only when sufficiency passes read-only."
            ),
        }
        fallback["strict_readiness_summary"] = {
            "status": strict.get("status"),
            "reasons": list(strict.get("reasons") or []),
            "failed_sections": list(strict.get("failed_sections") or []),
            "manifest_present": bool((strict.get("bootstrap_manifest") or {}).get("present")),
            "manifest_dry_run": bool((strict.get("bootstrap_manifest") or {}).get("dry_run")),
        }
        return fallback

    strict["fallback"] = {
        "decision": FALLBACK_DECISION_BLOCKED,
        "allow_existing_index_fallback": True,
        "strict_status": strict.get("status"),
        "strict_reasons": list(strict.get("reasons") or []),
        "fallback_status": fallback.get("status"),
        "fallback_reasons": list(fallback.get("reasons") or []),
        "fallback_failed_sections": list(fallback.get("failed_sections") or []),
    }
    strict["fallback_readiness_summary"] = {
        "status": fallback.get("status"),
        "reasons": list(fallback.get("reasons") or []),
        "failed_sections": list(fallback.get("failed_sections") or []),
        "collection_doc_count": (fallback.get("summary") or {}).get("collection_doc_count"),
        "sparse_sidecar_doc_count": (fallback.get("summary") or {}).get("sparse_sidecar_doc_count"),
    }
    return strict


def resolve_fact_vector_readiness_receipt_path(
    *,
    artifact_dir: str,
    gate_id: str,
    section: str = "",
) -> Path:
    ad = str(artifact_dir or "").strip()
    filename = PRE_U0_RECEIPT if gate_id == PRE_U0_GATE_ID else POST_U0_RECEIPT
    if gate_id not in {PRE_U0_GATE_ID, POST_U0_GATE_ID}:
        safe_gate = str(gate_id or "fact_vector_readiness").replace("/", "_")
        filename = f"{safe_gate}.json"
    if ad:
        out = Path(ad)
        out.mkdir(parents=True, exist_ok=True)
        return out / filename
    root = _repo_root()
    bucket = root / "artifacts" / "apps_rg" / "preflight_receipts"
    bucket.mkdir(parents=True, exist_ok=True)
    safe_section = str(section or "all").strip().replace("/", "_") or "all"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return bucket / f"{Path(filename).stem}_{safe_section}_{stamp}.json"


def write_fact_vector_readiness_receipt(path: Path, receipt: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def enforce_fact_vector_readiness(
    *,
    artifact_dir: str,
    gate_id: str,
    block_code: str,
    section: str = "",
    target_context: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    chroma_path: str | None = None,
    manifest_path: Path | None = None,
    require_manifest_alignment: bool = True,
    allow_existing_index_fallback: bool = False,
    sections_in_scope: Any = None,
) -> dict[str, Any]:
    scoped_sections = sections_in_scope
    if scoped_sections is None and section:
        scoped_sections = (section,)
    if require_manifest_alignment and allow_existing_index_fallback:
        receipt = build_fact_vector_readiness_with_fallback_receipt(
            repo_root=repo_root,
            chroma_path=chroma_path,
            manifest_path=manifest_path,
            gate_id=gate_id,
            block_code=block_code,
            target_context=target_context,
            allow_existing_index_fallback=allow_existing_index_fallback,
            sections_in_scope=scoped_sections,
        )
    else:
        receipt = build_fact_vector_readiness_receipt(
            repo_root=repo_root,
            chroma_path=chroma_path,
            manifest_path=manifest_path,
            gate_id=gate_id,
            block_code=block_code,
            target_context=target_context,
            require_manifest_alignment=require_manifest_alignment,
            sections_in_scope=scoped_sections,
        )
    receipt_path = resolve_fact_vector_readiness_receipt_path(
        artifact_dir=artifact_dir,
        gate_id=gate_id,
        section=section,
    )
    receipt["receipt_path"] = str(receipt_path)
    write_fact_vector_readiness_receipt(receipt_path, receipt)
    if receipt.get("status") != STATUS_PASS:
        raise FactVectorReadinessError(receipt)
    return receipt


__all__ = [
    "BGE_M3_MODEL_ID",
    "BLOCKED_POST_U0_SECTION_SUFFICIENCY",
    "BLOCKED_PRE_U0_FACT_VECTOR_READINESS",
    "EXPECTED_BGE_DIMENSION",
    "FactVectorReadinessError",
    "DIRECT_VECTOR_LANES",
    "GENERATED_LANES",
    "POST_U0_GATE_ID",
    "POST_U0_RECEIPT",
    "PRE_U0_GATE_ID",
    "PRE_U0_RECEIPT",
    "STATUS_BLOCKED",
    "STATUS_PASS",
    "build_fact_vector_readiness_receipt",
    "build_fact_vector_readiness_with_fallback_receipt",
    "enforce_fact_vector_readiness",
    "FALLBACK_DECISION_BLOCKED",
    "FALLBACK_DECISION_NOT_NEEDED",
    "FALLBACK_DECISION_USED_EXISTING_INDEX",
    "resolve_fact_vector_readiness_receipt_path",
    "SPARSE_SIDE_CAR_REL",
    "write_fact_vector_readiness_receipt",
]
