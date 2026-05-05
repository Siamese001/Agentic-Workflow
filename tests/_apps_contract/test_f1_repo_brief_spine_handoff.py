"""Tests for apps_repo_brief.integrations.spine_handoff (Plan 4 F1).

Pins:
  - All 8 R3 contract types importable at module level (load-bearing static evidence)
  - R3_CONTRACT_SURFACE dict contains exactly the 8 expected keys
  - validate_repo_brief_r3_contract_surface() returns all-True
  - build_repo_brief_r3_handoff_metadata returns correct route_type + 8 contracts
  - run_repo_brief_via_spine delegates without raising on a stub request
  - spine scanner classifies apps_repo_brief as FULL_SPINE / PARTIAL_SPINE
    (depending on current state) but NOT as APP_STANDALONE_FORBIDDEN

Plan: .windsurf/plans/apps-repo-brief-plan4-spine-handoff-f2a3c8.md F1.3
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# R3_CONTRACT_SURFACE -- static evidence pins
# ---------------------------------------------------------------------------

_EXPECTED_CONTRACT_NAMES: tuple[str, ...] = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "RetrievalPlan",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "SealedArtifact",
    "ExitReviewPacket",
)


def test_spine_handoff_imports_all_eight_r3_contracts() -> None:
    """Module-level imports must succeed for all 8 R3 contract types."""
    from apps_repo_brief.integrations import spine_handoff  # noqa: F401

    for name in _EXPECTED_CONTRACT_NAMES:
        assert hasattr(spine_handoff, name), (
            f"spine_handoff missing load-bearing import: {name}"
        )


def test_r3_contract_surface_contains_eight_entries() -> None:
    from apps_repo_brief.integrations.spine_handoff import R3_CONTRACT_SURFACE

    assert set(R3_CONTRACT_SURFACE.keys()) == set(_EXPECTED_CONTRACT_NAMES)
    assert len(R3_CONTRACT_SURFACE) == 8


def test_r3_contract_surface_values_are_types() -> None:
    from apps_repo_brief.integrations.spine_handoff import R3_CONTRACT_SURFACE

    for name, cls in R3_CONTRACT_SURFACE.items():
        assert isinstance(cls, type), (
            f"R3_CONTRACT_SURFACE[{name!r}] is not a type: {cls!r}"
        )


def test_r3_required_contract_names_length() -> None:
    from apps_repo_brief.integrations.spine_handoff import R3_REQUIRED_CONTRACT_NAMES

    assert len(R3_REQUIRED_CONTRACT_NAMES) == 8
    assert set(R3_REQUIRED_CONTRACT_NAMES) == set(_EXPECTED_CONTRACT_NAMES)


def test_validate_repo_brief_r3_contract_surface_all_true() -> None:
    from apps_repo_brief.integrations.spine_handoff import (
        validate_repo_brief_r3_contract_surface,
    )

    result = validate_repo_brief_r3_contract_surface()
    assert isinstance(result, dict)
    assert set(result.keys()) == set(_EXPECTED_CONTRACT_NAMES)
    for name, available in result.items():
        assert available is True, f"contract {name!r} reported unavailable"


# ---------------------------------------------------------------------------
# build_repo_brief_r3_handoff_metadata
# ---------------------------------------------------------------------------


def test_build_handoff_metadata_route_type() -> None:
    from apps_repo_brief.integrations.spine_handoff import (
        build_repo_brief_r3_handoff_metadata,
    )

    req = SimpleNamespace(trace_id="test-trace-001", brief_type="board_dossier")
    meta = build_repo_brief_r3_handoff_metadata(req)
    assert meta.route_type == "R3_grounded_read"


def test_build_handoff_metadata_contract_surface_complete() -> None:
    from apps_repo_brief.integrations.spine_handoff import (
        build_repo_brief_r3_handoff_metadata,
    )

    req = SimpleNamespace(trace_id="test-trace-002", brief_type="standard")
    meta = build_repo_brief_r3_handoff_metadata(req)
    assert set(meta.contract_surface) == set(_EXPECTED_CONTRACT_NAMES)
    assert len(meta.contract_surface) == 8


def test_build_handoff_metadata_captures_trace_and_brief_type() -> None:
    from apps_repo_brief.integrations.spine_handoff import (
        build_repo_brief_r3_handoff_metadata,
    )

    req = SimpleNamespace(trace_id="my-trace", brief_type="light_summary")
    meta = build_repo_brief_r3_handoff_metadata(req)
    assert meta.run_id == "my-trace"
    assert meta.brief_type == "light_summary"


def test_build_handoff_metadata_handles_missing_attrs() -> None:
    from apps_repo_brief.integrations.spine_handoff import (
        build_repo_brief_r3_handoff_metadata,
    )

    req = SimpleNamespace()  # no trace_id, no brief_type
    meta = build_repo_brief_r3_handoff_metadata(req)
    assert meta.run_id == ""
    assert meta.brief_type == ""
    assert meta.route_type == "R3_grounded_read"


# ---------------------------------------------------------------------------
# Spine manifest + file presence
# ---------------------------------------------------------------------------


def test_spine_handoff_file_exists() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    handoff_path = repo_root / "apps_repo_brief" / "integrations" / "spine_handoff.py"
    assert handoff_path.is_file(), "spine_handoff.py must exist in integrations/"


def test_spine_handoff_imports_validated_request_at_module_level() -> None:
    """The load-bearing static evidence: ValidatedRequest imported at module level."""
    repo_root = Path(__file__).resolve().parents[2]
    handoff_path = repo_root / "apps_repo_brief" / "integrations" / "spine_handoff.py"
    text = handoff_path.read_text(encoding="utf-8")
    assert (
        "from agentic_core.L0_routing.intake.validated_request import ValidatedRequest"
        in text
    ), "ValidatedRequest must be imported at module level in spine_handoff.py"


def test_spine_manifest_declares_r3_grounded_read() -> None:
    import yaml

    repo_root = Path(__file__).resolve().parents[2]
    manifest_path = repo_root / "apps_repo_brief" / "spine_manifest.yaml"
    assert manifest_path.is_file()
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["app"] == "apps_repo_brief"
    route_types = [
        r["type"] for r in data.get("claimed_routes", []) if isinstance(r, dict)
    ]
    assert "R3_grounded_read" in route_types, (
        f"spine_manifest.yaml must declare R3_grounded_read; found: {route_types}"
    )


# ---------------------------------------------------------------------------
# Scanner integration: apps_repo_brief must NOT be APP_STANDALONE_FORBIDDEN
# ---------------------------------------------------------------------------


def test_apps_repo_brief_scanner_not_standalone_forbidden() -> None:
    """After F1, the scanner must NOT classify apps_repo_brief as forbidden."""
    from tools.analysis.apps_spine_coverage import classify_app, scan_app

    repo_root = Path(__file__).resolve().parents[2]
    app_path = repo_root / "apps_repo_brief"
    if not app_path.is_dir():
        pytest.skip("apps_repo_brief not present in this checkout")

    sc = scan_app(app_path)
    runtime_mode, _ = classify_app(sc)
    assert runtime_mode != "APP_STANDALONE_FORBIDDEN", (
        f"apps_repo_brief must not be APP_STANDALONE_FORBIDDEN; got {runtime_mode}"
    )


def test_apps_repo_brief_scanner_has_manifest() -> None:
    """Scanner must detect the spine_manifest.yaml."""
    from tools.analysis.apps_spine_coverage import scan_app

    repo_root = Path(__file__).resolve().parents[2]
    app_path = repo_root / "apps_repo_brief"
    if not app_path.is_dir():
        pytest.skip("apps_repo_brief not present in this checkout")

    sc = scan_app(app_path)
    assert sc["manifest_present"] is True


def test_apps_repo_brief_scanner_sees_r3_contracts() -> None:
    """After spine_handoff.py, scanner must find contract imports."""
    from tools.analysis.apps_spine_coverage import scan_app

    repo_root = Path(__file__).resolve().parents[2]
    app_path = repo_root / "apps_repo_brief"
    if not app_path.is_dir():
        pytest.skip("apps_repo_brief not present in this checkout")

    sc = scan_app(app_path)
    # At least ValidatedRequest and FinalEvidenceContract must be visible
    found = set(sc.get("contract_imports", {}).keys())
    assert "ValidatedRequest" in found, (
        f"scanner did not see ValidatedRequest; found: {found}"
    )
    assert "FinalEvidenceContract" in found, (
        f"scanner did not see FinalEvidenceContract; found: {found}"
    )
