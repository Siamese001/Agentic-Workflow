"""W1 — apps_rg U0 core runtime package ingest (pa-exec-flowchart-gap-f2a8c3)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from apps_rg.runtime.bindings.u0_binding import (
    APPS_RG_TASK_CLASS,
    AppsRgU0RejectedError,
    u0_validate_apps_rg,
)
from apps_rg.runtime.bindings.u0_package_ingest import (
    AppsRgRuntimePackageRegistry,
    U0PackageValidationError,
    assert_package_files_on_disk,
    default_package_ref,
    ingest_apps_rg_runtime_package,
)
from apps_rg.runtime.bindings.u0_rejection import (
    AppsRgIngressReasonCode,
    AppsRgRejectedRequestNotice,
)
from apps_rg.runtime.dispatch.apps_rg_dispatch import apps_rg_parse


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _thin_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "app_id": "apps_rg",
        "task_class": APPS_RG_TASK_CLASS,
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "source_resume_text": "Leadership profile content.",
        "job_description_text": "Senior Director role description.",
        "manual_brief_path": "artifact:brief",
    }
    base.update(overrides)
    return base


class TestPackageSsotOnDisk:
    def test_registry_and_package_yaml_exist(self) -> None:
        assert_package_files_on_disk()

    def test_registry_resolves_resume_generation_package(self) -> None:
        registry = AppsRgRuntimePackageRegistry()
        ref, _schema, reason = registry.resolve_default_package_ref(
            "apps_rg",
            APPS_RG_TASK_CLASS,
            {"request_id": "req-test"},
        )
        assert ref == default_package_ref()
        assert "Resolved" in reason or ref

    def test_registry_lists_domain_contract_refs(self) -> None:
        pkg_path = _repo_root() / default_package_ref()
        data = yaml.safe_load(pkg_path.read_text(encoding="utf-8"))
        refs = data.get("profile_refs") or {}
        assert "route_profile" in refs
        assert "retrieval_profile" in refs
        assert (_repo_root() / refs["route_profile"]).is_file()


class TestPackageIngestHelper:
    def test_ingest_returns_digest_and_receipt(self) -> None:
        result = ingest_apps_rg_runtime_package()
        assert result.package.package_id
        assert len(result.package.package_digest) == 64
        assert result.validation_receipt.validation_passed is True
        assert result.package_dict.get("route_profile_ref")

    def test_registry_parse_failure_is_typed_validation_error(self, tmp_path: Path) -> None:
        registry_path = tmp_path / "apps_rg" / "config" / "domain_contract" / "runtime_package_registry.yaml"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text("default_packages: [", encoding="utf-8")

        registry = AppsRgRuntimePackageRegistry(registry_base_path=tmp_path)

        with pytest.raises(U0PackageValidationError) as exc_info:
            registry.load_app_registry("apps_rg")

        assert exc_info.value.field == "runtime_package_registry"
        assert exc_info.value.reason_code == "registry_parse_error"
        assert exc_info.value.receipt["registry_path"] == str(registry_path)


class TestU0ValidatePackageWiring:
    def test_validated_request_stamps_identity_fields(self) -> None:
        env = apps_rg_parse(_thin_payload())
        vr = u0_validate_apps_rg(env)
        assert vr.session_id
        assert vr.trace_root
        assert vr.caller_scope_baseline.startswith("user:") or vr.caller_scope_baseline.startswith(
            "tenant:"
        )

    def test_app_payload_carries_runtime_customization_package(self) -> None:
        env = apps_rg_parse(_thin_payload())
        vr = u0_validate_apps_rg(env)
        rcp = vr.app_payload.get("runtime_customization_package")
        assert isinstance(rcp, dict)
        assert rcp.get("route_profile_ref")
        assert len(str(rcp.get("package_digest") or "")) == 64

    def test_profile_manifest_binds_package_ref_and_digest(self) -> None:
        env = apps_rg_parse(_thin_payload())
        vr = u0_validate_apps_rg(env)
        pm = vr.app_payload.get("profile_manifest") or {}
        assert pm.get("runtime_customization_package_ref") == default_package_ref()
        assert len(str(pm.get("runtime_customization_package_digest") or "")) == 64

    def test_package_validation_receipt_on_app_payload(self) -> None:
        env = apps_rg_parse(_thin_payload())
        vr = u0_validate_apps_rg(env)
        receipt = vr.app_payload.get("package_validation_receipt")
        assert receipt and receipt.get("validation_passed") is True


class TestU0TerminalRejection:
    def test_missing_required_keys_emits_rejected_notice(self) -> None:
        class _EnvelopeMissingTargets:
            app_payload = {
                "app_id": "apps_rg",
                "task_class": APPS_RG_TASK_CLASS,
                "source_resume_text": "text only",
                "job_description_text": "jd",
            }

        with pytest.raises(AppsRgU0RejectedError) as exc_info:
            u0_validate_apps_rg(_EnvelopeMissingTargets())
        notice = exc_info.value.notice
        assert isinstance(notice, AppsRgRejectedRequestNotice)
        assert notice.rejection_reason == AppsRgIngressReasonCode.FIELD_TYPE_MISMATCH
        assert "target_company" in str(notice.machine_readable_detail.get("missing_keys", []))
