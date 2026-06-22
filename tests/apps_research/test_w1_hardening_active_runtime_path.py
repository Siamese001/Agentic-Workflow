"""apps-test-model: SPINE BINDING.

W1 Hardening Tests for apps_research U0 Runtime Customization Package

Validates that the canonical profile spine path is wired into the active
runtime entrypoint (not the retired core dispatch shim).

Required checks:
1. Active entrypoint uses U0-bound AppRuntimeProfile
2. No parallel retired dispatch import path
3. Package-driven U0 v2 remains available for package tests
4. Contract handoff proof for v2
5. Ownership boundary clean
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agentic_core.runtime.contracts.apps_research_runtime_package import (
    RuntimeCustomizationPackage,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.entry.u0_apps_research_binding import (
    u0_validate_apps_research,
)
from apps_research.runtime.u0.binding import u0_validate_apps_research_v2


class TestActiveEntrypointUsesProfileSpine:
    """Verify active entrypoint uses canonical profile + research handoff."""

    def test_profile_builder_binds_core_u0(self):
        from apps_research.runtime.profile_builder import build_app_runtime_contract

        profile = build_app_runtime_contract()
        assert profile.u0 is u0_validate_apps_research
        assert profile.app_id == "apps_research"

    def test_main_module_uses_spine_handoff_not_stub_l2(self):
        main_path = Path("apps_research/__main__.py")
        source = main_path.read_text(encoding="utf-8")
        assert "_run_profile_spine" in source
        assert "run_research_via_spine" in source
        assert "APPS_RESEARCH_L2_FORCE_STUB" not in source
        assert "resolve_company_brief_capability" not in source
        assert "from apps_research.integrations.governed_research_run import" not in source
        assert "GovernedResearchRun(" not in source
        assert "apps_research_dispatch" not in source

    def test_main_profile_spine_invokes_research_handoff(self, monkeypatch, tmp_path):
        from apps_research import __main__ as main_mod

        class _Record:
            run_id = "run-main-profile"
            topic = "TestCorp"
            company_brief_text = "TestCorp targeting brief"
            confidence_score = 0.8
            support_coverage = 0.8
            hop_terminal_error = ""
            fec_run_context = {}

        with patch(
            "apps_research.integrations.spine_handoff.run_research_via_spine",
            return_value=_Record(),
        ) as run_handoff:
            monkeypatch.setattr(main_mod, "_apps_research_runs_root", lambda: tmp_path)

            code = main_mod._run_profile_spine(
                ["--topic", "TestCorp", "--mode", "brief", "--depth", "standard"]
            )

        assert code == 0
        run_handoff.assert_called_once()
        assert (tmp_path / "run-main-profile" / "company_brief.json").exists()


class TestNoParallelRetiredDispatchPath:
    """Verify retired core dispatch module is not part of the live path."""

    def test_core_dispatch_module_absent(self):
        dispatch_path = Path("agentic_core/runtime/entry/apps_research_dispatch.py")
        assert not dispatch_path.exists(), (
            "agentic_core.runtime.entry.apps_research_dispatch must remain deleted; "
            "use apps_research.integrations.spine_handoff"
        )

    def test_runtime_entry_dispatch_module_removed(self):
        dispatch_path = Path("apps_research/runtime/entry/dispatch.py")
        assert not dispatch_path.is_file(), (
            "apps_research.runtime.entry.dispatch tombstone removed; "
            "use apps_research.integrations.spine_handoff"
        )


class TestContractHandoffProof:
    """Verify contract handoff includes all required fields (U0 v2 direct)."""

    def test_validated_request_includes_runtime_package_ref(self):
        pkg = RuntimeCustomizationPackage(
            package_id="test-pkg-ref",
            task_class="company_brief",
        )

        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-req-ref",
            run_id="test-run-ref",
        )

        validated, _receipt, _ctx = u0_validate_apps_research_v2(envelope)

        assert validated.app_payload["runtime_customization_package"]["package_digest"]

    def test_validated_request_includes_app_id(self):
        pkg = RuntimeCustomizationPackage(package_id="test-appid")

        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-req-appid",
            run_id="test-run-appid",
        )

        validated, _, _ = u0_validate_apps_research_v2(envelope)

        assert validated.app_id == "apps_research"

    def test_validated_request_includes_task_class(self):
        pkg = RuntimeCustomizationPackage(
            package_id="test-taskclass",
            task_class="company_brief",
        )

        envelope = RequestEnvelope(
            payload=AppsRgIngressPayload(
                app_id="apps_research",
                target_company="TestCorp",
                user_constraints={
                    "runtime_customization_package": pkg.to_dict(),
                },
            ),
            request_id="test-req-task",
            run_id="test-run-task",
        )

        validated, _, _ = u0_validate_apps_research_v2(envelope)

        assert validated.task_class == "company_brief"


class TestOwnershipBoundaryClean:
    """Verify apps_research package contains declarative refs only."""

    def test_package_no_callable_refs(self):
        pkg = RuntimeCustomizationPackage(package_id="test-no-callables")

        string_fields = [
            pkg.route_profile_ref,
            pkg.cache_profile_ref,
            pkg.judge_profile_ref,
            pkg.prompt_profile_ref,
        ]

        for field in string_fields:
            assert isinstance(field, str), f"Field {field} must be string ref, not callable"

    def test_package_read_only_by_default(self):
        pkg = RuntimeCustomizationPackage(package_id="test-readonly")

        assert pkg.write_policy == "read_only"
