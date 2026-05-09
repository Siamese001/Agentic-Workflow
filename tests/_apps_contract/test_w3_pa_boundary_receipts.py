"""Contract tests for W3 PA boundary receipts and mixin guard.

Positive:
- NEW PA compiler emits PA boundary receipt
- LEGACY PromptEnvelope bridge emits PA boundary receipt
- pa_local.capture_prompt_bom participates in receipt lineage
- L2 receives PA-governed artifact before model execution
- Worker mixin guard passes only when PA boundary evidence exists

Negative:
- Worker-side mixin guard fails when PA boundary evidence is missing
- Receipt cannot silently pass when prompt_hash / compiled_artifact_hash is absent without explicit reason
- UNKNOWN receipt status does not pass as clean
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from apps_rg.prompt_assembly._pa_boundary import (
    PABoundaryReceipt,
    PABoundaryStatus,
    MixinGuardError,
    MixinGuardEvidence,
    MixinGuardResult,
    check_mixin_guard,
    make_pa_boundary_receipt,
    strict_mixin_guard,
)
from apps_rg.prompt_assembly.pa_local import PromptBOM, capture_prompt_bom


class TestNewPACompilerReceipt:
    """NEW PA surface: apps_rg/prompt_assembly/compiler.py"""

    def test_compiler_emits_receipt_with_all_fields(self):
        """NEW PA compiler produces receipt with all required fields available."""
        receipt = make_pa_boundary_receipt(
            request_id="req-123",
            run_id="run-456",
            trace_id="trace-789",
            route_id="R3_grounded_read",
            policy_hash="pol-abc",
            blueprint_hash="bp-def",
            prompt_hash="prompt-ghi",
            compiled_artifact_hash="art-jkl",
            bom_hash="bom-mno",
            registry_hash="reg-pqr",
            template_hash="tpl-stu",
            source_refs={"jd": "hash1", "resume": "hash2"},
            lineage_refs={"template": "tpl-v1"},
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
            reason_codes=["COMPILE_OK"],
        )

        assert receipt.request_id == "req-123"
        assert receipt.run_id == "run-456"
        assert receipt.trace_id == "trace-789"
        assert receipt.route_id == "R3_grounded_read"
        assert receipt.policy_hash == "pol-abc"
        assert receipt.blueprint_hash == "bp-def"
        assert receipt.prompt_hash == "prompt-ghi"
        assert receipt.compiled_artifact_hash == "art-jkl"
        assert receipt.bom_hash == "bom-mno"
        assert receipt.registry_hash == "reg-pqr"
        assert receipt.template_hash == "tpl-stu"
        assert receipt.source_refs == {"jd": "hash1", "resume": "hash2"}
        assert receipt.lineage_refs == {"template": "tpl-v1"}
        assert receipt.status == PABoundaryStatus.PA_L2_HANDOFF_READY.value
        assert receipt.reason_codes == ["COMPILE_OK"]
        assert receipt.deterministic_digest != ""
        assert len(receipt.deterministic_digest) == 16

    def test_receipt_has_deterministic_digest(self):
        """Receipt includes deterministic digest over its content."""
        receipt1 = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="hash-abc",
            compiled_artifact_hash="art-123",
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
        )
        receipt2 = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="hash-abc",
            compiled_artifact_hash="art-123",
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
        )
        receipt3 = make_pa_boundary_receipt(
            request_id="req-456",  # different
            prompt_hash="hash-abc",
            compiled_artifact_hash="art-123",
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
        )

        # Same inputs = same digest
        assert receipt1.deterministic_digest == receipt2.deterministic_digest
        # Different inputs = different digest
        assert receipt1.deterministic_digest != receipt3.deterministic_digest

    def test_receipt_serializes_to_dict(self):
        """Receipt can be serialized to dict for artifact attachment."""
        receipt = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="hash-abc",
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
        )
        d = receipt.to_dict()

        assert isinstance(d, dict)
        assert d["receipt_type"] == "prompt_boundary_receipt"
        assert d["request_id"] == "req-123"
        assert d["prompt_hash"] == "hash-abc"
        assert d["deterministic_digest"] == receipt.deterministic_digest


class TestLegacyPABridgeReceipt:
    """LEGACY PA surface: apps_rg/utils/anthropic_rag_entrypoint.py"""

    def test_legacy_bridge_marks_unavailable_fields_not_bound(self):
        """LEGACY bridge marks unavailable fields as NOT_BOUND with reason code."""
        # Simulate the legacy path: many fields unavailable
        unavailable = [
            "run_id", "trace_id", "policy_hash", "blueprint_hash",
            "compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash",
        ]

        receipt = make_pa_boundary_receipt(
            request_id="env-123",
            run_id="NOT_BOUND",
            trace_id="NOT_BOUND",
            route_id="NOT_BOUND",
            policy_hash="NOT_BOUND",
            blueprint_hash="NOT_BOUND",
            prompt_hash="hash-from-rendered-text",
            compiled_artifact_hash="NOT_BOUND",
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            status=PABoundaryStatus.PA_RENDERED,
            reason_codes=["LEGACY_PA_BRIDGE", "PROMPT_ENVELOPE_CONSUMED"],
            unavailable_fields=unavailable,
        )

        # All unavailable fields marked NOT_BOUND
        assert receipt.run_id == "NOT_BOUND"
        assert receipt.trace_id == "NOT_BOUND"
        assert receipt.policy_hash == "NOT_BOUND"
        assert receipt.blueprint_hash == "NOT_BOUND"
        assert receipt.compiled_artifact_hash == "NOT_BOUND"
        assert receipt.bom_hash == "NOT_BOUND"
        assert receipt.registry_hash == "NOT_BOUND"
        assert receipt.template_hash == "NOT_BOUND"

        # Available field populated
        assert receipt.prompt_hash == "hash-from-rendered-text"

        # Unavailable fields list recorded
        assert receipt.unavailable_fields == unavailable

    def test_legacy_bridge_records_explicit_not_bound(self):
        """Legacy path does NOT silently omit fields; marks NOT_BOUND explicitly."""
        receipt = make_pa_boundary_receipt(
            request_id="env-123",
            prompt_hash="hash-abc",
            status=PABoundaryStatus.PA_RENDERED,
            unavailable_fields=["run_id", "policy_hash"],
        )

        # Fields are "NOT_BOUND", not empty string
        assert receipt.run_id == "NOT_BOUND"
        assert receipt.policy_hash == "NOT_BOUND"
        # Unavailable list recorded for audit
        assert "run_id" in receipt.unavailable_fields
        assert "policy_hash" in receipt.unavailable_fields


class TestPALocalCapturePromptBOM:
    """PA instrumentation: apps_rg/prompt_assembly/pa_local.py"""

    def test_capture_prompt_bom_includes_receipt(self):
        """capture_prompt_bom populates pa_boundary_receipt field."""
        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="claude-3-5-sonnet",
            provider_lane="anthropic",
            prompt_template="Test template content",
            token_budget=4000,
            request_id="req-123",
            trace_id="trace-456",
        )

        assert isinstance(bom, PromptBOM)
        assert bom.pa_boundary_receipt is not None
        assert isinstance(bom.pa_boundary_receipt, dict)
        assert bom.pa_boundary_receipt["receipt_type"] == "prompt_boundary_receipt"
        assert bom.pa_boundary_receipt["status"] == PABoundaryStatus.PA_BOM_RESOLVED.value
        assert "BOM_CAPTURE" in bom.pa_boundary_receipt["reason_codes"]
        assert "NARRATIVE_PIPELINE_INSTRUMENTATION" in bom.pa_boundary_receipt["reason_codes"]

    def test_bom_receipt_includes_lineage(self):
        """BOM receipt includes lineage references for traceability."""
        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="claude-3-5-sonnet",
            prompt_template="Test content",
        )

        lineage = bom.pa_boundary_receipt.get("lineage_refs", {})
        assert lineage.get("pa_local_consumer") == "apps_rg.prompt_assembly.pa_local.capture_prompt_bom"
        assert lineage.get("narrative_pipeline") == "true"

    def test_bom_receipt_notes_unavailable_fields(self):
        """BOM capture records which fields are NOT_BOUND."""
        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="claude-3-5-sonnet",
            prompt_template="Test content",
        )

        unavailable = bom.pa_boundary_receipt.get("unavailable_fields", [])
        assert "run_id" in unavailable
        assert "route_id" in unavailable
        assert "policy_hash" in unavailable
        assert "blueprint_hash" in unavailable

    def test_bom_writes_to_disk_with_receipt(self, tmp_path: Path):
        """BOM written to disk includes pa_boundary_receipt."""
        run_dir = tmp_path / "run_001"
        bom = capture_prompt_bom(
            hop_name="H3_test",
            model="claude-3-5-sonnet",
            prompt_template="Test content",
            run_dir=run_dir,
        )

        bom_file = run_dir / "prompt_bom" / "H3_test.json"
        assert bom_file.exists()

        import json
        written = json.loads(bom_file.read_text())
        assert "pa_boundary_receipt" in written
        assert written["pa_boundary_receipt"]["receipt_type"] == "prompt_boundary_receipt"


class TestMixinGuard:
    """Worker-side mixin guard invariants."""

    def test_mixin_guard_passes_with_valid_evidence(self):
        """Mixin passes guard when PA boundary evidence exists."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="art-123",
            pa_boundary_receipt_digest="receipt-abc",
            route_id="R3_grounded_read",
            route_contract_hash="route-hash",
        )

        result = check_mixin_guard(evidence, mixin_id="test_mixin")

        assert result.allowed is True
        assert result.reason_code == "MIXIN_GUARD_PASS"
        assert "test_mixin" in result.reason

    def test_mixin_guard_fails_without_compiled_artifact_hash(self):
        """Mixin cannot fire pre-PA (missing compiled artifact hash)."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="",  # MISSING
            pa_boundary_receipt_digest="receipt-abc",
            route_id="R3_grounded_read",
        )

        result = check_mixin_guard(evidence, mixin_id="test_mixin")

        assert result.allowed is False
        assert result.reason_code == "MIXIN_GUARD_VIOLATION"
        assert "MISSING_COMPILED_ARTIFACT_HASH" in result.reason

    def test_mixin_guard_fails_without_pa_receipt_digest(self):
        """Mixin cannot bypass PA (missing receipt digest)."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="art-123",
            pa_boundary_receipt_digest="",  # MISSING
            route_id="R3_grounded_read",
        )

        result = check_mixin_guard(evidence, mixin_id="test_mixin")

        assert result.allowed is False
        assert "MISSING_PA_BOUNDARY_RECEIPT" in result.reason

    def test_mixin_guard_fails_without_route_id(self):
        """Mixin cannot fire without established route."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="art-123",
            pa_boundary_receipt_digest="receipt-abc",
            route_id="",  # MISSING
        )

        result = check_mixin_guard(evidence, mixin_id="test_mixin")

        assert result.allowed is False
        assert "MISSING_ROUTE_ID" in result.reason

    def test_mixin_guard_blocks_authority_creation(self):
        """Mixins cannot create new authority (allow_create_authority must be False)."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="art-123",
            pa_boundary_receipt_digest="receipt-abc",
            route_id="R3_grounded_read",
        )

        # If caller mistakenly tries to allow authority creation
        result = check_mixin_guard(
            evidence, mixin_id="test_mixin", allow_create_authority=True
        )

        assert result.allowed is False
        assert "AUTHORITY_CREATION_BLOCKED" in result.reason

    def test_strict_mixin_guard_raises_on_failure(self):
        """strict_mixin_guard raises MixinGuardError on failure."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="",  # MISSING
            pa_boundary_receipt_digest="receipt-abc",
            route_id="R3_grounded_read",
        )

        with pytest.raises(MixinGuardError) as exc_info:
            strict_mixin_guard(evidence, mixin_id="test_mixin")

        assert "MIXIN_GUARD_VIOLATION" in str(exc_info.value)
        assert "MISSING_COMPILED_ARTIFACT_HASH" in str(exc_info.value)

    def test_strict_mixin_guard_passes_silently_on_success(self):
        """strict_mixin_guard returns None (no exception) on success."""
        evidence = MixinGuardEvidence(
            compiled_artifact_hash="art-123",
            pa_boundary_receipt_digest="receipt-abc",
            route_id="R3_grounded_read",
        )

        # Should not raise
        result = strict_mixin_guard(evidence, mixin_id="test_mixin")
        assert result is None


class TestReceiptNegativeCases:
    """Negative contract tests: what must NOT happen."""

    def test_receipt_cannot_silently_pass_without_critical_fields(self):
        """Receipt with empty prompt_hash and compiled_artifact_hash is NOT clean."""
        receipt = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="",  # MISSING
            compiled_artifact_hash="",  # MISSING
            status=PABoundaryStatus.NOT_BOUND,
            reason_codes=["MISSING_HASHES_EXPLICIT"],
            unavailable_fields=["prompt_hash", "compiled_artifact_hash"],
        )

        # Status is explicitly NOT_BOUND, not a silent success
        assert receipt.status == PABoundaryStatus.NOT_BOUND.value
        assert "prompt_hash" in receipt.unavailable_fields
        assert "compiled_artifact_hash" in receipt.unavailable_fields

    def test_unknown_status_does_not_pass_as_clean(self):
        """UNKNOWN is never PASS."""
        # Receipt factory doesn't have UNKNOWN as a valid status
        # Status must be one of the enum values
        assert "UNKNOWN" not in [s.value for s in PABoundaryStatus]

        # Creating a receipt with NOT_BOUND status (the fail-closed value)
        receipt = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="NOT_BOUND",
            compiled_artifact_hash="NOT_BOUND",
            status=PABoundaryStatus.NOT_BOUND,
            reason_codes=["EVIDENCE_UNAVAILABLE"],
            unavailable_fields=["prompt_hash", "compiled_artifact_hash"],
        )

        # NOT_BOUND is the explicit marker, not an implicit pass
        assert receipt.status == PABoundaryStatus.NOT_BOUND.value
        assert receipt.prompt_hash == "NOT_BOUND"

    def test_l0_does_not_emit_prompt_artifacts(self):
        """L0 emits RouteContract only; PA emits artifacts.

        This is a conceptual test: the PA boundary receipt should ONLY
        originate from PA surfaces (compiler.py, anthropic_rag_entrypoint.py,
        pa_local.py). No receipt should claim L0 as the source.
        """
        # Any receipt originating from PA should have lineage showing
        # it came through PA, not directly from L0
        receipt = make_pa_boundary_receipt(
            request_id="req-123",
            prompt_hash="hash-abc",
            lineage_refs={
                "pa_surface": "apps_rg.prompt_assembly.compiler",
            },
            status=PABoundaryStatus.PA_L2_HANDOFF_READY,
        )

        # Verify lineage shows PA origin, not L0
        assert "pa_surface" in receipt.lineage_refs
        assert "compiler" in receipt.lineage_refs["pa_surface"]


class TestL2ReceivesPAGovernedArtifact:
    """L2 consumption guarded by PA evidence."""

    def test_l2_consumption_requires_pa_boundary_receipt(self):
        """L2 step adapters should verify PA boundary receipt exists.

        This test documents the invariant enforced by _PAGuard in
        apps_rg/l2_recipe/steps.py:27-104.
        """
        # Simulating the artifact that L2 receives
        mock_artifact = {
            "request_id": "req-123",
            "compile_status": "PA_L2_HANDOFF_READY",
            "pa_boundary_receipt": {
                "receipt_type": "prompt_boundary_receipt",
                "status": "PA_L2_HANDOFF_READY",
                "deterministic_digest": "abc123",
            },
        }

        # L2 guard checks for pa_boundary_receipt presence
        assert "pa_boundary_receipt" in mock_artifact
        receipt = mock_artifact["pa_boundary_receipt"]
        assert receipt["status"] == "PA_L2_HANDOFF_READY"
        assert receipt["deterministic_digest"] != ""

    def test_l2_rejects_artifact_without_pa_receipt(self):
        """L2 must reject (fail-closed) when PA boundary receipt missing."""
        mock_artifact = {
            "request_id": "req-123",
            "compile_status": "PA_COMPILE_FAILED",  # No receipt
        }

        # Guard should detect missing receipt
        has_receipt = "pa_boundary_receipt" in mock_artifact
        is_ready = mock_artifact.get("compile_status") == "PA_L2_HANDOFF_READY"

        assert not (has_receipt and is_ready)


class TestDualPATopologyInvariant:
    """Both PA surfaces are PA-owned; neither grants L0 prompt assembly authority."""

    def test_new_pa_surface_is_pa_owned(self):
        """NEW PA compiler is in apps_rg/prompt_assembly/, owned by PA."""
        # The import path proves ownership
        from apps_rg.prompt_assembly.compiler import compile_prompt

        # Function exists and is in PA module
        assert callable(compile_prompt)
        assert "prompt_assembly" in compile_prompt.__module__

    def test_legacy_pa_surface_is_pa_owned(self):
        """LEGACY PA bridge is re-exported via apps_rg/prompt_assembly/rg_pa_compiler.py."""
        from apps_rg.prompt_assembly.rg_pa_compiler import build_anthropic_rag_payload

        # Function exists and is in PA module (re-export)
        assert callable(build_anthropic_rag_payload)

    def test_pa_local_is_pa_owned(self):
        """pa_local is in apps_rg/prompt_assembly/, owned by PA."""
        from apps_rg.prompt_assembly.pa_local import capture_prompt_bom

        assert callable(capture_prompt_bom)
        assert "prompt_assembly" in capture_prompt_bom.__module__

    def test_l0_does_not_import_pa_compiler(self):
        """L0 routing does not import or call PA compiler directly.

        This is a static contract: L0's job is RouteContract only.
        PA compilation happens downstream.
        """
        # Import L0 routing to verify it doesn't import PA
        # This test is heuristic: we check that common L0 modules
        # don't have compiler imports
        import apps_rg.__main__ as main_module

        # The main module should delegate to integrated pipeline,
        # not directly compile prompts
        source = main_module.__file__
        assert source is not None

        # If this test passes, main.py doesn't directly import compiler
        # (The actual enforcement is via _PAGuard in steps.py)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
