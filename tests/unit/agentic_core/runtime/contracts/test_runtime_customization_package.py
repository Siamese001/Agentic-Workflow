"""Unit tests for agentic_core.runtime.contracts.runtime_customization_package.

W6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P2 U0 contract.
``runtime_customization_package`` (L_RUNTIME) is the app-agnostic base contract
that carries package metadata + profile refs into the governed spine. This suite
covers the pure, deterministic surface: frozen dataclass defaults, the
``__post_init__`` auto-digest, digest determinism / field sensitivity,
``to_dict``/``from_dict`` round-trip + unknown-field capture, ``validate_schema``
required-field + schema branches, the ``ValidationStatus`` enum member set, the
``PackageValidationReceipt`` frozen receipt, and the two exception types.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.runtime_customization_package import (
    PackageDigestMismatchError,
    PackageValidationReceipt,
    RuntimeCustomizationPackage,
    UnknownPackageFieldError,
    ValidationStatus,
)


def _pkg(**overrides):
    base = {"package_id": "pkg-1", "app_id": "apps_rg", "task_class": "draft"}
    base.update(overrides)
    return RuntimeCustomizationPackage(**base)


class TestValidationStatusEnum:
    def test_member_values(self) -> None:
        assert {s.value for s in ValidationStatus} == {
            "valid",
            "invalid",
            "auto_injected",
            "explicit",
        }


class TestConstructionDefaults:
    def test_minimal_defaults(self) -> None:
        p = RuntimeCustomizationPackage(package_id="pkg-1")
        assert p.package_version == "1.0.0"
        assert p.app_id == ""
        assert p.task_class == ""
        assert p.package_origin == "unknown"
        assert p.auto_injected_runtime_package is False
        assert p.validation_status == "unknown"

    def test_default_collections_are_independent(self) -> None:
        a = RuntimeCustomizationPackage(package_id="a")
        b = RuntimeCustomizationPackage(package_id="b")
        assert a.profile_refs == {} and a.registry_digest_set == []
        assert a.validation_errors == [] and a.extra == {}
        # default_factory must not share instances across objects.
        assert a.profile_refs is not b.profile_refs
        assert a.extra is not b.extra

    def test_frozen(self) -> None:
        p = _pkg()
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.app_id = "other"  # type: ignore[misc]


class TestPostInitDigest:
    def test_digest_auto_computed_when_absent(self) -> None:
        p = _pkg()
        assert p.package_digest
        assert len(p.package_digest) == 64  # sha-256 hexdigest

    def test_explicit_digest_preserved(self) -> None:
        p = _pkg(package_digest="explicit-digest")
        assert p.package_digest == "explicit-digest"


class TestDigestDeterminism:
    def test_same_inputs_same_digest(self) -> None:
        assert _pkg().package_digest == _pkg().package_digest

    @pytest.mark.parametrize(
        "field,value",
        [
            ("package_id", "pkg-2"),
            ("package_version", "2.0.0"),
            ("app_id", "apps_qna"),
            ("task_class", "score"),
            ("package_ref", "some/ref.yaml"),
            ("policy_hash", "ph"),
            ("blueprint_hash", "bh"),
        ],
    )
    def test_field_change_changes_digest(self, field: str, value: str) -> None:
        assert _pkg(**{field: value}).package_digest != _pkg().package_digest

    def test_profile_refs_change_changes_digest(self) -> None:
        assert _pkg(profile_refs={"route": "r.yaml"}).package_digest != _pkg().package_digest

    def test_extra_change_changes_digest(self) -> None:
        assert _pkg(extra={"k": "v"}).package_digest != _pkg().package_digest

    def test_excluded_fields_do_not_change_digest(self) -> None:
        # registry_digest_set, package_origin, validation_* are NOT in the digest body.
        baseline = _pkg().package_digest
        assert _pkg(registry_digest_set=["x"]).package_digest == baseline
        assert _pkg(package_origin="explicit").package_digest == baseline
        assert _pkg(validation_status="valid").package_digest == baseline


class TestSerialization:
    def test_to_dict_keys(self) -> None:
        d = _pkg().to_dict()
        for key in (
            "package_id",
            "package_version",
            "app_id",
            "task_class",
            "package_digest",
            "profile_refs",
            "extra",
        ):
            assert key in d

    def test_round_trip_preserves_identity_fields(self) -> None:
        original = _pkg(profile_refs={"route": "r.yaml"}, extra={"a": 1})
        restored = RuntimeCustomizationPackage.from_dict(original.to_dict())
        assert restored.package_id == original.package_id
        assert restored.app_id == original.app_id
        assert restored.profile_refs == original.profile_refs
        assert restored.package_digest == original.package_digest

    def test_from_dict_routes_unknown_fields_to_extra(self) -> None:
        p = RuntimeCustomizationPackage.from_dict(
            {"package_id": "pkg-1", "mystery_field": "boo"}
        )
        assert p.extra["mystery_field"] == "boo"

    def test_from_dict_merges_unknown_into_existing_extra(self) -> None:
        p = RuntimeCustomizationPackage.from_dict(
            {"package_id": "pkg-1", "extra": {"known": 1}, "surprise": 2}
        )
        assert p.extra == {"known": 1, "surprise": 2}


class TestValidateSchema:
    def test_valid_package_passes(self) -> None:
        ok, errors = _pkg().validate_schema()
        assert ok is True
        assert errors == []

    @pytest.mark.parametrize(
        "missing,expected",
        [
            ("package_id", "package_id is required"),
            ("app_id", "app_id is required"),
            ("task_class", "task_class is required"),
        ],
    )
    def test_missing_required_field_reported(self, missing: str, expected: str) -> None:
        kwargs = {"package_id": "pkg-1", "app_id": "apps_rg", "task_class": "draft"}
        kwargs[missing] = ""
        ok, errors = RuntimeCustomizationPackage(**kwargs).validate_schema()
        assert ok is False
        assert expected in errors

    def test_unknown_extra_field_flagged_by_schema(self) -> None:
        p = _pkg(extra={"weird": 1})
        ok, errors = p.validate_schema(schema={"allowed_fields": [], "required_fields": []})
        assert ok is False
        assert "Unknown field in extra: weird" in errors

    def test_required_schema_field_missing_flagged(self) -> None:
        p = _pkg(extra={})
        ok, errors = p.validate_schema(
            schema={"allowed_fields": ["needed"], "required_fields": ["needed"]}
        )
        assert ok is False
        assert "Required field missing in extra: needed" in errors

    def test_schema_allowed_and_present_passes(self) -> None:
        p = _pkg(extra={"needed": 1})
        ok, errors = p.validate_schema(
            schema={"allowed_fields": ["needed"], "required_fields": ["needed"]}
        )
        assert ok is True
        assert errors == []


class TestPackageValidationReceipt:
    def test_construction_and_default_schema_version(self) -> None:
        r = PackageValidationReceipt(
            package_id="pkg-1",
            package_version="1.0.0",
            task_class="draft",
            validation_passed=True,
            unknown_fields_found=[],
            digest_verified=True,
            timestamp_iso="2026-06-14T00:00:00Z",
        )
        assert r.schema_version == "AG9.U0.PKG.1"
        assert r.validation_passed is True

    def test_receipt_is_frozen(self) -> None:
        r = PackageValidationReceipt(
            package_id="pkg-1",
            package_version="1.0.0",
            task_class="draft",
            validation_passed=True,
            unknown_fields_found=[],
            digest_verified=True,
            timestamp_iso="2026-06-14T00:00:00Z",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.validation_passed = False  # type: ignore[misc]


class TestExceptions:
    def test_unknown_field_error_default_message(self) -> None:
        exc = UnknownPackageFieldError("weird")
        assert exc.field == "weird"
        assert "weird" in str(exc)
        assert isinstance(exc, Exception)

    def test_unknown_field_error_custom_message(self) -> None:
        exc = UnknownPackageFieldError("weird", message="custom")
        assert str(exc) == "custom"

    def test_digest_mismatch_error_fields_and_message(self) -> None:
        exc = PackageDigestMismatchError(expected="a" * 32, actual="b" * 32)
        assert exc.expected == "a" * 32
        assert exc.actual == "b" * 32
        assert "expected" in str(exc) and "got" in str(exc)
