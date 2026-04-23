"""SSOT for guardian-comment exemption checks on ADG layer violations.

Canonical location for the `# guardian: allow-layer-violation` lookback rule.
Before this module existed, three separate consumers duplicated the same
slice/substring check:
  - tools/generate/validation/gates.py  (_query_sc1_gravity, etc.)
  - tools/generate/reporting/reports.py (p0_count accumulator)
  - tools/adg/core/p0_wave_plan.py      (MCP adg_p0_wave_plan tool)

That duplication was itself an SSOT violation — and the p0_wave_plan path had
silently drifted (no guardian filter applied, causing false-positive P0s for
benchmark lazy imports with valid guardian comments).

Rules:
  * The exemption comment MUST appear within a window that covers the
    violation line plus 1 line before and up to 4 lines after (handles both
    continuation lines and multi-line `from X import (...)` blocks where
    the guardian comment lives on the closing `)`).
  * Path is repo-relative from ROOT.
  * File-read failures are non-fatal — the violation is NOT exempted (fail-closed:
    assume a violation when we cannot prove exemption).

This module has zero external dependencies beyond pathlib, so it can be imported
from any layer without creating new cross-layer edges.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_GUARDIAN_MARKER: str = "guardian: allow-layer-violation"


@lru_cache(maxsize=1024)
def _read_file_lines(path_str: str) -> tuple[str, ...]:
    """Cache file lines per absolute path. LRU-bounded to avoid memory bloat.

    Returns empty tuple if the file cannot be read — caller treats this as
    "no exemption" (fail-closed).
    """
    try:
        return tuple(Path(path_str).read_text(encoding="utf-8", errors="ignore").splitlines())
    except (OSError, UnicodeDecodeError, ValueError):
        return ()


def is_layer_violation_exempted(
    source_file: str | Path | None,
    line_no: int | None,
    *,
    repo_root: Path,
) -> bool:
    """Return True if a `guardian: allow-layer-violation` comment covers this line.

    Args:
        source_file: repo-relative path (str or Path) or absolute path.
        line_no: 1-indexed line number from the ADG edges table.
        repo_root: absolute path to the repo root (for relative resolution).

    Returns:
        True when the marker appears on line_no OR line_no - 1 of the source
        file; False otherwise (including on all error conditions).
    """
    if not source_file or not line_no or line_no <= 0:
        return False
    src_path = Path(source_file)
    if not src_path.is_absolute():
        src_path = (repo_root / src_path).resolve()
    lines = _read_file_lines(str(src_path))
    if not lines:
        return False
    # 1-indexed line_no → 0-indexed list: line at idx (line_no - 1).
    # Window: 1 line before to 4 lines after (inclusive). Covers single-line
    # imports, continuation-line imports, and multi-line `from X import (...)`
    # blocks where the guardian comment lives on the closing `)`.
    start = max(0, line_no - 2)
    end = min(len(lines), line_no + 4)
    window = lines[start:end]
    return any(_GUARDIAN_MARKER in ln for ln in window)


def clear_cache() -> None:
    """Drop the file-line cache. Use in tests or after on-disk edits."""
    _read_file_lines.cache_clear()


__all__ = ["is_layer_violation_exempted", "clear_cache"]
