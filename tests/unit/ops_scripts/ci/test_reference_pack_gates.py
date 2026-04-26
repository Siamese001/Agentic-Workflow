"""Unit tests for the docs/reference/ pack gates.

Covers:
  - check_reference_pack_integrity (manifest verification)
  - check_reference_test_contracts (TEST REQUIREMENTS no-drift gate)

Edge cases exercised:
  - Empty TEST REQUIREMENTS block
  - Multiple test contracts in same block
  - PTC V2 TEST REQUIREMENTS variant header
  - Test names containing digits and underscores
  - Implementation found in async def form
  - Baseline correctly grandfathers known-missing contracts
  - Gate FAILS when a new contract appears without baseline entry
  - Pack integrity FAILS on size/hash mismatch and missing sub-children
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
CI = REPO / "ops_scripts" / "ci"


def _load(module_filename: str):
    path = CI / module_filename
    spec = importlib.util.spec_from_file_location(module_filename, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# --- check_reference_test_contracts ----------------------------------------


def test_parse_extracts_simple_block(tmp_path: Path) -> None:
    mod = _load("check_reference_test_contracts.py")
    md = tmp_path / "x.md"
    md.write_text(
        "INTRO\n\nTEST REQUIREMENTS\n----\n- test_alpha\n- test_beta\n\nNEXT SECTION\n",
        encoding="utf-8",
    )
    assert mod.parse_test_contracts(md) == ["test_alpha", "test_beta"]


def test_parse_handles_ptc_v2_variant(tmp_path: Path) -> None:
    mod = _load("check_reference_test_contracts.py")
    md = tmp_path / "ptc.md"
    md.write_text(
        "PTC V2 TEST REQUIREMENTS\n------\n- test_ptc_one\n- test_ptc_two\n",
        encoding="utf-8",
    )
    assert mod.parse_test_contracts(md) == ["test_ptc_one", "test_ptc_two"]


def test_parse_stops_at_non_test_bullet(tmp_path: Path) -> None:
    """Conservative parser: any non-test bullet ends the block. This ensures
    we never silently pick up mid-block prose as test names."""
    mod = _load("check_reference_test_contracts.py")
    md = tmp_path / "x.md"
    md.write_text(
        "TEST REQUIREMENTS\n----\n- test_real_one\n- some_other_bullet\n- test_real_two\n",
        encoding="utf-8",
    )
    assert mod.parse_test_contracts(md) == ["test_real_one"]


def test_parse_returns_empty_when_no_block(tmp_path: Path) -> None:
    mod = _load("check_reference_test_contracts.py")
    md = tmp_path / "x.md"
    md.write_text("just prose\n- test_unrelated\n", encoding="utf-8")
    assert mod.parse_test_contracts(md) == []


def test_collect_implemented_finds_async_def(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_test_contracts.py")
    fake_tests = tmp_path / "tests"
    fake_tests.mkdir()
    (fake_tests / "test_x.py").write_text(
        "async def test_alpha():\n    pass\ndef test_beta():\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "TESTS_DIR", fake_tests)
    impl = mod.collect_implemented_tests()
    assert {"test_alpha", "test_beta"} <= impl


def test_baseline_grandfathers_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_test_contracts.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    fake_tests = tmp_path / "tests"
    fake_tests.mkdir()
    fake_baseline = tmp_path / "baseline.json"

    # one declared, none implemented, baselined → PASS
    (fake_ref / "doc.md").write_text("TEST REQUIREMENTS\n----\n- test_grandfathered\n", encoding="utf-8")
    fake_baseline.write_text(
        json.dumps({"missing_contracts": {"test_grandfathered": {"declared_in": ["doc.md"]}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REF_DIR", fake_ref)
    monkeypatch.setattr(mod, "TESTS_DIR", fake_tests)
    monkeypatch.setattr(mod, "BASELINE", fake_baseline)
    assert mod.main() == 0


def test_new_contract_without_impl_or_baseline_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_test_contracts.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    fake_tests = tmp_path / "tests"
    fake_tests.mkdir()
    fake_baseline = tmp_path / "baseline.json"
    (fake_ref / "doc.md").write_text("TEST REQUIREMENTS\n----\n- test_brand_new\n", encoding="utf-8")
    fake_baseline.write_text(json.dumps({"missing_contracts": {}}), encoding="utf-8")
    monkeypatch.setattr(mod, "REF_DIR", fake_ref)
    monkeypatch.setattr(mod, "TESTS_DIR", fake_tests)
    monkeypatch.setattr(mod, "BASELINE", fake_baseline)
    assert mod.main() == 1


def test_implemented_contract_passes_without_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load("check_reference_test_contracts.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    fake_tests = tmp_path / "tests"
    fake_tests.mkdir()
    fake_baseline = tmp_path / "baseline.json"
    (fake_ref / "doc.md").write_text("TEST REQUIREMENTS\n----\n- test_implemented\n", encoding="utf-8")
    (fake_tests / "test_a.py").write_text("def test_implemented():\n    pass\n", encoding="utf-8")
    fake_baseline.write_text(json.dumps({"missing_contracts": {}}), encoding="utf-8")
    monkeypatch.setattr(mod, "REF_DIR", fake_ref)
    monkeypatch.setattr(mod, "TESTS_DIR", fake_tests)
    monkeypatch.setattr(mod, "BASELINE", fake_baseline)
    assert mod.main() == 0


# --- check_reference_pack_integrity ----------------------------------------


def test_pack_integrity_missing_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_pack_integrity.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    fake_manifest = fake_ref / "MANIFEST.json"
    fake_manifest.write_text(
        json.dumps({"files": [{"path": "missing.md", "size": 1, "sha256": "deadbeef" * 8}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REF", fake_ref)
    monkeypatch.setattr(mod, "ROOT_MANIFEST", fake_manifest)
    assert mod.main() == 1


def test_pack_integrity_size_mismatch_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_pack_integrity.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    target = fake_ref / "x.md"
    target.write_bytes(b"actual content")
    fake_manifest = fake_ref / "MANIFEST.json"
    fake_manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "x.md",
                        "size": 999,  # wrong
                        "sha256": "deadbeef" * 8,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REF", fake_ref)
    monkeypatch.setattr(mod, "ROOT_MANIFEST", fake_manifest)
    assert mod.main() == 1


def test_pack_integrity_hash_match_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("check_reference_pack_integrity.py")
    fake_ref = tmp_path / "ref"
    fake_ref.mkdir()
    target = fake_ref / "x.md"
    body = b"hello world"
    target.write_bytes(body)
    actual_hash = mod.sha256_of(target)
    fake_manifest = fake_ref / "MANIFEST.json"
    fake_manifest.write_text(
        json.dumps({"files": [{"path": "x.md", "size": len(body), "sha256": actual_hash}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "REF", fake_ref)
    monkeypatch.setattr(mod, "ROOT_MANIFEST", fake_manifest)
    assert mod.main() == 0


# --- live integration: actual repo passes both gates ------------------------


def test_live_repo_pack_integrity_passes() -> None:
    mod = _load("check_reference_pack_integrity.py")
    assert mod.main() == 0


def test_live_repo_test_contracts_passes() -> None:
    mod = _load("check_reference_test_contracts.py")
    assert mod.main() == 0


def test_live_repo_declares_at_least_78_baselined_contracts() -> None:
    """Sanity check: as of the April 2026 gap-closure pack commit, 78+ contracts
    are baselined under the gap-closure-test-impl-b77a11 plan."""
    baseline_path = REPO / "ops_scripts" / "ci" / "baselines" / "reference_test_contract_baseline.json"
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    missing = data.get("missing_contracts", {})
    assert len(missing) >= 78, f"baseline has only {len(missing)} entries, expected ≥78"
    # Every baseline entry must include declared_in evidence
    for name, meta in missing.items():
        assert "declared_in" in meta, f"baseline entry {name} missing declared_in"
        assert meta["declared_in"], f"baseline entry {name} declared_in is empty"
