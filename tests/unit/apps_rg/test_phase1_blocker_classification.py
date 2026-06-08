"""W1 unit test: truthful pre-run blocker classification.

E2E-05: a lane that executed to an X3 verdict but failed the product bar (e.g.
competencies X3_BLOCK) must be labeled ``EXECUTED_X3_BLOCK``, not the misleading
``LANE_DISPATCH_EXIT_ERROR`` the old logic emitted (apps_rg AIG E2E remediation).
"""
from __future__ import annotations

from apps_rg.l2_recipe.modular_resume_generation import _derive_pre_run_blocker


def test_executed_x3_block_not_mislabeled():
    # competencies: ran to X3_BLOCK and carries exit_status=error -> EXECUTED wins.
    assert (
        _derive_pre_run_blocker({"x3_disposition": "X3_BLOCK", "exit_status": "error"})
        == "EXECUTED_X3_BLOCK"
    )


def test_executed_x3_allow():
    assert _derive_pre_run_blocker({"x3_disposition": "X3_ALLOW"}) == "EXECUTED_X3_ALLOW"


def test_prior_abort_is_missing_not_attempted():
    assert (
        _derive_pre_run_blocker({"prior_abort": "dispatch_exception:ibm_bullets:RustBindingsAPI"})
        == "MISSING_NOT_ATTEMPTED"
    )


def test_transport_fault_preserved():
    assert _derive_pre_run_blocker({"fault": "exception", "error": "boom"}) == "exception"


def test_dispatch_exit_error():
    assert _derive_pre_run_blocker({"exit_status": "error"}) == "LANE_DISPATCH_EXIT_ERROR"


def test_no_run_dir_default():
    assert _derive_pre_run_blocker({}) == "PHASE1_NO_RUN_DIR"
    assert _derive_pre_run_blocker(None) == "PHASE1_NO_RUN_DIR"
