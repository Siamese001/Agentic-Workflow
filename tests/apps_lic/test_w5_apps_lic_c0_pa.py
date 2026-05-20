"""W5 apps_lic C0/PA governed evidence handling — required proof tests.

Proves the W5 receipt criteria:

C0 tests:
  TC01. C0 emits FinalEvidenceContract for grounded apps_lic route.
  TC02. C0 blocks (WEAK/EMPTY support_status) when grounding_required=True
        and required evidence (lead_profile) is missing.
  TC03. EvidenceItem.allowed_prompt_slot == C0_EVIDENCE_DATA_ONLY on every item.
  TC04. EvidenceItem has source_id, source_type, chunk_digest, citation_anchor,
        source_lineage, support_status populated.
  TC05. fact_vec_ref/query_vec_ref are NOT_APPLICABLE with reason when no dense
        retrieval occurs.
  TC06. dense_score/bm25_score/metadata_score carry sentinel -1.0 (not 0.0 fake).
  TC07. citation_map and source_lineage_map are populated.
  TC08. evidence_strata has at least MUST_USE (for lead/campaign).
  TC09. contradiction_report exists and is NOT_APPLICABLE with reason.
  TC10. C0 does not import or call ChromaDB.
  TC11. C0 does not generate embeddings.
  TC12. C0 does not write L4.

PA tests:
  TPA01. PA emits CompiledPromptArtifact.
  TPA02. slot_lineage_map includes apps_lic evidence lineage (C0 fec hash ref).
  TPA03. component_hash_map includes evidence / l1_plan / route / app_payload_task_data.
  TPA04. prompt_hash is deterministic for same inputs (same compilation_hash).
  TPA05. PA keeps C0 evidence as data only (user_block_2 carries USER_INTENT origin).
  TPA06. PA does not promote lower-authority content into system/instructions.
  TPA07. PA does not read legacy envelope.payload.
  TPA08. PA rejects EvidenceItem with wrong allowed_prompt_slot.
  TPA09. PA system block carries SYSTEM_INTERNAL origin.
  TPA10. PA does not import or call ChromaDB.
  TPA11. PA does not generate embeddings.
  TPA12. PA does not write L4.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W5)
"""
from __future__ import annotations

import dataclasses
import importlib
import inspect
import json
from typing import Any

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_NOT_APPLICABLE,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.origin import Origin
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt
from apps_lic.runtime.bindings.l1_binding import l1_plan_apps_lic
from apps_lic.runtime.bindings.l0_binding import l0_route_apps_lic
from apps_lic.runtime.bindings.c0_binding import (
    APPS_LIC_C0_CERT_REF,
    c0_retrieve_apps_lic,
)
from apps_lic.runtime.bindings.pa_binding import (
    APPS_LIC_PA_CERT_REF,
    APPS_LIC_TARGET_MODEL,
    pa_compose_apps_lic,
)


# ---------------------------------------------------------------------------
# Canonical valid fixture
# ---------------------------------------------------------------------------

