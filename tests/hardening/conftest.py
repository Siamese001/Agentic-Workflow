"""Hardening suite conftest — zero-skip enforcement gate.

RC-2 remediation: any skipped test in tests/hardening/ is a CI failure.
Skips indicate a missing mandatory dependency (e.g. rank-bm25) or an
improperly guarded test — both are defects, not acceptable outcomes.

.windsurfrules §1.1: every line of changed logic MUST be covered.
.windsurfrules §30: no silent masking.
"""

from __future__ import annotations

import pytest

_SKIPPED_NODEIDS: list[str] = []


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Accumulate skipped reports from tests/hardening/.

    pytest.mark.skipif skips are reported during the 'setup' phase.
    pytest.skip() inside a test body is reported during the 'call' phase.
    Both are defects in the hardening suite — captured here.
    """
    if report.skipped and "hardening" in report.nodeid:
        _SKIPPED_NODEIDS.append(report.nodeid)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    """Fail the session if any hardening test was skipped."""
    if not _SKIPPED_NODEIDS:
        return

    msg = (
        f"\n\nZERO-SKIP GATE FAILED — tests/hardening/ had {len(_SKIPPED_NODEIDS)} skip(s):\n"
        + "\n".join(f"  SKIP  {n}" for n in _SKIPPED_NODEIDS)
        + "\n\nEvery skip = missing mandatory dependency or wrong guard. Fix it.\n"
        + "RC-2: pytest addopts has no zero-skip enforcement; this conftest is the gate.\n"
    )
    pytest.exit(msg, returncode=3)
