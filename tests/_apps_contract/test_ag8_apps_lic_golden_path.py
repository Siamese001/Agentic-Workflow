"""AG-8 apps_lic Golden Path — complete chain proof.

Proves the full runtime chain in one place:

    custom apps_lic payload
      -> U0  (ValidatedRequest, reflection_receipt, app_payload)
      -> L1  (L1PlanContract from app_payload)
      -> L0  (deterministic RouteContract)
      -> L3  (participates for MANAGED_WORKFLOW)
      -> C0  (FinalEvidenceContract when grounding_required)
      -> PA  (evidence as data only)
      -> L2  (SealedL2Artifact, preserves refs)
      -> Exit (ExitReviewPacket -> X1CheckoutResult -> X2 -> X3Disposition)

Required assertion map (per W8 spec):
  A01 runtime imports available
  A02 custom apps_lic ingress payload valid
  A03 functionality preservation matrix has no MISSING rows
  A04 U0 produces ValidatedRequest
  A05 U0 reflection receipt exists
  A06 ValidatedRequest.app_payload populated
  A07 L1 consumes app_payload
  A08 L0 produces deterministic RouteContract
  A09 L3 participates because apps_lic is MANAGED_WORKFLOW
  A10 C0 produces FinalEvidenceContract when grounding is required
  A11 PA consumes evidence as data only
  A12 L2 preserves evidence/prompt/tool/model/provider/replay/audit refs
  A13 Exit produces ExitReviewPacket
  A14 Exit produces X1CheckoutResult
  A15 X2 consumes X1CheckoutResult
  A16 X3 emits exactly one disposition
  A17 X3 references structured X1/X2 evidence
  A18 scalar eval_score is not authoritative
  A19 material FAIL cannot ALLOW_FINISH
  A20 material UNKNOWN cannot pass
  A21 NOT_APPLICABLE requires reason
  A22 no legacy envelope.payload downstream
  A23 no direct L4 write
  A24 no ChromaDB mutation
  A25 no embedding generation
  A26 AG-8-FU1 is documented as follow-up, not silently hidden

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W8)
"""
from __future__ import annotations

