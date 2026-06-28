"""Static SSOT: exec-summary regen must not use retired direct transport.

Regen remains routed through budgeted_regen_call/provider-neutral dispatch.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SECTIONS = REPO / "apps_rg" / "runtime" / "sections"

_WRAPPER = SECTIONS / "executive_summary_regen_dispatch.py"
_LANE = SECTIONS / "executive_summary_lane.py"
_FORBIDDEN = (
    SECTIONS / "executive_summary_judge_remediation.py",
    SECTIONS / "executive_summary_same_authority_regen_bridge.py",
    SECTIONS / "executive_summary_judge_regen_loop.py",
)

_CALL_RE = re.compile(r"\bcall_retired_provider_profile\s*\(")


def _call_sites(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [(i + 1, ln.strip()) for i, ln in enumerate(lines) if _CALL_RE.search(ln)]


def test_wrapper_is_only_regen_transport_site() -> None:
    sites = _call_sites(_WRAPPER)
    assert not sites, f"wrapper still has retired direct transport calls: {sites}"
    assert "budgeted_regen_call" in _WRAPPER.read_text(encoding="utf-8")


def test_forbidden_modules_do_not_call_retired_provider_directly() -> None:
    violations: list[str] = []
    for path in _FORBIDDEN:
        for line_no, snippet in _call_sites(path):
            violations.append(f"{path.relative_to(REPO)}:{line_no}: {snippet}")
    assert not violations, "regen must use budgeted_regen_call:\n" + "\n".join(violations)


def test_lane_has_no_scratch_direct_call() -> None:
    sites = _call_sites(_LANE)
    assert not sites, f"lane still has retired direct transport calls: {sites}"
