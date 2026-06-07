"""W9b — whole-run entrypoint parity contract."""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w9b_fixtures"


@pytest.fixture(scope="module", autouse=True)
def _ensure_w9b_fixtures() -> None:
    if not (FIXTURES / "production_entrypoint_accepted_hit.json").is_file():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "emit_r1b_w9b_fixtures.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def test_canonical_dispatch_wires_whole_run_preflight() -> None:
    mod = importlib.import_module("apps_rg.runtime.orchestration.canonical_dispatch")
    src = inspect.getsource(mod.run_canonical_full_resume_from_cli_primitives)
    assert "run_whole_run_cache_preflight" in src
    assert "build_cache_hit_dispatch_result" in src
    assert "run_integrated_single_action_spine" in src


def test_dispatch_apps_rg_run_delegates_to_canonical() -> None:
    mod = importlib.import_module("agentic_core.runtime.entry.apps_rg_dispatch")
    src = inspect.getsource(mod.dispatch_apps_rg_run)
    assert "run_canonical_apps_rg_from_cli_primitives" in src


def test_w9b_fixtures_present() -> None:
    for name in (
        "production_entrypoint_accepted_hit",
        "production_entrypoint_miss_fallthrough",
        "production_entrypoint_rejected_candidate",
        "entrypoint_audit_matrix",
    ):
        assert (FIXTURES / f"{name}.json").is_file(), name


def test_production_accepted_hit_fixture() -> None:
    payload = json.loads(
        (FIXTURES / "production_entrypoint_accepted_hit.json").read_text(encoding="utf-8")
    )
    assert payload["preflight"]["r1b_hit"] is True
    assert payload["dispatch_result"]["generation_skipped"] is True
    assert payload["dispatch_result"]["exit_bypassed"] is False


def test_production_miss_fixture() -> None:
    payload = json.loads(
        (FIXTURES / "production_entrypoint_miss_fallthrough.json").read_text(encoding="utf-8")
    )
    assert payload["r1b_hit"] is False
    assert payload["generation_required"] is True


def test_audit_matrix_fixture() -> None:
    matrix = json.loads((FIXTURES / "entrypoint_audit_matrix.json").read_text(encoding="utf-8"))
    wired = [r for r in matrix if r.get("status") == "wired_w9b"]
    assert len(wired) >= 2
