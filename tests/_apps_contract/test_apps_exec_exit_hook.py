"""Contract tests for apps_exec exit-hook adoption.

Plan: ``.windsurf/plans/apps-exec-research-exit-hook-adoption-a8d3c5.md`` W1.P3.

Verifies the wiring landed by W1.P2:
- `_load_cert_route_entry` parses `cert_route_registry.yaml` correctly.
- `_build_exit_receipts` populates `final_evidence_contract` via FEC.
- `_maybe_run_exit_hook` is fail-soft on every failure mode.
- `cert_route_registry.yaml` has `invoke_exit_eval=true` and the required
  `rubric_output_map_path` pointing at an on-disk file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_cert_route_registry_present() -> None:
    path = REPO_ROOT / "apps_exec" / "config" / "cert_route_registry.yaml"
    assert path.exists(), f"missing: {path}"


def test_cert_route_registry_has_invoke_exit_eval_true() -> None:
    from apps_exec.__main__ import _load_cert_route_entry

    path = REPO_ROOT / "apps_exec" / "config" / "cert_route_registry.yaml"
    entry = _load_cert_route_entry(path)
    assert entry is not None
    assert entry.get("invoke_exit_eval") is True
    assert entry.get("route_id") == "apps_exec.execution_v1"


def test_rubric_output_map_path_resolves() -> None:
    from apps_exec.__main__ import _load_cert_route_entry

    path = REPO_ROOT / "apps_exec" / "config" / "cert_route_registry.yaml"
    entry = _load_cert_route_entry(path)
    assert entry is not None
    rel = entry.get("rubric_output_map_path")
    assert isinstance(rel, str) and rel
    assert (REPO_ROOT / rel).exists(), f"rubric output map missing: {rel}"


def test_load_cert_route_entry_missing_file_returns_none() -> None:
    from apps_exec.__main__ import _load_cert_route_entry

    assert _load_cert_route_entry(REPO_ROOT / "nonexistent.yaml") is None


def test_build_exit_receipts_populates_fec() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer
    from apps_exec.cert.fec_producer import produce_fec
    from apps_exec.__main__ import _build_exit_receipts

    clear_registry()
    register_producer("apps_exec", produce_fec)

    from apps_shared.cert.fec_producer import resolve_fec

    fec = resolve_fec(
        "apps_exec",
        {"route_id": "apps_exec.execution_v1", "template_ids": ["exec_brief_v1"]},
    )
    receipts = _build_exit_receipts({"route_id": "apps_exec.execution_v1"}, fec)
    assert receipts["final_evidence_contract"]["producer"] == "apps_exec.cert.fec_producer"
    assert receipts["route_contract"] == {"route_id": "apps_exec.execution_v1"}
    assert "output" in receipts


def test_build_exit_receipts_handles_none_fec() -> None:
    from apps_exec.__main__ import _build_exit_receipts

    receipts = _build_exit_receipts({}, None)
    assert receipts["final_evidence_contract"] == {}


def test_maybe_run_exit_hook_fail_soft_no_registry(monkeypatch, tmp_path) -> None:
    """If the registry path resolves to nothing, hook is a no-op (no raise)."""
    from apps_exec.__main__ import _maybe_run_exit_hook

    # Should never raise regardless of input shape
    _maybe_run_exit_hook({})
    _maybe_run_exit_hook(None)


@pytest.fixture(autouse=True)
def _restore_registry():
    from apps_shared.cert.fec_producer import clear_registry

    yield
    clear_registry()
