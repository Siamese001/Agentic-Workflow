"""Lane hooks: RuntimeExhaustBundle after Exit, before L6 shadow (Wave 7)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.section_runtime_exhaust_spine_receipt import (
    assert_section_l6_may_consume_exhaust,
    emit_section_runtime_exhaust_spine_artifacts,
)


def finalize_section_runtime_exhaust_before_l6(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
    *,
    repo_root: Path,
) -> dict[str, Path]:
    """After ExitDispositionReceipt — emit exhaust bundle + handoff receipt; gate L6."""
    paths = emit_section_runtime_exhaust_spine_artifacts(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        repo_root=repo_root,
    )
    from apps_rg.runtime.spine.l6_shadow_eval_runner import (
        maybe_run_l6_v40_shadow_eval_for_section,
    )

    l6_paths = maybe_run_l6_v40_shadow_eval_for_section(
        artifact_dir,
        section_id=section_id,
        repo_root=repo_root,
        session_id=str(runtime_payload.get("session_id") or ""),
        tenant_id=str(runtime_payload.get("tenant_id") or ""),
        l5_certification_ref=str(runtime_payload.get("l5_certification_ref") or ""),
    )
    product_visible = bool(runtime_payload.get("product_visible", True))
    if product_visible and not l6_paths:
        raise RuntimeError(
            "product-visible apps_rg section runtime requires L6 v40 shadow eval output; "
            "set APPS_RG_L6_V40_SHADOW_EVAL_SKIP only for explicit local-dev waivers"
        )
    paths.update(l6_paths)
    return paths


def gate_section_l6_shadow_after_exhaust(
    artifact_dir: Path,
    runtime_payload: dict[str, Any],
) -> None:
    """Call immediately before build_l6_shadow_package."""
    assert_section_l6_may_consume_exhaust(runtime_payload, artifact_dir)


__all__ = [
    "finalize_section_runtime_exhaust_before_l6",
    "gate_section_l6_shadow_after_exhaust",
]
