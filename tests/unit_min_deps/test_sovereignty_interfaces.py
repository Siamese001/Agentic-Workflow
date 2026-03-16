"""
tests/unit_min_deps/test_sovereignty_interfaces.py

Sovereignty enforcement tests for the interface boundary layer.

Tests:
1. JSON-only ChangePackage validation
2. Reflection attack hardening (sealed client)
3. Authority blocks (commit/activate/execute)
4. Proposal-only enforcement
5. Dual injection requirement
6. AST sealed_interface_check passes on apps_*
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_sovereignty_interfaces")
_emit_applies_guardrail("p0", "test_sovereignty_interfaces", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereignty_interfaces", "policy_binding")
_emit_snapshots_state("p0", "test_sovereignty_interfaces", "state_snapshot")
emit_replay_key("p0", "test_sovereignty_interfaces")
emit_determinism_digest("p0", "test_sovereignty_interfaces")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# 1. JSON-only ChangePackage
# ---------------------------------------------------------------------------


class TestChangePackageJSONOnly:
    def _make(self):
        from agentic_core.interfaces.meta_learning import ChangePackage

        return ChangePackage

    def test_valid_json_payload_accepted(self):
        CP = self._make()
        pkg = CP(
            proposal_id="test-1",
            change_type="healing_pattern",
            parameters={"key": "value", "number": 42, "flag": True},
        )
        assert pkg.parameters["key"] == "value"

    def test_nested_json_accepted(self):
        CP = self._make()
        pkg = CP(
            proposal_id="test-2",
            change_type="threshold_adjustment",
            parameters={"nested": {"a": 1, "b": [1, 2, 3]}},
        )
        import json

        json.dumps(pkg.parameters)  # must not raise

    def test_lambda_rejected(self):
        CP = self._make()
        with pytest.raises(ValueError, match="JSON-serializable"):
            CP(
                proposal_id="test-3",
                change_type="healing_pattern",
                parameters={"callback": lambda x: x},
            )

    def test_object_rejected(self):
        CP = self._make()
        with pytest.raises(ValueError, match="JSON-serializable"):
            CP(
                proposal_id="test-4",
                change_type="healing_pattern",
                parameters={"obj": object()},
            )

    def test_frozen_immutable(self):
        CP = self._make()
        pkg = CP("id", "type", {"a": 1})
        with pytest.raises((AttributeError, TypeError)):
            pkg.proposal_id = "other"  # type: ignore[misc]

    def test_requires_approval_default_true(self):
        CP = self._make()
        pkg = CP("id", "type", {})
        assert pkg.requires_approval is True


# ---------------------------------------------------------------------------
# 2. Reflection attack hardening
# ---------------------------------------------------------------------------


class TestReflectionHardening:
    def _make_client(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        return SovereignMetaLearningClient(_FakeInner(), proposal_only=True)

    def test_no_dict_attribute(self):
        client = self._make_client()
        assert not hasattr(client, "__dict__")

    def test_getattr_unknown_blocked(self):
        client = self._make_client()
        with pytest.raises(AttributeError):
            _ = client.some_unknown_attribute

    def test_inner_client_not_accessible(self):
        client = self._make_client()
        with pytest.raises(AttributeError):
            _ = client._sealed_client  # type: ignore[attr-defined]

    def test_setattr_blocked(self):
        client = self._make_client()
        with pytest.raises(AttributeError):
            client.new_attr = "value"  # type: ignore[attr-defined]

    def test_delattr_blocked(self):
        client = self._make_client()
        with pytest.raises(AttributeError):
            del client.new_attr  # type: ignore[attr-defined]

    def test_mro_does_not_expose_inner_class_name(self):
        client = self._make_client()
        mro_names = [cls.__name__ for cls in client.__class__.__mro__]
        assert "MetaLearningClient" not in mro_names
        assert "_FakeInner" not in mro_names

    def test_slots_defined(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        assert hasattr(SovereignMetaLearningClient, "__slots__")
        assert "_sealed_client" in SovereignMetaLearningClient.__slots__


# ---------------------------------------------------------------------------
# 3. Authority blocks
# ---------------------------------------------------------------------------


class TestAuthorityBlocks:
    def _make_client(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        return SovereignMetaLearningClient(_FakeInner(), proposal_only=True)

    def test_commit_raises_permission_error(self):
        client = self._make_client()
        with pytest.raises(PermissionError, match="commit"):
            client.commit()

    def test_activate_raises_permission_error(self):
        client = self._make_client()
        with pytest.raises(PermissionError, match="activate"):
            client.activate()

    def test_execute_raises_permission_error(self):
        client = self._make_client()
        with pytest.raises(PermissionError, match="execute"):
            client.execute()

    def test_store_pattern_raises_permission_error(self):
        client = self._make_client()
        with pytest.raises(PermissionError, match="store_pattern"):
            client.store_pattern()


# ---------------------------------------------------------------------------
# 4. Proposal-only enforcement
# ---------------------------------------------------------------------------


class TestProposalOnly:
    def _make_client(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        return SovereignMetaLearningClient(_FakeInner(), proposal_only=True)

    def test_propose_healing_returns_change_package(self):
        from agentic_core.interfaces.meta_learning import ChangePackage

        client = self._make_client()
        result = client.propose_healing_pattern({"test": "data"})
        assert isinstance(result, ChangePackage)
        assert result.requires_approval is True
        assert result.change_type == "healing_pattern"

    def test_propose_threshold_returns_change_package(self):
        from agentic_core.interfaces.meta_learning import ChangePackage

        client = self._make_client()
        result = client.suggest_threshold_adjustment(0.85)
        assert isinstance(result, ChangePackage)
        assert result.requires_approval is True
        assert result.change_type == "threshold_adjustment"

    def test_proposal_id_is_unique(self):
        client = self._make_client()
        p1 = client.propose_healing_pattern({})
        p2 = client.propose_healing_pattern({})
        assert p1.proposal_id != p2.proposal_id


# ---------------------------------------------------------------------------
# 5. Dual injection requirement
# ---------------------------------------------------------------------------


class TestDualInjectionRequirement:
    def test_proposal_only_false_without_gates_raises(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        with pytest.raises(PermissionError, match="approval_gate"):
            SovereignMetaLearningClient(
                _FakeInner(),
                proposal_only=False,
                approval_gate=None,
                version_store=None,
            )

    def test_proposal_only_false_with_gates_allowed(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        class _FakeGate:
            pass

        client = SovereignMetaLearningClient(
            _FakeInner(),
            proposal_only=False,
            approval_gate=_FakeGate(),
            version_store=_FakeGate(),
        )
        assert client is not None

    def test_proposal_only_true_no_gates_allowed(self):
        from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient

        class _FakeInner:
            pass

        client = SovereignMetaLearningClient(_FakeInner(), proposal_only=True)
        assert client is not None


# ---------------------------------------------------------------------------
# 6. AST sealed_interface_check passes on apps_*
# ---------------------------------------------------------------------------


class TestSealedInterfaceCheck:
    def test_no_violations_in_apps_packages(self):
        from agentic_core.enforcement.sealed_interface_check_enforcer import run_check

        violations = run_check()
        assert violations == [], "Sovereignty violations found:\n" + "\n".join(violations)

    def test_direct_layer_import_is_detected(self, tmp_path):
        from agentic_core.enforcement.sealed_interface_check_enforcer import check_file

        bad_file = tmp_path / "bad_module.py"
        bad_file.write_text("from agentic_core.L1_cognition.engines.meta_client import MetaLearningClient\n")
        violations = check_file(bad_file)
        assert any("DIRECT_LAYER_IMPORT" in v for v in violations)

    def test_sealed_impl_import_is_detected(self, tmp_path):
        from agentic_core.enforcement.sealed_interface_check_enforcer import check_file

        bad_file = tmp_path / "bypass_attempt.py"
        bad_file.write_text(
            "from agentic_core.interfaces._meta_learning_impl import SovereignMetaLearningClient\n"
        )
        violations = check_file(bad_file)
        assert any("SEALED_IMPL_BYPASS" in v for v in violations)

    def test_clean_interface_import_not_flagged(self, tmp_path):
        from agentic_core.enforcement.sealed_interface_check_enforcer import check_file

        good_file = tmp_path / "good_module.py"
        good_file.write_text("from agentic_core.interfaces.meta_learning import get_sovereign_meta_client\n")
        violations = check_file(good_file)
        assert violations == []
