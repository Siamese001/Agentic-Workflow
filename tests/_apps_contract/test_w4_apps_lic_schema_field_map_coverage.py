"""W4 tests: apps_lic ingress contract schema regeneration and field-map coverage.

Verifies:
1. JSON Schema can be regenerated from AppsLicIngressContractV1 via Pydantic.
2. Schema matches the contract exactly (runtime_customization_package present).
3. All runtime_customization_package fields appear in schema.
4. Field-map covers every JSON pointer (silently_dropped == []).
5. runtime_customization_package pointers are MAPPED to ValidatedRequest.app_payload.*.
6. Derived fields (payload_digest, package_digest) have explicit receipts.
7. No new runtime behavior introduced (W4 is schema/field-map proof only).

Plan: apps-lic-w4-schema-field-map-proof
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIELD_MAP_PATH = (
    _REPO_ROOT / "apps_lic" / "contracts" / "apps_lic_ingress_field_map.v1.yaml"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    from tools.apps_lic.w4_schema_verify import generate_schema
    return generate_schema(write=True)


@pytest.fixture(scope="module")
def coverage_result(schema: dict[str, Any]) -> dict[str, Any]:
    from tools.apps_lic.w4_schema_verify import check_coverage
    return check_coverage(schema=schema, write=True)


@pytest.fixture(scope="module")
def field_map() -> dict[str, Any]:
    import yaml  # type: ignore[import]
    with open(_FIELD_MAP_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Test 1: Schema can be regenerated from Pydantic
# ---------------------------------------------------------------------------


class TestW4SchemaRegeneration:
    """W4 requirement 1 + 2: schema regenerated from Pydantic; matches contract."""

    def test_schema_is_generated_from_pydantic(self, schema: dict[str, Any]) -> None:
        """generate_schema() returns a non-empty dict."""
        assert isinstance(schema, dict)
        assert len(schema) > 0, "Schema must be non-empty"

    def test_schema_written_to_artifacts(self) -> None:
        """Schema file exists in artifacts/apps_lic/ after generation."""
        schema_path = _REPO_ROOT / "artifacts" / "apps_lic" / "apps_lic_ingress_contract_v1_schema.json"
        assert schema_path.exists(), f"Schema file missing at {schema_path}"
        data = json.loads(schema_path.read_text(encoding="utf-8"))
        assert "properties" in data, "Schema must have 'properties' key"

    def test_schema_title_matches_contract_class(self, schema: dict[str, Any]) -> None:
        """Schema title must reference AppsLicIngressContractV1."""
        title = schema.get("title", "")
        assert "AppsLicIngressContractV1" in title, (
            f"Expected 'AppsLicIngressContractV1' in schema title, got {title!r}"
        )

    def test_schema_has_transport_and_campaign(self, schema: dict[str, Any]) -> None:
        """Root-level required sections transport and campaign are in schema."""
        props = schema.get("properties", {})
        assert "transport" in props, "transport section missing from schema"
        assert "campaign" in props, "campaign section missing from schema"


# ---------------------------------------------------------------------------
# Test 2: runtime_customization_package in schema
# ---------------------------------------------------------------------------


class TestW4RuntimeCustomizationPackageInSchema:
    """W4 requirement 3: runtime_customization_package appears in schema."""

    def test_rcp_present_in_schema_properties(self, schema: dict[str, Any]) -> None:
        """runtime_customization_package must be a top-level property in the schema."""
        props = schema.get("properties", {})
        assert "runtime_customization_package" in props, (
            "runtime_customization_package missing from AppsLicIngressContractV1 schema"
        )

    def test_rcp_resolves_to_object_shape(self, schema: dict[str, Any]) -> None:
        """runtime_customization_package resolves to an object with known sub-fields."""
        from tools.apps_lic.w4_schema_verify import _collect_schema_pointers
        pointers = _collect_schema_pointers(schema)
        rcp_pointers = [p for p in pointers if p.startswith("/runtime_customization_package")]
        # Must have at least the top-level + all known sub-sections
        assert len(rcp_pointers) >= 30, (
            f"Expected >=30 runtime_customization_package pointers, got {len(rcp_pointers)}: "
            + str(rcp_pointers[:10])
        )

    def test_rcp_contains_profile_refs(self, schema: dict[str, Any]) -> None:
        """Key profile refs appear as schema pointers under rcp."""
        from tools.apps_lic.w4_schema_verify import _collect_schema_pointers
        pointers = set(_collect_schema_pointers(schema))
        required_pointers = {
            "/runtime_customization_package/exit_profile_ref",
            "/runtime_customization_package/learning_profile_ref",
            "/runtime_customization_package/meta_feedback_profile_ref",
            "/runtime_customization_package/cache_bypass_policy",
            "/runtime_customization_package/route_policy",
            "/runtime_customization_package/write_policy",
            "/runtime_customization_package/package_digest",
        }
        missing = required_pointers - pointers
        assert not missing, (
            f"runtime_customization_package sub-fields missing from schema: {sorted(missing)}"
        )

    def test_rcp_all_profile_ref_fields(self, schema: dict[str, Any]) -> None:
        """All 15 ProfileRef fields under rcp are in the schema."""
        from tools.apps_lic.w4_schema_verify import _collect_schema_pointers
        pointers = set(_collect_schema_pointers(schema))
        expected_refs = [
            "runtime_gate_profile_ref", "exit_profile_ref", "judge_profile_ref",
            "eval_rubric_ref", "threshold_profile_ref", "grader_roster_ref",
            "rubric_output_map_ref", "negative_controls_ref", "learning_profile_ref",
            "meta_feedback_profile_ref", "route_profile_ref", "retrieval_profile_ref",
            "prompt_profile_ref", "repair_profile_ref", "cache_profile_ref",
            "capability_profile_ref", "orchestration_profile_ref",
        ]
        missing = []
        for ref in expected_refs:
            ptr = f"/runtime_customization_package/{ref}"
            if ptr not in pointers:
                missing.append(ptr)
        assert not missing, (
            f"ProfileRef fields missing from schema: {missing}"
        )


# ---------------------------------------------------------------------------
# Test 3: Field-map coverage — no silently dropped fields
# ---------------------------------------------------------------------------


class TestW4FieldMapCoverage:
    """W4 requirement 4 + 8: field map covers all pointers, fail closed on drops."""

    def test_no_silently_dropped_fields(self, coverage_result: dict[str, Any]) -> None:
        """silently_dropped_fields must be empty — fail closed."""
        dropped = coverage_result["silently_dropped_fields"]
        assert dropped == [], (
            f"W4 FAIL: {len(dropped)} silently dropped fields detected:\n"
            + "\n".join(f"  {p}" for p in dropped)
        )

    def test_coverage_result_status_is_pass(self, coverage_result: dict[str, Any]) -> None:
        """Coverage result status must be PASS."""
        assert coverage_result["status"] == "PASS", (
            f"Coverage check returned status={coverage_result['status']!r}; "
            f"dropped={coverage_result['silently_dropped_fields']}"
        )

    def test_total_pointers_is_positive(self, coverage_result: dict[str, Any]) -> None:
        """total_pointers must be > 0 — proves the schema was actually enumerated."""
        assert coverage_result["total_pointers"] > 0

    def test_coverage_result_written_to_artifacts(self) -> None:
        """Coverage result JSON exists in artifacts/apps_lic/."""
        out = _REPO_ROOT / "artifacts" / "apps_lic" / "w4_field_map_coverage_result.json"
        assert out.exists(), f"Coverage result file missing at {out}"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "silently_dropped_fields" in data


# ---------------------------------------------------------------------------
# Test 4: runtime_customization_package pointers are MAPPED
# ---------------------------------------------------------------------------


class TestW4RcpPointersAreMapped:
    """W4 requirement 6: rcp pointers mapped to ValidatedRequest.app_payload.*"""

    def test_rcp_pointers_covered_in_field_map(
        self, schema: dict[str, Any], field_map: dict[str, Any]
    ) -> None:
        """Every /runtime_customization_package pointer has a field-map entry."""
        from tools.apps_lic.w4_schema_verify import (
            _collect_schema_pointers,
            _resolve_with_patterns,
        )
        mappings = field_map.get("mappings", {})
        pattern_mappings = field_map.get("pattern_mappings", {})
        section_aggregations = field_map.get("section_aggregations", {})

        pointers = _collect_schema_pointers(schema)
        rcp_pointers = [p for p in pointers if p.startswith("/runtime_customization_package")]

        uncovered = []
        for ptr in rcp_pointers:
            status = _resolve_with_patterns(ptr, mappings, pattern_mappings, section_aggregations)
            if status is None:
                uncovered.append(ptr)

        assert not uncovered, (
            f"{len(uncovered)} rcp pointers not covered in field map:\n"
            + "\n".join(f"  {p}" for p in uncovered)
        )

    def test_rcp_top_level_pointer_maps_to_app_payload(self, field_map: dict[str, Any]) -> None:
        """The /runtime_customization_package mapping targets app_payload."""
        mappings = field_map.get("mappings", {})
        entry = mappings.get("/runtime_customization_package", {})
        assert entry.get("status") == "MAPPED", (
            "/runtime_customization_package field-map entry must be MAPPED"
        )
        target = entry.get("target", "")
        assert "ValidatedRequest.app_payload.runtime_customization_package" in target, (
            f"rcp target must include app_payload path, got: {target!r}"
        )

    def test_rcp_pointer_count_matches_coverage_result(
        self, schema: dict[str, Any], coverage_result: dict[str, Any]
    ) -> None:
        """Coverage result rcp count matches direct schema enumeration."""
        from tools.apps_lic.w4_schema_verify import _collect_schema_pointers
        pointers = _collect_schema_pointers(schema)
        rcp_count = len([p for p in pointers if p.startswith("/runtime_customization_package")])
        assert coverage_result["runtime_customization_package_pointer_count"] == rcp_count


# ---------------------------------------------------------------------------
# Test 5: Derived fields have explicit receipts
# ---------------------------------------------------------------------------


class TestW4DerivedFieldReceipts:
    """W4 requirement 7: derived fields have explicit receipts."""

    def test_payload_digest_has_derived_receipt(self, field_map: dict[str, Any]) -> None:
        """/payload_digest must have status=DERIVED with a non-empty reason."""
        entry = field_map.get("mappings", {}).get("/payload_digest", {})
        assert entry.get("status") == "DERIVED", (
            f"/payload_digest must be DERIVED; got {entry.get('status')!r}"
        )
        assert entry.get("reason"), "/payload_digest must have a non-empty reason"

    def test_package_digest_has_derived_receipt(self, field_map: dict[str, Any]) -> None:
        """/runtime_customization_package/package_digest must have an explicit receipt."""
        ptr = "/runtime_customization_package/package_digest"
        entry = field_map.get("mappings", {}).get(ptr, {})
        assert entry.get("status") in ("DERIVED", "MAPPED"), (
            f"{ptr} must be DERIVED or MAPPED; got {entry.get('status')!r}"
        )
        assert entry.get("reason"), f"{ptr} must have a non-empty reason"

    def test_derived_receipts_via_verify_helper(self) -> None:
        """verify_derived_receipts() returns True for both required derived pointers."""
        from tools.apps_lic.w4_schema_verify import verify_derived_receipts
        receipts = verify_derived_receipts()
        for pointer, ok in receipts.items():
            assert ok, f"Derived field {pointer!r} missing explicit receipt in field map"


# ---------------------------------------------------------------------------
# Test 6: No runtime behavior changed
# ---------------------------------------------------------------------------


class TestW4NoRuntimeBehaviorChanged:
    """W4 requirement 9/10: W4 is proof-only; W3.5 boundary not regressed."""

    def test_w35_tests_still_importable(self) -> None:
        """W3.5 test module can be imported without error."""
        import importlib
        mod = importlib.import_module(
            "tests._apps_contract.test_w3_apps_lic_exit_l6_package_consumption"
        )
        assert mod is not None

    def test_exit_profile_fail_closed_still_applies(self) -> None:
        """_load_exit_profile still raises AppsLicExitProfileError on missing config."""
        import pytest
        from apps_lic.runtime.bindings.exit_binding import (
            AppsLicExitProfileError,
            _load_exit_profile,
        )
        import apps_lic.runtime.bindings.exit_binding as _mod
        from pathlib import Path

        # Patch to a non-existent path
        original = _mod._EXIT_PROFILE_PATH
        _mod._EXIT_PROFILE_PATH = Path("/tmp/__nonexistent_w4_probe__.json")
        try:
            with pytest.raises(AppsLicExitProfileError, match="fail_closed"):
                _load_exit_profile(None)
        finally:
            _mod._EXIT_PROFILE_PATH = original

    def test_u0_adapter_imports_cleanly(self) -> None:
        """U0 adapter still imports cleanly — no regressions from W4."""
        import importlib
        mod = importlib.import_module("apps_lic.runtime.u0.adapter")
        assert hasattr(mod, "apps_lic_u0_adapt")


if __name__ == "__main__":
    import pytest as _pytest
    _pytest.main([__file__, "-v"])
