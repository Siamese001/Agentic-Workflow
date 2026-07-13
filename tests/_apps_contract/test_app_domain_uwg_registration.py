"""UWG registration tests for the app-domain contract pack.

Covers plan §P7.2:
- Apps cannot write directly to L4 (UWG anti-bypass).
- App contracts register through UWG and produce UWGCommitReceipt.
- L4 records carry deterministic_digest.
- Lookup by (app_id, task_class) resolves the active contract.
- Deprecated contract resolution fails closed.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-domain-contract-fortknox-c4d8e2.md`` §P7.2.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L4_state.contracts import (
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppInputContractRecord,
    AppOutputSchemaRecord,
    AppThresholdProfileRecord,
    AppGraderRosterRecord,
    AppRetrievalProfileRecord,
    AppPromptProfileRecord,
    AppCapabilityProfileRecord,
    AppRouteProfileRecord,
    AppFixtureRecord,
    AppNegativeControlRecord,
    DeprecatedAppContractError,
    InMemoryAppDomainStore,
    ScoreDimension,
    TaskClassEntry,
    UnknownAppContractError,
    reset_default_app_domain_store,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.uwg import (
    AppDomainContractBundle,
    DurableWriteGateway,
    discover_app_contract_dirs,
    load_bundle_from_dir,
    register_bundle,
)
from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway
from agentic_core.L4_state.uwg.durable_write_gateway import compute_state_diffs_digest

REPO_ROOT = Path(__file__).resolve().parents[2]
_TEST_REGISTRATION_PROOF = {
    "l5_certification_ref": "test:valid:app-domain-registration",
    "clearance_proof_id": "clearance::test::app-domain-registration",
    "commit_request_signature": "signature::test::app-domain-registration",
}


def _register(bundle: AppDomainContractBundle):
    return register_bundle(bundle, **_TEST_REGISTRATION_PROOF)


# ---------------------------------------------------------------------------
# Fixture: minimal valid bundle for testing
# ---------------------------------------------------------------------------


def _minimal_bundle(app_id: str = "apps_rg", task_class: str = "rg") -> AppDomainContractBundle:
    return AppDomainContractBundle(
        contract=AppDomainContractRecord(
            app_domain_contract_id=f"adc::{app_id}::v1",
            app_id=app_id,
            app_version="1.0.0",
            domain="test_domain",
            owner_surface=app_id,
            status="active",
            task_classes=(TaskClassEntry(task_class=task_class, kind="generation", description="x"),),
            negative_control_refs=(f"aneg::{app_id}::{task_class}::x",),
        ),
        input_contract=AppInputContractRecord(
            input_contract_id=f"aic::{app_id}::{task_class}::v1",
            app_id=app_id,
            task_class=task_class,
            version="1.0.0",
            status="active",
            missing_input_behavior="fail_closed",
            ambiguity_behavior="escalate",
        ),
        output_schema=AppOutputSchemaRecord(
            output_schema_id=f"aos::{app_id}::{task_class}::v1",
            app_id=app_id,
            task_class=task_class,
            version="1.0.0",
            status="active",
            output_type="structured_record",
        ),
        eval_rubrics=(
            AppEvalRubricRecord(
                eval_rubric_id=f"aer::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                score_dimensions=(
                    ScoreDimension(
                        dimension_id="grounding",
                        description="x",
                        weight=1.0,
                        grader_type="deterministic",
                        min_required_score=0.9,
                    ),
                ),
            ),
        ),
        threshold_profiles=(
            AppThresholdProfileRecord(
                threshold_profile_id=f"atp::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                overall_pass_threshold=0.75,
            ),
        ),
        grader_rosters=(
            AppGraderRosterRecord(
                grader_roster_id=f"agr::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                deterministic_graders=("g1",),
            ),
        ),
        retrieval_profiles=(
            AppRetrievalProfileRecord(
                retrieval_profile_id=f"arp::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                freshness_class="bounded",
            ),
        ),
        prompt_profiles=(
            AppPromptProfileRecord(
                prompt_profile_id=f"app::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                output_schema_ref=f"aos::{app_id}::{task_class}::v1",
            ),
        ),
        capability_profiles=(
            AppCapabilityProfileRecord(
                capability_profile_id=f"acp::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                side_effect_class="read_only",
            ),
        ),
        route_profiles=(
            AppRouteProfileRecord(
                route_profile_id=f"arpf::{app_id}::{task_class}::v1",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                default_route_id=f"{app_id}.default",
            ),
        ),
        fixtures=(
            AppFixtureRecord(
                fixture_id=f"afix::{app_id}::{task_class}::g",
                app_id=app_id,
                task_class=task_class,
                fixture_type="golden",
                version="1.0.0",
                status="active",
                input_ref="test_input",
                expected_disposition="ALLOW",
            ),
        ),
        negative_controls=(
            AppNegativeControlRecord(
                negative_control_id=f"aneg::{app_id}::{task_class}::x",
                app_id=app_id,
                task_class=task_class,
                version="1.0.0",
                status="active",
                expected_failure_dimension="grounding",
                expected_failure_reason="test",
                input_ref="test_neg_input",
            ),
        ),
    )


@pytest.fixture(autouse=True)
def _reset_state():
    reset_default_gateway()
    reset_default_app_domain_store()
    yield
    reset_default_gateway()
    reset_default_app_domain_store()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAppCannotWriteDirectly:
    """§P7.2 — apps must not be able to bypass UWG."""

    def test_app_surface_rejected_as_commit_source(self) -> None:
        """Directly attempting to submit a commit with an apps_* source_surface
        must fail UWG validation (non-exit source)."""
        from agentic_core.L4_state.contracts.records import (
            CommitRequest,
            ReadSurfaceRefreshPlan,
            RollbackPlan,
            StateDiff,
            stamp_digest as _sd,
        )

        gw = DurableWriteGateway()
        sd = _sd(
            StateDiff(
                state_diff_id="sd-1",
                target_surface="l4.app_domain.AppDomainContractRecord",
                operation_type="app_domain_contract_register",
                after_candidate="x",
                schema_ref="x",
                blast_radius="registry_scoped",
                rollback_plan_ref="rp-1",
                proposed_by_surface="apps_rg",
                created_at="0",
            ),
        )
        rp = _sd(
            RollbackPlan(
                rollback_plan_id="rp-1",
                blast_radius="registry_scoped",
                target_surfaces=("l4.app_domain.AppDomainContractRecord",),
            ),
        )
        refresh = _sd(
            ReadSurfaceRefreshPlan(
                refresh_plan_id="rfp-1",
                source_commit_receipt_ref="",
                before_snapshot=gw.last_snapshot_id,
                expected_after_snapshot="",
                stale_projection_policy="serve_with_warn",
                retry_policy="none",
                policy_hash="p",
                blueprint_hash="b",
                affected_surfaces=("l4.app_domain.AppDomainContractRecord",),
            ),
        )
        req = _sd(
            CommitRequest(
                commit_request_id="cr-1",
                cleared_exit_review_packet_ref="erp::x",
                request_id="r",
                run_id="r",
                trace_root="t",
                tenant_id="t",
                policy_hash="p",
                blueprint_hash="b",
                route_contract_ref="rc",
                replay_key="k",
                rollback_plan_ref="rp-1",
                blast_radius="registry_scoped",
                source_surface="apps_rg",  # FORBIDDEN
                l5_certification_ref="test:valid:direct-write-negative",
                l5_certification_refs=("test:valid:direct-write-negative",),
                clearance_proof_id="clearance::test::direct-write-negative",
                registry_digest_set=(sd.deterministic_digest,),
                staged_diff_hash=compute_state_diffs_digest([sd]),
                commit_request_signature="signature::test::direct-write-negative",
                state_diff_refs=("sd-1",),
                gate_verdict_refs=("gv-1",),
            ),
        )
        commit_receipt, blocked, _ = gw.commit(
            commit_request=req,
            state_diffs=[sd],
            rollback_plan=rp,
            refresh_plan=refresh,
        )
        assert commit_receipt is None
        assert blocked is not None
        # Exact reason codes are UWG-internal, but the failure mode must
        # be either non_exit_source or non_authorized source.
        reason_str = " ".join(blocked.blocked_reason_codes)
        assert "non_exit_source" in reason_str or "non_authorized" in reason_str


class TestRegistrationGoesThroughUWG:
    def test_minimal_bundle_registers(self) -> None:
        bundle = _minimal_bundle()
        receipt = _register(bundle)
        assert receipt.accepted is True
        assert receipt.commit_receipt is not None
        assert receipt.blocked_receipt is None
        # 1 contract + input + output + 1 rubric + 1 threshold + 1 roster +
        # 1 retrieval + 1 prompt + 1 capability + 1 route + 0 orch + 1 fixture + 1 negative = 12
        assert receipt.state_diff_count == 12

    def test_registration_digest_is_stable(self) -> None:
        # Same bundle content across independent registrations ⇒ same digest
        r1 = _register(_minimal_bundle())
        reset_default_gateway()
        reset_default_app_domain_store()
        r2 = _register(_minimal_bundle())
        assert r1.bundle_digest == r2.bundle_digest

    def test_l4_record_has_deterministic_digest(self) -> None:
        from agentic_core.L4_state.contracts import get_default_app_domain_store

        _register(_minimal_bundle())
        store = get_default_app_domain_store()
        rec = store.get_contract("apps_rg", "rg")
        assert rec.deterministic_digest != ""
        # Rubric digest too
        rub = store.get_eval_rubric("aer::apps_rg::rg::v1")
        assert rub.deterministic_digest != ""


class TestLookupFailsClosed:
    def test_unknown_app_raises(self) -> None:
        store = InMemoryAppDomainStore()
        with pytest.raises(UnknownAppContractError):
            store.get_contract("apps_ghost", "any")

    def test_deprecated_app_raises(self) -> None:
        store = InMemoryAppDomainStore()
        contract = AppDomainContractRecord(
            app_domain_contract_id="adc::apps_rg::v1",
            app_id="apps_rg",
            app_version="1.0.0",
            domain="x",
            owner_surface="apps_rg",
            status="deprecated",
            # Deprecated contracts don't need task_classes/negative_controls
            task_classes=(),
            negative_control_refs=(),
        )
        store.put_contract(stamp_digest(contract))
        with pytest.raises(DeprecatedAppContractError):
            store.get_contract("apps_rg", "rg")

    def test_draft_app_raises_unless_allow_draft(self) -> None:
        from agentic_core.L4_state.contracts import DraftAppContractError

        store = InMemoryAppDomainStore()
        contract = AppDomainContractRecord(
            app_domain_contract_id="adc::apps_rg::v1",
            app_id="apps_rg",
            app_version="1.0.0",
            domain="x",
            owner_surface="apps_rg",
            status="draft",
            task_classes=(TaskClassEntry(task_class="rg", kind="generation", description="x"),),
        )
        store.put_contract(stamp_digest(contract))
        with pytest.raises(DraftAppContractError):
            store.get_contract("apps_rg", "rg")
        # With allow_draft=True it succeeds
        rec = store.get_contract("apps_rg", "rg", allow_draft=True)
        assert rec.status == "draft"


class TestE2EAllApps:
    """Full sweep: every apps_*/config/domain_contract registers clean."""

    def test_all_discovered_apps_register(self) -> None:
        dirs = discover_app_contract_dirs(REPO_ROOT)
        required = {
            "apps_exec",
            "apps_lic",
            "apps_qna",
            "apps_research",
            "apps_underwriting_ai",
        }
        assert required <= set(dirs), f"missing app contracts: {sorted(required - set(dirs))}"
        accepted = 0
        for app_id in sorted(dirs):
            bundle = load_bundle_from_dir(dirs[app_id])
            receipt = _register(bundle)
            assert receipt.accepted, f"{app_id} registration blocked"
            accepted += 1
        assert accepted == len(dirs)

    def test_apps_underwriting_ai_is_active(self) -> None:
        """W2.P4 closed (plan apps-eval-harness-parity-f8d4a2): apps_underwriting_ai
        promoted draft→active after RubricOutputMapper producer landed. If this
        test fails, the manifest/rubric was downgraded back to draft — regression."""
        from agentic_core.L4_state.contracts import get_default_app_domain_store

        dirs = discover_app_contract_dirs(REPO_ROOT)
        bundle = load_bundle_from_dir(dirs["apps_underwriting_ai"])
        _register(bundle)
        store = get_default_app_domain_store()
        rec = store.get_contract("apps_underwriting_ai", "*")
        assert rec.status == "active", (
            "apps_underwriting_ai was flipped to status=active in W2.P4; "
            f"got {rec.status!r} — regression to draft"
        )