_VALID_RAW: dict[str, Any] = {
    "apps_lic_contract_version": "v1",
    "transport": {
        "app_id": "apps_lic",
        "task_class": "outreach_message",
        "request_id": "req_lic_w5_001",
        "run_id": "run_lic_w5_001",
        "tenant_id": "apps_lic",
        "trace_id": "trace_lic_w5_001",
        "submitted_at": "2026-05-10T12:00:00+00:00",
    },
    "campaign": {
        "request_type": "outreach_draft",
        "campaign_objective": "Drive renewal conversation with enterprise prospect",
        "channel": "email",
        "audience_segment": "enterprise_renewal",
        "action_required": "draft_and_cert",
        "workflow_required": "managed_workflow_hop",
        "grounding_required": True,
        "side_effect_class": "read_only",
    },
    "forbidden_send_modes": {
        "modes": [
            "send_now",
            "auto_send",
            "connector_send",
            "email_outbox_send",
            "linkedin_send",
            "sms_send",
            "external_http_post",
        ]
    },
    "entity_refs": {
        "lead_profile": {
            "verified_name": "Jane Smith",
            "title": "VP Technology",
            "seniority_class": "VP",
            "company_name": "Acme Corp",
            "industry": "Technology",
            "consent_attested": True,
        },
        "lead_ref": None,
        "sender_profile": {
            "sender_id": "sender_001",
            "name": "Amit Ayer",
            "title": "SVP AI Solutions",
        },
        "sender_ref": None,
        "company_profile": None,
        "company_ref": None,
    },
    "personalization": {
        "inputs": {"recent_win_reference": "Acme closed $2M deal in Q1"},
    },
    "generation_hints": {},
    "tone_constraints": {},
    "output_format": {},
    "research_requirements": {},
    "routing_policy": {},
    "validation_policy": {},
    "gate_decision_policy": {"halt_on_validation_failure": True},
    "qa_report": {},
    "integration_target": None,
    "hitl_policy": {"bypass_hitl_freeze": False},
    "pii_policy": {
        "pii_detection_mode": "strict",
        "redact_on_warn": True,
        "fail_on_pii_detect": True,
    },
    "governance_shield": {"shield_required": True},
    "antipattern_policy": {"enabled": True},
    "source_lineage": {"source_lineage_required": True},
    "ab_test": {},
    "replay_audit": {
        "idempotency_key": "idem_lic_w5_001",
        "replay_refs": [],
        "audit_refs": [],
    },
    "runtime_customization_package": {
        # package_digest = SHA-256 of canonical JSON of {} (no profile_refs supplied).
        # Recompute if any fields are added: hashlib.sha256(json.dumps(
        #   {k: v for k, v in pkg.items() if k != 'package_digest'},
        #   sort_keys=True, separators=(',',':')).encode()).hexdigest()
        "package_digest": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
    },
    "payload_digest": "",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_validated_request(raw: dict[str, Any] | None = None) -> ValidatedRequest:
    vr, _ = apps_lic_u0_adapt(raw or _VALID_RAW)
    return vr


def _make_l1(vr: ValidatedRequest) -> L1PlanContract:
    return l1_plan_apps_lic(vr)


def _make_route(l1: L1PlanContract) -> RouteContract:
    return l0_route_apps_lic(l1)


def _make_fec(route: RouteContract, vr: ValidatedRequest) -> FinalEvidenceContract:
    return c0_retrieve_apps_lic(route, vr)


def _canonical_pipeline() -> tuple[ValidatedRequest, L1PlanContract, RouteContract, FinalEvidenceContract]:
    vr = _make_validated_request()
    l1 = _make_l1(vr)
    route = _make_route(l1)
    fec = _make_fec(route, vr)
    return vr, l1, route, fec


def _import_lines(module_name: str) -> list[str]:
    """Return only import/from-import lines from a module's source."""
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    return [
        line.strip()
        for line in src.splitlines()
        if line.strip().startswith("import ") or line.strip().startswith("from ")
    ]


# ---------------------------------------------------------------------------
# TC01 — C0 emits FinalEvidenceContract for grounded apps_lic route
# ---------------------------------------------------------------------------

class TestTC01_C0EmitsFEC:
    def test_returns_final_evidence_contract(self):
        vr, _, route, fec = _canonical_pipeline()
        assert isinstance(fec, FinalEvidenceContract)

    def test_identity_quad_threaded(self):
        vr, _, route, fec = _canonical_pipeline()
        assert fec.request_id == route.request_id
        assert fec.run_id == route.run_id
        assert fec.app_id == "apps_lic"
        assert fec.trace_id == route.trace_id
        assert fec.tenant_id == route.tenant_id

    def test_has_evidence_items(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.evidence_items) >= 1

    def test_support_target_met_when_lead_and_campaign_present(self):
        _, _, _, fec = _canonical_pipeline()
        assert fec.support_target_met is True

    def test_support_status_pass_when_grounding_met(self):
        _, _, _, fec = _canonical_pipeline()
        assert fec.support_status == SUPPORT_STATUS_PASS

    def test_cert_ref_populated(self):
        _, _, _, fec = _canonical_pipeline()
        assert fec.l5_certification_ref == APPS_LIC_C0_CERT_REF

    def test_retrieval_plan_ref_inline(self):
        _, _, _, fec = _canonical_pipeline()
        assert "inline" in fec.retrieval_plan_ref

    def test_compilation_hash_non_empty(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.compilation_hash) == 64

    def test_final_evidence_digest_non_empty(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.final_evidence_digest) == 64

    def test_schema_version_w5(self):
        _, _, _, fec = _canonical_pipeline()
        assert "W5" in fec.schema_version


# ---------------------------------------------------------------------------
# TC02 — C0 WEAK/EMPTY when grounding_required=True but evidence missing
# ---------------------------------------------------------------------------

class TestTC02_C0WeakWhenEvidenceMissing:
    def _make_no_lead_request(self) -> tuple[RouteContract, ValidatedRequest]:
        """Build a ValidatedRequest/route with empty lead_profile.

        U0 rejects empty lead_profile, so we use the canonical pipeline then
        surgically patch app_payload to simulate the post-U0 evidence-missing
        scenario that C0 must handle defensively.
        """
        vr, l1, route, _ = _canonical_pipeline()
        # Patch app_payload to clear lead_profile (simulates corrupted/stripped payload)
        patched_payload = {**vr.app_payload}
        patched_entity_refs = {**patched_payload.get("entity_refs", {})}
        patched_entity_refs["lead_profile"] = {}
        patched_payload["entity_refs"] = patched_entity_refs
        patched_vr = dataclasses.replace(vr, app_payload=patched_payload)
        return route, patched_vr

    def test_support_status_not_pass_when_lead_missing(self):
        route, vr = self._make_no_lead_request()
        fec = c0_retrieve_apps_lic(route, vr)
        assert fec.support_status in (SUPPORT_STATUS_WEAK, SUPPORT_STATUS_EMPTY)

    def test_support_target_met_false_when_lead_missing(self):
        route, vr = self._make_no_lead_request()
        fec = c0_retrieve_apps_lic(route, vr)
        assert fec.support_target_met is False

    def test_unknown_reason_populated_when_not_pass(self):
        route, vr = self._make_no_lead_request()
        fec = c0_retrieve_apps_lic(route, vr)
        if fec.support_status in (SUPPORT_STATUS_WEAK, SUPPORT_STATUS_EMPTY):
            assert fec.unknown_reason != ""

    def test_grounding_required_true_does_not_auto_upgrade_to_pass(self):
        """Hard law: grounding_required=True never silently upgrades WEAK→PASS."""
        route, vr = self._make_no_lead_request()
        assert route.grounding_required is True
        fec = c0_retrieve_apps_lic(route, vr)
        assert fec.support_status_is_passing() is False

    def test_raises_on_missing_entity_refs(self):
        vr = _make_validated_request()
        l1 = _make_l1(vr)
        route = _make_route(l1)
        # Manually corrupt app_payload by passing a route with a fake vr
        bad_vr = dataclasses.replace(vr, app_payload={})
        with pytest.raises(ValueError, match="entity_refs"):
            c0_retrieve_apps_lic(route, bad_vr)


# ---------------------------------------------------------------------------
# TC03 — allowed_prompt_slot == C0_EVIDENCE_DATA_ONLY on every item
# ---------------------------------------------------------------------------

class TestTC03_AllowedPromptSlot:
    def test_every_item_has_c0_evidence_data_only_slot(self):
        _, _, _, fec = _canonical_pipeline()
        for item in fec.evidence_items:
            assert item.allowed_prompt_slot == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY, (
                f"EvidenceItem {item.source} has wrong allowed_prompt_slot: "
                f"{item.allowed_prompt_slot!r}"
            )

    def test_sentinel_constant_value(self):
        assert ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY == "C0_EVIDENCE_DATA_ONLY"


# ---------------------------------------------------------------------------
# TC04 — EvidenceItem has required fields populated
# ---------------------------------------------------------------------------

class TestTC04_EvidenceItemFields:
    def test_lead_item_has_source_id(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        assert len(lead_items) >= 1
        assert lead_items[0].source_id != ""

    def test_lead_item_has_source_type_app_payload_inline(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        assert lead_items[0].source_type == "app_payload_inline"

    def test_lead_item_has_chunk_digest(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        assert len(lead_items[0].chunk_digest) == 64

    def test_lead_item_has_citation_anchor(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        assert lead_items[0].citation_anchor != ""
        assert "lead_profile" in lead_items[0].citation_anchor

    def test_lead_item_has_source_lineage_fields(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        it = lead_items[0]
        assert it.source_uri_or_ref != ""
        assert it.source_owner_or_authority != ""

    def test_lead_item_support_status_pass(self):
        _, _, _, fec = _canonical_pipeline()
        lead_items = [it for it in fec.evidence_items if "lead_profile" in it.source]
        assert lead_items[0].support_status == SUPPORT_STATUS_PASS

    def test_all_items_have_evidence_id(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.evidence_id != "", f"Missing evidence_id on {it.source!r}"

    def test_all_items_have_evidence_digest(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert len(it.evidence_digest) == 64, f"Bad evidence_digest on {it.source!r}"


# ---------------------------------------------------------------------------
# TC05 — fact_vec_ref / query_vec_ref are NOT_APPLICABLE with reason
# ---------------------------------------------------------------------------

class TestTC05_VectorFieldsNotApplicable:
    def test_fact_vec_ref_not_applicable(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.fact_vec_ref == STATUS_NOT_APPLICABLE, (
                f"Expected NOT_APPLICABLE fact_vec_ref on {it.source!r}, "
                f"got {it.fact_vec_ref!r}"
            )

    def test_query_vec_ref_not_applicable(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.query_vec_ref == STATUS_NOT_APPLICABLE, (
                f"Expected NOT_APPLICABLE query_vec_ref on {it.source!r}, "
                f"got {it.query_vec_ref!r}"
            )

    def test_not_applicable_reason_present_on_every_item(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.not_applicable_reason != "", (
                f"EvidenceItem {it.source!r} missing not_applicable_reason"
            )

    def test_not_applicable_reason_mentions_no_embeddings(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            reason = it.not_applicable_reason.lower()
            assert "embedding" in reason or "chromadb" in reason or "dense" in reason, (
                f"not_applicable_reason on {it.source!r} does not mention embeddings/chromadb/dense"
            )

    def test_fec_query_vec_ref_not_applicable(self):
        _, _, _, fec = _canonical_pipeline()
        assert fec.query_vec_ref == STATUS_NOT_APPLICABLE


# ---------------------------------------------------------------------------
# TC06 — dense_score / bm25_score / metadata_score carry -1.0 sentinel
# ---------------------------------------------------------------------------

class TestTC06_DenseScoresSentinel:
    def test_dense_score_sentinel(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.dense_score == -1.0, (
                f"Expected dense_score=-1.0 on {it.source!r}, got {it.dense_score}"
            )

    def test_bm25_score_sentinel(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.bm25_score == -1.0, (
                f"Expected bm25_score=-1.0 on {it.source!r}, got {it.bm25_score}"
            )

    def test_metadata_score_sentinel(self):
        _, _, _, fec = _canonical_pipeline()
        for it in fec.evidence_items:
            assert it.metadata_score == -1.0, (
                f"Expected metadata_score=-1.0 on {it.source!r}, got {it.metadata_score}"
            )


# ---------------------------------------------------------------------------
# TC07 — citation_map and source_lineage_map populated
# ---------------------------------------------------------------------------

class TestTC07_CitationAndLineageMaps:
    def test_citation_map_non_empty(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.citation_map) >= 1

    def test_citation_map_entries_are_tuples(self):
        _, _, _, fec = _canonical_pipeline()
        for entry in fec.citation_map:
            assert isinstance(entry, tuple) and len(entry) == 2

    def test_source_lineage_map_non_empty(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.source_lineage_map) >= 1

    def test_source_lineage_map_entries_are_tuples(self):
        _, _, _, fec = _canonical_pipeline()
        for entry in fec.source_lineage_map:
            assert isinstance(entry, tuple) and len(entry) == 2

    def test_citation_map_evidence_ids_match_items(self):
        _, _, _, fec = _canonical_pipeline()
        item_ids = {it.evidence_id for it in fec.evidence_items if it.evidence_id}
        cited_ids = {entry[0] for entry in fec.citation_map}
        assert cited_ids.issubset(item_ids)


# ---------------------------------------------------------------------------
# TC08 — evidence_strata has MUST_USE
# ---------------------------------------------------------------------------

class TestTC08_EvidenceStrata:
    def test_evidence_strata_non_empty(self):
        _, _, _, fec = _canonical_pipeline()
        assert len(fec.evidence_strata) >= 1

    def test_must_use_stratum_present(self):
        _, _, _, fec = _canonical_pipeline()
        stratum_labels = {row[0] for row in fec.evidence_strata}
        assert "MUST_USE" in stratum_labels

    def test_must_use_contains_lead_evidence(self):
        _, _, _, fec = _canonical_pipeline()
        must_use_row = next(
            (row for row in fec.evidence_strata if row[0] == "MUST_USE"), None
        )
        assert must_use_row is not None
        must_use_ids = must_use_row[1]
        assert len(must_use_ids) >= 1

    def test_supporting_stratum_present_when_personalization_exists(self):
        _, _, _, fec = _canonical_pipeline()
        stratum_labels = {row[0] for row in fec.evidence_strata}
        assert "SUPPORTING" in stratum_labels


# ---------------------------------------------------------------------------
# TC09 — contradiction_report is NOT_APPLICABLE with reason
# ---------------------------------------------------------------------------

class TestTC09_ContradictionReport:
    def test_contradiction_report_present(self):
        _, _, _, fec = _canonical_pipeline()
        assert fec.contradiction_report != ""

    def test_contradiction_report_not_applicable(self):
        _, _, _, fec = _canonical_pipeline()
        assert STATUS_NOT_APPLICABLE in fec.contradiction_report

    def test_contradiction_report_has_reason(self):
        _, _, _, fec = _canonical_pipeline()
        # Must include inline and/or apps_lic as context
        report = fec.contradiction_report.lower()
        assert "inline" in report or "apps_lic" in report


# ---------------------------------------------------------------------------
# TC10/TC11/TC12 — C0 no ChromaDB, no embeddings, no L4
# ---------------------------------------------------------------------------

class TestTC10_C0NoChromaDB:
    def test_c0_binding_does_not_import_chromadb(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        for line in lines:
            assert "chromadb" not in line.lower(), (
                f"C0 binding imports chromadb: {line!r}"
            )

    def test_c0_binding_does_not_import_chroma_client(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        for line in lines:
            assert "chroma" not in line.lower(), (
                f"C0 binding imports chroma-related: {line!r}"
            )


class TestTC11_C0NoEmbeddings:
    def test_c0_binding_does_not_import_sentence_transformers(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        for line in lines:
            assert "sentence_transformers" not in line.lower(), (
                f"C0 binding imports sentence_transformers: {line!r}"
            )

    def test_c0_binding_does_not_import_embedding(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        for line in lines:
            assert "embedding" not in line.lower(), (
                f"C0 binding imports embedding module: {line!r}"
            )


class TestTC12_C0NoL4Write:
    def test_c0_binding_does_not_import_l4_state(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        for line in lines:
            assert "L4_state" not in line and "l4_state" not in line.lower(), (
                f"C0 binding imports L4 state: {line!r}"
            )

    def test_c0_binding_does_not_import_database_write(self):
        lines = _import_lines("apps_lic.runtime.bindings.c0_binding")
        write_keywords = ["sqlite3", "sqlalchemy", "psycopg2", "pymongo"]
        for line in lines:
            for kw in write_keywords:
                assert kw not in line.lower(), (
                    f"C0 binding imports DB write lib {kw!r}: {line!r}"
                )


# ---------------------------------------------------------------------------
# TPA01 — PA emits CompiledPromptArtifact
# ---------------------------------------------------------------------------

class TestTPA01_PAEmitsCPA:
    def test_returns_compiled_prompt_artifact(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert isinstance(cpa, CompiledPromptArtifact)

    def test_identity_quad_threaded(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa.request_id == route.request_id
        assert cpa.run_id == route.run_id
        assert cpa.app_id == "apps_lic"
        assert cpa.trace_id == route.trace_id

    def test_three_prompt_blocks(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert len(cpa.prompt_blocks) == 3

    def test_target_model_set(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa.target_model == APPS_LIC_TARGET_MODEL

    def test_cert_ref_populated(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa.l5_certification_ref == APPS_LIC_PA_CERT_REF

    def test_evidence_digest_matches_fec_compilation_hash(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa.evidence_digest == fec.compilation_hash


# ---------------------------------------------------------------------------
# TPA02 — slot_lineage_map includes evidence lineage
# ---------------------------------------------------------------------------

class TestTPA02_SlotLineageMap:
    def test_slot_lineage_map_non_empty(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert len(cpa.slot_lineage_map) >= 3

    def test_evidence_slot_in_lineage_map(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "evidence" in cpa.slot_lineage_map

    def test_evidence_lineage_contains_fec_hash(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        evidence_lineage = cpa.slot_lineage_map.get("evidence", "")
        assert fec.compilation_hash[:16] in evidence_lineage

    def test_user_block_2_lineage_carries_c0_evidence_data_only(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        lineage = cpa.slot_lineage_map.get("user_block_2", "")
        assert "C0_EVIDENCE_DATA_ONLY" in lineage


# ---------------------------------------------------------------------------
# TPA03 — component_hash_map has required components
# ---------------------------------------------------------------------------

class TestTPA03_ComponentHashMap:
    def test_component_hash_map_has_evidence(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "evidence" in cpa.component_hash_map

    def test_component_hash_map_has_l1_plan(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "l1_plan" in cpa.component_hash_map

    def test_component_hash_map_has_route(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "route" in cpa.component_hash_map

    def test_component_hash_map_has_app_payload_task_data(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "app_payload_task_data" in cpa.component_hash_map

    def test_evidence_component_matches_fec_compilation_hash(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa.component_hash_map["evidence"] == fec.compilation_hash

    def test_all_hashes_are_hex_strings(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        for key, val in cpa.component_hash_map.items():
            assert isinstance(val, str) and len(val) == 64, (
                f"component_hash_map[{key!r}] is not a 64-char hex digest: {val!r}"
            )


# ---------------------------------------------------------------------------
# TPA04 — prompt_hash is deterministic for same inputs
# ---------------------------------------------------------------------------

class TestTPA04_Determinism:
    def test_same_inputs_produce_same_compilation_hash(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa1 = pa_compose_apps_lic(route, l1, fec, vr)
        cpa2 = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa1.compilation_hash == cpa2.compilation_hash

    def test_same_inputs_produce_same_evidence_digest(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa1 = pa_compose_apps_lic(route, l1, fec, vr)
        cpa2 = pa_compose_apps_lic(route, l1, fec, vr)
        assert cpa1.evidence_digest == cpa2.evidence_digest

    def test_fec_compilation_hash_deterministic(self):
        """FEC compilation_hash is stable across two C0 calls with same input."""
        vr, l1, route, _ = _canonical_pipeline()
        fec1 = c0_retrieve_apps_lic(route, vr)
        fec2 = c0_retrieve_apps_lic(route, vr)
        assert fec1.compilation_hash == fec2.compilation_hash


# ---------------------------------------------------------------------------
# TPA05 — PA keeps C0 evidence as data only (USER_INTENT origin on user blocks)
# ---------------------------------------------------------------------------

class TestTPA05_EvidenceAsDataOnly:
    def test_user_blocks_carry_user_intent_origin(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        for blk in cpa.prompt_blocks:
            if blk.role == "user":
                assert blk.origin == Origin.USER_INTENT, (
                    f"user block[{blk.block_index}] has origin={blk.origin!r}, "
                    "expected USER_INTENT"
                )

    def test_evidence_block_content_contains_source_label(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        # Block 2 is evidence data
        evidence_block = cpa.prompt_blocks[2]
        assert "EVIDENCE DATA" in evidence_block.content or "lead_profile" in evidence_block.content

    def test_evidence_data_appears_in_user_block_not_system(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        system_block = cpa.prompt_blocks[0]
        assert "Jane Smith" not in system_block.content, (
            "Lead name from evidence leaked into system block (data→instruction promotion)"
        )


# ---------------------------------------------------------------------------
# TPA06 — PA does not promote lower-authority content to instructions
# ---------------------------------------------------------------------------

class TestTPA06_NoLowerAuthorityPromotion:
    def test_system_block_has_system_internal_origin(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        system_block = cpa.prompt_blocks[0]
        assert system_block.role == "system"
        assert system_block.origin == Origin.SYSTEM_INTERNAL

    def test_pa_rejects_evidence_item_with_wrong_slot(self):
        vr, l1, route, fec = _canonical_pipeline()
        # Build a bad FEC with a tampered EvidenceItem slot
        bad_item = dataclasses.replace(
            fec.evidence_items[0],
            allowed_prompt_slot="INSTRUCTION_SLOT",
        )
        bad_fec = dataclasses.replace(fec, evidence_items=(bad_item,) + fec.evidence_items[1:])
        with pytest.raises(ValueError, match="airlock violation"):
            pa_compose_apps_lic(route, l1, bad_fec, vr)

    def test_no_retrieved_data_origin_in_system_block(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        for blk in cpa.prompt_blocks:
            if blk.role == "system":
                assert blk.origin != Origin.RETRIEVED_DATA, (
                    f"system block[{blk.block_index}] has RETRIEVED_DATA origin — "
                    "lower-authority content promoted to instruction slot"
                )


# ---------------------------------------------------------------------------
# TPA07 — PA does not read legacy envelope.payload
# ---------------------------------------------------------------------------

class TestTPA07_NoLegacyEnvelopePayload:
    def test_pa_binding_does_not_import_apps_lic_ingress(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "AppsLicIngressPayload" not in line, (
                f"PA binding imports AppsLicIngressPayload: {line!r}"
            )
            assert "AppsLicRequestEnvelope" not in line, (
                f"PA binding imports AppsLicRequestEnvelope: {line!r}"
            )

    def test_pa_binding_does_not_import_apps_lic_ingress_module(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "apps_lic.ingress" not in line.lower(), (
                f"PA binding imports apps_lic.ingress: {line!r}"
            )


# ---------------------------------------------------------------------------
# TPA08 — PA rejects wrong allowed_prompt_slot (already in TPA06)
# ---------------------------------------------------------------------------

class TestTPA08_PARejectsWrongSlot:
    def test_pa_raises_on_wrong_slot(self):
        vr, l1, route, fec = _canonical_pipeline()
        bad_item = dataclasses.replace(
            fec.evidence_items[0],
            allowed_prompt_slot="SYSTEM_INSTRUCTION",
        )
        bad_fec = dataclasses.replace(fec, evidence_items=(bad_item,) + fec.evidence_items[1:])
        with pytest.raises(ValueError):
            pa_compose_apps_lic(route, l1, bad_fec, vr)


# ---------------------------------------------------------------------------
# TPA09 — PA system block carries SYSTEM_INTERNAL origin
# ---------------------------------------------------------------------------

class TestTPA09_SystemBlockOrigin:
    def test_system_block_origin(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        system_blocks = [b for b in cpa.prompt_blocks if b.role == "system"]
        assert len(system_blocks) == 1
        assert system_blocks[0].origin == Origin.SYSTEM_INTERNAL

    def test_system_preamble_contains_governance(self):
        vr, l1, route, fec = _canonical_pipeline()
        cpa = pa_compose_apps_lic(route, l1, fec, vr)
        assert "GOVERNANCE" in cpa.system_preamble or "governed" in cpa.system_preamble.lower()


# ---------------------------------------------------------------------------
# TPA10/TPA11/TPA12 — PA no ChromaDB, no embeddings, no L4
# ---------------------------------------------------------------------------

class TestTPA10_PANoChromaDB:
    def test_pa_binding_does_not_import_chromadb(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "chromadb" not in line.lower(), (
                f"PA binding imports chromadb: {line!r}"
            )


class TestTPA11_PANoEmbeddings:
    def test_pa_binding_does_not_import_sentence_transformers(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "sentence_transformers" not in line.lower(), (
                f"PA binding imports sentence_transformers: {line!r}"
            )

    def test_pa_binding_does_not_import_embedding(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "embedding" not in line.lower(), (
                f"PA binding imports embedding module: {line!r}"
            )


class TestTPA12_PANoL4Write:
    def test_pa_binding_does_not_import_l4_state(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        for line in lines:
            assert "L4_state" not in line and "l4_state" not in line.lower(), (
                f"PA binding imports L4 state: {line!r}"
            )

    def test_pa_binding_does_not_import_database_write(self):
        lines = _import_lines("apps_lic.runtime.bindings.pa_binding")
        write_keywords = ["sqlite3", "sqlalchemy", "psycopg2", "pymongo"]
        for line in lines:
            for kw in write_keywords:
                assert kw not in line.lower(), (
                    f"PA binding imports DB write lib {kw!r}: {line!r}"
                )
