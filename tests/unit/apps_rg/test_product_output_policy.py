"""Product fail-closed policy helpers."""

from __future__ import annotations

import pytest

from apps_rg.runtime.product_output_policy import (
    product_fail_closed_runtime,
    require_live_bge_embeddings,
)
from apps_rg.runtime.section_cli_defaults import resolve_allow_non_allow_exit_zero


def test_product_fail_closed_default_all_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    monkeypatch.delenv("APPS_RG_WHOLE_RUN_ENVELOPE", raising=False)
    assert product_fail_closed_runtime() is True
    assert require_live_bge_embeddings() is True


def test_test_harness_disables_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")
    assert product_fail_closed_runtime() is False
    assert require_live_bge_embeddings() is False


def test_allow_non_allow_exit_zero_denied_on_product(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    monkeypatch.setenv("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", "1")
    assert resolve_allow_non_allow_exit_zero(True) is False
    assert resolve_allow_non_allow_exit_zero(False) is False
