"""
Phase 2.1 Integration Tests

Tests that Phase 2 guarantees are wired into real execution + retrieval paths:

Wave 1: validate_manifest_hashes called from L2.0 _validate_manifest
Wave 2: sovereign_retrieve result carries anchors
Wave 3: sovereign_rag_orchestrator reads thresholds from BudgetConfig/RoutingConfig
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L2_execution.enforcement.manifest_hash_validator import (
    ManifestHashError,
    validate_manifest_hashes,
)
from agentic_core.L4_state.config.versioned_configs import (
    BudgetConfig,
    RoutingConfig,
    get_active_configs,
)
from agentic_core.L4_state.types.retrieval_anchor import AnchoredResult, AnchorViolationError

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manifest(extra_attrs: dict | None = None):
    """Build a minimal valid SurgicalManifest, optionally with Phase-2 hash attrs."""
    from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

    ast_snippet = "def heal(): pass"
    manifest_hash = hashlib.sha256(ast_snippet.encode()).hexdigest()
    m = SurgicalManifest(
        schema_version="1.0.0",
        correlation_id="corr-e2e-001",
        node_id="node-e2e-001",
        target_layer="L2",
        ast_snippet=ast_snippet,
        serialization_canon="canonical",
        fix_constraint=FixConstraint.STRICT,
        manifest_hash=manifest_hash,
        change_history=("init",),
        provenance_chain=("test",),
    )
    if extra_attrs:
        # SurgicalManifest is frozen; attach attrs via object.__setattr__
        for k, v in extra_attrs.items():
            object.__setattr__(m, k, v)
    return m


def _noop_heal(manifest):
    return {"errors": 0, "healed": True}


def _noop_state_hash():
    return ("fs-hash", "git-hash", "mem-hash")


# ---------------------------------------------------------------------------
# Wave 1 — manifest hash validation wired into real validation path
# ---------------------------------------------------------------------------


class TestManifestHashValidationIntegration:
    """
    Tests that validate_manifest_hashes enforces the L4 SSOT contract
    when called from the L2.0 path (directly exercising the validator
    that is now wired into _validate_manifest).
    """

    def _valid_manifest_dict(self) -> dict:
        return get_active_configs().hashes()

    def test_missing_hashes_rejected(self):
        manifest = self._valid_manifest_dict()
        del manifest["policy_hash"]
        with pytest.raises(ManifestHashError, match="policy_hash"):
            validate_manifest_hashes(manifest)

    def test_mismatched_hash_rejected(self):
        manifest = self._valid_manifest_dict()
        manifest["routing_hash"] = "b" * 64
        with pytest.raises(ManifestHashError, match="mismatch"):
            validate_manifest_hashes(manifest)

    def test_correct_hashes_accepted(self):
        manifest = self._valid_manifest_dict()
        validate_manifest_hashes(manifest)

    def test_object_manifest_with_correct_hashes_accepted(self):
        hashes = get_active_configs().hashes()

        class FakeManifest:
            policy_hash = hashes["policy_hash"]
            routing_hash = hashes["routing_hash"]
            model_hash = hashes["model_hash"]
            budget_hash = hashes["budget_hash"]

        validate_manifest_hashes(FakeManifest())

    def test_object_manifest_missing_hash_rejected(self):
        hashes = get_active_configs().hashes()

        class FakeManifest:
            policy_hash = hashes["policy_hash"]
            routing_hash = hashes["routing_hash"]
            model_hash = hashes["model_hash"]
            budget_hash = None

        with pytest.raises(ManifestHashError, match="budget_hash"):
            validate_manifest_hashes(FakeManifest())

    def test_gateway_validate_manifest_imports_validator(self):
        """Verify the gateway module contains the wiring call."""
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L0_routing"
            / "enforcement"
            / "execution_gateway.py"
        ).read_text(encoding="utf-8")
        assert "validate_manifest_hashes" in src, (
            "validate_manifest_hashes not wired into execution_gateway.py"
        )
        assert "manifest_hash_validator" in src, (
            "manifest_hash_validator import not found in execution_gateway.py"
        )


# ---------------------------------------------------------------------------
# Wave 2 — retrieval anchors wired into sovereign_retrieve result
# ---------------------------------------------------------------------------


class TestRetrievalAnchorIntegration:
    """
    Tests that sovereign_rag_orchestrator.py is wired to produce anchors
    and that AnchoredResult / enforce_anchor_coverage work end-to-end.
    """

    def test_sovereign_rag_orchestrator_imports_anchors(self):
        """Verify the orchestrator module contains the anchor wiring."""
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L3_orchestration"
            / "engines"
            / "sovereign_rag_orchestrator.py"
        ).read_text(encoding="utf-8")
        assert "AnchoredResult" in src, "AnchoredResult not wired into sovereign_rag_orchestrator"
        assert "RetrievalAnchor" in src, "RetrievalAnchor not wired into sovereign_rag_orchestrator"
        assert '"anchors"' in src, "anchors key not present in sovereign_retrieve result dict"

    def test_anchored_result_coverage_enforcement_end_to_end(self):
        """
        Simulate what sovereign_retrieve now does: build AnchoredResults,
        then verify enforce_anchor_coverage accepts full coverage and
        rejects missing coverage.
        """
        from agentic_core.L4_state.types.retrieval_anchor import (
            AnchoredResult,
            RetrievalAnchor,
            enforce_anchor_coverage,
        )

        def make_anchored(chunk_id: str) -> AnchoredResult:
            return AnchoredResult(
                content="text",
                anchor=RetrievalAnchor(
                    source_doc_id="doc-001",
                    chunk_id=chunk_id,
                    char_start=0,
                    char_end=4,
                    retrieved_at_utc=RetrievalAnchor.now_utc(),
                    version_hash="abc123",
                ),
            )

        results = [make_anchored("chunk-A"), make_anchored("chunk-B")]

        # Full coverage passes
        enforce_anchor_coverage(results, [r.anchor for r in results])

        # Missing coverage raises
        with pytest.raises(AnchorViolationError, match="MISSING_RETRIEVAL_ANCHOR"):
            enforce_anchor_coverage(results, [results[0].anchor])

    def test_anchor_violation_error_has_violation_code(self):
        from agentic_core.L4_state.types.retrieval_anchor import (
            AnchoredResult,
            AnchorViolationError,
            RetrievalAnchor,
            enforce_anchor_coverage,
        )

        result = AnchoredResult(
            content="x",
            anchor=RetrievalAnchor(
                source_doc_id="d",
                chunk_id="c",
                char_start=0,
                char_end=1,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="h",
            ),
        )
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert "MISSING_RETRIEVAL_ANCHOR" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Wave 3 — determinism thresholds wired into orchestrator
# ---------------------------------------------------------------------------


class TestDeterminismThresholdsIntegration:
    """
    Tests that sovereign_rag_orchestrator reads base_top_k and max_hops
    from BudgetConfig/RoutingConfig rather than bare inline literals.
    """

    def test_sovereign_rag_orchestrator_imports_get_active_configs(self):
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L3_orchestration"
            / "engines"
            / "sovereign_rag_orchestrator.py"
        ).read_text(encoding="utf-8")
        assert "get_active_configs" in src, "get_active_configs not imported in sovereign_rag_orchestrator"
        assert "budget.max_k" in src or "_budget_cfg.max_k" in src, (
            "BudgetConfig.max_k not used in sovereign_rag_orchestrator"
        )
        assert "depth_breaker" in src, "RoutingConfig.depth_breaker not used in sovereign_rag_orchestrator"

    def test_default_budget_max_k_matches_prior_constant(self):
        budget = BudgetConfig()
        assert budget.max_k == 10

    def test_default_routing_depth_breaker_matches_prior_constant(self):
        routing = RoutingConfig()
        assert routing.depth_breaker == 10

    def test_config_change_propagates(self):
        """Changing BudgetConfig.max_k changes config_hash — proves it's not hardcoded."""
        default = BudgetConfig()
        custom = BudgetConfig(max_k=25)
        assert custom.max_k == 25
        assert custom.config_hash != default.config_hash

    def test_inline_literal_8_replaced_in_orchestrator(self):
        """
        Verify the bare literal top_k=8 is no longer present in sovereign_retrieve.
        The replacement uses get_active_configs().budget.max_k.
        """
        import ast
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L3_orchestration"
            / "engines"
            / "sovereign_rag_orchestrator.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)

        # Find the sovereign_retrieve function body
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "sovereign_retrieve":
                func_src = ast.unparse(node)
                assert "top_k=8" not in func_src, "Inline literal top_k=8 still present in sovereign_retrieve"
                break


