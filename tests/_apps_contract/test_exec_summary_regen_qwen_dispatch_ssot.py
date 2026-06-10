"""Static SSOT: exec-summary regen must use budgeted_regen_call (W1 D6).

Allowed direct ``call_qwen_vllm``:
- ``executive_summary_regen_dispatch.py`` (wrapper internals)
- ``executive_summary_lane.py`` scratch first-call site only (single occurrence)
Forbidden in remediation/regen modules outside wrapper.
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

_CALL_RE = re.compile(r"\bcall_qwen_vllm\s*\(")


def _call_sites(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [(i + 1, ln.strip()) for i, ln in enumerate(lines) if _CALL_RE.search(ln)]


def test_wrapper_is_only_regen_transport_site() -> None:
    sites = _call_sites(_WRAPPER)
    assert sites, "budgeted wrapper must call transport internally"
    assert all("budgeted_regen_call" in _WRAPPER.read_text(encoding="utf-8") for _ in [0])


def test_forbidden_modules_do_not_call_qwen_directly() -> None:
    violations: list[str] = []
    for path in _FORBIDDEN:
        for line_no, snippet in _call_sites(path):
            violations.append(f"{path.relative_to(REPO)}:{line_no}: {snippet}")
    assert not violations, "regen must use budgeted_regen_call:\n" + "\n".join(violations)


def test_lane_has_single_scratch_direct_call() -> None:
    sites = _call_sites(_LANE)
    assert len(sites) == 1, f"expected one scratch call_qwen_vllm in lane, got {sites}"
