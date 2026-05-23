"""Shared fixtures for apps_rg contract tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _contract_tests_proof_pool_fixture_dev_bypass() -> None:
    """Direct ``resolve_section_proof_pool`` contract tests: non-product-certified bypass."""
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()
