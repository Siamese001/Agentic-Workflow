"""Governed headline claim-ledger fact-ID namespace resolution (apps_rg-only).

Maps model-visible employment bullet aliases (``bul_unify_*``) to canonical SRFS /
augmented-skills proof-pool IDs (``fact_*``) using index-aligned plan facts — never
widens the active proof pool allowlist.
"""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

MAPPING_SOURCE_INDEX_PARITY_V1 = "canonical_unify_bullet_index_parity_v1"
NAMESPACE_TO_SRFS = "srfs_canonical"


def proof_pool_requires_canonical_fact_namespace(metadata: dict[str, Any] | None) -> bool:
    pt = str((metadata or {}).get("proof_pool_type") or "").strip()
    return pt in (
        "selected_role_fact_set",
        "augmented_skills_graph",
        "augmented_skills_graph_c03_graphrag",
    )


def build_unify_alias_to_canonical_map(
    *,
    srfs_allowed_fact_ids: set[str],
    runtime_payload: dict[str, Any],
) -> dict[str, str]:
    """Index-aligned ``bul_unify_NNN`` -> active plan ``fact_*`` (governed crosswalk)."""
    allowed = {str(x) for x in srfs_allowed_fact_ids}
    if any(x.startswith("bul_unify_") for x in allowed):
        return {}
    plan_facts = list((runtime_payload.get("selected_fact_plan") or {}).get("facts") or [])
    plan_ids = [str(f.get("fact_id")) for f in plan_facts if f.get("fact_id")][: len(UNIFY_BULLET_IDS)]
    if len(plan_ids) < len(UNIFY_BULLET_IDS):
        plan_ids = sorted(x for x in allowed if str(x).startswith("fact_"))[: len(UNIFY_BULLET_IDS)]
    remap: dict[str, str] = {}
    for idx, legacy in enumerate(UNIFY_BULLET_IDS):
        if idx >= len(plan_ids):
            continue
        canonical = plan_ids[idx]
        if canonical in allowed:
            remap[legacy] = canonical
    return remap


def _source_fact_base_id(token: str) -> str:
    return str(token).split("_metric_")[0]


def resolve_single_source_fact_id(
    raw_id: str,
    *,
    remap: dict[str, str],
    srfs_allowed: set[str],
) -> tuple[str | None, dict[str, Any]]:
    """Resolve one token to a canonical proof-pool ID; fail closed when unmapped."""
    raw = str(raw_id).strip()
    if not raw:
        return None, {
            "original_id": raw,
            "canonical_id": None,
            "namespace_from": "empty",
            "namespace_to": NAMESPACE_TO_SRFS,
            "mapping_source": "",
            "mapping_confidence": 0.0,
            "allowed_by_srfs_slice": False,
            "failure_reason": "empty_id",
        }
    base = _source_fact_base_id(raw)
    metric_tail = raw.split("_metric_", 1)[1] if "_metric_" in raw else ""

    canonical_base: str | None = None
    namespace_from = "unknown"
    mapping_source = ""
    mapping_confidence = 0.0
    failure_reason: str | None = None

    if base in srfs_allowed:
        canonical_base = base
        namespace_from = "srfs_canonical"
        mapping_source = "identity"
        mapping_confidence = 1.0
    elif base in remap:
        canonical_base = remap[base]
        namespace_from = "unify_bullet_alias"
        mapping_source = MAPPING_SOURCE_INDEX_PARITY_V1
        mapping_confidence = 1.0
    elif base.startswith("bul_unify_"):
        failure_reason = "unmapped_unify_bullet_alias"
    elif base.startswith("fact_"):
        failure_reason = "fact_id_out_of_srfs_slice"
    else:
        failure_reason = "unrecognized_id_namespace"

    if canonical_base is None:
        return None, {
            "original_id": raw,
            "canonical_id": None,
            "namespace_from": namespace_from,
            "namespace_to": NAMESPACE_TO_SRFS,
            "mapping_source": mapping_source,
            "mapping_confidence": mapping_confidence,
            "allowed_by_srfs_slice": False,
            "failure_reason": failure_reason or "unresolved",
        }

    canonical = canonical_base
    if metric_tail:
        metric_id = f"{canonical_base}_metric_{metric_tail}"
        if metric_id in srfs_allowed:
            canonical = metric_id
        elif canonical_base not in srfs_allowed:
            return None, {
                "original_id": raw,
                "canonical_id": None,
                "namespace_from": namespace_from,
                "namespace_to": NAMESPACE_TO_SRFS,
                "mapping_source": mapping_source,
                "mapping_confidence": mapping_confidence,
                "allowed_by_srfs_slice": False,
                "failure_reason": "metric_suffix_not_in_srfs_slice",
            }

    allowed = canonical in srfs_allowed or canonical_base in srfs_allowed
    if not allowed:
        return None, {
            "original_id": raw,
            "canonical_id": canonical,
            "namespace_from": namespace_from,
            "namespace_to": NAMESPACE_TO_SRFS,
            "mapping_source": mapping_source,
            "mapping_confidence": mapping_confidence,
            "allowed_by_srfs_slice": False,
            "failure_reason": failure_reason or "canonical_not_in_srfs_slice",
        }

    return canonical, {
        "original_id": raw,
        "canonical_id": canonical,
        "namespace_from": namespace_from,
        "namespace_to": NAMESPACE_TO_SRFS,
        "mapping_source": mapping_source,
        "mapping_confidence": mapping_confidence,
        "allowed_by_srfs_slice": True,
        "failure_reason": None,
    }


