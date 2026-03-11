"""
Proto governance test — Phase A gate.

Fails if any active agent file in apps_lic/reasoning/, apps_rg/engines/,
apps_shared/reasoning/, or agentic_core/**/ has >80% comment lines.
Such files are dead weight consuming agent registry slots.

Marker: architecture
"""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENT_DIRS = [
    REPO_ROOT / APPS_LIC_DIR / "reasoning",
    REPO_ROOT / APPS_RG_DIR / "engines",
    REPO_ROOT / APPS_SHARED_DIR / "reasoning",
    REPO_ROOT / AGENTIC_CORE_DIR,
]

COMMENT_CEILING = 0.80  # 80% comment lines = dead weight


def _comment_ratio(py_path: Path) -> float:
    """Return fraction of non-blank lines that are pure comment lines."""
    lines = py_path.read_text(encoding="utf-8", errors="replace").splitlines()
    non_blank = [ln.strip() for ln in lines if ln.strip()]
    if not non_blank:
        return 0.0
    comment_lines = sum(1 for ln in non_blank if ln.startswith("#"))
    return comment_lines / len(non_blank)


def _collect_agent_files():
    results = []
    for base in AGENT_DIRS:
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            if py.name.startswith("_"):
                continue
            results.append(py)
    return results


@pytest.mark.architecture
def test_no_legacy_shells():
    """No active agent file should have >80% comment lines (dead weight gate)."""
    violations = []
    for py in _collect_agent_files():
        ratio = _comment_ratio(py)
        if ratio > COMMENT_CEILING:
            rel = py.relative_to(REPO_ROOT)
            violations.append(f"{rel}  ({ratio:.0%} comment lines)")

    if violations:
        lines = "\n  ".join(violations)
        pytest.fail(
            f"FAIL: {len(violations)} agent file(s) exceed {COMMENT_CEILING:.0%} comment-line ceiling "
            f"(dead weight gate):\n  {lines}"
        )
