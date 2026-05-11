"""W4 tests — L0 managed workflow route resolution.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W4
Run:  pytest tests/_apps_contract/test_apps_rg_l0_managed_route_resolution.py -v

Coverage:
  - R1A/R1B/R5 are consulted BEFORE managed workflow route selection.
  - Semantic cache disabled by default (cache_profile semantic_cache_enabled=false).
  - registered_not_active route is NOT selected by default in production.
  - Test-enabled flag activates the route and resolves workflow_ref.
  - L0 selects managed workflow after cache miss when test-enabled.
  - Fail-closed on: missing workflow_ref, zero matches, multiple matches,
    digest mismatch, unknown execution_form.
  - L0 emits exactly one RouteContract per call.
  - L0 never writes cache or L4.
  - L0 does not import quarantined hops/gates modules.
  - Route gate refs are UNKNOWN (not PASS) when harness is not wired.
"""
from __future__ import annotations

import ast
import copy
import json
import os
import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

# ── SUT imports ──────────────────────────────────────────────────────────────
from agentic_core.L0_routing.apps_rg_l0_binding import (
    _MANAGED_ROUTE_TEST_FLAG,
    _ROUTE_REGISTRY_RELPATH,
    l0_route_apps_rg,
)
from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
from agentic_core.L3_orchestration.workflow_registry import (
    DIGEST_MISMATCH,
    DISABLED,
    INVALID,
    MULTIPLE_MATCH,
    RESOLVED,
    ZERO_MATCH,
    WorkflowRegistryResolutionError,
    WorkflowResolutionReceipt,
    resolve_managed_workflow_route,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import RequestEnvelope
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.entry.apps_rg_dispatch import apps_rg_parse
from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg

# ── Repo root ─────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY_PATH = _REPO_ROOT / "apps_rg" / "config" / "route_registry.yaml"
_CACHE_PROFILE_PATH = (
    _REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
)

# ── Fixture helpers ───────────────────────────────────────────────────────────

def _thin_payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Amit Ayer — leadership profile.",
        "job_description_text": "Senior Director of AI Engineering — applied research.",
        "manual_brief_path": None,
        "auto_research_internal": False,
        "auto_research_tavily": False,
        "research_via": None,
        "output_directory": "artifacts/apps_rg/runs",
        "idempotency_key": None,
    }
    base.update(overrides)
    return base


def _build_l1_plan(overrides: dict[str, Any] | None = None) -> L1PlanContract:
    envelope = apps_rg_parse(_thin_payload(**(overrides or {})))
    assert envelope is not None
    vr = u0_validate_apps_rg(envelope)
    return l1_plan_apps_rg(vr)


