"""Env helpers for pytest subprocesses that need mock X1D judges (not product CLI)."""

from __future__ import annotations

import os
from typing import Mapping

ENV_TEST_HARNESS = "APPS_RG_TEST_HARNESS"
ENV_MOCK_JUDGES = "APPS_RG_MOCK_JUDGES"


def with_mock_judges_test_harness(
    base: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Merge base env with test-harness mock-judge flags (``python -m apps_rg`` only)."""
    out = {**os.environ, **dict(base or {})}
    out[ENV_TEST_HARNESS] = "1"
    out[ENV_MOCK_JUDGES] = "1"
    return out
