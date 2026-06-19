"""Regression test for the apps_research -> U0 -> apps_rg briefing handoff."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.orchestration.canonical_dispatch import _materialize_fallback_brief


def test_materialize_fallback_brief_is_disabled(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="fallback brief materialization is disabled"):
        _materialize_fallback_brief(
            target_company="Acme Co",
            target_role="SVP IT Strategy",
            jd_path=None,
            request_id="req-1",
            run_id="run-1",
            trace_id="trace-1",
        )
