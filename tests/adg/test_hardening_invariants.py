"""
Invariant tests for hardening fixes (Sections 1-7).

These tests lock the contracts introduced by the hardening addendum fixes:
  S1: ExecutionContext.create() signature lock
  S2: DispositionDecision schema strict (no tuple unpacking)
  S3: Hierarchy Healer type safety (frozenset guard)
  S4: Territory path canonicalization
  S6: Artifact write integrity (mkdir before write)
  S7: Telemetry schema deduplication
"""

import inspect
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "test_hardening_invariants")
emit_determinism_digest("p0", "test_hardening_invariants")
_emit_records_execution_trace(str(uuid.uuid4()), "L0_ROUTING", "test_hardening_invariants")
_emit_applies_guardrail(str(uuid.uuid4()), "test_hardening_invariants", "p0_governance")
_emit_signs_execution_trace(str(uuid.uuid4()), "test_hash", "test_hash", 0)


# ---------------------------------------------------------------------------
# S1: ExecutionContext.create() signature lock
# ---------------------------------------------------------------------------

class TestExecutionContextSignatureLock:
    """Ensure ExecutionContext.create() rejects stale kwargs."""

    def test_create_accepted_params(self):
        """create() must accept only the canonical param set — no execution_request_id."""
        from agentic_core.L2_execution.context.execution_context import ExecutionContext

        sig = inspect.signature(ExecutionContext.create)
        accepted = set(sig.parameters.keys()) - {"cls"}
        # execution_request_id must NOT be accepted (it's auto-generated inside create)
        assert "execution_request_id" not in accepted, (
            "ExecutionContext.create() must not accept execution_request_id — "
            "it is generated internally"
        )
        # These observability fields must NOT be on create()
        for forbidden in ("execution_start_tick", "execution_end_tick",
                          "execution_status", "failure_classification"):
            assert forbidden not in accepted, (
                f"ExecutionContext.create() must not accept '{forbidden}'"
            )

    def test_create_required_params_present(self):
        """create() must require the canonical fields."""
        from agentic_core.L2_execution.context.execution_context import ExecutionContext

        sig = inspect.signature(ExecutionContext.create)
        params = sig.parameters
        # These must be present
        for required in ("run_id", "capability_token", "policy_hash",
                         "execution_input", "execution_target"):
            assert required in params, f"Missing required param: {required}"


# ---------------------------------------------------------------------------
# S2: DispositionDecision schema strict
# ---------------------------------------------------------------------------

class TestDispositionDecisionSchemaStrict:
    """DispositionDecision must reject non-mapping unpacking."""

    def test_tuple_rejected(self):
        """Passing a tuple as **kwargs must raise TypeError."""
        from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import DispositionDecision

        with pytest.raises(TypeError):
            DispositionDecision(**("ARCHIVE", "/tmp", "reason", 0.9))  # type: ignore[arg-type]

    def test_dict_accepted(self):
        """Passing a dict with valid keys must succeed."""
        from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import DispositionDecision

        d = DispositionDecision(**{"action": "KEEP", "reason": "test"})
        assert d.action == "KEEP"
        assert d.reason == "test"


# ---------------------------------------------------------------------------
# S3: Hierarchy Healer type safety
# ---------------------------------------------------------------------------

