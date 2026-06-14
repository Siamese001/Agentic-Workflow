"""Unit tests for agentic_core.L1_cognition.package_driven_l1_binding.

Wave 6.1 (P2 untested-module coverage). App-agnostic L1 binding that emits
planning hints from app-owned config. Covers the HintSource enum, AppHint /
PackageDrivenL1Plan dataclasses, the pure ``_extract_hint_from_profile``
dispatch, ``l1_plan_to_contract`` conversion, the end-to-end builder with a
real on-disk profile, and the documented NoneType-profile crash.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from agentic_core.L1_cognition.package_driven_l1_binding import (
    AppHint,
    HintSource,
    PackageDrivenL1Plan,
    _extract_hint_from_profile,
    l1_plan_package_driven,
    l1_plan_to_contract,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest


def _vr(**kw: object) -> ValidatedRequest:
    base: dict[str, object] = {
        "request_id": "req-1",
        "run_id": "run-1",
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "payload_digest": "d",
        "authority_validation_receipt": None,
        "trace_id": "trace-1",
        "tenant_id": "tenant-1",
        "l5_certification_ref": "cert-ok",
        "app_payload": {},
    }
    base.update(kw)
    return ValidatedRequest(**base)  # type: ignore[arg-type]


class TestHintSourceEnum:
    def test_members(self) -> None:
        assert {s.value for s in HintSource} == {
            "app_config",
            "payload",
            "package_ref",
            "default",
        }


class TestAppHint:
    def test_defaults(self) -> None:
        h = AppHint(hint_name="x", hint_value=1, hint_source="payload")
        assert h.confidence == "high"

    def test_frozen(self) -> None:
        h = AppHint(hint_name="x", hint_value=1, hint_source="payload")
        with pytest.raises(dataclasses.FrozenInstanceError):
            h.hint_value = 2  # type: ignore[misc]


class TestPackageDrivenL1Plan:
    def test_defaults(self) -> None:
        plan = PackageDrivenL1Plan(
            request_id="r",
            run_id="run",
            app_id="apps_rg",
            task_class="resume_generation",
            tenant_id="tn",
            app_hints=[],
            runtime_package_ref="pkg",
            l1_planning_profile_ref="prof",
        )
        assert plan.has_runtime_authority is False
        assert plan.schema_version == "AG9.L1.PKG.1"
        assert plan.trace_id == ""

    def test_frozen(self) -> None:
        plan = PackageDrivenL1Plan(
            request_id="r",
            run_id="run",
            app_id="a",
            task_class="t",
            tenant_id="tn",
            app_hints=[],
            runtime_package_ref="",
            l1_planning_profile_ref="",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            plan.app_id = "b"  # type: ignore[misc]


class TestExtractHintFromProfile:
    def test_payload_wins_first(self) -> None:
        h = _extract_hint_from_profile(
            "any_hint", profile={}, payload={"any_hint": 7}, package={}
        )
        assert h is not None
        assert h.hint_value == 7
        assert h.hint_source == "payload"

    def test_package_origin_explicit(self) -> None:
        h = _extract_hint_from_profile(
            "runtime_package_origin_hint", profile={}, payload={}, package={}
        )
        assert h is not None
        assert h.hint_value == "explicit"
        assert h.hint_source == "package"

    def test_package_origin_auto_injected(self) -> None:
        h = _extract_hint_from_profile(
            "runtime_package_origin_hint",
            profile={},
            payload={},
            package={"auto_injected_runtime_package": True},
        )
        assert h is not None
        assert h.hint_value == "auto_injected"

    def test_profile_section_resolved(self) -> None:
        profile = {"source_scope": {"default_sources": ["web", "internal"]}}
        h = _extract_hint_from_profile(
            "source_scope_hint", profile=profile, payload={}, package={}
        )
        assert h is not None
        assert h.hint_value == ["web", "internal"]
        assert h.hint_source == "app_config"

    def test_unknown_hint_returns_none(self) -> None:
        assert (
            _extract_hint_from_profile(
                "totally_unknown_hint", profile={}, payload={}, package={}
            )
            is None
        )

    def test_profile_missing_section_returns_none(self) -> None:
        assert (
            _extract_hint_from_profile(
                "source_scope_hint", profile={}, payload={}, package={}
            )
            is None
        )


class TestBuilderWithRealProfile:
    """l1_plan_package_driven crashes on a missing profile (see bug test), so
    exercise it against a real on-disk profile written under repo_root."""

    @pytest.fixture()
    def profile_ref(self) -> str:
        # repo_root resolution matches the module: parents[3] of the source file.
        import agentic_core.L1_cognition.package_driven_l1_binding as mod

        repo_root = Path(mod.__file__).resolve().parents[3]
        rel = "tests/unit/agentic_core/L1_cognition/_tmp_l1_profile.yaml"
        target = repo_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "source_scope:\n"
            "  default_sources: [internal]\n"
            "execution_hints:\n"
            "  grounding_required: true\n",
            encoding="utf-8",
        )
        try:
            yield rel
        finally:
            target.unlink(missing_ok=True)

    def test_builder_emits_plan_with_core_hints(self, profile_ref: str) -> None:
        if __import__("agentic_core.L1_cognition.package_driven_l1_binding", fromlist=["yaml"]).yaml is None:
            pytest.skip("PyYAML not available")
        vr = _vr(app_payload={"target_company": "Acme", "depth": "deep"})
        plan = l1_plan_package_driven(vr, l1_planning_profile_ref=profile_ref)
        assert isinstance(plan, PackageDrivenL1Plan)
        assert plan.app_id == "apps_rg"
        assert plan.has_runtime_authority is False
        names = {h.hint_name for h in plan.app_hints}
        assert "task_class_hint" in names
        assert "company_entity_hint" in names
        assert "risk_hint" in names

    def test_builder_risk_hint_marks_entity_ambiguity(self, profile_ref: str) -> None:
        if __import__("agentic_core.L1_cognition.package_driven_l1_binding", fromlist=["yaml"]).yaml is None:
            pytest.skip("PyYAML not available")
        vr = _vr(app_payload={})  # no target_company -> ambiguity
        plan = l1_plan_package_driven(vr, l1_planning_profile_ref=profile_ref)
        risk = next(h for h in plan.app_hints if h.hint_name == "risk_hint")
        assert risk.hint_value["entity_ambiguity"] is True


class TestBuilderTypeGuard:
    def test_non_validated_request_raises_typeerror(self) -> None:
        with pytest.raises(TypeError, match="Expected ValidatedRequest"):
            l1_plan_package_driven({"not": "a request"})  # type: ignore[arg-type]


class TestKnownBug:
    def test_missing_profile_crashes_with_nonetype_iter(self) -> None:
        """REGRESSION/BUG MARKER: when the resolved profile YAML does not exist,
        _load_l1_planning_profile returns None and the builder passes None into
        _extract_hint_from_profile, raising 'argument of type NoneType is not
        iterable'. Documents current (buggy) behavior."""
        vr = _vr(app_payload={"target_company": "Acme"})
        with pytest.raises(TypeError, match="NoneType"):
            l1_plan_package_driven(
                vr, l1_planning_profile_ref="does/not/exist/profile.yaml"
            )


class TestL1PlanToContract:
    def test_conversion_passes_unsupported_kwargs_to_contract(self) -> None:
        """BUG MARKER: l1_plan_to_contract calls L1PlanContract(task_class=...,
        app_hints=...) but the canonical L1PlanContract has neither parameter,
        so the conversion raises TypeError for ANY input. Documents the current
        (broken) behavior — the function is unusable as written."""
        plan = PackageDrivenL1Plan(
            request_id="r",
            run_id="run",
            app_id="apps_rg",
            task_class="resume_generation",
            tenant_id="tn",
            app_hints=[AppHint(hint_name="task_class_hint", hint_value="t", hint_source="x")],
            runtime_package_ref="",
            l1_planning_profile_ref="",
            trace_id="trace",
        )
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            l1_plan_to_contract(plan)
