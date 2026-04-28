"""Tests for L5_safety/identity/pre_l5_sweep.py."""

import pytest

from agentic_core.L5_safety.identity.pre_l5_sweep import (
    PreL5SweepResult,
    run_pre_l5_sweep,
)
from agentic_core.L5_safety.identity.principal_verifier import VerificationStatus


def test_run_pre_l5_sweep_function_exists():
    """Test that run_pre_l5_sweep function exists and can be imported."""
    assert run_pre_l5_sweep is not None


def test_pre_l5_sweep_result_exists():
    """Test that PreL5SweepResult dataclass exists."""
    assert PreL5SweepResult is not None


def test_pre_l5_sweep_result_all_pass_property():
    """Test that all_pass property returns True when all checks pass."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=True,
        registry_reason="",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    assert result.all_pass is True


def test_pre_l5_sweep_result_all_pass_false_on_verification_fail():
    """Test that all_pass property returns False when verification fails."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.FAIL,
        failures=("TEST_FAILURE",),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=True,
        registry_reason="",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    assert result.all_pass is False


def test_pre_l5_sweep_result_all_pass_false_on_registry_drift():
    """Test that all_pass property returns False when registry drift detected."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=False,
        registry_reason="REGISTRY_DIGEST_MISMATCH",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    assert result.all_pass is False


def test_pre_l5_sweep_result_needs_step_up_on_verification_step_up():
    """Test that needs_step_up returns True when verification requires step-up."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.STEP_UP_REQUIRED,
        failures=("STEP_UP_REASON",),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=True,
        registry_reason="",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    assert result.needs_step_up is True


def test_pre_l5_sweep_result_needs_step_up_on_drift():
    """Test that needs_step_up returns True when drift detected but identity passes."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=False,
        registry_reason="REGISTRY_DIGEST_MISMATCH",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    assert result.needs_step_up is True


def test_pre_l5_sweep_result_combined_failures():
    """Test that combined_failures aggregates failures from all gates."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.FAIL,
        failures=("REVOKED_TOKEN",),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=False,
        registry_reason="REGISTRY_DIGEST_MISMATCH",
        data_authority_all_match=False,
        data_authority_drifts=("rag_kb", "training_data"),
    )
    
    failures = result.combined_failures
    assert "REVOKED_TOKEN" in failures
    assert "REGISTRY:REGISTRY_DIGEST_MISMATCH" in failures
    assert "DATA_AUTHORITY_DRIFT:rag_kb" in failures
    assert "DATA_AUTHORITY_DRIFT:training_data" in failures
    assert len(failures) == 4


def test_pre_l5_sweep_result_to_dict():
    """Test that to_dict() returns complete dictionary representation."""
    from agentic_core.L5_safety.identity.principal_verifier import VerificationResult
    
    verification = VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )
    
    result = PreL5SweepResult(
        verification=verification,
        registry_match=True,
        registry_reason="",
        data_authority_all_match=True,
        data_authority_drifts=(),
    )
    
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict["all_pass"] is True
    assert result_dict["needs_step_up"] is False
    assert result_dict["registry_match"] is True
    assert result_dict["data_authority_all_match"] is True
    assert "verification" in result_dict
    assert isinstance(result_dict["combined_failures"], list)
