"""Tests for ops_scripts/ci/check_dead_methods_ratchet.py (W5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ops_scripts.ci import check_dead_methods_ratchet as mod


# ---- AST method collection ----------------------------------------------


def _write_py(tmp_path: Path, rel: str, src: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src, encoding="utf-8")
    return p


def test_collect_class_methods_basic(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
class Foo:
    def alpha(self): ...
    def beta(self): ...
    def _private(self): ...
""",
    )
    out = mod.collect_class_methods(f)
    names = [m for _, m, _ in out]
    assert "alpha" in names
    assert "beta" in names
    assert "_private" not in names


def test_collect_skips_abstractmethod(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
from abc import abstractmethod
class Foo:
    @abstractmethod
    def pure(self): ...
    def concrete(self): ...
""",
    )
    names = [m for _, m, _ in mod.collect_class_methods(f)]
    assert "concrete" in names
    assert "pure" not in names


def test_collect_skips_property_and_fixture(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
class Foo:
    @property
    def name(self): ...
    @fixture
    def thing(self): ...
    def real(self): ...
""",
    )
    names = [m for _, m, _ in mod.collect_class_methods(f)]
    assert "real" in names
    assert "name" not in names
    assert "thing" not in names


def test_collect_skips_framework_methods(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
class Foo:
    def setUp(self): ...
    def model_post_init(self, _): ...
    def custom(self): ...
""",
    )
    names = [m for _, m, _ in mod.collect_class_methods(f)]
    assert "custom" in names
    assert "setUp" not in names
    assert "model_post_init" not in names


def test_collect_ignores_nested_classes(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
def outer():
    class Nested:
        def nm(self): ...
    return Nested

class Top:
    def t(self): ...
""",
    )
    names = [c + "." + m for c, m, _ in mod.collect_class_methods(f)]
    assert "Top.t" in names
    # Nested class inside function not top-level -> skipped
    assert not any("Nested" in n for n in names)


def test_collect_bad_syntax_returns_empty(tmp_path: Path) -> None:
    f = _write_py(tmp_path, "m.py", "def : bad ! syntax")
    assert mod.collect_class_methods(f) == []


# ---- decorator filter ---------------------------------------------------


def test_is_skipped_decorator_detects_calls(tmp_path: Path) -> None:
    f = _write_py(
        tmp_path,
        "m.py",
        """
class Foo:
    @pytest_fixture(scope="module")
    def fx(self): ...
    def real(self): ...
""",
    )
    names = [m for _, m, _ in mod.collect_class_methods(f)]
    assert "real" in names
    assert "fx" not in names


# ---- name index ---------------------------------------------------------


def test_name_index_captures_attr_calls(tmp_path: Path) -> None:
    _write_py(tmp_path, "caller.py", "x.alpha()\ny.beta('arg')\nz['gamma']\n\"delta\" in spec")
    got = mod.build_method_name_index([tmp_path / "caller.py"])
    assert "alpha" in got
    assert "beta" in got
    assert "gamma" in got
    assert "delta" in got


def test_name_index_handles_unreadable(tmp_path: Path) -> None:
    # Non-existent path -> no crash, just empty
    got = mod.build_method_name_index([tmp_path / "missing.py"])
    assert got == set()


# ---- anchor loading ----------------------------------------------------


def test_load_dynamic_anchor_patterns_absent(tmp_path: Path) -> None:
    assert mod.load_dynamic_anchor_patterns(tmp_path / "nope.yaml") == []


def test_load_dynamic_anchor_patterns_parses(tmp_path: Path) -> None:
    p = tmp_path / "anchors.yaml"
    p.write_text(
        "anchors:\n  - pattern: 'tools/debug/*.py'\n    reason: x\n",
        encoding="utf-8",
    )
    assert mod.load_dynamic_anchor_patterns(p) == ["tools/debug/*.py"]


# ---- smoke test on the real repo ---------------------------------------


@pytest.mark.slow
def test_gate_runs_on_real_snapshot() -> None:
    """Smoke: gate executes on the latest ADG without crashing."""
    from ops_scripts.ci._adg_wiring_gate_base import (
        connect_snapshot,
        latest_snapshot,
    )

    conn = connect_snapshot(latest_snapshot())
    try:
        violations = mod.DeadMethodsRatchetGate().run(conn)
    finally:
        conn.close()
    # Just validate return type; actual count is tracked by baseline.
    assert isinstance(violations, list)