class TestHealerInputTypes:
    """Hierarchy healer methods must reject non-dict violations."""

    def test_heal_rejects_frozenset_with_error_dict(self):
        """heal() must not crash on frozenset input."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyHealerAgent

        agent = HierarchyHealerAgent.__new__(HierarchyHealerAgent)
        # frozenset has no .get() — must return error dict, not raise
        result = agent.heal(frozenset({"type", "file"}))
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "frozenset" in result["error"]

    def test_heal_rejects_frozenset(self):
        """heal() must not crash on frozenset input."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyHealerAgent

        agent = HierarchyHealerAgent.__new__(HierarchyHealerAgent)
        result = agent.heal(frozenset({"type", "file"}))
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_heal_accepts_dict(self):
        """heal() must work with a valid dict."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyHealerAgent

        agent = HierarchyHealerAgent.__new__(HierarchyHealerAgent)
        # Missing file path → returns skipped, but doesn't crash
        result = agent.heal({"type": "STRUCTURE"})
        assert isinstance(result, dict)
        assert result["status"] == "skipped"


# ---------------------------------------------------------------------------
# S4: Territory path canonicalization
# ---------------------------------------------------------------------------

class TestTerritoryPathResolution:
    """L-layer territory names must resolve under agentic_core/."""

    def test_l_layer_resolves_under_agentic_core(self):
        """L0_routing must resolve to project_root/agentic_core/L0_routing, not project_root/L0_routing."""
        from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

        project_root = Path(__file__).resolve().parents[2]
        for layer in ("L0_routing", "L1_cognition", "L2_execution",
                       "L3_orchestration", "L5_safety"):
            bare_path = project_root / layer
            canonical_path = project_root / AGENTIC_CORE_DIR / layer
            # The bare path must NOT exist (it's not a real directory)
            assert not bare_path.exists(), (
                f"Bare L-layer path should not exist: {bare_path}"
            )
            # The canonical path MUST exist
            assert canonical_path.exists(), (
                f"Canonical L-layer path must exist: {canonical_path}"
            )


# ---------------------------------------------------------------------------
# S6: Artifact write integrity
# ---------------------------------------------------------------------------

class TestArtifactWriteIntegrity:
    """Artifact write functions must ensure directory exists."""

    def test_post_validation_mkdir(self, tmp_path):
        """_write_post_validation_json must create output_dir if missing."""
        from agentic_core.L0_routing.scripts._ssot_validation_artifacts import (
            _write_post_validation_json,
        )

        nested_dir = tmp_path / "deep" / "nested" / "dir"
        pre_path = tmp_path / "pre_validation.json"
        # Create empty pre_validation so it can be loaded
        pre_path.write_text('{"findings": []}', encoding="utf-8")

        _write_post_validation_json(
            pre_validation_path=pre_path,
            phase3_result={"remaining_violations": []},
            trace_id="test-trace",
            territory="test",
            output_dir=nested_dir,
        )
        output = nested_dir / "post_validation.json"
        assert output.exists(), "post_validation.json must be written"
        assert output.stat().st_size > 0, "post_validation.json must not be empty"


# ---------------------------------------------------------------------------
# S7: Telemetry schema deduplication
# ---------------------------------------------------------------------------

class TestTelemetrySchemaDedup:
    """Non-canonical key warnings must be deduplicated into a single message."""

    def test_single_warning_for_multiple_keys(self):
        """_warn_non_canonical_keys must emit at most 1 warning regardless of key count."""
        from agentic_core.utils.decorators_util import _warn_non_canonical_keys

        result = {
            "violations_found": 0,
            "custom_key_1": "a",
            "custom_key_2": "b",
            "custom_key_3": "c",
            "_internal": True,
        }
        with patch("agentic_core.utils.decorators_util.Logger") as mock_logger:
            _warn_non_canonical_keys(result, "TestAgent")
            # Must emit exactly 1 warning, not 4
            assert mock_logger.warning.call_count == 1
            msg = mock_logger.warning.call_args[0][0]
            assert "4 non-canonical key(s)" in msg

    def test_no_warning_for_canonical_keys(self):
        """No warning when all keys are canonical."""
        from agentic_core.utils.decorators_util import _warn_non_canonical_keys

        result = {"violations_found": 5, "violations_fixed": 3, "errors": 0}
        with patch("agentic_core.utils.decorators_util.Logger") as mock_logger:
            _warn_non_canonical_keys(result, "TestAgent")
            mock_logger.warning.assert_not_called()
