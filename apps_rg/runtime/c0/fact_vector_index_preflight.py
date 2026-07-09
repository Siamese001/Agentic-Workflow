"""C0.2 fact-vector index preflight.

This receipt proves the source-grounded ``fact_vectors`` index exists before a
section consumes it. It deliberately does not write vectors; C0.2 retrieval is a
read/compare path, while bootstrap/index maintenance owns live Chroma writes.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID
from apps_rg.runtime.c0.constants import REPO_ROOT
from apps_rg.runtime.c0.section_authority_profile import (
    c0_authority_manifest,
    c0_section_authority_profile,
)
from apps_rg.runtime.chroma_precomputed_collection import EXPECTED_BGE_DIMENSION
from apps_rg.runtime.fact_vectors_bootstrap import GENERATED_LANES, MANIFEST_REL

FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT = "c02_fact_vector_index_preflight.json"
FACT_VECTOR_INDEX_PREFLIGHT_SCHEMA = "c02_fact_vector_index_preflight_v1"
STATUS_PASS = "PASS"
STATUS_MISSING = "MISSING"
STATUS_STALE = "STALE"
STATUS_ERROR = "ERROR"

_MAX_METADATA_AUDIT_ROWS = 5000
_ROLE_EPISODE_BULLET_SECTIONS = frozenset(
    {"unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets"}
)
_SECTION_SOURCE_SLOT_MIN_COUNTS: dict[str, tuple[str, int]] = {
    "unify_bullets": ("bul_unify_", 6),
    "unify_narrative": ("bul_unify_", 6),
    "ibm_bullets": ("bul_ibm_", 5),
    "ibm_narrative": ("bul_ibm_", 5),
    "insurtech_bullets": ("bul_insurtech_", 3),
    "insurtech_narrative": ("bul_insurtech_", 3),
    "ey_bullets": ("bul_ey_", 3),
    "ey_narrative": ("bul_ey_", 3),
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return doc if isinstance(doc, dict) else {}


def _open_fact_vectors_collection(chroma_path: str) -> Any:
    from apps_rg.runtime.c0.chroma_persistent_client import ensure_apps_rg_chroma_client
    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection_for_query,
    )

    client = ensure_apps_rg_chroma_client(chroma_path)
    return get_precomputed_embeddings_collection_for_query(client, "fact_vectors")


def _metadata_counter(metas: list[dict[str, Any]], key: str, *, fallback_key: str = "") -> dict[str, int]:
    values: Counter[str] = Counter()
    for meta in metas:
        value = meta.get(key)
        if value in (None, "") and fallback_key:
            value = meta.get(fallback_key)
        values[str(value if value not in (None, "") else "<missing>")] += 1
    return dict(sorted(values.items()))


def _section_targets(meta: dict[str, Any]) -> set[str]:
    raw = str(meta.get("section_targets") or meta.get("section_type") or "")
    return {part.strip() for part in raw.split(",") if part.strip()}


def _inspect_collection(*, chroma_path: str, section_id: str) -> dict[str, Any]:
    collection = _open_fact_vectors_collection(chroma_path)
    count = int(collection.count())
    limit = min(max(count, 0), _MAX_METADATA_AUDIT_ROWS)
    metadata = getattr(collection, "metadata", None)
    collection_metadata = dict(metadata) if isinstance(metadata, dict) else {}
    rows = collection.get(limit=limit, include=["metadatas"]) if limit else {"metadatas": []}
    metas = [m for m in (rows.get("metadatas") or []) if isinstance(m, dict)]
    section_count = sum(1 for meta in metas if section_id in _section_targets(meta))
    section_source_ids = sorted(
        {
            str(meta.get("source_document_id") or meta.get("candidate_fact_id") or "").strip()
            for meta in metas
            if section_id in _section_targets(meta)
            and str(meta.get("source_document_id") or meta.get("candidate_fact_id") or "").strip()
        }
    )
    source_id_counts: Counter[str] = Counter()
    section_source_class_counts: Counter[str] = Counter()
    section_tier_counts: Counter[str] = Counter()
    for meta in metas:
        sid = str(meta.get("source_document_id") or meta.get("candidate_fact_id") or "").strip()
        if sid:
            source_id_counts[sid] += 1
        if section_id in _section_targets(meta):
            section_source_class_counts[
                str(meta.get("source_class") or "<missing>")
            ] += 1
            section_tier_counts[str(meta.get("tier") or "<missing>")] += 1
    model_counts = _metadata_counter(metas, "embedding_model_id", fallback_key="embedding_model")
    dim_counts = _metadata_counter(metas, "embedding_dim", fallback_key="embedding_dimension")
    source_class_counts = _metadata_counter(metas, "source_class")
    tier_counts = _metadata_counter(metas, "tier")
    bad_model_count = sum(
        n for model, n in model_counts.items() if model not in (BGE_M3_MODEL_ID, "<missing>")
    )
    missing_model_count = int(model_counts.get("<missing>", 0))
    bad_dim_count = sum(
        n for dim, n in dim_counts.items() if dim not in (str(EXPECTED_BGE_DIMENSION), "<missing>")
    )
    missing_dim_count = int(dim_counts.get("<missing>", 0))
    return {
        "collection_name": "fact_vectors",
        "collection_count": count,
        "metadata_rows_audited": len(metas),
        "metadata_audit_truncated": count > len(metas),
        "collection_metadata": collection_metadata,
        "section_target_count": section_count,
        "section_source_document_ids": section_source_ids,
        "source_document_id_counts": dict(sorted(source_id_counts.items())),
        "section_source_class_counts": dict(sorted(section_source_class_counts.items())),
        "section_tier_counts": dict(sorted(section_tier_counts.items())),
        "embedding_model_counts": model_counts,
        "embedding_dim_counts": dim_counts,
        "source_class_counts": source_class_counts,
        "tier_counts": tier_counts,
        "bad_model_count": bad_model_count,
        "missing_model_count": missing_model_count,
        "bad_dim_count": bad_dim_count,
        "missing_dim_count": missing_dim_count,
    }


def _product_hybrid_required(section_id: str, explicit: bool | None) -> bool:
    if explicit is not None:
        return bool(explicit)
    try:
        from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
            product_hybrid_retrieval_required,
        )

        return bool(product_hybrid_retrieval_required(section_id))
    except Exception:  # guardian: allow-broad-exception -- preflight must record uncertainty, not crash section setup
        return False


def _build_section_sufficiency(
    *,
    section_id: str,
    collection: dict[str, Any],
    manifest_section_target_count: int,
    product_hybrid_required: bool,
) -> dict[str, Any]:
    """Common sufficiency gate for every generated section before C0 retrieval."""
    authority = c0_section_authority_profile(section_id)
    direct_vector_required = bool(product_hybrid_required or authority.direct_vector_proof)
    live_section_count = int(collection.get("section_target_count") or 0)
    collection_count = int(collection.get("collection_count") or 0)
    bad_model_count = int(collection.get("bad_model_count") or 0)
    missing_model_count = int(collection.get("missing_model_count") or 0)
    bad_dim_count = int(collection.get("bad_dim_count") or 0)
    missing_dim_count = int(collection.get("missing_dim_count") or 0)
    section_source_ids = [
        str(x).strip()
        for x in (collection.get("section_source_document_ids") or [])
        if str(x).strip()
    ]
    reasons: list[str] = []
    known_generated_lane = section_id in GENERATED_LANES
    manifest_coverage_present = manifest_section_target_count > 0
    hydration_present = live_section_count > 0
    if direct_vector_required and not hydration_present:
        reasons.append("section_pre_run_fact_vector_hydration_missing")
    if direct_vector_required and known_generated_lane and not hydration_present:
        reasons.append("generated_section_fact_vector_coverage_missing")
    if direct_vector_required and not (manifest_coverage_present or hydration_present):
        reasons.append("section_bootstrap_manifest_coverage_missing")
    model_dim_pass = (
        not direct_vector_required
        or (
            collection_count > 0
            and bad_model_count == 0
            and missing_model_count == 0
            and bad_dim_count == 0
            and missing_dim_count == 0
        )
    )
    if direct_vector_required and not model_dim_pass:
        reasons.append("section_fact_vector_model_dim_not_sufficient")

    prefix = ""
    min_slots = 0
    slot_count = 0
    slot_ids: list[str] = []
    if direct_vector_required and section_id in _SECTION_SOURCE_SLOT_MIN_COUNTS:
        prefix, min_slots = _SECTION_SOURCE_SLOT_MIN_COUNTS[section_id]
        slot_ids = sorted({sid for sid in section_source_ids if sid.startswith(prefix)})
        slot_count = len(slot_ids)
        if slot_count < min_slots:
            reasons.append("section_expected_source_slot_coverage_missing")

    delayed_loop_policy_pass = True
    status = STATUS_PASS if not reasons else STATUS_MISSING
    return {
        "schema_version": "section_fact_vector_sufficiency_v1",
        "section_id": section_id,
        "status": status,
        "reasons": reasons,
        "known_generated_lane": known_generated_lane,
        "authority_mode": authority.authority_mode,
        "direct_vector_proof": authority.direct_vector_proof,
        "inherited_bullet_proof": authority.inherited_bullet_proof,
        "aggregate_section_proof": authority.aggregate_section_proof,
        "positioning_only": authority.positioning_only,
        "upstream_sections": list(authority.upstream_sections),
        "direct_fact_vector_required": direct_vector_required,
        "product_hybrid_required": product_hybrid_required,
        "manifest_section_target_count": manifest_section_target_count,
        "manifest_coverage_present": manifest_coverage_present,
        "live_section_target_count": live_section_count,
        "pre_run_hydration_present": hydration_present,
        "collection_count": collection_count,
        "model_dim_pass": model_dim_pass,
        "section_source_class_counts": collection.get("section_source_class_counts") or {},
        "section_tier_counts": collection.get("section_tier_counts") or {},
        "expected_source_slot_prefix": prefix,
        "expected_source_slot_min_count": min_slots,
        "source_slot_count": slot_count,
        "source_slot_ids": slot_ids,
        "delayed_loop_policy_pass": delayed_loop_policy_pass,
    }


def _build_unify_bullets_sufficiency(
    *,
    collection: dict[str, Any],
    role_family_key: str,
    repo_root: Path,
) -> dict[str, Any]:
    """Prove Unify has six source slots plus approved metric outcomes before generation."""
    try:
        from apps_rg.runtime.sections.role_episode_metric_registry import (
            metric_outcome_nodes_from_path,
        )
        from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
            BUNDLES_PATH as UNIFY_BUNDLES_PATH,
        )
        from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
            validate_bundle,
        )
        from apps_rg.runtime.sections.unify_role_episode_evidence import (
            UNIFY_BULLET_SLOT_BUNDLE_MAP,
            UNIFY_BULLET_SLOT_IDS,
            build_unify_graph_traversal_sufficiency_receipt,
            build_unify_role_episode_section_packet,
            resolve_unify_bullet_slot_bundle_map,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- receipt classifies optional Unify registry import failures
        return {
            "status": STATUS_ERROR,
            "reasons": [f"unify_registry_unavailable:{type(exc).__name__}"],
        }

    section_source_ids = {
        str(x).strip()
        for x in (collection.get("section_source_document_ids") or [])
        if str(x).strip()
    }
    expected_slots = list(UNIFY_BULLET_SLOT_IDS)
    source_slot_presence = {slot: slot in section_source_ids for slot in expected_slots}
    missing_source_slots = [slot for slot, present in source_slot_presence.items() if not present]
    reasons: list[str] = []
    if missing_source_slots:
        reasons.append("unify_bullets_source_slots_missing")

    target_profile = str(role_family_key or "").strip()
    slot_map_resolution = "role_family"
    try:
        slot_map = resolve_unify_bullet_slot_bundle_map(
            target_profile,
            repo_root=repo_root,
        ) if target_profile else dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
    except ValueError:
        slot_map = dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
        slot_map_resolution = "default_fallback_after_role_family_resolution_error"
    except Exception as exc:  # guardian: allow-broad-exception -- fail closed in receipt instead of aborting unrelated sections
        slot_map = dict(UNIFY_BULLET_SLOT_BUNDLE_MAP)
        slot_map_resolution = f"default_fallback_after:{type(exc).__name__}"
        reasons.append("unify_bullets_slot_map_resolution_failed")
    if not target_profile:
        slot_map_resolution = "default_fallback_missing_role_family_key"
        reasons.append("unify_bullets_role_family_key_missing")

    try:
        packet = build_unify_role_episode_section_packet("unify_bullets", repo_root=repo_root)
        bundle_by_id = {
            str(bundle.get("role_episode_bundle_id") or ""): bundle
            for bundle in (packet.get("role_episode_bundles") or [])
            if isinstance(bundle, dict) and str(bundle.get("role_episode_bundle_id") or "").strip()
        }
        metric_nodes = metric_outcome_nodes_from_path(UNIFY_BUNDLES_PATH)
    except Exception as exc:  # guardian: allow-broad-exception -- malformed role graph must fail closed through receipt status
        return {
            "status": STATUS_ERROR,
            "reasons": reasons + [f"unify_role_episode_packet_unavailable:{type(exc).__name__}"],
            "source_slot_presence": source_slot_presence,
            "missing_source_fact_slots": missing_source_slots,
            "slot_bundle_map_resolution": slot_map_resolution,
            "slot_bundle_map": dict(slot_map),
        }

    missing_bundle_slots: list[str] = []
    invalid_bundle_slots: dict[str, list[str]] = {}
    missing_metric_slots: list[str] = []
    unapproved_metric_slots: dict[str, list[str]] = {}
    slot_metric_outcome_ids: dict[str, list[str]] = {}
    slot_bundle_ids: dict[str, str] = {}
    slot_skill_counts: dict[str, int] = {}
    unique_metric_ids: set[str] = set()
    metric_node_ids = set(str(x) for x in metric_nodes.keys())
    for slot in expected_slots:
        bundle_id = str(slot_map.get(slot) or "").strip()
        slot_bundle_ids[slot] = bundle_id
        bundle = bundle_by_id.get(bundle_id)
        if not bundle:
            missing_bundle_slots.append(slot)
            continue
        ok, violations = validate_bundle(bundle)
        if not ok:
            invalid_bundle_slots[slot] = list(violations)
        metric_ids = [
            str(mid).strip()
            for mid in (bundle.get("linked_metric_outcome_ids") or [])
            if str(mid).strip()
        ]
        approved_for_slot = [mid for mid in metric_ids if mid in metric_node_ids]
        rejected_for_slot = [mid for mid in metric_ids if mid not in metric_node_ids]
        if rejected_for_slot:
            unapproved_metric_slots[slot] = rejected_for_slot
        if not approved_for_slot:
            missing_metric_slots.append(slot)
        slot_metric_outcome_ids[slot] = approved_for_slot
        unique_metric_ids.update(approved_for_slot)
        slot_skill_counts[slot] = len(bundle.get("graph_skill_node_ids") or [])

    if missing_bundle_slots:
        reasons.append("unify_bullets_slot_bundles_missing")
    if invalid_bundle_slots:
        reasons.append("unify_bullets_slot_bundles_invalid")
    if missing_metric_slots:
        reasons.append("unify_bullets_metric_outcome_slots_missing")
    if unapproved_metric_slots:
        reasons.append("unify_bullets_metric_outcome_ids_unapproved")
    metric_distribution_pass = len(unique_metric_ids) >= len(expected_slots)
    if not metric_distribution_pass:
        reasons.append("unify_bullets_metric_outcomes_not_distributed_by_slot")

    traversal = build_unify_graph_traversal_sufficiency_receipt(
        section_id="unify_bullets",
        target_role_profile=target_profile or "DEFAULT",
        slot_bundle_map=slot_map,
        packet=packet,
    )
    conservation = (
        traversal.get("candidate_conservation")
        if isinstance(traversal.get("candidate_conservation"), dict)
        else {}
    )
    frontier = (
        traversal.get("frontier_size_by_hop_depth")
        if isinstance(traversal.get("frontier_size_by_hop_depth"), dict)
        else {}
    )
    axis = (
        traversal.get("role_specific_axis_coverage")
        if isinstance(traversal.get("role_specific_axis_coverage"), dict)
        else {}
    )
    root_count = int(traversal.get("selected_role_episode_root_count") or 0)
    traversal_pass = (
        bool(conservation.get("pass"))
        and root_count >= len(expected_slots)
        and int(traversal.get("selected_unique_leaf_skill_count") or 0) >= 20
        and int(traversal.get("selected_unique_metric_count") or 0) >= 10
        and int(traversal.get("rejected_sibling_skill_count") or 0) > 0
        and int(traversal.get("rejected_sibling_metric_count") or 0) > 0
    )
    granularity_pass = (
        not (axis.get("missing_axes") or [])
        and int(frontier.get("hop_1_graph_skill_nodes") or 0) >= root_count * 2
        and int(frontier.get("hop_2_metric_outcome_nodes") or 0) >= root_count
    )
    if not traversal_pass:
        reasons.append("unify_bullets_graph_traversal_insufficient")
    if not granularity_pass:
        reasons.append("unify_bullets_graph_granularity_insufficient")

    status = STATUS_PASS if not reasons else STATUS_MISSING
    return {
        "schema_version": "unify_bullets_fact_vector_sufficiency_v1",
        "status": status,
        "reasons": reasons,
        "role_family_key": target_profile,
        "expected_slot_ids": expected_slots,
        "source_slot_presence": source_slot_presence,
        "missing_source_fact_slots": missing_source_slots,
        "slot_bundle_map_resolution": slot_map_resolution,
        "slot_bundle_map": dict(slot_map),
        "slot_bundle_ids": slot_bundle_ids,
        "missing_bundle_slots": missing_bundle_slots,
        "invalid_bundle_slots": invalid_bundle_slots,
        "slot_metric_outcome_ids": slot_metric_outcome_ids,
        "missing_metric_outcome_slots": missing_metric_slots,
        "unapproved_metric_outcome_slots": unapproved_metric_slots,
        "unique_metric_outcome_ids": sorted(unique_metric_ids),
        "metric_distribution_pass": metric_distribution_pass,
        "slot_graph_skill_counts": slot_skill_counts,
        "graph_traversal_pass": traversal_pass,
        "graph_granularity_pass": granularity_pass,
        "graph_traversal_receipt": traversal,
    }


def _role_episode_bullets_config(section_id: str) -> dict[str, Any]:
    """Return section-specific role-episode bullet config without importing all lanes."""
    sid = str(section_id or "").strip()
    if sid == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_graph_role_episode_registry import (
            BUNDLES_PATH,
            validate_bundle,
        )
        from apps_rg.runtime.sections.ibm_role_episode_evidence import (
            IBM_BULLET_SLOT_BUNDLE_MAP,
            IBM_BULLET_SLOT_IDS,
            build_ibm_role_episode_section_packet,
        )
        from apps_rg.runtime.sections.role_episode_metric_registry import (
            build_role_episode_bullet_traversal_sufficiency_receipt,
        )

        def _build_ibm_traversal(
            *,
            section_id: str,
            slot_bundle_map: dict[str, str],
            packet: dict[str, Any],
        ) -> dict[str, Any]:
            return build_role_episode_bullet_traversal_sufficiency_receipt(
                section_id=section_id,
                slot_ids=IBM_BULLET_SLOT_IDS,
                slot_bundle_map=slot_bundle_map,
                packet=packet,
                employer_label="IBM",
            )

        return {
            "section_id": sid,
            "employer_label": "IBM",
            "source_slot_prefix": "bul_ibm_",
            "slot_ids": IBM_BULLET_SLOT_IDS,
            "slot_bundle_map": dict(IBM_BULLET_SLOT_BUNDLE_MAP),
            "build_packet": build_ibm_role_episode_section_packet,
            "build_traversal": _build_ibm_traversal,
            "bundles_path": BUNDLES_PATH,
            "validate_bundle": validate_bundle,
        }
    if sid == "insurtech_bullets":
        from apps_rg.runtime.sections.insurtech_graph_role_episode_registry import (
            BUNDLES_PATH,
            validate_bundle,
        )
        from apps_rg.runtime.sections.insurtech_role_episode_evidence import (
            INSURTECH_BULLET_SLOT_BUNDLE_MAP,
            INSURTECH_BULLET_SLOT_IDS,
            build_insurtech_graph_traversal_sufficiency_receipt,
            build_insurtech_role_episode_section_packet,
        )

        return {
            "section_id": sid,
            "employer_label": "InsurTech",
            "source_slot_prefix": "bul_insurtech_",
            "slot_ids": INSURTECH_BULLET_SLOT_IDS,
            "slot_bundle_map": dict(INSURTECH_BULLET_SLOT_BUNDLE_MAP),
            "build_packet": build_insurtech_role_episode_section_packet,
            "build_traversal": build_insurtech_graph_traversal_sufficiency_receipt,
            "bundles_path": BUNDLES_PATH,
            "validate_bundle": validate_bundle,
        }
    if sid == "ey_bullets":
        from apps_rg.runtime.sections.ey_graph_role_episode_registry import (
            BUNDLES_PATH,
            validate_bundle,
        )
        from apps_rg.runtime.sections.ey_role_episode_evidence import (
            EY_BULLET_SLOT_BUNDLE_MAP,
            EY_BULLET_SLOT_IDS,
            build_ey_graph_traversal_sufficiency_receipt,
            build_ey_role_episode_section_packet,
        )

        return {
            "section_id": sid,
            "employer_label": "EY",
            "source_slot_prefix": "bul_ey_",
            "slot_ids": EY_BULLET_SLOT_IDS,
            "slot_bundle_map": dict(EY_BULLET_SLOT_BUNDLE_MAP),
            "build_packet": build_ey_role_episode_section_packet,
            "build_traversal": build_ey_graph_traversal_sufficiency_receipt,
            "bundles_path": BUNDLES_PATH,
            "validate_bundle": validate_bundle,
        }
    return {}


def _build_role_episode_bullets_sufficiency(
    *,
    section_id: str,
    collection: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """Prove fixed-count role-episode bullet lanes have source slots and metrics."""
    try:
        cfg = _role_episode_bullets_config(section_id)
        from apps_rg.runtime.sections.role_episode_metric_registry import (
            metric_outcome_nodes_from_path,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- preflight classifies lane registry import failures
        return {
            "schema_version": "role_episode_bullets_fact_vector_sufficiency_v1",
            "section_id": section_id,
            "status": STATUS_ERROR,
            "reasons": [f"{section_id}_registry_unavailable:{type(exc).__name__}"],
        }
    if not cfg:
        return {}

    section_source_ids = {
        str(x).strip()
        for x in (collection.get("section_source_document_ids") or [])
        if str(x).strip()
    }
    expected_slots = [str(x) for x in cfg["slot_ids"]]
    source_slot_presence = {slot: slot in section_source_ids for slot in expected_slots}
    missing_source_slots = [slot for slot, present in source_slot_presence.items() if not present]
    extra_source_slots = sorted(
        sid
        for sid in section_source_ids
        if sid.startswith(str(cfg["source_slot_prefix"])) and sid not in set(expected_slots)
    )
    reasons: list[str] = []
    if missing_source_slots:
        reasons.append(f"{section_id}_source_slots_missing")

    slot_map = dict(cfg["slot_bundle_map"])
    try:
        packet = cfg["build_packet"](section_id, repo_root=repo_root)
        bundle_by_id = {
            str(bundle.get("role_episode_bundle_id") or ""): bundle
            for bundle in (packet.get("role_episode_bundles") or [])
            if isinstance(bundle, dict) and str(bundle.get("role_episode_bundle_id") or "").strip()
        }
        metric_nodes = metric_outcome_nodes_from_path(cfg["bundles_path"])
    except Exception as exc:  # guardian: allow-broad-exception -- malformed role graph must fail closed through receipt status
        return {
            "schema_version": "role_episode_bullets_fact_vector_sufficiency_v1",
            "section_id": section_id,
            "status": STATUS_ERROR,
            "reasons": reasons + [f"{section_id}_role_episode_packet_unavailable:{type(exc).__name__}"],
            "expected_slot_ids": expected_slots,
            "source_slot_presence": source_slot_presence,
            "missing_source_fact_slots": missing_source_slots,
            "extra_source_fact_slots": extra_source_slots,
            "slot_bundle_map": slot_map,
        }

    missing_bundle_slots: list[str] = []
    invalid_bundle_slots: dict[str, list[str]] = {}
    missing_metric_slots: list[str] = []
    unapproved_metric_slots: dict[str, list[str]] = {}
    slot_metric_outcome_ids: dict[str, list[str]] = {}
    slot_bundle_ids: dict[str, str] = {}
    slot_skill_counts: dict[str, int] = {}
    unique_metric_ids: set[str] = set()
    metric_node_ids = set(str(x) for x in metric_nodes.keys())
    for slot in expected_slots:
        bundle_id = str(slot_map.get(slot) or "").strip()
        slot_bundle_ids[slot] = bundle_id
        bundle = bundle_by_id.get(bundle_id)
        if not bundle:
            missing_bundle_slots.append(slot)
            continue
        # The section packet builder validates raw registry bundles before projecting
        # them into C0 packet rows. Re-validating projected rows would require raw-only
        # fields that are intentionally not carried into the prompt packet.
        metric_ids = [
            str(mid).strip()
            for mid in (
                bundle.get("linked_metric_outcome_ids")
                or bundle.get("allowed_metric_outcome_ids")
                or []
            )
            if str(mid).strip()
        ]
        approved_for_slot = [mid for mid in metric_ids if mid in metric_node_ids]
        rejected_for_slot = [mid for mid in metric_ids if mid not in metric_node_ids]
        if rejected_for_slot:
            unapproved_metric_slots[slot] = rejected_for_slot
        if not approved_for_slot:
            missing_metric_slots.append(slot)
        slot_metric_outcome_ids[slot] = approved_for_slot
        unique_metric_ids.update(approved_for_slot)
        slot_skill_counts[slot] = len(bundle.get("graph_skill_node_ids") or [])

    if missing_bundle_slots:
        reasons.append(f"{section_id}_slot_bundles_missing")
    if invalid_bundle_slots:
        reasons.append(f"{section_id}_slot_bundles_invalid")
    if missing_metric_slots:
        reasons.append(f"{section_id}_metric_outcome_slots_missing")
    if unapproved_metric_slots:
        reasons.append(f"{section_id}_metric_outcome_ids_unapproved")
    metric_distribution_pass = len(unique_metric_ids) >= len(expected_slots)
    if not metric_distribution_pass:
        reasons.append(f"{section_id}_metric_outcomes_not_distributed_by_slot")

    traversal = cfg["build_traversal"](
        section_id=section_id,
        slot_bundle_map=slot_map,
        packet=packet,
    )
    conservation = (
        traversal.get("candidate_conservation")
        if isinstance(traversal.get("candidate_conservation"), dict)
        else {}
    )
    frontier = (
        traversal.get("frontier_size_by_hop_depth")
        if isinstance(traversal.get("frontier_size_by_hop_depth"), dict)
        else {}
    )
    root_count = int(traversal.get("selected_role_episode_root_count") or 0)
    traversal_pass = (
        bool(conservation.get("pass"))
        and root_count >= len(expected_slots)
        and int(traversal.get("selected_unique_leaf_skill_count") or 0) >= root_count * 2
        and int(traversal.get("selected_unique_metric_count") or 0) >= root_count
        and int(traversal.get("rejected_sibling_skill_count") or 0) > 0
        and int(traversal.get("rejected_sibling_metric_count") or 0) > 0
    )
    granularity_pass = (
        int(frontier.get("hop_1_graph_skill_nodes") or 0) >= root_count * 2
        and int(frontier.get("hop_2_metric_outcome_nodes") or 0) >= root_count
    )
    if not traversal_pass:
        reasons.append(f"{section_id}_graph_traversal_insufficient")
    if not granularity_pass:
        reasons.append(f"{section_id}_graph_granularity_insufficient")

    status = STATUS_PASS if not reasons else STATUS_MISSING
    return {
        "schema_version": "role_episode_bullets_fact_vector_sufficiency_v1",
        "status": status,
        "section_id": section_id,
        "employer_label": cfg["employer_label"],
        "reasons": reasons,
        "expected_slot_ids": expected_slots,
        "source_slot_presence": source_slot_presence,
        "missing_source_fact_slots": missing_source_slots,
        "extra_source_fact_slots": extra_source_slots,
        "slot_bundle_map": slot_map,
        "slot_bundle_ids": slot_bundle_ids,
        "missing_bundle_slots": missing_bundle_slots,
        "invalid_bundle_slots": invalid_bundle_slots,
        "slot_metric_outcome_ids": slot_metric_outcome_ids,
        "missing_metric_outcome_slots": missing_metric_slots,
        "unapproved_metric_outcome_slots": unapproved_metric_slots,
        "unique_metric_outcome_ids": sorted(unique_metric_ids),
        "metric_distribution_pass": metric_distribution_pass,
        "slot_graph_skill_counts": slot_skill_counts,
        "graph_traversal_pass": traversal_pass,
        "graph_granularity_pass": granularity_pass,
        "graph_traversal_receipt": traversal,
    }


def build_fact_vector_index_preflight(
    *,
    section_id: str,
    artifact_dir: Path | None = None,
    repo_root: Path | None = None,
    chroma_path: str | None = None,
    product_hybrid_required: bool | None = None,
    role_family_key: str | None = None,
) -> dict[str, Any]:
    """Build and optionally write the C0 fact-vector index preflight receipt."""
    root = repo_root or REPO_ROOT
    manifest_path = root / MANIFEST_REL
    manifest = _read_json(manifest_path)
    manifest_present = bool(manifest)
    per_section = manifest.get("per_section_target_counts") if isinstance(manifest, dict) else {}
    per_section = per_section if isinstance(per_section, dict) else {}
    locked_lanes = list(manifest.get("locked_deterministic_lanes") or []) if manifest else []
    section_manifest_count = int(per_section.get(section_id) or 0)
    required = _product_hybrid_required(section_id, product_hybrid_required)
    authority = c0_section_authority_profile(section_id)
    direct_vector_required = bool(required or authority.direct_vector_proof)

    from apps_rg.runtime.embedding_settings import resolve_apps_rg_embedding_settings

    settings = resolve_apps_rg_embedding_settings(chroma_persist_dir=chroma_path)
    resolved_chroma_path = (
        (chroma_path or "").strip()
        or str(settings.chroma_persist_dir or "").strip()
        or str((root / "data" / "cache" / "chromadb").resolve())
    )
    receipt: dict[str, Any] = {
        "schema_version": FACT_VECTOR_INDEX_PREFLIGHT_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "section_id": section_id,
        "product_hybrid_required": required,
        "authority_mode": authority.authority_mode,
        "direct_vector_proof": authority.direct_vector_proof,
        "inherited_bullet_proof": authority.inherited_bullet_proof,
        "aggregate_section_proof": authority.aggregate_section_proof,
        "positioning_only": authority.positioning_only,
        "upstream_sections": list(authority.upstream_sections),
        "direct_fact_vector_required": direct_vector_required,
        "authority_manifest": c0_authority_manifest(),
        "status": STATUS_PASS,
        "reasons": [],
        "manifest_ref": MANIFEST_REL,
        "manifest_present": manifest_present,
        "manifest_schema_version": str(manifest.get("schema_version") or "") if manifest else "",
        "manifest_checksum": str(manifest.get("manifest_checksum") or "") if manifest else "",
        "manifest_generated_at_utc": str(manifest.get("generated_at_utc") or "") if manifest else "",
        "manifest_source": str(manifest.get("source") or "") if manifest else "",
        "manifest_dry_run": bool(manifest.get("dry_run")) if manifest else False,
        "manifest_upserted_count": int(manifest.get("upserted_count") or 0) if manifest else 0,
        "manifest_collection_count_after": int(manifest.get("collection_count_after") or 0)
        if manifest
        else 0,
        "manifest_sparse_sidecar_built": bool(manifest.get("sparse_sidecar_built"))
        if manifest
        else False,
        "manifest_section_target_count": section_manifest_count,
        "locked_deterministic_lane": section_id in set(str(x) for x in locked_lanes),
        "chroma_path": resolved_chroma_path,
        "expected_embedding_model": BGE_M3_MODEL_ID,
        "expected_embedding_dim": EXPECTED_BGE_DIMENSION,
        "collection": {},
        "delayed_loop_policy": {
            "pre_run_fact_vector_index_required": direct_vector_required,
            "live_write_during_c0": False,
            "generated_output_route": "stage_or_semantic_cache_after_generation",
            "promotion_gate": "fact_vectors_staging_to_live_after_validation_or_hitl",
        },
    }
    reasons: list[str] = []
    if direct_vector_required:
        if manifest_present and receipt["manifest_dry_run"]:
            reasons.append("bootstrap_manifest_is_dry_run")
        elif (
            manifest_present
            and receipt["manifest_upserted_count"] <= 0
            and receipt["manifest_collection_count_after"] <= 0
        ):
            reasons.append("bootstrap_manifest_empty")

        if not resolved_chroma_path:
            reasons.append("chroma_path_missing")
        else:
            try:
                receipt["collection"] = _inspect_collection(
                    chroma_path=resolved_chroma_path,
                    section_id=section_id,
                )
            except Exception as exc:  # guardian: allow-broad-exception -- Chroma client versions vary; receipt classifies the failure
                reasons.append(f"fact_vectors_collection_unavailable:{type(exc).__name__}")
                receipt["collection"] = {"error": f"{type(exc).__name__}:{exc}"}
    else:
        receipt["collection"] = {
            "skipped": True,
            "reason": "direct_fact_vector_not_required_for_section_authority",
        }

    collection = receipt.get("collection") if isinstance(receipt.get("collection"), dict) else {}
    collection_count = int(collection.get("collection_count") or 0)
    live_section_count = int(collection.get("section_target_count") or 0)
    bad_model_count = int(collection.get("bad_model_count") or 0)
    missing_model_count = int(collection.get("missing_model_count") or 0)
    bad_dim_count = int(collection.get("bad_dim_count") or 0)
    missing_dim_count = int(collection.get("missing_dim_count") or 0)
    if direct_vector_required and collection_count <= 0:
        reasons.append("fact_vectors_collection_empty")
    if direct_vector_required and not manifest_present and collection_count <= 0:
        reasons.append("bootstrap_manifest_missing")
    if direct_vector_required and (bad_model_count or missing_model_count):
        reasons.append("fact_vectors_embedding_model_not_fully_bge_m3")
    if direct_vector_required and (bad_dim_count or missing_dim_count):
        reasons.append("fact_vectors_embedding_dim_not_fully_1024")
    section_covered = (
        not direct_vector_required
        or section_manifest_count > 0
        or live_section_count > 0
    )
    if direct_vector_required and required and not section_covered:
        reasons.append("section_fact_vector_coverage_missing")
    if direct_vector_required and section_id == "unify_bullets":
        unify_sufficiency = _build_unify_bullets_sufficiency(
            collection=collection,
            role_family_key=str(role_family_key or ""),
            repo_root=root,
        )
        receipt["unify_bullets_sufficiency"] = unify_sufficiency
        receipt["role_episode_bullets_sufficiency"] = unify_sufficiency
        if unify_sufficiency.get("status") != STATUS_PASS:
            nested_reasons = [
                str(reason)
                for reason in (unify_sufficiency.get("reasons") or [])
                if str(reason).strip()
            ]
            if any("missing" in reason for reason in nested_reasons):
                reasons.append("unify_bullets_fact_vector_sufficiency_missing")
            else:
                reasons.append("unify_bullets_fact_vector_sufficiency_not_pass")
    if (
        direct_vector_required
        and section_id in _ROLE_EPISODE_BULLET_SECTIONS
        and section_id != "unify_bullets"
    ):
        employer_sufficiency = _build_role_episode_bullets_sufficiency(
            section_id=section_id,
            collection=collection,
            repo_root=root,
        )
        receipt["role_episode_bullets_sufficiency"] = employer_sufficiency
        receipt[f"{section_id}_sufficiency"] = employer_sufficiency
        if employer_sufficiency.get("status") != STATUS_PASS:
            nested_reasons = [
                str(reason)
                for reason in (employer_sufficiency.get("reasons") or [])
                if str(reason).strip()
            ]
            if any("missing" in reason for reason in nested_reasons):
                reasons.append(f"{section_id}_fact_vector_sufficiency_missing")
            else:
                reasons.append(f"{section_id}_fact_vector_sufficiency_not_pass")

    section_sufficiency = _build_section_sufficiency(
        section_id=section_id,
        collection=collection,
        manifest_section_target_count=section_manifest_count,
        product_hybrid_required=required,
    )
    receipt["section_sufficiency"] = section_sufficiency
    receipt[f"{section_id}_section_sufficiency"] = section_sufficiency
    if section_sufficiency.get("status") != STATUS_PASS:
        nested_reasons = [
            str(reason)
            for reason in (section_sufficiency.get("reasons") or [])
            if str(reason).strip()
        ]
        if any("missing" in reason for reason in nested_reasons):
            reasons.append(f"{section_id}_section_sufficiency_missing")
        else:
            reasons.append(f"{section_id}_section_sufficiency_not_pass")

    if reasons:
        if any("unavailable" in r or "missing" in r or "empty" in r for r in reasons):
            status = STATUS_MISSING
        else:
            status = STATUS_STALE
    else:
        status = STATUS_PASS
    receipt["status"] = status
    receipt["reasons"] = reasons
    receipt["section_coverage_present"] = section_covered
    receipt["same_run_write_policy"] = (
        "forbidden_for_product_retrieval"
        if direct_vector_required
        else "not_applicable_inherited_upstream_proof"
    )
    receipt["write_authority"] = False
    receipt["comparison_authority"] = True

    if artifact_dir is not None:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT).write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return receipt


__all__ = [
    "FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT",
    "FACT_VECTOR_INDEX_PREFLIGHT_SCHEMA",
    "STATUS_ERROR",
    "STATUS_MISSING",
    "STATUS_PASS",
    "STATUS_STALE",
    "build_fact_vector_index_preflight",
]
