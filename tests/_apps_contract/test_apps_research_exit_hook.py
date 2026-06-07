"""Contract tests for apps_research exit-hook adoption.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-exec-research-exit-hook-adoption-a8d3c5.md`` W2.P3.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cert_route_registry_present() -> None:
    path = REPO_ROOT / "apps_research" / "config" / "cert_route_registry.yaml"
    assert path.exists(), f"missing: {path}"


def test_cert_route_registry_has_invoke_exit_eval_true() -> None:
    from apps_research.__main__ import _load_cert_route_entry

    path = REPO_ROOT / "apps_research" / "config" / "cert_route_registry.yaml"
    entry = _load_cert_route_entry(path)
    assert entry is not None
    assert entry.get("invoke_exit_eval") is True
    assert entry.get("route_id") == "apps_research.company_brief_v1"


def test_rubric_output_map_path_resolves() -> None:
    from apps_research.__main__ import _load_cert_route_entry

    path = REPO_ROOT / "apps_research" / "config" / "cert_route_registry.yaml"
    entry = _load_cert_route_entry(path)
    assert entry is not None
    rel = entry.get("rubric_output_map_path")
    assert isinstance(rel, str) and rel
    assert (REPO_ROOT / rel).exists(), f"rubric output map missing: {rel}"


def test_load_cert_route_entry_missing_file_returns_none() -> None:
    from apps_research.__main__ import _load_cert_route_entry

    assert _load_cert_route_entry(REPO_ROOT / "nonexistent.yaml") is None


def test_build_exit_receipts_populates_fec() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_research.cert.fec_producer import produce_fec
    from apps_research.__main__ import _build_exit_receipts

    clear_registry()
    register_producer("apps_research", produce_fec)

    fec = resolve_fec(
        "apps_research",
        {"route_id": "apps_research.company_brief_v1", "template_ids": ["company_brief_v1"]},
    )
    receipts = _build_exit_receipts({"route_id": "apps_research.company_brief_v1"}, fec)
    assert receipts["final_evidence_contract"]["producer"] == "apps_research.cert.fec_producer"
    assert receipts["route_contract"] == {"route_id": "apps_research.company_brief_v1"}
    assert "output" in receipts


def test_build_exit_receipts_handles_none_fec() -> None:
    from apps_research.__main__ import _build_exit_receipts

    receipts = _build_exit_receipts({}, None)
    assert receipts["final_evidence_contract"] == {}


def test_maybe_run_exit_hook_fail_soft() -> None:
    from apps_research.__main__ import _maybe_run_exit_hook

    _maybe_run_exit_hook({})
    _maybe_run_exit_hook(None)


@pytest.fixture(autouse=True)
def _restore_registry():
    from apps_shared.cert.fec_producer import clear_registry

    yield
    clear_registry()
