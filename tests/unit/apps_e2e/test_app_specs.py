"""Unit tests for tools.certification.apps_e2e.app_specs.

Pure data — no apps execution. Verifies the registry shape, runnable
predicate, and per-app expectations are coherent.
"""
from __future__ import annotations

from tools.certification.apps_e2e.app_specs import (
    APP_SPECS, AppSpec, find_spec, runnable_specs,
)


def test_registry_is_non_empty() -> None:
    assert len(APP_SPECS) >= 7


def test_every_spec_has_canonical_app_name() -> None:
    for s in APP_SPECS:
        assert s.app_name.startswith("apps_"), s.app_name
        assert s.app_name.replace("apps_", "").islower() or "_" in s.app_name


def test_app_packages_are_unique() -> None:
    names = [s.app_name for s in APP_SPECS]
    assert len(names) == len(set(names))
    pkgs = [s.app_package for s in APP_SPECS]
    assert len(pkgs) == len(set(pkgs))


def test_all_apps_runnable_post_w12() -> None:
    """Post-W12 (2026-05-02): every app is runtime-certified, no skeletons."""
    runnables = {s.app_name for s in runnable_specs()}
    # apps_rg is the reference app -- must always be runnable
    assert "apps_rg" in runnables
    # apps_underwriting_ai promoted from skeleton waiver to SPINE_COMPLETE_CERTIFIED
    # in W12 (plan apps-fort-knox-parity-c5d9a3 §23) -- user mandate.
    assert "apps_underwriting_ai" in runnables
    assert "apps_qna" in runnables  # promoted in W11


def test_find_spec_returns_known_app() -> None:
    s = find_spec("apps_rg")
    assert isinstance(s, AppSpec)
    assert s.app_name == "apps_rg"


def test_find_spec_returns_none_for_unknown() -> None:
    assert find_spec("apps_bogus_xyz") is None


def test_entrypoint_command_format() -> None:
    for s in APP_SPECS:
        assert s.entrypoint_command.startswith(f"python -m {s.app_package}")


def test_managed_workflow_apps_expect_static_dag() -> None:
    """Coherence: if expected_route_form == MANAGED_WORKFLOW, expects_static_dag must be True."""
    for s in APP_SPECS:
        if s.expected_route_form == "MANAGED_WORKFLOW":
            assert s.expects_static_dag, (
                f"{s.app_name}: MANAGED_WORKFLOW route_form requires expects_static_dag=True"
            )


def test_no_skeleton_apps_remain() -> None:
    """Post-W12: there are no longer any unrunnable skeleton apps.

    Plan: apps-fort-knox-parity-c5d9a3 §23 -- apps_underwriting_ai promoted
    from WAIVED_SKELETON to SPINE_COMPLETE_CERTIFIED.
    """
    not_runnable = [s.app_name for s in APP_SPECS if not s.runnable]
    assert not_runnable == [], f"Unexpected skeleton apps: {not_runnable}"
