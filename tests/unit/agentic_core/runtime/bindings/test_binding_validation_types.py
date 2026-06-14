"""Unit tests for agentic_core.runtime.bindings.binding_validation_types.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``binding_validation_types`` (L_RUNTIME) holds plain dataclasses carrying
per-section / compat / handoff validation outcomes. These are pure mutable
dataclasses with default-factory list fields; coverage targets construction,
field defaults, mutation independence, and the SectionStatus literal contract.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.bindings.binding_validation_types import (
    ExitCompatValidationResult,
    L6HandoffValidationResult,
    MalformedRefRecord,
    SectionValidationDetail,
)


class TestSectionValidationDetail:
    def test_required_fields(self) -> None:
        d = SectionValidationDetail(section_name="profile", status="PASS")
        assert d.section_name == "profile"
        assert d.status == "PASS"

    def test_list_defaults_empty(self) -> None:
        d = SectionValidationDetail(section_name="s", status="FAIL")
        assert d.errors == []
        assert d.warnings == []
        assert d.resolved_refs == []
        assert d.missing_refs == []
        assert d.malformed_refs == []
        assert d.hash_validation_results == []
        assert d.policy_validation_results == []

    def test_default_lists_are_independent_instances(self) -> None:
        a = SectionValidationDetail(section_name="a", status="PASS")
        b = SectionValidationDetail(section_name="b", status="PASS")
        a.errors.append("boom")
        assert a.errors == ["boom"]
        assert b.errors == []

    def test_mutable_fields_accept_explicit_values(self) -> None:
        d = SectionValidationDetail(
            section_name="s",
            status="FAIL",
            errors=["e1"],
            missing_refs=["ref://x"],
        )
        assert d.errors == ["e1"]
        assert d.missing_refs == ["ref://x"]


class TestMalformedRefRecord:
    def test_required_fields(self) -> None:
        r = MalformedRefRecord(context="ctx", detail="bad ref")
        assert r.context == "ctx"
        assert r.detail == "bad ref"

    def test_path_hint_defaults_none(self) -> None:
        assert MalformedRefRecord(context="c", detail="d").path_hint is None

    def test_path_hint_explicit(self) -> None:
        r = MalformedRefRecord(context="c", detail="d", path_hint="apps_x/foo.yaml")
        assert r.path_hint == "apps_x/foo.yaml"


class TestExitCompatValidationResult:
    def test_defaults(self) -> None:
        r = ExitCompatValidationResult(status="PASS")
        assert r.status == "PASS"
        assert r.errors == []
        assert r.warnings == []
        assert r.contract_path is None

    def test_contract_path_accepts_path(self) -> None:
        p = Path("certification/contract.json")
        r = ExitCompatValidationResult(status="FAIL", contract_path=p)
        assert r.contract_path == p

    def test_default_lists_independent(self) -> None:
        a = ExitCompatValidationResult(status="PASS")
        b = ExitCompatValidationResult(status="PASS")
        a.warnings.append("w")
        assert b.warnings == []


class TestL6HandoffValidationResult:
    def test_defaults(self) -> None:
        r = L6HandoffValidationResult(status="PASS")
        assert r.status == "PASS"
        assert r.errors == []
        assert r.warnings == []

    def test_explicit_errors(self) -> None:
        r = L6HandoffValidationResult(status="FAIL", errors=["missing exhaust"])
        assert r.status == "FAIL"
        assert r.errors == ["missing exhaust"]

    def test_default_lists_independent(self) -> None:
        a = L6HandoffValidationResult(status="PASS")
        b = L6HandoffValidationResult(status="PASS")
        a.errors.append("x")
        assert b.errors == []
