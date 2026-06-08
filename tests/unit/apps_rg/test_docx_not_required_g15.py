"""W5 / G15: DOCX is an optional export smoke only — never required for product success.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (decision #1).

``docx_output_required()`` defaults False, so gates and package X3 do not require a DOCX artifact;
it becomes required only when an operator explicitly opts in via APPS_RG_DOCX_OUTPUT_REQUIRED.
Pure product-mode lock test.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.product_output_policy import docx_output_required


def test_docx_not_required_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_DOCX_OUTPUT_REQUIRED", raising=False)
    assert docx_output_required() is False


def test_docx_required_only_when_explicitly_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", "1")
    assert docx_output_required() is True
    for off in ("false", "0", "no", "", "off"):
        monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", off)
        assert docx_output_required() is False
