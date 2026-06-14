"""Unit tests for agentic_core.L4_state.contracts.app_domain_lookup.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L4 surface.
``app_domain_lookup`` (L4_STATE) is the read-only resolution tier the L0
resolver consults to bind per-app refs. Fail-closed: deprecated/draft/unknown
records raise. Exercises the InMemoryAppDomainStore CRUD round-trip, the
fail-closed status gates, and the process-wide default-store accessors.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.contracts.app_domain import (
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppFixtureRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
    TaskClassEntry,
)
from agentic_core.L4_state.contracts.app_domain_lookup import (
    DeprecatedAppContractError,
    DraftAppContractError,
    InMemoryAppDomainStore,
    UnknownAppContractError,
    get_default_app_domain_store,
    reset_default_app_domain_store,
)


def _contract(*, app_id: str = "apps_rg", status: str = "active") -> AppDomainContractRecord:
    return AppDomainContractRecord(
        app_domain_contract_id=f"{app_id}-contract-1",
        app_id=app_id,
        app_version="1.0.0",
        domain="resume",
        owner_surface=app_id,
        status=status,
        task_classes=(
            TaskClassEntry(
                task_class="resume_generation",
                kind="generation",
                description="resume gen",
            ),
        ),
        negative_control_refs=("nc-1",),
    )


def _rubric(*, status: str = "active") -> AppEvalRubricRecord:
    return AppEvalRubricRecord(
        eval_rubric_id="rubric-1",
        app_id="apps_rg",
        task_class="resume_generation",
        version="1.0.0",
        status=status,
        score_dimensions=(
            ScoreDimension(
                dimension_id="accuracy",
                description="accuracy",
                weight=1.0,
                grader_type="deterministic",
            ),
        ),
    )


def _threshold(*, status: str = "active") -> AppThresholdProfileRecord:
    return AppThresholdProfileRecord(
        threshold_profile_id="thr-1",
        app_id="apps_rg",
        task_class="resume_generation",
        version="1.0.0",
        status=status,
        overall_pass_threshold=0.8,
    )


def _fixture(*, app_id: str = "apps_rg", fixture_type: str = "golden") -> AppFixtureRecord:
    return AppFixtureRecord(
        fixture_id=f"fix-{app_id}-{fixture_type}",
        app_id=app_id,
        task_class="resume_generation",
        fixture_type=fixture_type,
        version="1.0.0",
        status="active",
        input_ref="in-1",
        expected_disposition="ALLOW",
    )


class TestContractRoundTrip:
    def test_put_then_get_by_app_task(self) -> None:
        store = InMemoryAppDomainStore()
        rec = _contract()
        store.put_contract(rec)
        got = store.get_contract("apps_rg", "resume_generation")
        assert got is rec

    def test_get_falls_back_to_appwide_manifest(self) -> None:
        store = InMemoryAppDomainStore()
        rec = _contract()
        store.put_contract(rec)
        # task_class not explicitly registered → app-wide "*" manifest used.
        got = store.get_contract("apps_rg", "unregistered_task")
        assert got is rec

    def test_get_by_id(self) -> None:
        store = InMemoryAppDomainStore()
        rec = _contract()
        store.put_contract(rec)
        assert store.get_contract_by_id(rec.app_domain_contract_id) is rec

    def test_list_apps_sorted(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_contract(_contract(app_id="apps_rg"))
        store.put_contract(_contract(app_id="apps_lic"))
        assert store.list_apps() == ["apps_lic", "apps_rg"]


class TestFailClosed:
    def test_unknown_contract_raises(self) -> None:
        store = InMemoryAppDomainStore()
        with pytest.raises(UnknownAppContractError, match="no AppDomainContractRecord"):
            store.get_contract("apps_nope", "x")

    def test_unknown_contract_by_id_raises(self) -> None:
        store = InMemoryAppDomainStore()
        with pytest.raises(UnknownAppContractError):
            store.get_contract_by_id("missing")

    def test_deprecated_contract_raises(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_contract(_contract(status="deprecated"))
        with pytest.raises(DeprecatedAppContractError, match="is deprecated"):
            store.get_contract("apps_rg", "resume_generation")

    def test_draft_contract_raises_by_default(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_contract(_contract(status="draft"))
        with pytest.raises(DraftAppContractError, match="is draft"):
            store.get_contract("apps_rg", "resume_generation")

    def test_draft_contract_allowed_with_flag(self) -> None:
        store = InMemoryAppDomainStore()
        rec = _contract(status="draft")
        store.put_contract(rec)
        assert store.get_contract("apps_rg", "resume_generation", allow_draft=True) is rec


class TestSubcontractFailClosed:
    def test_eval_rubric_round_trip(self) -> None:
        store = InMemoryAppDomainStore()
        r = _rubric()
        store.put_eval_rubric(r)
        assert store.get_eval_rubric("rubric-1") is r

    def test_deprecated_rubric_raises(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_eval_rubric(_rubric(status="deprecated"))
        with pytest.raises(DeprecatedAppContractError):
            store.get_eval_rubric("rubric-1")

    def test_missing_rubric_raises(self) -> None:
        store = InMemoryAppDomainStore()
        with pytest.raises(UnknownAppContractError, match="no AppEvalRubricRecord"):
            store.get_eval_rubric("nope")

    def test_deprecated_threshold_raises(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_threshold_profile(_threshold(status="deprecated"))
        with pytest.raises(DeprecatedAppContractError):
            store.get_threshold_profile("thr-1")


class TestFixtureListing:
    def test_list_fixtures_for_app(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_fixture(_fixture(fixture_type="golden"))
        store.put_fixture(_fixture(fixture_type="regression"))
        store.put_fixture(_fixture(app_id="apps_lic", fixture_type="golden"))
        rg = store.list_fixtures_for_app("apps_rg")
        assert {r.fixture_id for r in rg} == {"fix-apps_rg-golden", "fix-apps_rg-regression"}

    def test_list_fixtures_filtered_by_type(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_fixture(_fixture(fixture_type="golden"))
        store.put_fixture(_fixture(fixture_type="regression"))
        only_golden = store.list_fixtures_for_app("apps_rg", fixture_type="golden")
        assert [r.fixture_type for r in only_golden] == ["golden"]


class TestClearAndDefaultStore:
    def test_clear_drops_records(self) -> None:
        store = InMemoryAppDomainStore()
        store.put_contract(_contract())
        store.clear()
        assert store.list_apps() == []
        with pytest.raises(UnknownAppContractError):
            store.get_contract("apps_rg", "resume_generation")

    def test_default_store_is_singleton(self) -> None:
        reset_default_app_domain_store()
        a = get_default_app_domain_store()
        b = get_default_app_domain_store()
        assert a is b

    def test_reset_default_store_replaces_instance(self) -> None:
        a = get_default_app_domain_store()
        reset_default_app_domain_store()
        b = get_default_app_domain_store()
        assert a is not b
