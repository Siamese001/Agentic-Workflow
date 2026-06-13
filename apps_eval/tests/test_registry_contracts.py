from __future__ import annotations

import pytest

from apps_eval.registry import load_apps_registry, load_suite, load_suites_registry


EXPECTED_SUITES = {
    "apps_rg.dev.resume_generation",
    "apps_rg.holdout.resume_generation",
    "apps_lic.dev.outreach_message",
    "apps_lic.holdout.outreach_message",
}


def test_registry_lists_only_supported_apps() -> None:
    assert set(load_apps_registry()) == {"apps_rg", "apps_lic"}


def test_registry_lists_only_supported_suites() -> None:
    suites = load_suites_registry()
    assert set(suites) == EXPECTED_SUITES
    assert {suite["app_id"] for suite in suites.values()} == {"apps_rg", "apps_lic"}


@pytest.mark.parametrize(
    "old_suite",
    [
        "routing_enforcement",
        "determinism_contracts",
        "orchestration_hop",
        "output_contracts",
        "exec_brief_generation",
        "ml_metrics_validation",
    ],
)
def test_old_suite_names_are_rejected(old_suite: str) -> None:
    with pytest.raises(ValueError):
        load_suite(old_suite)
