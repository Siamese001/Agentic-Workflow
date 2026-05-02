"""Read-only lookup APIs for app-domain contract records.

Sibling to ``lookup.py``. The runtime resolver
(``agentic_core/L0_routing/app_domain_resolver.py``) consults this surface
during L0 dispatch to bind per-app refs into the RouteContract.

Hard rules:

- Read-only. No mutation. UWG remains the sole write authority.
- Fail-closed: deprecated and unknown entries raise. The runtime is
  forbidden to fall back to an "any active rubric" default.
- Resolution by ``(app_id, task_class)`` is the canonical key. Resolution
  by record id is also exposed for proof bundle hydration.
- ``status == "active"`` is required for runtime resolution.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional, Tuple

from agentic_core.L4_state.contracts.app_domain import (
    AppCapabilityProfileRecord,
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppFixtureRecord,
    AppGraderRosterRecord,
    AppInputContractRecord,
    AppNegativeControlRecord,
    AppOrchestrationProfileRecord,
    AppOutputSchemaRecord,
    AppPromptProfileRecord,
    AppRetrievalProfileRecord,
    AppRouteProfileRecord,
    AppThresholdProfileRecord,
)


class AppDomainLookupError(RuntimeError):
    """Base for app-domain lookup failures."""


class UnknownAppContractError(AppDomainLookupError):
    """Raised when no contract exists for the requested (app_id, task_class)."""


class DeprecatedAppContractError(AppDomainLookupError):
    """Raised when the requested contract is deprecated."""


class DraftAppContractError(AppDomainLookupError):
    """Raised when the requested contract is still draft (forbidden at runtime)."""


class InMemoryAppDomainStore:
    """Thread-safe in-memory store of app-domain contract records.

    Production deployments substitute a durable backend; the contract
    surface (this class's public methods) is what the runtime depends on.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # Top-level manifest by (app_id, task_class) — task_class "*" is the
        # app-wide manifest covering all task_classes; task_class-specific
        # entries can override.
        self._contracts: Dict[Tuple[str, str], AppDomainContractRecord] = {}
        self._contract_by_id: Dict[str, AppDomainContractRecord] = {}
        # Subcontract maps keyed by record_id
        self._input_contracts: Dict[str, AppInputContractRecord] = {}
        self._output_schemas: Dict[str, AppOutputSchemaRecord] = {}
        self._eval_rubrics: Dict[str, AppEvalRubricRecord] = {}
        self._threshold_profiles: Dict[str, AppThresholdProfileRecord] = {}
        self._grader_rosters: Dict[str, AppGraderRosterRecord] = {}
        self._retrieval_profiles: Dict[str, AppRetrievalProfileRecord] = {}
        self._prompt_profiles: Dict[str, AppPromptProfileRecord] = {}
        self._capability_profiles: Dict[str, AppCapabilityProfileRecord] = {}
        self._route_profiles: Dict[str, AppRouteProfileRecord] = {}
        self._orchestration_profiles: Dict[str, AppOrchestrationProfileRecord] = {}
        self._fixtures: Dict[str, AppFixtureRecord] = {}
        self._negative_controls: Dict[str, AppNegativeControlRecord] = {}

    # ------------------------------------------------------------------
    # Registration (called only by the UWG-side registration adapter).
    # The store itself does NOT enforce "UWG is the sole writer" — that's
    # the registration adapter's job. The store is a passive read tier.
    # ------------------------------------------------------------------
    def put_contract(self, record: AppDomainContractRecord) -> None:
        with self._lock:
            self._contract_by_id[record.app_domain_contract_id] = record
            # The contract is keyed (app_id, "*") for the app-wide manifest.
            # A given app may register multiple manifests at task-class
            # granularity by including (app_id, task_class) keyed entries
            # — the apps in this codebase use a single manifest per app.
            self._contracts[(record.app_id, "*")] = record
            for tc in record.task_classes:
                self._contracts[(record.app_id, tc.task_class)] = record

    def put_input_contract(self, record: AppInputContractRecord) -> None:
        with self._lock:
            self._input_contracts[record.input_contract_id] = record

    def put_output_schema(self, record: AppOutputSchemaRecord) -> None:
        with self._lock:
            self._output_schemas[record.output_schema_id] = record

    def put_eval_rubric(self, record: AppEvalRubricRecord) -> None:
        with self._lock:
            self._eval_rubrics[record.eval_rubric_id] = record

    def put_threshold_profile(self, record: AppThresholdProfileRecord) -> None:
        with self._lock:
            self._threshold_profiles[record.threshold_profile_id] = record

    def put_grader_roster(self, record: AppGraderRosterRecord) -> None:
        with self._lock:
            self._grader_rosters[record.grader_roster_id] = record

    def put_retrieval_profile(self, record: AppRetrievalProfileRecord) -> None:
        with self._lock:
            self._retrieval_profiles[record.retrieval_profile_id] = record

    def put_prompt_profile(self, record: AppPromptProfileRecord) -> None:
        with self._lock:
            self._prompt_profiles[record.prompt_profile_id] = record

    def put_capability_profile(self, record: AppCapabilityProfileRecord) -> None:
        with self._lock:
            self._capability_profiles[record.capability_profile_id] = record

    def put_route_profile(self, record: AppRouteProfileRecord) -> None:
        with self._lock:
            self._route_profiles[record.route_profile_id] = record

    def put_orchestration_profile(self, record: AppOrchestrationProfileRecord) -> None:
        with self._lock:
            self._orchestration_profiles[record.orchestration_profile_id] = record

    def put_fixture(self, record: AppFixtureRecord) -> None:
        with self._lock:
            self._fixtures[record.fixture_id] = record

    def put_negative_control(self, record: AppNegativeControlRecord) -> None:
        with self._lock:
            self._negative_controls[record.negative_control_id] = record

    # ------------------------------------------------------------------
    # Read-only queries
    # ------------------------------------------------------------------
    def get_contract(
        self,
        app_id: str,
        task_class: str,
        *,
        allow_draft: bool = False,
    ) -> AppDomainContractRecord:
        """Return the contract for (app_id, task_class). Fail-closed."""
        with self._lock:
            record = self._contracts.get((app_id, task_class))
            if record is None:
                # Try the app-wide manifest before failing.
                record = self._contracts.get((app_id, "*"))
            if record is None:
                raise UnknownAppContractError(
                    f"no AppDomainContractRecord for app_id={app_id!r}, task_class={task_class!r}",
                )
            if record.status == "deprecated":
                raise DeprecatedAppContractError(
                    f"AppDomainContractRecord({record.app_domain_contract_id}) is deprecated",
                )
            if record.status == "draft" and not allow_draft:
                raise DraftAppContractError(
                    f"AppDomainContractRecord({record.app_domain_contract_id}) is draft",
                )
            return record

    def get_contract_by_id(self, contract_id: str) -> AppDomainContractRecord:
        with self._lock:
            record = self._contract_by_id.get(contract_id)
            if record is None:
                raise UnknownAppContractError(
                    f"no AppDomainContractRecord with id {contract_id!r}",
                )
            return record

    def get_eval_rubric(self, rubric_id: str) -> AppEvalRubricRecord:
        with self._lock:
            r = self._eval_rubrics.get(rubric_id)
            if r is None:
                raise UnknownAppContractError(f"no AppEvalRubricRecord {rubric_id!r}")
            if r.status == "deprecated":
                raise DeprecatedAppContractError(f"AppEvalRubricRecord({rubric_id}) deprecated")
            return r

    def get_threshold_profile(self, profile_id: str) -> AppThresholdProfileRecord:
        with self._lock:
            r = self._threshold_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppThresholdProfileRecord {profile_id!r}")
            if r.status == "deprecated":
                raise DeprecatedAppContractError(
                    f"AppThresholdProfileRecord({profile_id}) deprecated",
                )
            return r

    def get_grader_roster(self, roster_id: str) -> AppGraderRosterRecord:
        with self._lock:
            r = self._grader_rosters.get(roster_id)
            if r is None:
                raise UnknownAppContractError(f"no AppGraderRosterRecord {roster_id!r}")
            return r

    def get_retrieval_profile(self, profile_id: str) -> AppRetrievalProfileRecord:
        with self._lock:
            r = self._retrieval_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppRetrievalProfileRecord {profile_id!r}")
            return r

    def get_prompt_profile(self, profile_id: str) -> AppPromptProfileRecord:
        with self._lock:
            r = self._prompt_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppPromptProfileRecord {profile_id!r}")
            return r

    def get_capability_profile(self, profile_id: str) -> AppCapabilityProfileRecord:
        with self._lock:
            r = self._capability_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppCapabilityProfileRecord {profile_id!r}")
            return r

    def get_route_profile(self, profile_id: str) -> AppRouteProfileRecord:
        with self._lock:
            r = self._route_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppRouteProfileRecord {profile_id!r}")
            return r

    def get_orchestration_profile(self, profile_id: str) -> AppOrchestrationProfileRecord:
        with self._lock:
            r = self._orchestration_profiles.get(profile_id)
            if r is None:
                raise UnknownAppContractError(f"no AppOrchestrationProfileRecord {profile_id!r}")
            return r

    def get_input_contract(self, contract_id: str) -> AppInputContractRecord:
        with self._lock:
            r = self._input_contracts.get(contract_id)
            if r is None:
                raise UnknownAppContractError(f"no AppInputContractRecord {contract_id!r}")
            return r

    def get_output_schema(self, schema_id: str) -> AppOutputSchemaRecord:
        with self._lock:
            r = self._output_schemas.get(schema_id)
            if r is None:
                raise UnknownAppContractError(f"no AppOutputSchemaRecord {schema_id!r}")
            return r

    def get_fixture(self, fixture_id: str) -> AppFixtureRecord:
        with self._lock:
            r = self._fixtures.get(fixture_id)
            if r is None:
                raise UnknownAppContractError(f"no AppFixtureRecord {fixture_id!r}")
            return r

    def get_negative_control(self, control_id: str) -> AppNegativeControlRecord:
        with self._lock:
            r = self._negative_controls.get(control_id)
            if r is None:
                raise UnknownAppContractError(f"no AppNegativeControlRecord {control_id!r}")
            return r

    def list_apps(self) -> List[str]:
        with self._lock:
            return sorted({app_id for (app_id, _) in self._contracts})

    def list_fixtures_for_app(
        self, app_id: str, *, fixture_type: Optional[str] = None,
    ) -> List[AppFixtureRecord]:
        with self._lock:
            out = [r for r in self._fixtures.values() if r.app_id == app_id]
            if fixture_type is not None:
                out = [r for r in out if r.fixture_type == fixture_type]
            return out

    def list_negative_controls_for_app(
        self, app_id: str,
    ) -> List[AppNegativeControlRecord]:
        with self._lock:
            return [r for r in self._negative_controls.values() if r.app_id == app_id]

    def clear(self) -> None:
        """Test hook — drop all records."""
        with self._lock:
            self._contracts.clear()
            self._contract_by_id.clear()
            self._input_contracts.clear()
            self._output_schemas.clear()
            self._eval_rubrics.clear()
            self._threshold_profiles.clear()
            self._grader_rosters.clear()
            self._retrieval_profiles.clear()
            self._prompt_profiles.clear()
            self._capability_profiles.clear()
            self._route_profiles.clear()
            self._orchestration_profiles.clear()
            self._fixtures.clear()
            self._negative_controls.clear()


# ----------------------------------------------------------------------------
# Process-wide default store
# ----------------------------------------------------------------------------

_default_store: Optional[InMemoryAppDomainStore] = None
_default_lock = threading.Lock()


def get_default_app_domain_store() -> InMemoryAppDomainStore:
    """Return the process-wide default store (lazy-initialized)."""
    global _default_store
    with _default_lock:
        if _default_store is None:
            _default_store = InMemoryAppDomainStore()
        return _default_store


def reset_default_app_domain_store() -> None:
    """Reset the default store. Test hook."""
    global _default_store
    with _default_lock:
        _default_store = InMemoryAppDomainStore()


__all__ = [
    "AppDomainLookupError",
    "UnknownAppContractError",
    "DeprecatedAppContractError",
    "DraftAppContractError",
    "InMemoryAppDomainStore",
    "get_default_app_domain_store",
    "reset_default_app_domain_store",
]
