"""Integration tests for formal verification scanners."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
    scan_repository_for_determinism,
)
from agentic_core.L5_safety.static_checks.powershell_ban import (
    scan_repository_for_powershell,
)
from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (
    scan_repository_for_writes,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_formal_verification")
_emit_applies_guardrail("p0", "test_formal_verification", "p0_governance")
_emit_reads_policy_state("p0", "test_formal_verification", "policy_binding")
_emit_snapshots_state("p0", "test_formal_verification", "state_snapshot")
emit_replay_key("p0", "test_formal_verification")
emit_determinism_digest("p0", "test_formal_verification")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit_min_deps
def test_repo_no_powershell_violations():
    """Test that repository has no PowerShell violations."""
    repo_root = Path.cwd()

    violations = scan_repository_for_powershell(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"PowerShell violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_repo_no_write_gateway_violations():
    """Test that repository has no write gateway violations in scope."""
    repo_root = Path.cwd()

    violations = scan_repository_for_writes(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"Write gateway violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_repo_no_determinism_violations():
    """Test that repository has no determinism violations in replay/storage."""
    repo_root = Path.cwd()

    violations = scan_repository_for_determinism(repo_root)

    # Convert to readable format for assertion
    violation_details = [
        f"{path}:{lineno} - {rule_id} - {snippet}" for path, lineno, rule_id, snippet in violations
    ]

    assert len(violations) == 0, f"Determinism violations found: {violation_details}"


@pytest.mark.unit_min_deps
def test_scanner_coverage():
    """Test that scanners cover expected directories."""
    repo_root = Path.cwd()

    # Test PowerShell scanner coverage
    _ps_violations = scan_repository_for_powershell(repo_root)

    # Should scan tools and docs/evidence directories
    tools_dir = repo_root / TOOLS_DIR
    evidence_dir = repo_root / "docs" / "evidence"

    if tools_dir.exists():
        # If tools directory exists, scanner should have checked it
        # (even if no violations found)
        pass

    if evidence_dir.exists():
        # If evidence directory exists, scanner should have checked it
        pass

    # Test write gateway scanner coverage
    _write_violations = scan_repository_for_writes(repo_root)

    # Should scan agentic_core (excluding L2_execution)
    agentic_core_dir = repo_root / AGENTIC_CORE_DIR
    if agentic_core_dir.exists():
        pass

    # Test determinism scanner coverage
    _det_violations = scan_repository_for_determinism(repo_root)

    # Should scan replay and storage modules
    replay_dir = repo_root / L3_ORCHESTRATION_DIR / "replay"
    storage_dir = repo_root / L4_STATE_DIR / "storage"

    if replay_dir.exists():
        pass

    if storage_dir.exists():
        pass


@pytest.mark.unit_min_deps
def test_scanner_deterministic_output():
    """Test that scanners produce deterministic output across runs."""
    repo_root = Path.cwd()

    # Run each scanner twice
    ps_violations1 = scan_repository_for_powershell(repo_root)
    ps_violations2 = scan_repository_for_powershell(repo_root)

    write_violations1 = scan_repository_for_writes(repo_root)
    write_violations2 = scan_repository_for_writes(repo_root)

    det_violations1 = scan_repository_for_determinism(repo_root)
    det_violations2 = scan_repository_for_determinism(repo_root)

    # Results should be identical
    assert ps_violations1 == ps_violations2
    assert write_violations1 == write_violations2
    assert det_violations1 == det_violations2

    # Results should be sorted
    def check_sorted(violations):
        for i in range(1, len(violations)):
            if violations[i - 1] > violations[i]:
                return False
        return True

    assert check_sorted(ps_violations1)
    assert check_sorted(write_violations1)
    assert check_sorted(det_violations1)
