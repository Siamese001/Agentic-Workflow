"""Section-lane hooks for canonical L2 authority and compatibility mirrors."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.section_l2_spine_receipt import (
    COMPILED_PROMPT_ARTIFACT,
    L2_EXECUTION_PACKET_ARTIFACT,
    assert_section_l2_spine_preconditions,
    build_l2_execution_packet_for_section,
    emit_l2_execution_packet_artifact,
    emit_section_l2_spine_receipt_artifacts,
)


def _product_visible(runtime_payload: dict[str, Any]) -> bool:
    return bool(runtime_payload.get("product_visible", True))


def prepare_section_l2_before_provider(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    *,
    provider_lane: str,
    model_lane: str | None = None,
) -> dict[str, Any]:
    """Run E1/E2 before a product section provider call.

    Non-product/fixture lanes retain the legacy mirror packet. Product-visible
    lanes cannot reach the provider until signed U0/L0/PA authority validates.
    """
    runtime_payload.setdefault("compiled_prompt_artifact_ref", COMPILED_PROMPT_ARTIFACT)
    assert_section_l2_spine_preconditions(runtime_payload, artifact_dir)

    if _product_visible(runtime_payload):
        from apps_rg.runtime.section_l2_authority import prepare_section_l2_authority

        packet = prepare_section_l2_authority(
            artifact_dir,
            section_id,
            runtime_payload,
            provider_lane=provider_lane,
            model_lane=model_lane,
        )
    else:
        packet = build_l2_execution_packet_for_section(
            section_id=section_id,
            runtime_payload=runtime_payload,
            provider_lane=provider_lane,
            model_lane=model_lane,
        )
        emit_l2_execution_packet_artifact(artifact_dir, packet)
        runtime_payload["l2_execution_packet"] = packet
        runtime_payload["l2_execution_packet_ref"] = L2_EXECUTION_PACKET_ARTIFACT

    from apps_rg.runtime.spine.spine_span_emit import emit_spine_span_event

    emit_spine_span_event(
        artifact_dir,
        layer_key="L2",
        binding_seam=(
            "apps_rg/runtime/section_l2_authority.py"
            if _product_visible(runtime_payload)
            else "apps_rg/runtime/section_l2_spine_receipt.py"
        ),
        status="authority_validated" if _product_visible(runtime_payload) else "legacy_mirror",
        product_visible=_product_visible(runtime_payload),
    )
    return packet


def finalize_section_l2_after_output(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    *,
    section_output_ref: str | None = None,
    l2_output_ref: str = "l2_output.json",
) -> dict[str, Path]:
    """Seal observed E3 output and derive section mirrors from the canonical bundle."""
    if _product_visible(runtime_payload):
        from apps_rg.runtime.section_l2_authority import finalize_section_l2_authority

        paths = finalize_section_l2_authority(
            artifact_dir,
            section_id,
            runtime_payload,
            section_output_ref=section_output_ref,
            l2_output_ref=l2_output_ref,
        )
    else:
        paths = emit_section_l2_spine_receipt_artifacts(
            artifact_dir,
            section_id=section_id,
            runtime_payload=runtime_payload,
            l2_output_ref=l2_output_ref,
            section_output_ref=section_output_ref,
        )

    from apps_rg.runtime.graph_skills_run_artifacts import persist_graph_skills_lane_artifacts

    persist_graph_skills_lane_artifacts(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
    )
    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_spine_exit_after_sealed_l2

    finalize_section_spine_exit_after_sealed_l2(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
    )
    return paths


__all__ = ["finalize_section_l2_after_output", "prepare_section_l2_before_provider"]
