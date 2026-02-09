"""
V15 Integration Wiring Tests — End-to-End Contract Enforcement.

Proves that P1/P2 contracts are exercised in a real execution path
via V15ExecutionGateway. Each test demonstrates a specific contract
is active at runtime.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
    GatewayResult,
    V15ExecutionGateway,
)
from agentic_core.L0_maintenance.types.v15_p2_contracts import (
    ForbiddenInputError,
)
from agentic_core.L0_maintenance.types.v15_p2_types import (
    FixConstraint,
    SurgicalManifest,
)

# ---- helpers ----------------------------------------------------------------


def _make_manifest(**overrides) -> SurgicalManifest:
    snippet = overrides.pop("ast_snippet", "x = 1")
    defaults = {
        "schema_version": "1.0.0",
        "correlation_id": "00000000-0000-0000-0000-000000000001",
        "node_id": "module.StructureHealerAgent.heal_repository",
        "target_layer": "L5",
        "ast_snippet": snippet,
        "serialization_canon": hashlib.sha256(snippet.encode()).hexdigest(),
        "fix_constraint": FixConstraint.STRICT,
        "manifest_hash": hashlib.sha256(snippet.encode()).hexdigest(),
        "change_history": ("initial",),
        "provenance_chain": ("art-001",),
    }
    defaults.update(overrides)
    return SurgicalManifest(**defaults)


def _stable_state_hash() -> tuple[str, str, str]:
    """Simulates a stable state (no mutation occurred)."""
    return ("fs_aaa", "git_bbb", "mem_ccc")


def _mutated_state_hash() -> tuple[str, str, str]:
    """Simulates a mutated state (healing wrote files)."""
    return ("fs_CHANGED", "git_CHANGED", "mem_CHANGED")


_state_call_count = 0


def _state_hash_mutates_once() -> tuple[str, str, str]:
    """First call returns stable, subsequent calls return mutated."""
    global _state_call_count
    _state_call_count += 1
    if _state_call_count <= 1:
        return ("fs_aaa", "git_bbb", "mem_ccc")
    return ("fs_AFTER", "git_AFTER", "mem_AFTER")


def _success_heal(manifest: SurgicalManifest) -> dict:
    return {"violations_found": 2, "violations_fixed": 2, "errors": 0, "skipped": 0}


def _failing_heal(manifest: SurgicalManifest) -> dict:
    return {"violations_found": 1, "violations_fixed": 0, "errors": 1, "skipped": 0}


def _raising_heal(manifest: SurgicalManifest) -> dict:
    raise RuntimeError("Simulated healing crash")


# =============================================================================
# §1.1 — Non-manifest input is rejected at the gateway
# =============================================================================


class TestGatewayRejectsNonManifest:
    """§1.1: Gateway rejects any input that is not a SurgicalManifest."""

    def test_dict_rejected(self):
        gw = V15ExecutionGateway()
        with pytest.raises(ForbiddenInputError, match="dict"):
            gw.execute({"raw": "data"}, _success_heal, _stable_state_hash)

    def test_string_rejected(self):
        gw = V15ExecutionGateway()
        with pytest.raises(ForbiddenInputError, match="str"):
            gw.execute("some/path.py", _success_heal, _stable_state_hash)

    def test_none_rejected(self):
        gw = V15ExecutionGateway()
        with pytest.raises(ForbiddenInputError, match="NoneType"):
            gw.execute(None, _success_heal, _stable_state_hash)

    def test_valid_manifest_accepted(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _success_heal, _stable_state_hash)
        assert isinstance(result, GatewayResult)
        assert result.success is True


# =============================================================================
# §13.1 — Semantic clock advances deterministically
# =============================================================================


class TestGatewaySemanticClock:
    """§13.1: Clock advances only on valid StateCommit, never on failure."""

    def test_clock_advances_on_success(self):
        gw = V15ExecutionGateway()
        assert gw.clock.step_id == 0

        result = gw.execute(_make_manifest(), _success_heal, _stable_state_hash)
        assert result.success is True
        assert result.semantic_clock_tick == 1
        assert gw.clock.step_id == 1

    def test_clock_does_not_advance_on_failure(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _failing_heal, _stable_state_hash)
        assert result.success is False
        assert gw.clock.step_id == 0

    def test_clock_does_not_advance_on_exception(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _raising_heal, _stable_state_hash)
        assert result.success is False
        assert gw.clock.step_id == 0

    def test_multiple_successes_advance_monotonically(self):
        gw = V15ExecutionGateway()
        m1 = _make_manifest(correlation_id="c1")
        m2 = _make_manifest(correlation_id="c2")
        m3 = _make_manifest(correlation_id="c3")

        gw.execute(m1, _success_heal, _stable_state_hash)
        gw.execute(m2, _success_heal, _stable_state_hash)
        gw.execute(m3, _success_heal, _stable_state_hash)

        assert gw.clock.step_id == 3
        assert gw.clock.vector_clock["L5"] == 3


# =============================================================================
# §10.2/§10.3 — Rollback restores hashes exactly
# =============================================================================


class TestGatewayRollbackIntegrity:
    """§10.3: On failure, rollback verification checks pre-mutation hashes."""

    def test_rollback_verified_on_failure_stable_state(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _failing_heal, _stable_state_hash)
        assert result.success is False
        assert result.rollback_verified is True

    def test_rollback_verified_on_exception_stable_state(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _raising_heal, _stable_state_hash)
        assert result.success is False
        assert result.rollback_verified is True
        assert result.error is not None

    def test_rollback_fails_if_state_drifted(self):
        gw = V15ExecutionGateway()

        call_count = 0

        def drifting_state() -> tuple[str, str, str]:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return ("fs_aaa", "git_bbb", "mem_ccc")
            return ("fs_DRIFTED", "git_bbb", "mem_ccc")

        result = gw.execute(_make_manifest(), _failing_heal, drifting_state)
        assert result.success is False
        assert result.rollback_verified is False
        assert "filesystem" in (result.error or "")

    def test_pre_snapshot_captured(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _success_heal, _stable_state_hash)
        assert result.pre_snapshot is not None
        assert result.pre_snapshot.filesystem_hash == "fs_aaa"

    def test_post_snapshot_captured_on_success(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _success_heal, _stable_state_hash)
        assert result.post_snapshot is not None

    def test_no_post_snapshot_on_failure(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _failing_heal, _stable_state_hash)
        assert result.post_snapshot is None


# =============================================================================
# §5.1 — Dedupe via SHA-256
# =============================================================================


class TestGatewayDedupe:
    """§5.1: Duplicate signals are detected via SHA-256."""

    def test_first_execution_not_dedupe(self):
        gw = V15ExecutionGateway()
        result = gw.execute(_make_manifest(), _success_heal, _stable_state_hash)
        assert result.dedupe_hit is False

    def test_second_identical_execution_is_dedupe(self):
        gw = V15ExecutionGateway()
        m = _make_manifest()
        gw.execute(m, _success_heal, _stable_state_hash)
        result = gw.execute(m, _success_heal, _stable_state_hash)
        assert result.dedupe_hit is True

    def test_different_manifests_not_dedupe(self):
        gw = V15ExecutionGateway()
        m1 = _make_manifest(correlation_id="c1")
        m2 = _make_manifest(correlation_id="c2")
        gw.execute(m1, _success_heal, _stable_state_hash)
        result = gw.execute(m2, _success_heal, _stable_state_hash)
        assert result.dedupe_hit is False