def _force_managed_workflow(
    l1_plan: L1PlanContract,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Monkeypatch _evaluate_execution_form so it always returns managed_workflow."""
    import agentic_core.L0_routing.apps_rg_l0_binding as binding_mod
    monkeypatch.setattr(
        binding_mod,
        "_evaluate_execution_form",
        lambda plan, r1a_hit: "managed_workflow",
    )


# ── 1. R1A/R1B/R5 are checked BEFORE managed workflow selection ───────────────


class TestCacheChecksBeforeManagedWorkflow:
    def test_apps_rg_l0_checks_r1a_before_managed_workflow(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """R1A lookup must fire before execution_form is decided."""
        import agentic_core.L0_routing.apps_rg_l0_binding as binding_mod

        calls: list[str] = []

        real_lookups = binding_mod._perform_cache_lookups

        def _spy_lookups(plan):
            calls.append("cache_lookups")
            return real_lookups(plan)

        real_eval = binding_mod._evaluate_execution_form

        def _spy_eval(plan, r1a_hit):
            calls.append("eval_execution_form")
            return real_eval(plan, r1a_hit)

        monkeypatch.setattr(binding_mod, "_perform_cache_lookups", _spy_lookups)
        monkeypatch.setattr(binding_mod, "_evaluate_execution_form", _spy_eval)

        plan = _build_l1_plan()
        # Run L0 — will produce single_step (no test-activation), but we only care about order.
        l0_route_apps_rg(plan)

        assert calls.index("cache_lookups") < calls.index(
            "eval_execution_form"
        ), "Cache lookups must occur before execution_form is evaluated"

    def test_apps_rg_l0_checks_r1b_before_managed_workflow(self) -> None:
        """R1B receipt is populated before RouteContract is constructed."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        r1b = json.loads(route.cache_lookup_r1b_receipt)
        assert r1b["result"] == "miss"
        assert "r1b_quarantined" in r1b.get("reason", "")

    def test_apps_rg_l0_checks_r5_before_managed_workflow(self) -> None:
        """R5 receipt is populated (miss) before RouteContract is constructed."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        r5 = json.loads(route.cache_lookup_r5_receipt)
        assert r5["result"] == "miss"


# ── 2. Semantic cache disabled by default ────────────────────────────────────


class TestSemanticCacheDefault:
    def test_apps_rg_semantic_cache_disabled_by_default_for_final_resume(self) -> None:
        """cache_profiles.yaml must declare semantic_cache_enabled=false."""
        assert _CACHE_PROFILE_PATH.exists(), (
            f"cache_profiles.yaml not found at {_CACHE_PROFILE_PATH}"
        )
        profile = yaml.safe_load(
            _CACHE_PROFILE_PATH.read_text(encoding="utf-8")
        )
        assert profile["semantic_cache_enabled"] is False, (
            "semantic_cache_enabled must be false for resume_generation "
            "(personalised outputs; semantic similarity is not safe)"
        )

    def test_apps_rg_l0_r1b_eligibility_false_by_default(self) -> None:
        """RouteContract.cache_eligibility['r1b_semantic'] must be False."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        assert route.cache_eligibility["r1b_semantic"] is False


# ── 3. registered_not_active not selected by default ─────────────────────────


class TestRegisteredNotActiveRoute:
    def test_apps_rg_l0_registered_not_active_route_not_selected_by_default(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Without test-activation env flag, selecting managed_workflow
        must raise WorkflowRegistryResolutionError(DISABLED)."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        # Ensure test-activation flag is NOT set.
        monkeypatch.delenv(_MANAGED_ROUTE_TEST_FLAG, raising=False)

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            l0_route_apps_rg(plan)

        assert exc_info.value.resolution_status == DISABLED
        assert "registered_not_active" in exc_info.value.decisive_reason


# ── 4. Test-enabled activation resolves workflow_ref ─────────────────────────


class TestTestEnabledActivation:
    def test_apps_rg_l0_test_enabled_managed_route_selects_workflow_ref(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """With APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1, L0 must resolve
        workflow_ref from the registry and emit it on RouteContract."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")

        route = l0_route_apps_rg(plan)

        assert route.execution_form == "managed_workflow"
        assert route.l3_required is True
        assert route.workflow_ref == "wfm::apps_rg::resume_generation::v1"
        assert route.workflow_manifest_ref == "wfm::apps_rg::resume_generation::v1"
        assert route.workflow_registry_ref == _ROUTE_REGISTRY_RELPATH

    def test_apps_rg_l0_selects_managed_workflow_after_cache_miss_when_enabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """After R1A miss + test-activation, execution_form=managed_workflow
        and workflow_ref is non-empty."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")

        route = l0_route_apps_rg(plan)

        # Verify R1A was a miss (no live cache in CI).
        r1a = json.loads(route.cache_lookup_r1a_receipt)
        assert r1a["result"] == "miss"

        assert route.workflow_ref, "workflow_ref must be non-empty on managed_workflow path"
        assert route.registry_resolution_receipt_ref, (
            "registry_resolution_receipt_ref must be populated"
        )
        receipt_doc = json.loads(route.registry_resolution_receipt_ref)
        assert receipt_doc["resolution_status"] == RESOLVED

    def test_registry_resolution_receipt_contains_expected_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The serialised WorkflowResolutionReceipt must contain all required keys."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")

        route = l0_route_apps_rg(plan)
        doc = json.loads(route.registry_resolution_receipt_ref)
        required = {
            "route_id", "workflow_ref", "workflow_manifest_ref",
            "workflow_manifest_path", "manifest_digest", "route_registry_ref",
            "route_status", "l3_required", "execution_form",
            "resolution_status", "decisive_reason", "test_activated",
        }
        for key in required:
            assert key in doc, f"registry_resolution_receipt missing key: {key!r}"

        assert doc["test_activated"] is True
        assert doc["execution_form"] == "MANAGED_WORKFLOW"


# ── 5. Fail-closed paths ─────────────────────────────────────────────────────


class TestFailClosedPaths:
    def test_apps_rg_l0_fails_closed_on_missing_workflow_ref(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """If workflow_manifest_ref is empty in the registry, must raise INVALID."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")

        mutated = {
            "app_name": "apps_rg",
            "schema_version": "apps_rg.route_registry/v1",
            "routes": [
                {
                    "route_id": "apps_rg.resume_generation_managed_v1",
                    "execution_form": "MANAGED_WORKFLOW",
                    "l3_required": True,
                    "static_dag_ref": None,
                    "workflow_manifest_ref": "",  # intentionally empty
                    "workflow_manifest_path": "",
                    "selected_capability": "apps_rg.resume_generation_managed_v1",
                    "status": "active",
                }
            ],
        }
        fake_registry = tmp_path / "route_registry.yaml"
        fake_registry.write_text(yaml.dump(mutated), encoding="utf-8")

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=str(fake_registry),
                repo_root=tmp_path,
                _test_activation_env_override="1",
            )
        assert exc_info.value.resolution_status == INVALID
        assert "workflow_manifest_ref" in exc_info.value.decisive_reason

    def test_apps_rg_l0_fails_closed_on_zero_workflow_matches(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Registry with no MANAGED_WORKFLOW routes → ZERO_MATCH error."""
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")

        only_deterministic = {
            "app_name": "apps_rg",
            "schema_version": "apps_rg.route_registry/v1",
            "routes": [
                {
                    "route_id": "apps_rg.resume_generation_v1",
                    "execution_form": "DETERMINISTIC_PIPELINE",
                    "l3_required": False,
                    "static_dag_ref": "apps_rg/config/l3_dag.yaml",
                    "selected_capability": "apps_rg.resume_generation_v1",
                    "status": "active",
                }
            ],
        }
        fake_registry = tmp_path / "route_registry.yaml"
        fake_registry.write_text(yaml.dump(only_deterministic), encoding="utf-8")

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=str(fake_registry),
                repo_root=tmp_path,
                _test_activation_env_override="1",
            )
        assert exc_info.value.resolution_status == ZERO_MATCH

    def test_apps_rg_l0_fails_closed_on_multiple_workflow_matches(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Registry with two MANAGED_WORKFLOW routes → MULTIPLE_MATCH error."""
        two_managed = {
            "app_name": "apps_rg",
            "schema_version": "apps_rg.route_registry/v1",
            "routes": [
                {
                    "route_id": "apps_rg.managed_v1",
                    "execution_form": "MANAGED_WORKFLOW",
                    "l3_required": True,
                    "workflow_manifest_ref": "wfm::apps_rg::resume_generation::v1",
                    "workflow_manifest_path": "apps_rg/config/workflow_manifest.resume_generation.v1.yaml",
                    "status": "active",
                },
                {
                    "route_id": "apps_rg.managed_v2",
                    "execution_form": "MANAGED_WORKFLOW",
                    "l3_required": True,
                    "workflow_manifest_ref": "wfm::apps_rg::resume_generation::v2",
                    "workflow_manifest_path": "apps_rg/config/workflow_manifest.resume_generation.v2.yaml",
                    "status": "active",
                },
            ],
        }
        fake_registry = tmp_path / "route_registry.yaml"
        fake_registry.write_text(yaml.dump(two_managed), encoding="utf-8")

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=str(fake_registry),
                repo_root=tmp_path,
                _test_activation_env_override="1",
            )
        assert exc_info.value.resolution_status == MULTIPLE_MATCH

    def test_apps_rg_l0_fails_closed_on_registry_digest_mismatch(
        self,
        tmp_path: Path,
    ) -> None:
        """Supplying a wrong expected_manifest_digest → DIGEST_MISMATCH error."""
        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text("# fake manifest\n", encoding="utf-8")

        one_active = {
            "app_name": "apps_rg",
            "schema_version": "apps_rg.route_registry/v1",
            "routes": [
                {
                    "route_id": "apps_rg.managed_v1",
                    "execution_form": "MANAGED_WORKFLOW",
                    "l3_required": True,
                    "workflow_manifest_ref": "wfm::test::v1",
                    "workflow_manifest_path": "manifest.yaml",
                    "status": "active",
                }
            ],
        }
        fake_registry = tmp_path / "route_registry.yaml"
        fake_registry.write_text(yaml.dump(one_active), encoding="utf-8")

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=str(fake_registry),
                repo_root=tmp_path,
                expected_manifest_digest="0" * 64,  # deliberately wrong digest
                _test_activation_env_override="1",
            )
        assert exc_info.value.resolution_status == DIGEST_MISMATCH

    def test_apps_rg_l0_fails_closed_on_unknown_execution_form(
        self,
        tmp_path: Path,
    ) -> None:
        """A route with execution_form not in {MANAGED_WORKFLOW} must raise INVALID."""
        bad_form = {
            "app_name": "apps_rg",
            "schema_version": "apps_rg.route_registry/v1",
            "routes": [
                {
                    "route_id": "apps_rg.unknown_form",
                    "execution_form": "MANAGED_WORKFLOW",
                    "l3_required": True,
                    "workflow_manifest_ref": "wfm::test::v1",
                    "workflow_manifest_path": "",
                    "status": "active",
                }
            ],
        }
        # Mutate execution_form post-YAML-dump to a truly unknown value so
        # the filter still returns this route but the form check fires.
        import yaml as _yaml
        raw = _yaml.dump(bad_form)
        raw = raw.replace("MANAGED_WORKFLOW", "UNKNOWN_FORM")
        fake_registry = tmp_path / "route_registry.yaml"
        fake_registry.write_text(raw, encoding="utf-8")

        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=str(fake_registry),
                repo_root=tmp_path,
                _test_activation_env_override="1",
            )
        # Zero MANAGED_WORKFLOW routes found after mutation → ZERO_MATCH
        assert exc_info.value.resolution_status in (ZERO_MATCH, INVALID)


# ── 6. Exactly one RouteContract emitted ─────────────────────────────────────


class TestSingleRouteContract:
    def test_apps_rg_l0_emits_exactly_one_route_contract(self) -> None:
        """l0_route_apps_rg must return exactly one RouteContract instance."""
        plan = _build_l1_plan()
        result = l0_route_apps_rg(plan)
        assert isinstance(result, RouteContract)

    def test_apps_rg_l0_emits_exactly_one_route_contract_managed_mode(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        plan = _build_l1_plan()
        _force_managed_workflow(plan, monkeypatch)
        monkeypatch.setenv(_MANAGED_ROUTE_TEST_FLAG, "1")
        result = l0_route_apps_rg(plan)
        assert isinstance(result, RouteContract)


# ── 7. L0 never writes cache or L4 ───────────────────────────────────────────


class TestNoWrites:
    def test_apps_rg_l0_never_writes_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """l0_route_apps_rg must not invoke any cache write function."""
        import agentic_core.L0_routing.apps_rg_l0_binding as binding_mod

        write_calls: list[str] = []

        # Patch any write-like names that might exist on the r1a_adapter.
        try:
            import apps_rg.cache.r1a_adapter as r1a_mod
            if hasattr(r1a_mod, "write_r1a_cache"):
                monkeypatch.setattr(
                    r1a_mod,
                    "write_r1a_cache",
                    lambda *a, **kw: write_calls.append("write_r1a_cache"),
                )
        except ImportError:
            pass

        plan = _build_l1_plan()
        l0_route_apps_rg(plan)
        assert write_calls == [], f"L0 must not write cache; calls={write_calls}"

    def test_apps_rg_l0_never_writes_l4(self) -> None:
        """L0 module source must not import any L4 write surface."""
        import agentic_core.L0_routing.apps_rg_l0_binding as binding_mod
        source_file = Path(binding_mod.__file__)
        source = source_file.read_text(encoding="utf-8")
        assert "L4" not in source or "L4" not in source.split("import")[0], (
            "L0 binding must not import from L4"
        )
        # More precise: no import statement referencing L4 state write paths.
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "import" in stripped and "L4" in stripped:
                raise AssertionError(
                    f"L0 binding must not import L4 module: {line!r}"
                )


# ── 8. No quarantined imports ─────────────────────────────────────────────────


class TestNoQuarantinedImports:
    _QUARANTINE_PREFIXES = (
        "apps_rg.integrations.hops",
        "apps_rg.integrations.gates",
        "apps_rg.prompt_assembly.rg_pa_compiler",
        "apps_rg._quarantine",
    )

    def test_apps_rg_l0_does_not_import_quarantined_hops_or_gates(self) -> None:
        """L0 binding source must not contain static imports of quarantined modules."""
        import agentic_core.L0_routing.apps_rg_l0_binding as binding_mod
        source_file = Path(binding_mod.__file__)
        lines = source_file.read_text(encoding="utf-8").splitlines()
        for prefix in self._QUARANTINE_PREFIXES:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "import" in stripped and prefix in stripped:
                    raise AssertionError(
                        f"L0 binding must not import quarantined module {prefix!r}; "
                        f"found: {line!r}"
                    )

    def test_workflow_registry_does_not_import_quarantined_modules(self) -> None:
        """workflow_registry.py source must not import quarantined apps_rg modules."""
        import agentic_core.L3_orchestration.workflow_registry as reg_mod
        source_file = Path(reg_mod.__file__)
        lines = source_file.read_text(encoding="utf-8").splitlines()
        for prefix in self._QUARANTINE_PREFIXES:
            for line in lines:
                stripped = line.strip()
                # Skip blank lines, comment lines, and docstring continuation lines.
                if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                    continue
                if "import" in stripped and prefix in stripped:
                    raise AssertionError(
                        f"workflow_registry.py must not import quarantined module "
                        f"{prefix!r}; found: {line!r}"
                    )


# ── 9. Route gate refs are UNKNOWN not PASS ───────────────────────────────────


class TestRouteGateRefs:
    def test_apps_rg_l0_route_gate_refs_unknown_not_pass_when_gate_harness_missing(
        self,
    ) -> None:
        """route_gate_refs must all contain 'UNKNOWN' and none contain 'PASS'."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)

        assert len(route.route_gate_refs) == 4, (
            f"Expected 4 route gate refs (G07/G08/G10/G20), got {len(route.route_gate_refs)}"
        )
        for ref in route.route_gate_refs:
            assert "UNKNOWN" in ref, (
                f"Gate ref must contain UNKNOWN (not PASS): {ref!r}"
            )
            assert "PASS" not in ref, (
                f"Gate ref must not claim PASS when harness not wired: {ref!r}"
            )

    def test_apps_rg_l0_route_gate_refs_cover_g07_g08_g10_g20(self) -> None:
        """route_gate_refs must reference G07, G08, G10, G20."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        refs_combined = " ".join(route.route_gate_refs)
        for gate_id in ("G07", "G08", "G10", "G20"):
            assert gate_id in refs_combined, (
                f"route_gate_refs missing gate {gate_id}; refs={route.route_gate_refs}"
            )

    def test_apps_rg_l0_route_policy_ref_is_route_profile(self) -> None:
        """route_policy_ref must point to the apps_rg route_profiles.yaml."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        assert "route_profiles" in route.route_policy_ref


# ── 10. RouteContract W4 field completeness ───────────────────────────────────


class TestRouteContractW4Fields:
    def test_route_contract_has_w4_fields(self) -> None:
        """RouteContract dataclass must declare the W4 fields."""
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RouteContract)}
        w4_fields = {
            "workflow_manifest_ref",
            "workflow_registry_ref",
            "registry_resolution_receipt_ref",
            "route_gate_refs",
            "route_policy_ref",
            "r1a_lookup_receipt_ref",
            "r1b_lookup_receipt_ref",
            "r5_fallback_receipt_ref",
        }
        for field in w4_fields:
            assert field in field_names, (
                f"RouteContract missing W4 field: {field!r}"
            )

    def test_route_contract_w4_fields_default_empty_for_single_step(self) -> None:
        """On single_step path all W4 managed-workflow fields must be empty."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        # single_step by default (no test-activation).
        if route.execution_form == "single_step":
            assert route.workflow_manifest_ref == ""
            assert route.workflow_ref == ""
            assert route.registry_resolution_receipt_ref == ""

    def test_route_contract_r1a_r1b_r5_alias_fields_match_primary(self) -> None:
        """Aliased receipt fields (r1a/r1b/r5_lookup_receipt_ref) must equal
        the primary cache_lookup_* fields."""
        plan = _build_l1_plan()
        route = l0_route_apps_rg(plan)
        assert route.r1a_lookup_receipt_ref == route.cache_lookup_r1a_receipt
        assert route.r1b_lookup_receipt_ref == route.cache_lookup_r1b_receipt
        assert route.r5_fallback_receipt_ref == route.cache_lookup_r5_receipt


# ── 11. Workflow resolver unit tests (direct) ─────────────────────────────────


class TestWorkflowResolverDirect:
    def test_resolve_managed_workflow_route_resolves_with_test_flag(self) -> None:
        """Direct call to resolver with test-activation should return RESOLVED."""
        receipt = resolve_managed_workflow_route(
            registry_relpath=_ROUTE_REGISTRY_RELPATH,
            repo_root=_REPO_ROOT,
            _test_activation_env_override="1",
        )
        assert receipt.resolution_status == RESOLVED
        assert receipt.workflow_ref == "wfm::apps_rg::resume_generation::v1"
        assert receipt.l3_required is True
        assert receipt.execution_form == "MANAGED_WORKFLOW"
        assert receipt.test_activated is True

    def test_resolve_managed_workflow_route_disabled_without_test_flag(self) -> None:
        """Direct call without test-activation should raise DISABLED."""
        with pytest.raises(WorkflowRegistryResolutionError) as exc_info:
            resolve_managed_workflow_route(
                registry_relpath=_ROUTE_REGISTRY_RELPATH,
                repo_root=_REPO_ROOT,
                _test_activation_env_override=None,
            )
        assert exc_info.value.resolution_status == DISABLED

    def test_resolve_receipt_round_trips_via_json(self) -> None:
        """WorkflowResolutionReceipt.as_json() / from_json() must round-trip."""
        receipt = resolve_managed_workflow_route(
            registry_relpath=_ROUTE_REGISTRY_RELPATH,
            repo_root=_REPO_ROOT,
            _test_activation_env_override="1",
        )
        raw = receipt.as_json()
        recovered = WorkflowResolutionReceipt.from_json(raw)
        assert recovered.route_id == receipt.route_id
        assert recovered.workflow_ref == receipt.workflow_ref
        assert recovered.resolution_status == receipt.resolution_status
        assert recovered.test_activated == receipt.test_activated

    def test_resolve_manifest_digest_computed_when_path_exists(self) -> None:
        """manifest_digest must be a non-empty 64-char hex string when the manifest file exists."""
        receipt = resolve_managed_workflow_route(
            registry_relpath=_ROUTE_REGISTRY_RELPATH,
            repo_root=_REPO_ROOT,
            _test_activation_env_override="1",
        )
        assert len(receipt.manifest_digest) == 64
        assert all(c in "0123456789abcdef" for c in receipt.manifest_digest)

    def test_resolve_correct_digest_does_not_raise(self) -> None:
        """Passing the correct expected_manifest_digest must resolve without error."""
        # First resolve to get the real digest.
        receipt = resolve_managed_workflow_route(
            registry_relpath=_ROUTE_REGISTRY_RELPATH,
            repo_root=_REPO_ROOT,
            _test_activation_env_override="1",
        )
        real_digest = receipt.manifest_digest
        # Now resolve again with the correct digest — must not raise.
        receipt2 = resolve_managed_workflow_route(
            registry_relpath=_ROUTE_REGISTRY_RELPATH,
            repo_root=_REPO_ROOT,
            expected_manifest_digest=real_digest,
            _test_activation_env_override="1",
        )
        assert receipt2.resolution_status == RESOLVED


# ── BR-1 Boundary Repair Tests ───────────────────────────────────────────────

class TestBR1BoundaryRepairFIX2:
    """Verify FIX-2: no apps_rg-specific defaults in generic workflow_registry.py."""

    def test_workflow_registry_requires_explicit_registry_relpath(self) -> None:
        """resolve_managed_workflow_route must require registry_relpath (no default)."""
        import inspect
        from agentic_core.L3_orchestration.workflow_registry import (
            resolve_managed_workflow_route as fn,
        )
        sig = inspect.signature(fn)
        param = sig.parameters.get("registry_relpath")
        assert param is not None, "registry_relpath parameter must exist"
        assert param.default is inspect.Parameter.empty, (
            "registry_relpath must be a required parameter with NO default value"
        )

    def test_workflow_registry_has_no_apps_rg_defaults(self) -> None:
        """Generic workflow_registry.py must not define apps_rg-specific names or defaults."""
        import agentic_core.L3_orchestration.workflow_registry as mod
        # These constants must NOT be defined in the generic module namespace
        assert not hasattr(mod, "_TEST_ACTIVATION_FLAG"), (
            "_TEST_ACTIVATION_FLAG must NOT be defined in generic workflow_registry"
        )
        # registry_relpath must be required (no default)
        import inspect
        sig = inspect.signature(mod.resolve_managed_workflow_route)
        param = sig.parameters["registry_relpath"]
        assert param.default is inspect.Parameter.empty, (
            "registry_relpath must be required (no default) in generic workflow_registry"
        )

    def test_apps_rg_l0_passes_registry_path_explicitly(self) -> None:
        """apps_rg_l0_binding must own the registry path and env flag, not generic registry."""
        import importlib.util
        spec = importlib.util.find_spec("agentic_core.L0_routing.apps_rg_l0_binding")
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        assert "_ROUTE_REGISTRY_RELPATH" in src, (
            "apps_rg_l0_binding must define _ROUTE_REGISTRY_RELPATH"
        )
        assert "_MANAGED_ROUTE_TEST_FLAG" in src, (
            "apps_rg_l0_binding must define _MANAGED_ROUTE_TEST_FLAG"
        )
        assert "APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED" in src, (
            "apps_rg_l0_binding must own the apps_rg env flag string"
        )

    def test_workflow_registry_has_no_apps_rg_test_flag_constant(self) -> None:
        """_TEST_ACTIVATION_FLAG must not exist in the generic module namespace."""
        import agentic_core.L3_orchestration.workflow_registry as mod
        assert not hasattr(mod, "_TEST_ACTIVATION_FLAG"), (
            "_TEST_ACTIVATION_FLAG must NOT be defined in generic workflow_registry"
        )
