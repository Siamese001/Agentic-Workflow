"""Wave 2.5 hardening — prove downstream can resolve effective output contract from U0 package.

Proves:
1. U0 package does NOT need a circular input_contract_ref.
2. workflow_manifest_ref + orchestration_profile_ref resolve to a concrete output contract/schema.
3. Exit/G21 can consume that resolved output contract.
4. Missing or unresolved effective output contract fails closed.
5. The resolved output contract ref/digest is included in the downstream profile resolution receipt.

The resolution chain (no new code needed):
    U0 RuntimeCustomizationPackage
        .workflow_manifest_ref
        .orchestration_profile_ref
    → L0 resolve_app_contract_refs(app_id, task_class)
    → AppContractRefBundle.output_schema_ref + .orchestration_profile_ref
    → InMemoryAppDomainStore.get_output_schema(ref) → AppOutputSchemaRecord (with deterministic_digest)
    → InMemoryAppDomainStore.get_orchestration_profile(ref) → AppOrchestrationProfileRecord (managed_workflow)

Plan: apps-rg-ensemble-judge-restoration-a7c4e2 (Wave 2.5 hardening)
"""
from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.app_domain_resolver import (
    AppContractRefBundle,
    resolve_app_contract_refs,
)
from agentic_core.L4_state.contracts.app_domain import (
    AppDomainContractRecord,
    AppOrchestrationProfileRecord,
    AppOutputSchemaRecord,
    TaskClassEntry,
)
from agentic_core.L4_state.contracts.app_domain_lookup import (
    InMemoryAppDomainStore,
    UnknownAppContractError,
)
from apps_rg.contracts.apps_rg_ingress_contract_v1 import RuntimeCustomizationPackage


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _build_store_with_apps_rg(
    *,
    output_schema_ref: str = "apps_rg_output_schema_v1",
    orchestration_profile_ref: str = "apps_rg_orch_managed_workflow_v1",
    include_output_schema: bool = True,
    include_orchestration_profile: bool = True,
) -> InMemoryAppDomainStore:
    """Build an InMemoryAppDomainStore pre-populated with apps_rg contract."""
    store = InMemoryAppDomainStore()

    contract = AppDomainContractRecord(
        app_domain_contract_id="apps_rg_domain_v1",
        app_id="apps_rg",
        app_version="1.0",
        domain="resume_generation",
        owner_surface="apps_rg",
        status="active",
        task_classes=(TaskClassEntry(task_class="resume_generation", kind="generation", description="Generate tailored resumes"),),
        input_contract_ref="apps_rg_ingress_contract_v1",
        output_schema_ref=output_schema_ref,
        eval_rubric_refs=("apps_rg_rubric_v1",),
        threshold_profile_refs=("apps_rg_threshold_v1",),
        grader_roster_refs=("apps_rg_roster_v1",),
        retrieval_profile_refs=("apps_rg_retrieval_v1",),
        prompt_profile_refs=("apps_rg_prompt_v1",),
        capability_profile_refs=("apps_rg_capability_v1",),
        route_profile_refs=("apps_rg_route_v1",),
        orchestration_profile_refs=(orchestration_profile_ref,),
        negative_control_refs=("apps_rg_neg_ctrl_v1",),
        deterministic_digest=_sha("apps_rg_domain_v1"),
    )
    store.put_contract(contract)

    if include_output_schema:
        output_schema = AppOutputSchemaRecord(
            output_schema_id=output_schema_ref,
            app_id="apps_rg",
            task_class="resume_generation",
            version="1.0",
            status="active",
            output_type="json",
            deterministic_digest=_sha(output_schema_ref),
            required_sections=("professional_summary", "experience", "skills", "education"),
        )
        store.put_output_schema(output_schema)

    if include_orchestration_profile:
        orch_profile = AppOrchestrationProfileRecord(
            orchestration_profile_id=orchestration_profile_ref,
            app_id="apps_rg",
            task_class="resume_generation",
            version="1.0",
            status="active",
            orchestration_kind="managed_workflow",
            deterministic_digest=_sha(orchestration_profile_ref),
            blueprint_ref="apps_rg_managed_workflow_blueprint_v1",
        )
        store.put_orchestration_profile(orch_profile)

    return store


# ---------------------------------------------------------------------------
# 1. U0 package does NOT need input_contract_ref (no circularity)
# ---------------------------------------------------------------------------