def apply_headline_claim_ledger_fact_id_resolution(
    parsed: dict[str, Any],
    *,
    srfs_allowed_fact_ids: set[str],
    runtime_payload: dict[str, Any],
    proof_pool_metadata: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Rewrite ``claim_ledger`` to canonical proof IDs; preserve aliases for audit."""
    if not proof_pool_requires_canonical_fact_namespace(proof_pool_metadata):
        return parsed, None

    srfs_allowed = {str(x) for x in srfs_allowed_fact_ids}
    remap = build_unify_alias_to_canonical_map(
        srfs_allowed_fact_ids=srfs_allowed,
        runtime_payload=runtime_payload,
    )
    ledger_in = list(parsed.get("claim_ledger") or [])
    resolutions: list[dict[str, Any]] = []
    unresolved: list[str] = []
    new_rows: list[dict[str, Any]] = []

    for row in ledger_in:
        if not isinstance(row, dict):
            continue
        raw_ids = list(row.get("source_fact_ids") or [])
        canonical_ids: list[str] = []
        aliases: list[str] = []
        for raw in raw_ids:
            canon, rec = resolve_single_source_fact_id(
                str(raw),
                remap=remap,
                srfs_allowed=srfs_allowed,
            )
            resolutions.append(rec)
            if rec.get("failure_reason"):
                unresolved.append(str(raw))
            if canon:
                if canon not in canonical_ids:
                    canonical_ids.append(canon)
            orig_base = _source_fact_base_id(str(raw))
            if orig_base != (canon or "") and str(raw).strip():
                alias_entry = str(raw).strip()
                if alias_entry not in aliases:
                    aliases.append(alias_entry)

        canonical_ids = sorted(canonical_ids)
        if not canonical_ids:
            continue
        new_row: dict[str, Any] = {
            "claim_text": str(row.get("claim_text") or "").strip(),
            "source_fact_ids": canonical_ids,
        }
        if aliases:
            new_row["raw_source_fact_aliases"] = sorted(aliases)
            new_row["source_fact_aliases"] = sorted(aliases)
        new_rows.append(new_row)

    out = dict(parsed)
    out["claim_ledger"] = new_rows

    all_canonical: set[str] = set()
    all_aliases: set[str] = set()
    for row in new_rows:
        for fid in row.get("source_fact_ids") or []:
            all_canonical.add(str(fid))
        for a in row.get("raw_source_fact_aliases") or []:
            all_aliases.add(str(a))

    status = "PASS" if not unresolved else "FAIL"
    receipt: dict[str, Any] = {
        "resolution_status": status,
        "mapping_source_default": MAPPING_SOURCE_INDEX_PARITY_V1,
        "alias_crosswalk_size": len(remap),
        "alias_crosswalk": dict(sorted(remap.items())),
        "resolutions": resolutions,
        "unresolved_alias_count": len(unresolved),
        "unresolved_aliases": sorted(set(unresolved)),
        "canonical_source_fact_ids": sorted(all_canonical),
        "raw_source_fact_aliases": sorted(all_aliases),
        "proof_pool_type": str(proof_pool_metadata.get("proof_pool_type") or ""),
    }
    if unresolved:
        receipt["failure_reason"] = "one_or_more_source_fact_ids_unresolved_for_srfs_slice"

    out.setdefault("change_log", [])
    if isinstance(out["change_log"], list):
        out["change_log"].append(
            {
                "operation": "headline_srfs_fact_id_namespace_resolution",
                "resolution_status": status,
                "unresolved_alias_count": len(unresolved),
                "canonical_source_fact_ids": sorted(all_canonical),
            }
        )

    return out, receipt


def headline_fact_namespace_metric_fields(
    parsed: dict[str, Any] | None,
    resolution_receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Fields for ``section_metric_receipt.json`` fact namespace reporting."""
    if resolution_receipt is None:
        return {
            "fact_id_namespace_mode": "employment_bullet_or_base_fallback",
            "alias_resolution_used": False,
            "unresolved_alias_count": 0,
            "canonical_source_fact_ids": [],
            "raw_source_fact_aliases": [],
        }
    ledger = list((parsed or {}).get("claim_ledger") or [])
    canon: set[str] = set()
    aliases: set[str] = set()
    for row in ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            canon.add(str(fid))
        for a in row.get("raw_source_fact_aliases") or row.get("source_fact_aliases") or []:
            aliases.add(str(a))
    return {
        "fact_id_namespace_mode": "srfs_canonical_with_alias_resolution",
        "alias_resolution_used": bool(resolution_receipt.get("resolutions")),
        "unresolved_alias_count": int(resolution_receipt.get("unresolved_alias_count") or 0),
        "canonical_source_fact_ids": sorted(canon) or list(resolution_receipt.get("canonical_source_fact_ids") or []),
        "raw_source_fact_aliases": sorted(aliases) or list(resolution_receipt.get("raw_source_fact_aliases") or []),
        "fact_id_resolution_status": str(resolution_receipt.get("resolution_status") or ""),
    }


__all__ = [
    "MAPPING_SOURCE_INDEX_PARITY_V1",
    "apply_headline_claim_ledger_fact_id_resolution",
    "build_unify_alias_to_canonical_map",
    "headline_fact_namespace_metric_fields",
    "proof_pool_requires_canonical_fact_namespace",
    "resolve_single_source_fact_id",
]
