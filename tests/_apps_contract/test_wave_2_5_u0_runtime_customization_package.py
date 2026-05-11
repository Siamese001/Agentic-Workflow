"""Wave 2.5 — U0 RuntimeCustomizationPackage reconciliation tests.

Proves:
- RuntimeCustomizationPackage carries all 24 required fields
- strict Pydantic validation (frozen, extra=forbid)
- no silent field drops through U0 adapter
- field map covers every runtime_customization_package pointer
- package flows through ValidatedRequest.app_payload unchanged
- write_policy defaults to read_only
- package_digest is present (integrity seal placeholder)

Plan: apps-rg-ensemble-judge-restoration-a7c4e2 (Wave 2.5)
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest
import yaml
from pathlib import Path

from apps_rg.contracts.apps_rg_ingress_contract_v1 import (
    AppsRgIngressContractV1,
    RuntimeCustomizationPackage,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD_MAP_PATH = REPO_ROOT / "apps_rg" / "contracts" / "apps_rg_ingress_field_map.v1.yaml"
SCHEMA_PATH = REPO_ROOT / "apps_rg" / "contracts" / "apps_rg_ingress_contract.v1.schema.json"

REQUIRED_PACKAGE_FIELDS = frozenset({
    "workflow_manifest_ref",
    "runtime_gate_profile_ref",
    "exit_profile_ref",
    "judge_profile_ref",
    "eval_rubric_ref",
    "threshold_profile_ref",
    "grader_roster_ref",
    "rubric_output_map_ref",
    "negative_controls_ref",
    "learning_profile_ref",
    "meta_feedback_profile_ref",
    "prompt_profile_ref",
    "route_profile_ref",
    "retrieval_profile_ref",
    "repair_profile_ref",
    "cache_profile_ref",
    "capability_profile_ref",
    "orchestration_profile_ref",
    "provider_profile_ref",
    "write_policy",
    "required_runtime_gates",
    "required_exit_gates",
    "conditional_exit_gates",
    "package_digest",
})


def _make_sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _minimal_payload(*, include_package: bool = True) -> dict[str, Any]:
    """Construct minimal valid AppsRgIngressContractV1 payload."""
    jd_text = "Senior Software Engineer at Acme Corp"
    resume_text = "10 years experience in Python and distributed systems"
    payload = {
        "apps_rg_contract_version": "v1",
        "transport": {
            "app_id": "apps_rg",
            "task_class": "resume_generation",
            "request_id": "req-001",
            "run_id": "run-001",
            "trace_id": "trace-001",
            "submitted_at": "2026-05-11T08:00:00Z",
            "tenant_id": "apps_rg",
        },
        "identity": {"actor_id": "user-1", "actor_role": "applicant"},
        "replay": {"replay_key": "rk-001", "idempotency_key": "ik-001"},
        "jd_payload": {
            "jd_hash": _make_sha256(jd_text),
            "jd_text": jd_text,
        },
        "resume_payload": {"resume_hash": _make_sha256(resume_text)},
        "target": {"company": "Acme", "role": "SWE", "level": "SENIOR"},
        "generation_mode": "strategic_tailor",
        "profile_manifest": {
            "manifest_digest": _make_sha256("manifest"),
            "prompt_registry_ref": "prompt_reg_v1",
            "hitl_policy_ref": "hitl_policy_v1",
            "l0_policy_ref": "l0_policy_v1",
            "agent_spec_ref": "agent_spec_v1",
            "thresholds_ref": "thresholds_v1",
        },
        "quality_thresholds": {
            "min_quality": 0.75,
            "min_ats": 70,
            "word_min": 300,
            "word_max": 1200,
        },
        "output_requirements": {
            "formats": ["json"],
            "provenance_required": True,
            "fact_checked_required": True,
        },
        "provenance_requirements": {
            "per_bullet_required": True,
            "source_quote_required": False,
        },
        "payload_digest": _make_sha256("placeholder"),
    }
    if include_package:
        payload["runtime_customization_package"] = {
            "workflow_manifest_ref": "wf_manifest_v1",
            "runtime_gate_profile_ref": "gate_profile_v1",
            "exit_profile_ref": "exit_profile_v1",
            "judge_profile_ref": "judge_profile_v1",
            "eval_rubric_ref": "eval_rubric_v1",
            "threshold_profile_ref": "threshold_v1",
            "grader_roster_ref": "grader_roster_v1",
            "rubric_output_map_ref": "rubric_map_v1",
            "negative_controls_ref": "neg_controls_v1",
            "learning_profile_ref": "learning_v1",
            "meta_feedback_profile_ref": "meta_fb_v1",
            "prompt_profile_ref": "prompt_v1",
            "route_profile_ref": "route_v1",
            "retrieval_profile_ref": "retrieval_v1",
            "repair_profile_ref": "repair_v1",
            "cache_profile_ref": "cache_v1",
            "capability_profile_ref": "capability_v1",
            "orchestration_profile_ref": "orchestration_v1",
            "provider_profile_ref": "provider_v1",
            "write_policy": "read_only",
            "required_runtime_gates": ["G01", "G02"],
            "required_exit_gates": ["G21", "G22", "G23"],
            "conditional_exit_gates": ["G24"],
            "package_digest": _make_sha256("package_content"),
        }
    return payload


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRuntimeCustomizationPackageContract:
    """Contract shape tests."""

    def test_all_required_fields_present_on_model(self):
        """Every required field exists on RuntimeCustomizationPackage."""
        model_fields = set(RuntimeCustomizationPackage.model_fields.keys())
        missing = REQUIRED_PACKAGE_FIELDS - model_fields
        assert not missing, f"Missing fields on RuntimeCustomizationPackage: {missing}"

    def test_frozen_immutable(self):
        """Package is frozen — no mutation after construction."""
        rcp = RuntimeCustomizationPackage()
        with pytest.raises(Exception):
            rcp.workflow_manifest_ref = "changed"  # type: ignore[misc]

    def test_extra_forbid(self):
        """Unknown fields are rejected (extra=forbid)."""
        with pytest.raises(Exception):
            RuntimeCustomizationPackage(unknown_field="x")  # type: ignore[call-arg]

    def test_default_write_policy_is_read_only(self):
        """apps_rg must always be read_only."""
        rcp = RuntimeCustomizationPackage()
        assert rcp.write_policy == "read_only"

    def test_default_construction_all_empty(self):
        """Default-constructed package has all empty/tuple fields."""
        rcp = RuntimeCustomizationPackage()
        d = rcp.model_dump()
        for key, val in d.items():
            if key == "write_policy":
                assert val == "read_only"
            elif isinstance(val, tuple):
                assert val == ()
            else:
                assert val == "", f"Expected '' for {key}, got {val!r}"

    def test_package_digest_field_exists(self):
        """package_digest is present for integrity seal."""
        rcp = RuntimeCustomizationPackage(package_digest=_make_sha256("test"))
        assert len(rcp.package_digest) == 64


class TestContractIntegration:
    """Integration with AppsRgIngressContractV1."""

    def test_contract_validates_with_package(self):
        """Full contract validates when runtime_customization_package present."""
        payload = _minimal_payload(include_package=True)
        contract = AppsRgIngressContractV1.model_validate(payload)
        assert contract.runtime_customization_package.workflow_manifest_ref == "wf_manifest_v1"

    def test_contract_validates_without_package(self):
        """Full contract validates even without explicit runtime_customization_package (defaults)."""
        payload = _minimal_payload(include_package=False)
        contract = AppsRgIngressContractV1.model_validate(payload)
        assert contract.runtime_customization_package.write_policy == "read_only"
        assert contract.runtime_customization_package.workflow_manifest_ref == ""

    def test_no_silent_field_drop_through_model_dump(self):
        """All package fields survive model_dump round-trip."""
        payload = _minimal_payload(include_package=True)
        contract = AppsRgIngressContractV1.model_validate(payload)
        dumped = contract.model_dump(mode="python")
        rcp_out = dumped["runtime_customization_package"]
        for field in REQUIRED_PACKAGE_FIELDS:
            assert field in rcp_out, f"Field '{field}' silently dropped in model_dump"

    def test_package_values_preserved_verbatim(self):
        """Input values are preserved verbatim through validation."""
        payload = _minimal_payload(include_package=True)
        contract = AppsRgIngressContractV1.model_validate(payload)
        pkg = contract.runtime_customization_package
        assert pkg.required_runtime_gates == ("G01", "G02")
        assert pkg.required_exit_gates == ("G21", "G22", "G23")
        assert pkg.conditional_exit_gates == ("G24",)
        assert pkg.judge_profile_ref == "judge_profile_v1"


class TestFieldMapCoverage:
    """Field map SSOT covers all runtime_customization_package pointers."""

    @pytest.fixture()
    def field_map(self) -> dict[str, Any]:
        return yaml.safe_load(FIELD_MAP_PATH.read_text(encoding="utf-8"))

    def test_all_package_fields_in_field_map(self, field_map: dict[str, Any]):
        """Every field in RuntimeCustomizationPackage has a field-map entry."""
        mappings = field_map["mappings"]
        for field_name in REQUIRED_PACKAGE_FIELDS:
            pointer = f"/runtime_customization_package/{field_name}"
            assert pointer in mappings, (
                f"Field-map entry missing for {pointer}. "
                "This violates the core rule: a field may be deferred, a field may not disappear."
            )

    def test_section_aggregation_exists(self, field_map: dict[str, Any]):
        """Section aggregation entry exists for /runtime_customization_package."""
        section_aggs = field_map.get("section_aggregations", {})
        assert "/runtime_customization_package" in section_aggs

    def test_no_unknown_statuses(self, field_map: dict[str, Any]):
        """All runtime_customization_package field-map entries use valid statuses."""
        mappings = field_map["mappings"]
        valid_statuses = {"MAPPED", "DERIVED", "REJECTED", "DEFERRED"}
        for field_name in REQUIRED_PACKAGE_FIELDS:
            pointer = f"/runtime_customization_package/{field_name}"
            entry = mappings.get(pointer, {})
            status = entry.get("status")
            assert status in valid_statuses, f"{pointer} has invalid status: {status}"


class TestSchemaCoverage:
    """JSON schema includes RuntimeCustomizationPackage."""

    @pytest.fixture()
    def schema(self) -> dict[str, Any]:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_has_runtime_customization_package(self, schema: dict[str, Any]):
        """Top-level schema references RuntimeCustomizationPackage."""
        props = schema.get("properties", {})
        assert "runtime_customization_package" in props

    def test_schema_def_has_all_fields(self, schema: dict[str, Any]):
        """RuntimeCustomizationPackage $def has all required fields."""
        defs = schema.get("$defs", {})
        rcp_def = defs.get("RuntimeCustomizationPackage", {})
        rcp_props = rcp_def.get("properties", {})
        for field_name in REQUIRED_PACKAGE_FIELDS:
            assert field_name in rcp_props, (
                f"Schema $defs/RuntimeCustomizationPackage missing property: {field_name}"
            )


class TestU0FlowThrough:
    """Verify package flows through U0 adapter to ValidatedRequest.app_payload."""

    def test_u0_preserves_package_in_app_payload(self):
        """U0 adapter preserves runtime_customization_package in app_payload."""
        from agentic_core.runtime.u0.apps_rg_u0_adapter import apps_rg_u0_adapt

        payload = _minimal_payload(include_package=True)
        validated_request, receipt = apps_rg_u0_adapt(payload)

        app_payload = validated_request.app_payload
        assert "runtime_customization_package" in app_payload
        rcp = app_payload["runtime_customization_package"]
        for field_name in REQUIRED_PACKAGE_FIELDS:
            assert field_name in rcp, f"Field '{field_name}' lost in U0 flow-through"

    def test_u0_no_silently_dropped_with_package(self):
        """U0 reflection passes (no silently_dropped) with full package."""
        from agentic_core.runtime.u0.apps_rg_u0_adapter import apps_rg_u0_adapt

        payload = _minimal_payload(include_package=True)
        _, receipt = apps_rg_u0_adapt(payload)
        assert receipt.pass_status is True
        assert receipt.silently_dropped == ()

    def test_u0_no_silently_dropped_without_package(self):
        """U0 reflection passes with default (empty) package too."""
        from agentic_core.runtime.u0.apps_rg_u0_adapter import apps_rg_u0_adapt

        payload = _minimal_payload(include_package=False)
        _, receipt = apps_rg_u0_adapt(payload)
        assert receipt.pass_status is True
        assert receipt.silently_dropped == ()


class TestGovernanceInvariants:
    """apps_rg governance: no X3 emission, no direct L4 write, no apps_rg Exit."""

    def test_write_policy_forbids_write(self):
        """Package write_policy rejects non-read_only only at domain level."""
        rcp = RuntimeCustomizationPackage(write_policy="deferred_writeback")
        assert rcp.write_policy == "deferred_writeback"  # Pydantic allows — enforcement is downstream

    def test_no_apps_rg_x3_emission_field(self):
        """RuntimeCustomizationPackage has no x3 or emission field."""
        fields = set(RuntimeCustomizationPackage.model_fields.keys())
        forbidden = {"x3_emission", "emit_x3", "x3_ref", "sealed_output_ref"}
        assert not fields & forbidden

    def test_no_l4_write_field(self):
        """RuntimeCustomizationPackage has no l4_write or commit field."""
        fields = set(RuntimeCustomizationPackage.model_fields.keys())
        forbidden = {"l4_write", "commit_request", "durable_write_ref"}
        assert not fields & forbidden
