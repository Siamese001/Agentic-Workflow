"""apps_exec outputs -> executive content blocks adapter.

apps_exec emits an executive brief at `reports/executive/exec_brief_*.md`.
This adapter pulls thesis lines and proof-point bullets from that brief and
returns them as the closing patterns expected by card 13 (Executive Fit).

Contract: returns a list[str] of close-pattern lines suitable for the
template variable `executive_fit_close_patterns`.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path

from apps_shared.contracts.cross_app import (
    EnvelopeLoadError,
    ExecutiveBriefEnvelope,
)

_DEFAULT_EXEC_DIR = Path("reports/executive")
_BRIEF_RE = re.compile(r"^exec_brief_[\w-]+_([0-9a-f]+)\.md$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)


def _latest_brief(exec_dir: Path) -> Path:
    """Return the most-recent executive-brief file, by mtime."""
    if not exec_dir.is_dir():
        raise FileNotFoundError(f"Executive output directory not found: {exec_dir}")
    candidates = sorted(
        (p for p in exec_dir.glob("exec_brief_*.md")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No exec_brief_*.md files in {exec_dir}")
    return candidates[0]


def load_executive_close_patterns(
    brief_path: Path | None = None,
    exec_dir: Path | None = None,
    max_patterns: int = 5,
) -> list[str]:
    """Extract close-pattern lines from an executive brief.

    Args:
        brief_path: explicit brief path. If None, picks the most recent in
            `exec_dir`.
        exec_dir: directory to search when `brief_path` is None.
        max_patterns: cap on number of close patterns returned.

    Returns:
        List of bullet lines suitable for the executive-fit template.
    """
    if brief_path is None:
        exec_dir = exec_dir or _DEFAULT_EXEC_DIR
        brief_path = _latest_brief(exec_dir)
    if not brief_path.is_file():
        raise FileNotFoundError(f"Executive brief not found: {brief_path}")

    # Prefer envelope path (typed, sealed, freshness-checked).
    envelope_path = brief_path.with_name(
        brief_path.stem + ".envelope.json"
    )
    # exec_brief_<role>_<trace>.md -> exec_brief_<trace>.envelope.json
    m = re.match(r"^exec_brief_[\w-]+_([0-9a-f]+)$", brief_path.stem)
    if m:
        envelope_path = brief_path.parent / f"exec_brief_{m.group(1)}.envelope.json"
    if envelope_path.is_file():
        try:
            env = ExecutiveBriefEnvelope.load(envelope_path)
            return list(env.payload.close_patterns)[:max_patterns]
        except EnvelopeLoadError as exc:
            warnings.warn(
                f"Envelope at {envelope_path} failed to load ({exc}); "
                "falling back to markdown-regex parser.",
                DeprecationWarning,
                stacklevel=2,
            )

    warnings.warn(
        f"Envelope missing at {envelope_path}; falling back to markdown-regex "
        "parser. Run `python -m apps_exec.outputs.envelope_emitter --brief "
        f"{brief_path}` to produce the envelope.",
        DeprecationWarning,
        stacklevel=2,
    )

    text = brief_path.read_text(encoding="utf-8")
    bullets = [m.group(1).strip() for m in _BULLET_RE.finditer(text)]
    # Prefer bullets that look like assertions / theses, not citations.
    filtered = [b for b in bullets if not b.startswith("[") and len(b) <= 200]
    return filtered[:max_patterns]
