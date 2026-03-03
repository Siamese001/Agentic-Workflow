"""V15 P9.4 — Backward Compatibility Safety Nets.

Proves older callsites that omit newer kwargs continue to work:
1) execute() works with only positional args (no kwargs)
2) Missing policy_config defaults to {}
3) Enforced modes behave correctly without explicit mode kwarg
4) Legacy heal_fn signatures (no **kwargs) are not broken by gateway
"""

from __future__ import annotations

import hashlib
import os
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.enforcement.execution_gateway import (
    GatewayResult,
    V15ExecutionGateway,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    V15HardFailAbort,
)

# ===========================================================================
# Helpers
# ===========================================================================


def _make_manifest(seed: str):
    """Create a distinct valid SurgicalManifest from a seed."""
    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
    from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

    _hex8 = hashlib.sha256(seed.encode()).hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    snippet = f"{seed}()"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id=f"Node_{seed}",
        target_layer="L0",
        ast_snippet=snippet,
        serialization_canon=seed,
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


def _stub_hashes():
    return (
        hashlib.sha256(b"fs").hexdigest(),
        hashlib.sha256(b"git").hexdigest(),
        hashlib.sha256(b"mem").hexdigest(),
    )


# ===========================================================================
# A) Legacy Execute Call — Positional Only
# ===========================================================================


class TestLegacyPositionalCall:
    """gateway.execute() with only required positional args, no kwargs."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": ""})
    def test_positional_only_off_mode(self):
        """OFF mode: positional-only call succeeds."""
        gw = V15ExecutionGateway()
        m = _make_manifest("pos_off")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        # Positional only: execution_input, heal_fn, state_hash_fn
        r = gw.execute(m, heal, _stub_hashes)
        assert isinstance(r, GatewayResult)
        assert r.success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_positional_only_log_mode(self):
        """LOG mode: positional-only call succeeds."""
        gw = V15ExecutionGateway()
        m = _make_manifest("pos_log")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        r = gw.execute(m, heal, _stub_hashes)
        assert isinstance(r, GatewayResult)
        assert r.success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": ""})
    def test_default_trace_id_used(self):
        """When trace_id omitted, default 'gw-default' is used without error."""
        gw = V15ExecutionGateway()
        m = _make_manifest("pos_trace")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        # No trace_id kwarg
        r = gw.execute(m, heal, _stub_hashes)
        assert r.success is True


# ===========================================================================
# B) Missing policy_config Default
# ===========================================================================


class TestMissingPolicyConfig:
    """Absence of policy_config kwarg must not raise; defaults to {}."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_no_policy_config_kwarg(self):
        """Execute without policy_config kwarg succeeds."""
        gw = V15ExecutionGateway()
        m = _make_manifest("no_policy")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        # No policy_config in kwargs
        r = gw.execute(m, heal, _stub_hashes, trace_id=m.correlation_id)
        assert r.success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_explicit_policy_config_still_works(self):
        """Explicit policy_config kwarg is accepted and used."""
        gw = V15ExecutionGateway()
        m = _make_manifest("with_policy")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        r = gw.execute(
            m,
            heal,
            _stub_hashes,
            trace_id=m.correlation_id,
            policy_config={"key": "value"},
        )
        assert r.success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_empty_policy_config_equivalent_to_omitted(self):
        """Empty dict policy_config produces same result as omitted."""
        gw = V15ExecutionGateway()
        m1 = _make_manifest("policy_empty")
        m2 = _make_manifest("policy_omit")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        r1 = gw.execute(m1, heal, _stub_hashes, trace_id=m1.correlation_id, policy_config={})
        r2 = gw.execute(m2, heal, _stub_hashes, trace_id=m2.correlation_id)
        assert r1.success == r2.success


# ===========================================================================
# C) Mode Defaulting — Env-Only, No Explicit Mode Kwarg
# ===========================================================================


class TestModeDefaulting:
    """Enforced modes work correctly via env only, without explicit mode kwarg."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_soft_mode_via_env_only(self):
        """SOFT_FAIL triggered by env, no mode kwarg needed."""
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        m = _make_manifest("compat_soft")

        _orig_inner = gw._execute_inner

        def _force_violation(*args, **kwargs):
            pipe = PipeOrderEnforcer()
            gw._pipe_advance(pipe, "hash_verification", "compat-soft")
            return _orig_inner(*args, **kwargs)

        with patch.object(gw, "_execute_inner", _force_violation):
            r = gw.execute(m, lambda mn: {"status": "ok", "errors": 0}, _stub_hashes)

        assert r.success is False
        assert "SOFT_FAIL" in r.error

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_mode_via_env_only(self):
        """HARD_FAIL triggered by env, no mode kwarg needed."""
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()
        with pytest.raises(V15HardFailAbort):
            gw._pipe_advance(pipe, "hash_verification", "compat-hard")

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_log_mode_via_env_only(self):
        """LOG_ONLY mode via env, no explicit kwarg, succeeds without abort."""
        gw = V15ExecutionGateway()
        m = _make_manifest("compat_log")

        def heal(manifest):
            return {"status": "ok", "errors": 0}

        r = gw.execute(m, heal, _stub_hashes)
        assert r.success is True
        assert r.error is None


# ===========================================================================
# D) Legacy heal_fn Signature — No **kwargs Injection
# ===========================================================================


class TestLegacyHealFnSignature:
    """Gateway must not inject kwargs into heal_fn. Legacy signatures must work."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_heal_fn_receives_only_manifest(self):
        """heal_fn must be called with exactly one positional arg (manifest)."""
        call_args = []

        def strict_heal(manifest):
            call_args.append(manifest)
            return {"status": "ok", "errors": 0}

        gw = V15ExecutionGateway()
        m = _make_manifest("strict_heal")
        r = gw.execute(m, strict_heal, _stub_hashes, trace_id=m.correlation_id)
        assert r.success is True
        assert len(call_args) == 1
        assert call_args[0].node_id == "Node_strict_heal"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_heal_fn_no_kwargs_accepted(self):
        """A heal_fn that does NOT accept **kwargs must not fail."""

        def legacy_heal(manifest):
            # Strict signature: no **kwargs
            return {"status": "ok", "errors": 0}

        gw = V15ExecutionGateway()
        m = _make_manifest("legacy_no_kwargs")
        # Must not raise TypeError about unexpected kwargs
        r = gw.execute(m, legacy_heal, _stub_hashes, trace_id=m.correlation_id)
        assert r.success is True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_heal_fn_with_extra_kwargs_also_works(self):
        """A heal_fn that accepts **kwargs also works (forward-compat)."""
        received_kwargs = {}

        def modern_heal(manifest, **kwargs):
            received_kwargs.update(kwargs)
            return {"status": "ok", "errors": 0}

        gw = V15ExecutionGateway()
        m = _make_manifest("modern_kwargs")
        r = gw.execute(m, modern_heal, _stub_hashes, trace_id=m.correlation_id)
        assert r.success is True
        # Gateway should NOT have injected any kwargs into heal_fn
        assert received_kwargs == {}
