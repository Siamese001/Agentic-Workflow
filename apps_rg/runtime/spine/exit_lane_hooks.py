"""Lane hooks: section Exit spine receipts after L2 seal (Wave 6)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.spine.exit_artifacts import emit_section_exit_spine_artifacts


def finalize_section_exit_after_l2(
    artifact_dir: Path,
    section_id: str,
    runtime_payload: dict[str, Any],
) -> dict[str, Path]:
    """After SealedL2Artifact + section x3 mirror — emit canonical Exit receipts."""
    return emit_section_exit_spine_artifacts(
        artifact_dir,
        section_id=section_id,
        runtime_payload=runtime_payload,
    )


__all__ = ["finalize_section_exit_after_l2"]