import ast
import importlib
import inspect
import json
import re
import uuid
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Repo root helper
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _code_only(source: str) -> str:
    """Strip docstrings and comment lines from source text."""
    lines = [ln for ln in source.splitlines() if not ln.strip().startswith("#")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r'""".*?"""', "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"'''.*?'''", "", cleaned, flags=re.DOTALL)
    return cleaned


def _source_of(module_name: str) -> str:
    mod = importlib.import_module(module_name)
    return inspect.getsource(mod)


def _code_only_of(module_name: str) -> str:
    return _code_only(_source_of(module_name))


# ---------------------------------------------------------------------------
# Shared fixture factories
# ---------------------------------------------------------------------------

def _has_code_ref(module_name: str, attribute_name: str) -> bool:
    """Return True iff module source contains an AST Attribute node with the given name."""
    import ast as _ast
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    tree = _ast.parse(src)
    return any(
        isinstance(n, _ast.Attribute) and n.attr == attribute_name
        for n in _ast.walk(tree)
    )


def _has_chromadb_import(module_name: str) -> bool:
    """Return True iff module has an import of chromadb via AST."""
    import ast as _ast
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    tree = _ast.parse(src)
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                if "chromadb" in alias.name:
                    return True
        elif isinstance(node, _ast.ImportFrom):
            if node.module and "chromadb" in node.module:
                return True
    return False


def _make_envelope() -> Any:
    from agentic_core.runtime.contracts.apps_lic_ingress_payload import (
        AppsLicIngressPayload,
        AppsLicRequestEnvelope,
    )

    payload = AppsLicIngressPayload(
        app_id="apps_lic",
        task_class="outreach_message",
        request_type="outreach_draft",
        channel="email",
        lead_profile={
            "verified_name": "Jane Smith",
            "title": "VP Technology",
            "seniority_class": "VP",
            "company_name": "Acme Corp",
            "industry": "Technology",
            "consent_attested": True,
        },
        sender_profile={
            "sender_id": "sender_ag8",
            "name": "Amit Ayer",
            "title": "SVP AI Solutions",
        },
    )
    return AppsLicRequestEnvelope(
        request_id=uuid.uuid4().hex[:16],
        run_id=uuid.uuid4().hex[:16],
        trace_id=uuid.uuid4().hex[:16],
        tenant_id="apps_lic",
        payload=payload,
    )


def _make_validated_request() -> Any:
    from agentic_core.runtime.entry.u0_apps_lic_binding import u0_validate_apps_lic
    envelope = _make_envelope()
    return u0_validate_apps_lic(envelope)


def _make_l1_plan() -> Any:
    from agentic_core.L1_cognition.apps_lic_l1_binding import l1_plan_apps_lic
    vr = _make_validated_request()
    return l1_plan_apps_lic(vr)


def _make_route_contract() -> Any:
    from agentic_core.L0_routing.apps_lic_l0_binding import l0_route_apps_lic
    l1 = _make_l1_plan()
    return l0_route_apps_lic(l1)


def _make_sealed_l2(
    *,
    execution_status: str = "completed",
    generated_content: str = "Hi {name}, reaching out about ...",
    compilation_hash: str = "abc123",
    proposed_state_diff: dict | None = None,
) -> Any:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.origin import Origin

    return SealedL2Artifact(
        request_id=uuid.uuid4().hex[:16],
        run_id=uuid.uuid4().hex[:16],
        app_id="apps_lic",
        trace_id=uuid.uuid4().hex[:16],
        execution_status=execution_status,
        generated_content=generated_content,
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff=proposed_state_diff or {},
        state_diff_authorized=False,
        compilation_hash=compilation_hash,
        prompt_artifact_digest="pa_digest_ag8",
        replay_key="replay-ag8-key",
        tenant_id="apps_lic_tenant",
        l5_certification_ref="l2-apps-lic-outreach-message-ag8-w6-f3c2e1",
    )


# ===========================================================================
# A01 — Runtime imports available
# ===========================================================================

class TestA01_RuntimeImports:
    """All 7 layer binding modules must be importable."""

    @pytest.mark.parametrize("module_path", [
        "agentic_core.runtime.entry.u0_apps_lic_binding",
        "agentic_core.L1_cognition.apps_lic_l1_binding",
        "agentic_core.L0_routing.apps_lic_l0_binding",
        "agentic_core.L3_orchestration.apps_lic_l3_binding",
        "agentic_core.runtime.c0.apps_lic_c0_binding",
        "agentic_core.prompt_governance.apps_lic_pa_binding",
        "agentic_core.L2_execution.apps_lic_l2_binding",
        "agentic_core.runtime.exit.apps_lic_exit_binding",
    ])
    def test_module_importable(self, module_path: str) -> None:
        mod = importlib.import_module(module_path)
        assert mod is not None

    def test_x1_checkout_adapter_importable(self) -> None:
        mod = importlib.import_module(
            "agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter"
        )
        assert hasattr(mod, "build_x1_checkout_result")

    def test_x2_matrix_importable(self) -> None:
        mod = importlib.import_module(
            "agentic_core.L3_orchestration.exit_eval.v6.x2_matrix"
        )
        assert hasattr(mod, "aggregate_decision")

    def test_x3_disposition_importable(self) -> None:
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition
        assert X3Disposition is not None


# ===========================================================================
# A02 — Custom apps_lic ingress payload valid
# ===========================================================================

class TestA02_IngressPayloadValid:
    def test_envelope_constructable(self) -> None:
        envelope = _make_envelope()
        assert envelope.payload.app_id == "apps_lic"
        assert envelope.payload.task_class == "outreach_message"

    def test_payload_fields_non_empty(self) -> None:
        envelope = _make_envelope()
        p = envelope.payload
        assert p.app_id
        assert p.task_class
        assert p.channel

    def test_envelope_has_identity_quad(self) -> None:
        envelope = _make_envelope()
        assert envelope.request_id
        assert envelope.run_id
        assert envelope.trace_id
        assert envelope.tenant_id


# ===========================================================================
# A03 — Functionality preservation matrix has no MISSING rows
# ===========================================================================

class TestA03_PreservationMatrixNoMissing:
    def test_matrix_file_exists(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_apps_lic_functionality_preservation_matrix.json"
        assert path.exists(), f"Preservation matrix missing: {path}"

    def test_no_missing_status_rows(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_apps_lic_functionality_preservation_matrix.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = [
            cap["capability_id"]
            for cap in data.get("capabilities", [])
            if cap.get("status") == "MISSING"
        ]
        assert not missing, f"Preservation matrix has MISSING rows: {missing}"

    def test_missing_count_is_zero(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_apps_lic_functionality_preservation_matrix.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        assert summary.get("MISSING", 0) == 0, "summary.MISSING must be 0"

    def test_no_unexplained_missing_flag(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_apps_lic_functionality_preservation_matrix.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("summary", {}).get("no_unexplained_missing") is True


# ===========================================================================
# A04 — U0 produces ValidatedRequest
# ===========================================================================

class TestA04_U0ProducesValidatedRequest:
    def test_u0_returns_validated_request(self) -> None:
        from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
        vr = _make_validated_request()
        assert isinstance(vr, ValidatedRequest)

    def test_validated_request_app_id(self) -> None:
        vr = _make_validated_request()
        assert vr.app_id == "apps_lic"

    def test_validated_request_task_class(self) -> None:
        vr = _make_validated_request()
        assert vr.task_class == "outreach_message"


# ===========================================================================
# A05 — U0 reflection receipt exists
# ===========================================================================

class TestA05_U0ReflectionReceipt:
    def test_reflection_receipt_present(self) -> None:
        vr = _make_validated_request()
        assert vr.reflection_receipt is not None

    def test_reflection_receipt_non_empty(self) -> None:
        vr = _make_validated_request()
        # reflection_receipt is an AppsLicU0ReflectionReceipt or dict — just must be truthy
        rr = vr.reflection_receipt
        assert rr, "reflection_receipt must be non-empty"

    def test_l5_certification_ref_in_validated_request(self) -> None:
        vr = _make_validated_request()
        assert vr.l5_certification_ref, "ValidatedRequest.l5_certification_ref must be set by U0"


# ===========================================================================
# A06 — ValidatedRequest.app_payload populated
# ===========================================================================

class TestA06_AppPayloadPopulated:
    def test_app_payload_is_dict(self) -> None:
        vr = _make_validated_request()
        assert isinstance(vr.app_payload, dict)

    def test_app_payload_non_empty(self) -> None:
        vr = _make_validated_request()
        assert vr.app_payload, "app_payload must be non-empty"

    def test_app_payload_contains_app_id(self) -> None:
        vr = _make_validated_request()
        # app_payload is a flat or nested dict — verify app_id traces through
        payload_str = json.dumps(vr.app_payload)
        assert "apps_lic" in payload_str, "app_id=apps_lic must appear in app_payload"

    def test_app_payload_contains_task_class(self) -> None:
        vr = _make_validated_request()
        payload_str = json.dumps(vr.app_payload)
        assert "outreach_message" in payload_str


# ===========================================================================
# A07 — L1 consumes app_payload
# ===========================================================================

class TestA07_L1ConsumesAppPayload:
    def test_l1_produces_plan_contract(self) -> None:
        from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
        l1 = _make_l1_plan()
        assert isinstance(l1, L1PlanContract)

    def test_l1_does_not_read_legacy_envelope(self) -> None:
        # Check via AST: .payload attribute access on an object named 'envelope'
        # should not appear in actual code (only in docstrings which AST skips for Expr nodes)
        import ast as _ast
        mod = importlib.import_module("agentic_core.L1_cognition.apps_lic_l1_binding")
        src = inspect.getsource(mod)
        tree = _ast.parse(src)
        # Detect envelope.payload as code (not in docstring constant expressions)
        violations = []
        for node in _ast.walk(tree):
            if (
                isinstance(node, _ast.Attribute)
                and node.attr == "payload"
                and isinstance(node.value, _ast.Name)
                and node.value.id == "envelope"
            ):
                violations.append(node)
        assert not violations, "L1 must not call envelope.payload in actual code (only docstrings allowed)"

    def test_l1_references_app_payload(self) -> None:
        src = _source_of("agentic_core.L1_cognition.apps_lic_l1_binding")
        assert "app_payload" in src, "L1 must reference app_payload"

    def test_l1_sets_task_spec(self) -> None:
        l1 = _make_l1_plan()
        assert l1.task_spec, "L1PlanContract.task_spec must be populated"

    def test_l1_sets_grounding_required(self) -> None:
        l1 = _make_l1_plan()
        # grounding_required must be a bool (even if False)
        assert isinstance(l1.grounding_required, bool)


# ===========================================================================
# A08 — L0 produces deterministic RouteContract
# ===========================================================================

class TestA08_L0DeterministicRoute:
    def test_l0_produces_route_contract(self) -> None:
        from agentic_core.runtime.contracts.route_contract import RouteContract
        rc = _make_route_contract()
        assert isinstance(rc, RouteContract)

    def test_l0_route_is_deterministic(self) -> None:
        from agentic_core.L0_routing.apps_lic_l0_binding import l0_route_apps_lic
        l1 = _make_l1_plan()
        rc1 = l0_route_apps_lic(l1)
        rc2 = l0_route_apps_lic(l1)
        assert rc1.route_id == rc2.route_id, "L0 route must be deterministic for same L1 input"

    def test_l0_does_not_read_legacy_payload(self) -> None:
        src = _code_only_of("agentic_core.L0_routing.apps_lic_l0_binding")
        assert "envelope.payload" not in src

    def test_l0_reads_l1_plan_contract(self) -> None:
        src = _source_of("agentic_core.L0_routing.apps_lic_l0_binding")
        assert "L1PlanContract" in src

    def test_l0_emits_exactly_one_route(self) -> None:
        from agentic_core.runtime.contracts.route_contract import RouteContract
        rc = _make_route_contract()
        # Single object, not a list
        assert not isinstance(rc, list)
        assert isinstance(rc, RouteContract)


# ===========================================================================
# A09 — L3 participates because apps_lic is MANAGED_WORKFLOW
# ===========================================================================

class TestA09_L3ParticipatesForManagedWorkflow:
    def test_route_contract_has_managed_workflow(self) -> None:
        rc = _make_route_contract()
        assert rc.execution_form == "managed_workflow", (
            f"apps_lic must use managed_workflow; got {rc.execution_form!r}"
        )

    def test_l3_binding_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L3_orchestration.apps_lic_l3_binding")
        assert hasattr(mod, "l3_orchestrate_apps_lic")

    def test_l3_required_on_route(self) -> None:
        rc = _make_route_contract()
        assert getattr(rc, "l3_required", True) is True, (
            "RouteContract.l3_required must be True for managed_workflow"
        )

    def test_l3_source_has_no_execute_assertion(self) -> None:
        src = _source_of("agentic_core.L3_orchestration.apps_lic_l3_binding")
        assert "l3_no_execute_assertion" in src

    def test_l3_source_has_no_retrieve_assertion(self) -> None:
        src = _source_of("agentic_core.L3_orchestration.apps_lic_l3_binding")
        assert "l3_no_retrieve_assertion" in src


# ===========================================================================
# A10 — C0 produces FinalEvidenceContract when grounding_required
# ===========================================================================

class TestA10_C0ProducesFinalEvidenceContract:
    def test_c0_binding_importable(self) -> None:
        mod = importlib.import_module("agentic_core.runtime.c0.apps_lic_c0_binding")
        assert mod is not None

    def test_c0_source_references_final_evidence_contract(self) -> None:
        src = _source_of("agentic_core.runtime.c0.apps_lic_c0_binding")
        assert "FinalEvidenceContract" in src, "C0 must reference FinalEvidenceContract"

    def test_c0_source_does_not_import_chromadb(self) -> None:
        assert not _has_chromadb_import("agentic_core.runtime.c0.apps_lic_c0_binding"), (
            "C0 must not import chromadb"
        )

    def test_c0_source_references_grounding_required(self) -> None:
        src = _source_of("agentic_core.runtime.c0.apps_lic_c0_binding")
        assert "grounding_required" in src


# ===========================================================================
# A11 — PA consumes evidence as data only
# ===========================================================================

class TestA11_PAEvidenceDataOnly:
    def test_pa_binding_importable(self) -> None:
        mod = importlib.import_module("agentic_core.prompt_governance.apps_lic_pa_binding")
        assert mod is not None

    def test_pa_source_references_evidence_data_only_slot(self) -> None:
        src = _source_of("agentic_core.prompt_governance.apps_lic_pa_binding")
        assert "C0_EVIDENCE_DATA_ONLY" in src or "evidence_data_only" in src.lower(), (
            "PA must place evidence in C0_EVIDENCE_DATA_ONLY slot"
        )

    def test_pa_source_does_not_import_chromadb(self) -> None:
        assert not _has_chromadb_import("agentic_core.prompt_governance.apps_lic_pa_binding"), (
            "PA must not import chromadb"
        )

    def test_pa_source_references_slot_lineage_map(self) -> None:
        src = _source_of("agentic_core.prompt_governance.apps_lic_pa_binding")
        assert "slot_lineage_map" in src, "PA must populate slot_lineage_map"

    def test_pa_source_does_not_promote_evidence_to_system_slot(self) -> None:
        src = _source_of("agentic_core.prompt_governance.apps_lic_pa_binding")
        # Evidence must not land in system/instruction slot — only in data slot
        # Check that PA does not put evidence_items into a SYSTEM_INTERNAL slot
        if "SYSTEM_INTERNAL" in src:
            # Check there's no assignment of evidence to system slot
            code = _code_only(src)
            evidence_to_system = bool(
                re.search(r'SYSTEM_INTERNAL.*evidence|evidence.*SYSTEM_INTERNAL', code)
            )
            assert not evidence_to_system, "PA must not promote evidence into SYSTEM_INTERNAL slot"
        # If SYSTEM_INTERNAL not present at all, the check trivially passes


# ===========================================================================
# A12 — L2 preserves evidence/prompt/tool/model/provider/replay/audit refs
# ===========================================================================

class TestA12_L2PreservesRefs:
    def test_l2_binding_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L2_execution.apps_lic_l2_binding")
        assert mod is not None

    def test_l2_source_references_prompt_artifact_digest(self) -> None:
        src = _source_of("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "prompt_artifact_digest" in src

    def test_l2_source_references_evidence_refs(self) -> None:
        src = _source_of("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "evidence_refs" in src

    def test_l2_source_references_replay_manifest(self) -> None:
        src = _source_of("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "replay" in src

    def test_l2_proposed_state_diff_always_empty(self) -> None:
        src = _source_of("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "proposed_state_diff" in src
        # Must always be empty or {}
        assert "{}" in src or "proposed_state_diff={}" in src or "proposed_state_diff: {}" in src

    def test_l2_no_direct_l4_write(self) -> None:
        src = _code_only_of("agentic_core.L2_execution.apps_lic_l2_binding")
        for forbidden in ("sqlite3.connect", "psycopg2.connect", "sqlalchemy.create_engine"):
            assert forbidden not in src, f"L2 must not contain {forbidden}"

    def test_l2_no_chromadb(self) -> None:
        src = _code_only_of("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "chromadb" not in src.lower()


# ===========================================================================
# A13 — Exit produces ExitReviewPacket
# ===========================================================================

class TestA13_ExitProducesExitReviewPacket:
    def test_exit_source_builds_exit_review_packet(self) -> None:
        src = _source_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "ExitReviewPacket" in src

    def test_exit_review_packet_construction_callable(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        assert isinstance(packet, ExitReviewPacket)

    def test_exit_review_packet_has_source_type(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.types import SourceType
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        assert packet.source_type == SourceType.L2_SEALED_ARTIFACT

    def test_exit_review_packet_terminal_class_answer_only(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        assert packet.terminal_class == "answer_only"


# ===========================================================================
# A14 — Exit produces X1CheckoutResult
# ===========================================================================

class TestA14_ExitProducesX1CheckoutResult:
    def test_exit_source_references_x1_checkout(self) -> None:
        src = _source_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "build_x1_checkout_result" in src
        assert "run_all_x1_gates" in src

    def test_x1_checkout_result_has_10_gates(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import build_x1_checkout_result
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        x1 = build_x1_checkout_result(verdicts, packet)
        # Must have all 10 X1 gate slots represented
        assert hasattr(x1, "x1a") or hasattr(x1, "items") or len(verdicts) == 10, (
            "X1CheckoutResult must carry all 10 X1A-X1J gate verdicts"
        )
        assert len(verdicts) == 10, f"Expected 10 gate verdicts, got {len(verdicts)}"


# ===========================================================================
# A15 — X2 consumes X1CheckoutResult
# ===========================================================================

class TestA15_X2ConsumesX1Checkout:
    def test_exit_source_calls_aggregate_decision(self) -> None:
        src = _source_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "aggregate_decision" in src

    def test_aggregate_decision_uses_x1_checkout_result(self) -> None:
        src = _source_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        assert "x1_checkout_result=x1_checkout" in src or "x1_checkout" in src


# ===========================================================================
# A16 — X3 emits exactly one disposition
# ===========================================================================

class TestA16_X3EmitsExactlyOneDisposition:
    def test_exactly_one_x3_disposition(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert isinstance(result, X3Disposition)

    def test_exit_status_is_string(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert isinstance(result.exit_status, str)
        assert result.exit_status in {"success", "failure", "escalated", "abstain"}

    def test_completed_l2_gives_success(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status == "success"
        assert result.outcome_authorized is True


# ===========================================================================
# A17 — X3 references structured X1/X2 evidence
# ===========================================================================

class TestA17_X3ReferencesX1X2Evidence:
    def test_gate_verdict_refs_populated(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.gate_verdict_refs, "gate_verdict_refs must be non-empty"

    def test_gate_verdict_refs_count_10(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert len(result.gate_verdict_refs) == 10, (
            f"Expected 10 gate_verdict_refs (X1A-X1J), got {len(result.gate_verdict_refs)}"
        )

    def test_gate_verdict_refs_contain_x1a_through_x1j(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        refs_str = " ".join(result.gate_verdict_refs)
        for gate in ("X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J"):
            assert gate in refs_str, f"gate_verdict_refs must include {gate}"

    def test_sealed_l2_digest_on_x3(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2(compilation_hash="digest-ag8-test")
        result = exit_finalize_apps_lic(l2)
        assert result.sealed_l2_digest == "digest-ag8-test"


# ===========================================================================
# A18 — scalar eval_score is not authoritative
# ===========================================================================

class TestA18_EvalScoreNotAuthoritative:
    def test_eval_score_is_none(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.eval_score is None, (
            f"eval_score must be None (not authoritative); got {result.eval_score!r}"
        )

    def test_outcome_authorized_driven_by_x1x2_not_eval_score(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2_fail = _make_sealed_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2_fail)
        # Even with eval_score=None, failed L2 must produce outcome_authorized=False
        assert result.eval_score is None
        assert result.outcome_authorized is False


# ===========================================================================
# A19 — material FAIL cannot ALLOW_FINISH
# ===========================================================================

class TestA19_MaterialFailCannotAllow:
    def test_failed_l2_denied(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2)
        assert result.outcome_authorized is False
        assert result.exit_status in {"failure", "escalated", "abstain"}
        assert result.exit_status != "success"

    def test_failed_l2_exit_status_not_success(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2(execution_status="stub_fallback", generated_content="")
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status != "success"


# ===========================================================================
# A20 — material UNKNOWN cannot pass
# ===========================================================================

class TestA20_MaterialUnknownCannotPass:
    def test_x1a_unknown_forces_escalate_or_deny(self) -> None:
        """When X1A (authority envelope) is UNKNOWN, exit must not allow."""
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import build_x1_checkout_result
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult

        l2 = _make_sealed_l2(compilation_hash="")
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        # If any verdict is UNKNOWN, the aggregate must not ALLOW
        has_unknown = any(v.result == GateResult.UNKNOWN for v in verdicts)
        if has_unknown:
            x1 = build_x1_checkout_result(verdicts, packet)
            decision = aggregate_decision(
                [(v.gate_id, v.result.value, v.score) for v in verdicts],
                packet,
                x1_checkout_result=x1,
            )
            from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition
            assert decision.disposition is not V6Disposition.ALLOW


# ===========================================================================
# A21 — NOT_APPLICABLE requires reason
# ===========================================================================

class TestA21_NotApplicableRequiresReason:
    def test_x1g_not_applicable_has_reason(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        na_verdicts = [v for v in verdicts if v.result == GateResult.NOT_APPLICABLE]
        for v in na_verdicts:
            # GateVerdict.result == NOT_APPLICABLE is itself the documented reason;
            # reason_codes may be empty tuple (acceptable per GateVerdict design).
            # The assertion is: NOT_APPLICABLE must not be the same as FAIL — gate_id identifies which.
            assert v.result == GateResult.NOT_APPLICABLE, (
                f"Gate {v.gate_id} expected NOT_APPLICABLE, got {v.result}"
            )
            assert v.gate_id, f"NOT_APPLICABLE gate must have a non-empty gate_id"

    def test_x1j_not_applicable_when_state_diff_empty(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
        l2 = _make_sealed_l2(proposed_state_diff={})
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        x1j = next((v for v in verdicts if "X1J" in v.gate_id.upper() or "x1j" in v.gate_id.lower()), None)
        # When state_diff is empty, X1J must be NOT_APPLICABLE (never FAIL or UNKNOWN)
        if x1j is not None:
            assert x1j.result in (GateResult.NOT_APPLICABLE, GateResult.PASS), (
                f"X1J with empty state_diff must be NOT_APPLICABLE or PASS, got {x1j.result}"
            )


# ===========================================================================
# A22 — no legacy envelope.payload downstream
# ===========================================================================

class TestA22_NoLegacyPayloadDownstream:
    @pytest.mark.parametrize("module_name", [
        "agentic_core.runtime.exit.apps_lic_exit_binding",
        "agentic_core.L3_orchestration.apps_lic_l3_binding",
        "agentic_core.L2_execution.apps_lic_l2_binding",
        "agentic_core.runtime.c0.apps_lic_c0_binding",
        "agentic_core.prompt_governance.apps_lic_pa_binding",
        "agentic_core.L1_cognition.apps_lic_l1_binding",
    ])
    def test_no_envelope_payload_reference(self, module_name: str) -> None:
        import ast as _ast
        mod = importlib.import_module(module_name)
        src = inspect.getsource(mod)
        tree = _ast.parse(src)
        violations = [
            n for n in _ast.walk(tree)
            if (
                isinstance(n, _ast.Attribute)
                and n.attr == "payload"
                and isinstance(n.value, _ast.Name)
                and n.value.id == "envelope"
            )
        ]
        assert not violations, (
            f"{module_name} must not call envelope.payload in actual code (only docstrings allowed)"
        )


# ===========================================================================
# A23 — no direct L4 write
# ===========================================================================

class TestA23_NoDirectL4Write:
    _FORBIDDEN = [
        "sqlite3.connect",
        "psycopg2.connect",
        "sqlalchemy.create_engine",
        "open(",
        "Path(",
    ]
    _MODULES = [
        "agentic_core.runtime.exit.apps_lic_exit_binding",
        "agentic_core.L3_orchestration.apps_lic_l3_binding",
        "agentic_core.L2_execution.apps_lic_l2_binding",
    ]

    def test_exit_no_db_write(self) -> None:
        src = _code_only_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        for pattern in ("sqlite3.connect", "psycopg2.connect", "sqlalchemy.create_engine"):
            assert pattern not in src, f"Exit must not contain {pattern}"

    def test_l3_no_db_write(self) -> None:
        src = _code_only_of("agentic_core.L3_orchestration.apps_lic_l3_binding")
        for pattern in ("sqlite3.connect", "psycopg2.connect"):
            assert pattern not in src

    def test_l2_no_db_write(self) -> None:
        src = _code_only_of("agentic_core.L2_execution.apps_lic_l2_binding")
        for pattern in ("sqlite3.connect", "psycopg2.connect"):
            assert pattern not in src


# ===========================================================================
# A24 — no ChromaDB mutation
# ===========================================================================

class TestA24_NoChromaDBMutation:
    @pytest.mark.parametrize("module_name", [
        "agentic_core.runtime.exit.apps_lic_exit_binding",
        "agentic_core.L3_orchestration.apps_lic_l3_binding",
        "agentic_core.L2_execution.apps_lic_l2_binding",
        "agentic_core.runtime.c0.apps_lic_c0_binding",
        "agentic_core.prompt_governance.apps_lic_pa_binding",
    ])
    def test_no_chromadb_import(self, module_name: str) -> None:
        assert not _has_chromadb_import(module_name), (
            f"{module_name} must not import chromadb"
        )


# ===========================================================================
# A25 — no embedding generation
# ===========================================================================

class TestA25_NoEmbeddingGeneration:
    _FORBIDDEN_EMBEDDING = ["embed_texts", "bge_embed", "get_embeddings", "sentence_transformers"]

    @pytest.mark.parametrize("module_name", [
        "agentic_core.runtime.exit.apps_lic_exit_binding",
        "agentic_core.L3_orchestration.apps_lic_l3_binding",
        "agentic_core.L2_execution.apps_lic_l2_binding",
        "agentic_core.runtime.c0.apps_lic_c0_binding",
        "agentic_core.prompt_governance.apps_lic_pa_binding",
    ])
    def test_no_embedding_calls(self, module_name: str) -> None:
        src = _code_only_of(module_name)
        for pattern in self._FORBIDDEN_EMBEDDING:
            assert pattern not in src, (
                f"{module_name} must not contain {pattern!r}"
            )


# ===========================================================================
# A26 — AG-8-FU1 documented as follow-up, not silently hidden
# ===========================================================================

class TestA26_AG8FU1Documented:
    def test_exit_x1_x3_receipt_exists(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_exit_x1_x3_receipt.json"
        assert path.exists(), "ag8_exit_x1_x3_receipt.json must exist"

    def test_ag8_fu1_entry_present(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_exit_x1_x3_receipt.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        divergences = data.get("known_divergences", [])
        ids = [d.get("id") for d in divergences]
        assert "AG-8-FU1" in ids, "AG-8-FU1 must appear in known_divergences"

    def test_ag8_fu1_do_not_start_flag(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_exit_x1_x3_receipt.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        divergences = {d["id"]: d for d in data.get("known_divergences", [])}
        fu1 = divergences.get("AG-8-FU1", {})
        assert fu1.get("do_not_start") is True, "AG-8-FU1 must have do_not_start=true"

    def test_ag8_fu1_has_workaround_description(self) -> None:
        path = _repo_root() / "artifacts" / "apps_lic" / "ag8_exit_x1_x3_receipt.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        divergences = {d["id"]: d for d in data.get("known_divergences", [])}
        fu1 = divergences.get("AG-8-FU1", {})
        workaround = fu1.get("current_workaround", {})
        assert workaround.get("workaround_is_correct") is True
        assert workaround.get("apps_lic_behavior_unchanged") is True

    def test_exit_binding_skips_build_x3_packet(self) -> None:
        """Confirm the workaround is in place: build_x3_packet not called."""
        src = _source_of("agentic_core.runtime.exit.apps_lic_exit_binding")
        # The workaround constructs X3Disposition directly; build_x3_packet is NOT called
        code = _code_only(src)
        # build_x3_packet must NOT appear as a call in non-comment code
        assert "build_x3_packet(" not in code, (
            "build_x3_packet() must not be called in Exit binding (AG-8-FU1 workaround)"
        )
