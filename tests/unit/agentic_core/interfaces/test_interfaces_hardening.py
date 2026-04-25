"""Hardening + regression tests for ``agentic_core/interfaces/`` cleanup.

Covers the 8-issue cleanup wave done on 2026-04-24:
  W1.1  IHealable -> IHealerProtocol alias
  W1.2  blackboard_lease_protocol stripped of inline filesystem impl
  W1.3  path_constants wildcard re-export
  W2.4  shared _principal_envelope_base helper
  W3.5  determinism.py emission strip
  W3.6  I*Protocol.py -> lowercase rename
  W3.7  gateways/ aggregator subpackage
  W3.8  __init__ docstring + path correctness
  W5    state_agents / meta_control defensive imports

All tests are import-only / pure-function and run without external services.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# W1.1 — IHealable is now an alias of IHealerProtocol
# ---------------------------------------------------------------------------


class TestHealerProtocolDedup:
    def test_ihealable_is_iheaperprotocol_alias(self):
        from agentic_core.interfaces.healer_protocol import IHealerProtocol
        from agentic_core.interfaces.orchestrator_protocol import IHealable

        assert IHealable is IHealerProtocol

    def test_iheaperprotocol_is_runtime_checkable(self):
        from agentic_core.interfaces.healer_protocol import IHealerProtocol

        class GoodHealer:
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
                return {"violations_found": 0, "violations_fixed": 0, "errors": [], "skipped": 0}

            def heal(self, violation):
                return {"status": "success", "details": "ok", "artifacts": [], "errors": []}

        assert isinstance(GoodHealer(), IHealerProtocol)

    def test_itieredagent_still_distinct_from_healer(self):
        from agentic_core.interfaces.healer_protocol import IHealerProtocol
        from agentic_core.interfaces.orchestrator_protocol import ITieredAgent

        assert ITieredAgent is not IHealerProtocol

    def test_iorchestrator_distinct_from_healer(self):
        from agentic_core.interfaces.healer_protocol import IHealerProtocol
        from agentic_core.interfaces.orchestrator_protocol import IOrchestratorProtocol

        assert IOrchestratorProtocol is not IHealerProtocol


# ---------------------------------------------------------------------------
# W1.2 — blackboard_lease_protocol stripped to Protocol-only
# ---------------------------------------------------------------------------


class TestBlackboardLeaseProtocolStrip:
    def test_protocol_and_exceptions_exported(self):
        from agentic_core.interfaces import blackboard_lease_protocol as mod

        assert hasattr(mod, "IBlackboardLeaseVerifier")
        assert issubclass(mod.SandboxViolationError, Exception)
        assert issubclass(mod.HealingLeaseError, Exception)
        assert issubclass(mod.PreservationViolationError, Exception)

    @pytest.mark.parametrize(
        "removed_symbol",
        [
            "read_file",
            "write_file",
            "move_file",
            "delete_file",
            "create_directory",
            "list_files",
            "validate_sandbox",
            "require_healing_lease",
            "get_project_root",
            "EXCLUDED_DIRS",
        ],
    )
    def test_filesystem_impl_removed(self, removed_symbol):
        from agentic_core.interfaces import blackboard_lease_protocol as mod

        assert not hasattr(mod, removed_symbol), (
            f"{removed_symbol} should have been stripped from "
            "agentic_core.interfaces.blackboard_lease_protocol; "
            "filesystem implementation belongs in L2_execution."
        )

    def test_protocol_runtime_checkable(self):
        from agentic_core.interfaces.blackboard_lease_protocol import IBlackboardLeaseVerifier

        class StubVerifier:
            def verify_healing_lease(self, agent_id, file_path):
                return True

            def log_security_event(self, agent_id, event_type, file_path, details=None):
                return None

        assert isinstance(StubVerifier(), IBlackboardLeaseVerifier)


# ---------------------------------------------------------------------------
# W1.3 — path_constants wildcard re-export
# ---------------------------------------------------------------------------


class TestPathConstantsShim:
    def test_documented_constants_importable(self):
        from agentic_core.interfaces.path_constants import (
            DEFAULT_SLEEP,
            MAX_RETRIES,
            THRESHOLD,
        )

        assert DEFAULT_SLEEP == 1.0
        assert THRESHOLD == 0.95
        assert MAX_RETRIES == 3

    def test_all_matches_ssot(self):
        from agentic_core.interfaces import path_constants as shim
        from agentic_core.L0_routing.config import path_constants as ssot

        assert list(shim.__all__) == list(ssot.__all__)

    def test_every_ssot_export_resolvable_through_shim(self):
        from agentic_core.interfaces import path_constants as shim
        from agentic_core.L0_routing.config import path_constants as ssot

        missing = [n for n in ssot.__all__ if not hasattr(shim, n)]
        assert not missing, f"shim missing SSOT exports: {missing}"


# ---------------------------------------------------------------------------
# W2.4 — shared _principal_envelope_base helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def principal_chain():
    from agentic_core.interfaces.principal_chain_types import (
        InvokingUserKind,
        PrincipalChain,
    )

    return PrincipalChain(
        invoking_user="alice@example.com",
        invoking_user_kind=InvokingUserKind.HUMAN,
        auth_method="oauth2",
        agent_id="agent_a",
        scope_tag="scope:test",
        scopes=("read", "suggest"),
    )


class TestPrincipalEnvelopeBase:
    def test_compose_replay_key_is_deterministic_across_dict_order(self):
        from agentic_core.interfaces._principal_envelope_base import compose_replay_key

        a = compose_replay_key({"x": 1, "y": 2, "z": 3})
        b = compose_replay_key({"z": 3, "y": 2, "x": 1})
        assert a == b
        assert len(a) == 64  # SHA-256 hex

    def test_compose_replay_key_changes_with_payload(self):
        from agentic_core.interfaces._principal_envelope_base import compose_replay_key

        assert compose_replay_key({"x": 1}) != compose_replay_key({"x": 2})

    def test_principal_chain_digest_is_stable(self, principal_chain):
        from agentic_core.interfaces._principal_envelope_base import (
            compute_principal_chain_digest,
        )

        d1 = compute_principal_chain_digest(principal_chain)
        d2 = compute_principal_chain_digest(principal_chain)
        assert d1 == d2
        assert len(d1) == 64

    def test_principal_chain_digest_changes_when_chain_handsoff(self, principal_chain):
        from agentic_core.interfaces._principal_envelope_base import (
            compute_principal_chain_digest,
        )

        before = compute_principal_chain_digest(principal_chain)
        after_chain = principal_chain.with_handoff(
            to_agent_id="agent_b",
            handoff_description="A->B",
            at_semantic_clock="tick:1",
        )
        after = compute_principal_chain_digest(after_chain)
        assert before != after

    def test_require_nonempty_passes_for_populated(self):
        from agentic_core.interfaces._principal_envelope_base import require_nonempty

        require_nonempty([("ctx: a", "x"), ("ctx: b", "y")])  # no raise

    @pytest.mark.parametrize("bad_value", ["", None])
    def test_require_nonempty_raises_on_empty(self, bad_value):
        from agentic_core.interfaces._principal_envelope_base import require_nonempty

        with pytest.raises(ValueError, match="bad required"):
            require_nonempty([("good", "x"), ("bad", bad_value)])


class TestPrincipalAwareWrite:
    def test_principal_replay_key_differs_from_base(self, principal_chain):
        from agentic_core.interfaces.principal_aware_write import (
            compute_principal_replay_key,
        )
        from agentic_core.interfaces.write_gateway import compute_replay_key

        base = compute_replay_key(
            plan_hash="ph",
            tool_calls=["t1", "t2"],
            stdout_digest="sd",
            state_diff_hash="sdh",
        )
        bound = compute_principal_replay_key(
            plan_hash="ph",
            tool_calls=["t1", "t2"],
            stdout_digest="sd",
            state_diff_hash="sdh",
            principal_chain=principal_chain,
        )
        assert base != bound

    def test_attach_principal_to_write_validates_required_fields(self, principal_chain):
        from agentic_core.interfaces.principal_aware_write import attach_principal_to_write

        env = attach_principal_to_write(
            plan_hash="ph",
            tool_calls=["t1"],
            stdout_digest="sd",
            state_diff_hash="sdh",
            principal_chain=principal_chain,
        )
        assert env.plan_hash == "ph"
        assert env.principal_chain_digest
        assert env.principal_replay_key

    def test_attach_principal_to_write_sorts_tool_calls(self, principal_chain):
        from agentic_core.interfaces.principal_aware_write import attach_principal_to_write

        env = attach_principal_to_write(
            plan_hash="ph",
            tool_calls=["t_z", "t_a", "t_m"],
            stdout_digest="sd",
            state_diff_hash="sdh",
            principal_chain=principal_chain,
        )
        assert env.tool_calls == ("t_a", "t_m", "t_z")

    @pytest.mark.parametrize(
        "missing_field",
        ["plan_hash", "stdout_digest", "state_diff_hash"],
    )
    def test_attached_write_rejects_missing_field(self, principal_chain, missing_field):
        from agentic_core.interfaces.principal_aware_write import attach_principal_to_write

        kwargs = dict(
            plan_hash="ph",
            tool_calls=["t1"],
            stdout_digest="sd",
            state_diff_hash="sdh",
            principal_chain=principal_chain,
        )
        kwargs[missing_field] = ""
        with pytest.raises(ValueError, match=missing_field):
            attach_principal_to_write(**kwargs)


class TestPrincipalAwareEgress:
    def test_attach_principal_to_egress_round_trip(self, principal_chain):
        from agentic_core.interfaces.principal_aware_egress import attach_principal_to_egress

        env = attach_principal_to_egress(
            egress_kind="llm_provider",
            target_id="anthropic:claude",
            request_digest="rd",
            response_digest="rsd",
            principal_chain=principal_chain,
        )
        assert env.egress_kind == "llm_provider"
        assert env.egress_replay_key
        d = env.to_dict()
        assert d["egress_kind"] == "llm_provider"
        assert "principal_chain" in d

    def test_egress_envelope_rejects_bad_egress_kind(self, principal_chain):
        from agentic_core.interfaces.principal_aware_egress import (
            PrincipalEgressEnvelope,
            compute_egress_replay_key,
        )
        from agentic_core.interfaces._principal_envelope_base import (
            compute_principal_chain_digest,
        )

        digest = compute_principal_chain_digest(principal_chain)
        replay_key = compute_egress_replay_key(
            egress_kind="llm_provider",
            target_id="t",
            request_digest="rd",
            response_digest="rsd",
            principal_chain=principal_chain,
        )
        with pytest.raises(ValueError, match="egress_kind"):
            PrincipalEgressEnvelope(
                egress_kind="invalid_kind",  # type: ignore[arg-type]
                target_id="t",
                request_digest="rd",
                response_digest="rsd",
                principal_chain=principal_chain,
                principal_chain_digest=digest,
                egress_replay_key=replay_key,
            )

    def test_egress_to_mcp_envelope_extension_shape(self, principal_chain):
        from agentic_core.interfaces.principal_aware_egress import attach_principal_to_egress

        env = attach_principal_to_egress(
            egress_kind="mcp_connector",
            target_id="conn:notion",
            request_digest="rd",
            response_digest="rsd",
            principal_chain=principal_chain,
        )
        ext = env.to_mcp_envelope_extension()
        assert set(ext.keys()) == {
            "x_agentic_principal_chain",
            "x_agentic_principal_digest",
            "x_agentic_egress_replay_key",
        }

    def test_write_and_egress_share_digest_helper(self, principal_chain):
        """Both surfaces import compute_principal_chain_digest from the same base."""
        from agentic_core.interfaces import _principal_envelope_base as base
        from agentic_core.interfaces import principal_aware_egress as egress
        from agentic_core.interfaces import principal_aware_write as write

        # principal_aware_write re-imports the symbol from base -> identity preserved
        assert write.compute_principal_chain_digest is base.compute_principal_chain_digest
        # principal_aware_egress imports from base too
        assert egress.compute_principal_chain_digest is base.compute_principal_chain_digest


# ---------------------------------------------------------------------------
# W3.5 — determinism.py emission strip
# ---------------------------------------------------------------------------


class TestDeterminismStrip:
    def test_canonical_functions_still_work(self):
        from agentic_core.interfaces.determinism import (
            DETERMINISM_EXCLUDED_FIELDS,
            canonical_bytes,
            canonical_hash,
            strip_nondeterministic,
        )

        assert "timestamp" in DETERMINISM_EXCLUDED_FIELDS
        # canonical_bytes delegates to L0; just verify it is callable + deterministic
        b1 = canonical_bytes({"a": 1, "b": 2})
        b2 = canonical_bytes({"b": 2, "a": 1})
        assert b1 == b2
        assert canonical_hash({"x": 1}) == canonical_hash({"x": 1})
        stripped = strip_nondeterministic({"keep": 1, "timestamp": "t"})
        assert "timestamp" not in stripped
        assert stripped["keep"] == 1

    def test_no_emit_symbols_at_module_scope(self):
        """Trace-emission calls were removed; confirm none leaked back in."""
        import agentic_core.interfaces.determinism as mod

        emit_attrs = [n for n in dir(mod) if n.startswith("_emit_")]
        assert not emit_attrs, f"determinism.py should not re-export emission helpers; found: {emit_attrs}"

    def test_lifecycle_trace_contract_not_imported(self):
        """The module must no longer transitively pull lifecycle_trace_contract."""
        import agentic_core.interfaces.determinism as mod

        assert "record_execution_trace" not in dir(mod)


# ---------------------------------------------------------------------------
# W3.6 — lowercase Protocol module names
# ---------------------------------------------------------------------------


class TestLowercaseProtocolModules:
    @pytest.mark.parametrize(
        "module_name",
        [
            "agentic_core.interfaces.healer_protocol",
            "agentic_core.interfaces.memory_store_protocol",
            "agentic_core.interfaces.orchestrator_protocol",
            "agentic_core.interfaces.blackboard_lease_protocol",
        ],
    )
    def test_lowercase_modules_importable(self, module_name):
        import importlib

        mod = importlib.import_module(module_name)
        assert mod is not None

    @pytest.mark.parametrize(
        "legacy_path",
        [
            "agentic_core.interfaces.IHealerProtocol",
            "agentic_core.interfaces.IMemoryStoreProtocol",
            "agentic_core.interfaces.IOrchestratorProtocol",
            "agentic_core.interfaces.IBlackboardLeaseVerifierProtocol",
        ],
    )
    def test_legacy_pascalcase_module_paths_gone(self, legacy_path):
        import importlib

        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(legacy_path)


# ---------------------------------------------------------------------------
# W3.7 — gateways/ aggregator
# ---------------------------------------------------------------------------


class TestGatewaysAggregator:
    def test_aggregator_re_exports_canonical_symbols(self):
        from agentic_core.interfaces.gateways import (
            EgressKind,
            GenerationRequest,
            InstructionPacket,
            PrincipalAttachedWrite,
            PrincipalEgressEnvelope,
            SovereignLLMGateway,
            UniversalWriteGateway,
            attach_principal_to_egress,
            attach_principal_to_write,
            compute_egress_replay_key,
            compute_principal_chain_digest,
            compute_principal_replay_key,
            compute_replay_key,
            get_write_gateway,
        )

        assert callable(get_write_gateway) or get_write_gateway is not None
        assert callable(compute_replay_key)
        assert callable(compose_replay_key := compute_principal_chain_digest)
        del compose_replay_key

    def test_aggregator_identity_preserved(self):
        """Symbols imported from gateways/ are the same object as the flat path."""
        from agentic_core.interfaces import gateway as flat_llm
        from agentic_core.interfaces import gateways
        from agentic_core.interfaces import write_gateway as flat_write

        assert gateways.SovereignLLMGateway is flat_llm.SovereignLLMGateway
        assert gateways.UniversalWriteGateway is flat_write.UniversalWriteGateway
        assert gateways.compute_replay_key is flat_write.compute_replay_key

    def test_flat_paths_still_work_for_backcompat(self):
        # 53 production consumers depend on these flat paths
        from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway
        from agentic_core.interfaces.principal_aware_egress import (
            PrincipalEgressEnvelope,
            attach_principal_to_egress,
        )
        from agentic_core.interfaces.principal_aware_write import (
            PrincipalAttachedWrite,
            attach_principal_to_write,
        )
        from agentic_core.interfaces.write_gateway import (
            InstructionPacket,
            UniversalWriteGateway,
        )

        # Just confirm import resolved; no behavior assertions needed here.
        for sym in (
            SovereignLLMGateway,
            GenerationRequest,
            UniversalWriteGateway,
            InstructionPacket,
            PrincipalAttachedWrite,
            attach_principal_to_write,
            PrincipalEgressEnvelope,
            attach_principal_to_egress,
        ):
            assert sym is not None


# ---------------------------------------------------------------------------
# W3.8 — __init__ exposes Sovereign Protocols + utility re-exports
# ---------------------------------------------------------------------------


class TestPackageInit:
    def test_sovereign_protocols_exported(self):
        from agentic_core.interfaces import (
            IHealerProtocol,
            IMemoryStoreProtocol,
            IOrchestratorProtocol,
        )

        assert IHealerProtocol is not None
        assert IMemoryStoreProtocol is not None
        assert IOrchestratorProtocol is not None

    def test_utility_protocol_reexports(self):
        from agentic_core.interfaces import (
            DetectionSignalProtocol,
            HumanReviewProtocol,
            MetaLearningProtocol,
            VerificationGateProtocol,
        )

        for proto in (
            DetectionSignalProtocol,
            HumanReviewProtocol,
            MetaLearningProtocol,
            VerificationGateProtocol,
        ):
            assert proto is not None

    def test_all_listed_symbols_resolvable(self):
        import agentic_core.interfaces as pkg

        missing = [n for n in pkg.__all__ if not hasattr(pkg, n)]
        assert not missing, f"__all__ lists symbols not present: {missing}"


# ---------------------------------------------------------------------------
# W5 — defensive imports in state_agents and meta_control
# ---------------------------------------------------------------------------


class TestDefensiveImports:
    def test_state_agents_imports_without_l4_anomaly_dep(self):
        # Module should import even if the underlying L4 chain has missing pieces
        import agentic_core.interfaces.state_agents as mod

        assert hasattr(mod, "CachedStateLedger")
        assert hasattr(mod, "CheckpointManager")

    def test_meta_control_imports_without_system_learning_subdep(self):
        import agentic_core.interfaces.meta_control as mod

        for sym in (
            "load_current",
            "apply_change_package_readonly",
            "ConfigDeltaArtifact",
            "canonical_json",
            "validate_component_allowed",
            "apply_meta_learning_rollout",
            "apply_with_invariants",
            "SemanticClockSnapshot",
            "CapabilityTokenArtifact",
        ):
            assert hasattr(mod, sym), f"meta_control missing {sym}"

    def test_missing_optional_dependency_stub_fails_loud_when_called(self):
        from agentic_core.interfaces.state_agents import _MissingOptionalDependency

        stub = _MissingOptionalDependency("Foo", "missing X")
        with pytest.raises(ModuleNotFoundError, match="Foo"):
            stub()
        with pytest.raises(ModuleNotFoundError, match="Foo"):
            stub.some_attr  # noqa: B018
