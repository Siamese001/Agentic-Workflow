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
    return emit_section_runtime_exhaust_spine_artifacts(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
        repo_root=repo_root,
    )


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
