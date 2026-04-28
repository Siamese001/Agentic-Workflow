"""Tests for the requirements ↔ ADG ↔ test crosswalk gate (W4)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.crosswalk.build_requirements_crosswalk import (  # noqa: E402
    build_crosswalk,
    load_registry,
    resolve,
)


class TestResolve:
    def test_fully_resolved_obligation(self, tmp_path: Path) -> None:
        gate = tmp_path / "ops_scripts" / "ci" / "gate.py"
        gate.parent.mkdir(parents=True)
        gate.write_text("# gate", encoding="utf-8")
        test = tmp_path / "tests" / "test_x.py"
        test.parent.mkdir(parents=True)
        test.write_text("# test", encoding="utf-8")

        r = resolve(
            {
                "id": "ob_a",
                "source": "src",
                "description": "d",
                "gate_script": "ops_scripts/ci/gate.py",
                "test_ids": ["tests/test_x.py::TestY::test_z"],
            },
            repo_root=tmp_path,
        )
        assert r.fully_resolved
        assert r.gate_script_resolved
        assert r.unresolved_test_ids == []

    def test_missing_gate_script_unresolved(self, tmp_path: Path) -> None:
        r = resolve(
            {"id": "ob_x", "gate_script": "nope.py", "test_ids": []},
            repo_root=tmp_path,
        )
        assert not r.gate_script_resolved
        assert not r.fully_resolved

    def test_missing_test_file_unresolved(self, tmp_path: Path) -> None:
        gate = tmp_path / "g.py"
        gate.write_text("", encoding="utf-8")
        r = resolve(
            {
                "id": "ob_y",
                "gate_script": "g.py",
                "test_ids": ["tests/missing.py::test_x"],
            },
            repo_root=tmp_path,
        )
        assert r.gate_script_resolved
        assert r.unresolved_test_ids == ["tests/missing.py::test_x"]
        assert not r.fully_resolved


class TestLoadRegistry:
    def test_missing_registry_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_registry(tmp_path / "nope.yaml")

    def test_non_mapping_top_level_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("- just: a list", encoding="utf-8")
        with pytest.raises(ValueError, match="must be a mapping"):
            load_registry(bad)

    def test_obligations_not_list_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("obligations: not-a-list", encoding="utf-8")
        with pytest.raises(ValueError, match="must be a list"):
            load_registry(bad)


class TestBuildCrosswalkAgainstLiveRegistry:
    def test_live_registry_fully_resolved(self) -> None:
        """The shipped obligations.yaml MUST resolve cleanly."""
        crosswalk = build_crosswalk()
        assert crosswalk["unresolved_count"] == 0, (
            f"unresolved obligations: "
            f"{[o for o in crosswalk['obligations'] if not o['gate_script_resolved'] or o['unresolved_test_ids']]}"
        )

    def test_live_registry_no_duplicate_ids(self) -> None:
        crosswalk = build_crosswalk()
        assert crosswalk["ids_with_duplicates"] == []

    def test_minimum_obligation_count(self) -> None:
        """Plan W4 implies a non-trivial obligation set; assert ≥5."""
        crosswalk = build_crosswalk()
        assert crosswalk["total_obligations"] >= 5