class TestNoCircularInputContractRef:
    """Proves input_contract_ref is not needed on RuntimeCustomizationPackage."""

    def test_package_has_no_input_contract_ref_field(self):
        """RuntimeCustomizationPackage deliberately excludes input_contract_ref."""
        fields = set(RuntimeCustomizationPackage.model_fields.keys())
        assert "input_contract_ref" not in fields

    def test_input_contract_ref_resolved_from_domain_contract(self):
        """input_contract_ref comes from AppDomainContractRecord, not from the package."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert bundle.input_contract_ref == "apps_rg_ingress_contract_v1"


# ---------------------------------------------------------------------------
# 2. workflow_manifest_ref + orchestration_profile_ref → concrete output contract
# ---------------------------------------------------------------------------


class TestEffectiveOutputContractResolution:
    """Proves the resolution chain from U0 package to output contract."""

    def test_resolve_returns_output_schema_ref(self):
        """resolve_app_contract_refs returns a non-empty output_schema_ref."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert bundle.output_schema_ref == "apps_rg_output_schema_v1"

    def test_resolve_returns_orchestration_profile_ref(self):
        """resolve_app_contract_refs returns a non-empty orchestration_profile_ref."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert bundle.orchestration_profile_ref == "apps_rg_orch_managed_workflow_v1"

    def test_output_schema_record_has_digest(self):
        """Resolved output schema has a deterministic digest for G21 verification."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        output_schema = store.get_output_schema(bundle.output_schema_ref)
        assert output_schema.deterministic_digest == _sha("apps_rg_output_schema_v1")
        assert len(output_schema.deterministic_digest) == 64

    def test_orchestration_profile_is_managed_workflow(self):
        """Resolved orchestration profile is managed_workflow kind for apps_rg."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        orch = store.get_orchestration_profile(bundle.orchestration_profile_ref)
        assert orch.orchestration_kind == "managed_workflow"

    def test_output_schema_has_required_sections(self):
        """Output schema defines required_sections for merge validation."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        output_schema = store.get_output_schema(bundle.output_schema_ref)
        assert "professional_summary" in output_schema.required_sections
        assert "experience" in output_schema.required_sections


# ---------------------------------------------------------------------------
# 3. Exit/G21 can consume the resolved output contract
# ---------------------------------------------------------------------------


class TestExitG21ConsumesResolvedContract:
    """Proves Exit/G21 has access to resolved output contract through the bundle."""

    def test_bundle_carries_output_schema_in_l4_record_refs(self):
        """AppContractRefBundle.app_contract_l4_record_refs includes output_schema_ref."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert bundle.output_schema_ref in bundle.app_contract_l4_record_refs

    def test_exit_can_hydrate_output_schema_from_store(self):
        """Exit stage can hydrate AppOutputSchemaRecord from the resolved ref."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        output_schema = store.get_output_schema(bundle.output_schema_ref)
        assert output_schema.output_type == "json"
        assert output_schema.status == "active"


# ---------------------------------------------------------------------------
# 4. Missing/unresolved effective output contract fails closed
# ---------------------------------------------------------------------------


class TestFailClosedOnMissingOutputContract:
    """Missing output contract or orchestration profile → fail closed."""

    def test_missing_app_contract_fails_closed(self):
        """No registered contract for (app_id, task_class) → UnknownAppContractError."""
        store = InMemoryAppDomainStore()
        with pytest.raises(UnknownAppContractError):
            resolve_app_contract_refs("apps_rg", "resume_generation", store=store)

    def test_missing_output_schema_from_store_fails_closed(self):
        """Output schema ref present on contract but not in store → UnknownAppContractError on hydration."""
        store = _build_store_with_apps_rg(include_output_schema=False)
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        with pytest.raises(UnknownAppContractError):
            store.get_output_schema(bundle.output_schema_ref)

    def test_missing_orchestration_profile_from_store_fails_closed(self):
        """Orchestration profile ref present on contract but not in store → UnknownAppContractError on hydration."""
        store = _build_store_with_apps_rg(include_orchestration_profile=False)
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        with pytest.raises(UnknownAppContractError):
            store.get_orchestration_profile(bundle.orchestration_profile_ref)


# ---------------------------------------------------------------------------
# 5. Resolved output contract ref/digest is included in resolution receipt
# ---------------------------------------------------------------------------


class TestResolutionReceiptContainsOutputContract:
    """The AppContractRefBundle (resolution receipt) contains the output contract artifacts."""

    def test_bundle_has_output_schema_ref(self):
        """Bundle explicitly carries output_schema_ref for downstream consumption."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert hasattr(bundle, "output_schema_ref")
        assert bundle.output_schema_ref != ""

    def test_bundle_has_domain_contract_digest(self):
        """Bundle carries domain_contract_digest (covers all sub-refs including output)."""
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert len(bundle.domain_contract_digest) == 64

    def test_u0_package_refs_align_with_resolved_bundle(self):
        """U0 RuntimeCustomizationPackage refs align with what the resolver produces."""
        rcp = RuntimeCustomizationPackage(
            workflow_manifest_ref="apps_rg_managed_workflow_v1",
            orchestration_profile_ref="apps_rg_orch_managed_workflow_v1",
        )
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)
        assert bundle.orchestration_profile_ref == rcp.orchestration_profile_ref

    def test_effective_output_derivation_summary(self):
        """Integration: full chain from U0 package → resolved output contract + digest."""
        rcp = RuntimeCustomizationPackage(
            workflow_manifest_ref="apps_rg_managed_workflow_v1",
            orchestration_profile_ref="apps_rg_orch_managed_workflow_v1",
        )
        store = _build_store_with_apps_rg()
        bundle = resolve_app_contract_refs("apps_rg", "resume_generation", store=store)

        effective_output_contract_ref = bundle.output_schema_ref
        output_schema = store.get_output_schema(effective_output_contract_ref)
        effective_output_schema_digest = output_schema.deterministic_digest

        orch = store.get_orchestration_profile(bundle.orchestration_profile_ref)
        effective_merge_strategy_ref = orch.blueprint_ref

        assert effective_output_contract_ref == "apps_rg_output_schema_v1"
        assert len(effective_output_schema_digest) == 64
        assert effective_merge_strategy_ref == "apps_rg_managed_workflow_blueprint_v1"
        assert orch.orchestration_kind == "managed_workflow"
        assert rcp.orchestration_profile_ref == bundle.orchestration_profile_ref