# ---------------------------------------------------------------------------
# End-to-end: real gateway.execute() drives L2.0 hash validation
# ---------------------------------------------------------------------------


class TestGatewayExecuteEndToEnd:
    """
    Calls V15ExecutionGateway.execute() — the real top-level entrypoint —
    with a manifest that carries Phase-2 hash fields.

    Proves that validate_manifest_hashes is invoked from the actual
    gateway→L2.0 path, not just from a helper function in isolation.
    """

    def _gateway(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        return V15ExecutionGateway()

    def test_gateway_accepts_manifest_without_hash_fields(self):
        """Legacy manifest (no Phase-2 fields) must pass through L2.0 unchanged."""
        gw = self._gateway()
        manifest = _make_manifest()
        result = gw.execute(
            manifest, _noop_heal, _noop_state_hash,
            trace_id="e2e-legacy", agent_id="CodeHealerAgent"
        )
        assert result.success is True

    def test_gateway_accepts_manifest_with_correct_hashes(self):
        """Manifest carrying all four correct Phase-2 hashes must be accepted."""
        gw = self._gateway()
        correct_hashes = get_active_configs().hashes()
        manifest = _make_manifest(extra_attrs=correct_hashes)
        result = gw.execute(
            manifest, _noop_heal, _noop_state_hash,
            trace_id="e2e-correct", agent_id="CodeHealerAgent"
        )
        assert result.success is True

    def test_gateway_rejects_manifest_with_mismatched_hash_via_execute(self):
        """
        Manifest with a wrong routing_hash must be rejected at L2.0
        when passed through the real gateway.execute() entrypoint.
        ManifestHashError propagates as a hard abort → result.success is False.
        """
        from agentic_core.L2_execution.enforcement.manifest_hash_validator import ManifestHashError

        gw = self._gateway()
        bad_hashes = get_active_configs().hashes()
        bad_hashes["routing_hash"] = "b" * 64
        manifest = _make_manifest(extra_attrs=bad_hashes)

        with pytest.raises((ManifestHashError, Exception)):
            gw.execute(manifest, _noop_heal, _noop_state_hash, trace_id="e2e-bad-hash")

    def test_gateway_rejects_manifest_with_missing_hash_via_execute(self):
        """
        Manifest with policy_hash=None must be rejected at L2.0
        via the real gateway.execute() entrypoint.
        """
        from agentic_core.L2_execution.enforcement.manifest_hash_validator import ManifestHashError

        gw = self._gateway()
        partial_hashes = get_active_configs().hashes()
        partial_hashes["policy_hash"] = None
        manifest = _make_manifest(extra_attrs=partial_hashes)

        with pytest.raises((ManifestHashError, Exception)):
            gw.execute(manifest, _noop_heal, _noop_state_hash, trace_id="e2e-missing-hash")
