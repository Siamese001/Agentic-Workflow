"""W5 / G15: DOCX is mandatory for product output by default.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (decision #1).
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.product_output_policy import docx_output_required


def test_docx_required_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_DOCX_OUTPUT_REQUIRED", raising=False)
    assert docx_output_required() is True


def test_docx_can_only_be_disabled_explicitly(monkeypatch: pytest.MonkeyPatch) -> None:
    for off in ("false", "0", "no", "off"):
        monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", off)
        assert docx_output_required() is False
    for on in ("1", "true", "yes", "on", ""):
        monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", on)
        assert docx_output_required() is True
