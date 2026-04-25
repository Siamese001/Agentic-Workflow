"""Smoke tests for human_review_queue_enforcer — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.human_review_queue_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_build_hil_policy_proposal_callable():
    assert callable(mod.build_hil_policy_proposal)
