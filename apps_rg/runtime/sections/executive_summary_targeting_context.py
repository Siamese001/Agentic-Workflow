"""Executive-summary freeze: selection + cap before PA; no post-compile targeting mutation."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.targeting_context_authority import (
    MaterialTargetingBundle,
    material_targeting_digest,
    sha256_hex64,
    store_material_targeting_bundle,
)
from apps_rg.runtime.sections.executive_summary_targeting_cap import (
    TARGETING_CAP_STRATEGY,
    _resolve_max_chars,
    compress_targeting_briefing_body,
    compress_targeting_jd_body,
)


def freeze_executive_summary_targeting_context(
    runtime_payload: dict[str, Any],
    *,
    gap_tokens: int = 0,
    authority_source_refs: dict[str, str] | None = None,
) -> dict[str, Any]:
    """All JD/briefing compression/selection happens here; compiled prompt is not re-trimmed."""
    jd_before = str(runtime_payload.get("jd_text") or "")
    br_before = str(runtime_payload.get("briefing") or "")
    refs = dict(authority_source_refs or {})
    refs.setdefault("freeze_stage", "pre_pa_executive_summary_v1")
    receipt: dict[str, Any] = {
        "schema": "executive_summary_targeting_context_freeze_v2",
        "targeting_cap_strategy": TARGETING_CAP_STRATEGY,
        "jd_chars_before": len(jd_before),
        "briefing_chars_before": len(br_before),
        "targeting_context_frozen": False,
        "bundle_digest_before": material_targeting_digest(jd_before, br_before),
    }
    if not jd_before.strip() and not br_before.strip():
        receipt["skip_reason"] = "empty_targeting_inputs"
        return receipt

    max_jd = _resolve_max_chars("JD", gap_tokens=gap_tokens)
    max_br = _resolve_max_chars("BRIEFING", gap_tokens=gap_tokens)
    jd_frozen = compress_targeting_jd_body(jd_before, max_jd) if jd_before.strip() else jd_before
    br_frozen = compress_targeting_briefing_body(br_before, max_br) if br_before.strip() else br_before
    bundle = MaterialTargetingBundle(
        authority_source_refs=refs,
        jd_text_frozen=jd_frozen,
        briefing_text_frozen=br_frozen,
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        bundle_digest=material_targeting_digest(jd_frozen, br_frozen),
    )
    store_material_targeting_bundle(runtime_payload, bundle)
    receipt.update(
        {
            "targeting_context_frozen": True,
            "jd_chars_after": len(jd_frozen),
            "briefing_chars_after": len(br_frozen),
            "max_jd_chars": max_jd,
            "max_briefing_chars": max_br,
            "gap_tokens": gap_tokens,
            "bundle_digest": bundle.bundle_digest,
            "bundle_digest_sha256_full": sha256_hex64(
                f"{jd_frozen}\n---\n{br_frozen}"
            ),
        }
    )
    return receipt


def role_family_key_from_proof_pool_metadata(meta: Any) -> str | None:
    if not isinstance(meta, dict):
        return None
    for block_key in ("graph_targeting", "exec_summary_graph_targeting"):
        block = meta.get(block_key)
        if isinstance(block, dict):
            rf = block.get("role_family_key")
            if rf:
                return str(rf)
    capsule = meta.get("graph_targeting_capsule")
    if isinstance(capsule, dict):
        rf = capsule.get("role_family_key")
        if rf:
            return str(rf)
    return None


__all__ = [
    "freeze_executive_summary_targeting_context",
    "role_family_key_from_proof_pool_metadata",
]
