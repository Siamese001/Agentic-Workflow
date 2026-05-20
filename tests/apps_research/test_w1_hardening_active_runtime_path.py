"""
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
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.entry.u0_apps_research_binding import (
    u0_validate_apps_research,
)
from apps_research.runtime.u0.binding import u0_validate_apps_research_v2
from agentic_core.runtime.contracts.apps_research_runtime_package import (
    RuntimeCustomizationPackage,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    AppsRgIngressPayload,
)


class TestActiveEntrypointUsesProfileSpine:
    """Verify active entrypoint uses canonical profile + core U0 binding."""

    def test_profile_builder_binds_core_u0(self):
        from apps_research.runtime.profile_builder import build_app_runtime_contract

        profile = build_app_runtime_contract()
        assert profile.u0 is u0_validate_apps_research
        assert profile.app_id == "apps_research"

    def test_main_module_uses_profile_spine_not_capability_registry(self):
        main_path = Path("apps_research/__main__.py")
        source = main_path.read_text(encoding="utf-8")
        assert "build_app_runtime_contract" in source
        assert "AppIngressRunner" in source
        assert "_run_profile_spine" in source
        assert "resolve_company_brief_capability" not in source
        assert "from apps_research.integrations.governed_research_run import" not in source
        assert "GovernedResearchRun(" not in source
        assert "apps_research_dispatch" not in source

    def test_main_profile_spine_invokes_u0_via_runner(self, monkeypatch):
        monkeypatch.setenv("APPS_RESEARCH_L2_FORCE_STUB", "1")
        from apps_research import __main__ as main_mod
        from apps_research.runtime.profile_builder import build_app_runtime_contract

        real_profile = build_app_runtime_contract()

        with patch(
            "agentic_core.runtime.entry.app_ingress_runner.AppIngressRunner"
        ) as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run.return_value = MagicMock(
                exit_status="success",
                outcome_authorized=True,
                output_artifact_path="/tmp/test.json",
            )
            mock_runner_cls.return_value = mock_runner

            code = main_mod._run_profile_spine(
                ["--topic", "TestCorp", "--mode", "brief", "--depth", "standard"]
            )

        assert code == 0
        mock_runner.run.assert_called_once()
        profile = mock_runner_cls.call_args.kwargs.get("profile") or mock_runner_cls.call_args[0][0]
        assert profile.u0 is u0_validate_apps_research
        assert profile.u0 is real_profile.u0


class TestNoParallelRetiredDispatchPath:
    """Verify retired core dispatch module is not part of the live path."""

    def test_core_dispatch_module_absent(self):
        dispatch_path = Path("agentic_core/runtime/entry/apps_research_dispatch.py")
        assert not dispatch_path.exists(), (
            "agentic_core.runtime.entry.apps_research_dispatch must remain deleted; "
            "use apps_research.runtime.profile_builder + AppIngressRunner"
        )

    def test_runtime_entry_dispatch_is_tombstone_only(self):
        import pytest as _pytest

        with _pytest.raises(ImportError, match="RETIRED"):
            import apps_research.runtime.entry.dispatch  # noqa: F401


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
