"""W10 — R1B UWG durable persistence contract."""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w10_fixtures"


@pytest.fixture(scope="module", autouse=True)
def _ensure_w10_fixtures() -> None:
    if not (FIXTURES / "uwg_admitted_promotion.json").is_file():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "emit_r1b_w10_fixtures.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def test_post_exit_ingest_wires_uwg_promotion() -> None:
    mod = importlib.import_module("apps_rg.cache.r1b_post_exit_ingest")
    src = inspect.getsource(mod.ingest_post_exit_from_run_dir)
    assert "promote_and_project_r1b_cache" in src


def test_cache_profile_uwg_block() -> None:
    import yaml

    path = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    block = doc.get("r1b_uwg_durable_promotion") or {}
    assert block.get("target_surface") == "l4.apps_rg.r1b_semantic_cache"
    assert block.get("l2_direct_write") == "forbidden"


def test_w10_fixtures_present() -> None:
    for name in (
        "uwg_admitted_promotion",
        "blocked_promotion",
        "l2_direct_write_blocked",
        "l6_direct_write_blocked",
        "file_backed_non_durable_manifest",
    ):
        assert (FIXTURES / f"{name}.json").is_file(), name


def test_admitted_fixture_has_uwg_receipt() -> None:
    payload = json.loads((FIXTURES / "uwg_admitted_promotion.json").read_text(encoding="utf-8"))
    assert payload["promotion_outcome"]["status"] == "ADMITTED"
    assert payload["promotion_outcome"]["uwg_commit_receipt_id"]


def test_file_backed_non_durable_fixture() -> None:
    payload = json.loads(
        (FIXTURES / "file_backed_non_durable_manifest.json").read_text(encoding="utf-8")
    )
    assert payload["is_durable_production_truth"] is False
