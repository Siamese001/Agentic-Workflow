"""Resolve executive-summary briefing variants (*_briefing_exec.md) for token budget."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BriefingExecResolution:
    """Result of optional swap from full research brief to exec digest."""

    original_path: Path
    resolved_path: Path
    swapped: bool
    reason: str
    exec_sibling_path: Path | None


def discover_exec_briefing_sibling(brief_path: Path) -> Path | None:
    """Return ``*_briefing_exec.md`` sibling when it exists next to a full briefing file."""
    p = Path(brief_path).resolve()
    if not p.is_file():
        return None
    name = p.name
    if name.endswith("_briefing_exec.md"):
        return p
    if name.endswith("_briefing.md"):
        candidate = p.with_name(name.replace("_briefing.md", "_briefing_exec.md"))
        return candidate if candidate.is_file() else None
    stem = p.stem
    if stem.endswith("_briefing"):
        candidate = p.with_name(f"{stem}_exec{p.suffix}")
        return candidate if candidate.is_file() else None
    return None


def auto_exec_brief_enabled() -> bool:
  raw = os.environ.get("APPS_RG_AUTO_EXEC_BRIEF", "").strip().lower()
  return raw in {"1", "true", "yes", "on"}


def resolve_manual_brief_path(
    manual_brief: str,
    *,
    auto_exec: bool | None = None,
) -> BriefingExecResolution:
    """Optionally swap full briefing for exec digest when env requests it."""
    ref = str(manual_brief or "").strip()
    if not ref or ref.startswith(("http://", "https://")):
        return BriefingExecResolution(
            original_path=Path(ref) if ref else Path("."),
            resolved_path=Path(ref) if ref else Path("."),
            swapped=False,
            reason="not_a_local_file",
            exec_sibling_path=None,
        )
    original = Path(ref).resolve()
    sibling = discover_exec_briefing_sibling(original)
    use_auto = auto_exec_brief_enabled() if auto_exec is None else bool(auto_exec)
    if use_auto and sibling is not None and sibling.resolve() != original.resolve():
        return BriefingExecResolution(
            original_path=original,
            resolved_path=sibling.resolve(),
            swapped=True,
            reason="APPS_RG_AUTO_EXEC_BRIEF",
            exec_sibling_path=sibling.resolve(),
        )
    return BriefingExecResolution(
        original_path=original,
        resolved_path=original,
        swapped=False,
        reason="unchanged",
        exec_sibling_path=sibling.resolve() if sibling else None,
    )


__all__ = [
    "BriefingExecResolution",
    "auto_exec_brief_enabled",
    "discover_exec_briefing_sibling",
    "resolve_manual_brief_path",
]
