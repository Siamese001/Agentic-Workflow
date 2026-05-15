"""L6 shadow handoff for headline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict

SECTION_ID = "headline"


def build_l6_shadow_package(
    *,
    artifact_dir: Path,
    repo_root: Path,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
) -> dict[str, Any]:
    return build_l6_shadow_handoff_dict(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=SECTION_ID,
        prompt_id=prompt_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )


__all__ = ["build_l6_shadow_package"]
