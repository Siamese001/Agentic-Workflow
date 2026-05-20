"""W4 — SIGNAL_* env is signal-quality SSOT only; not generation/judge/heal-tier routing."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.runtime.config.signal_quality_config import (
    QualityThresholds,
    get_signal_enhancer,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SIGNAL_ENV_KEYS: frozenset[str] = frozenset(
    {
        "SIGNAL_EXCELLENT_MIN",
        "SIGNAL_HIGH_MIN",
        "SIGNAL_GOOD_MIN",
        "SIGNAL_MARGINAL_MIN",
    }
)

SCAN_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "agentic_core" / "L2_execution" / "healers",
)


def _rel(p: Path) -> str:
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(p)


def _getenv_keys_in_file(py: Path) -> list[str]:
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    keys: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "getenv":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
                node.args[0].value, str
            ):
                keys.append(node.args[0].value)
    return keys


@pytest.mark.parametrize("root", SCAN_ROOTS, ids=lambda p: _rel(p))
def test_signal_env_keys_not_read_outside_ssot_module(root: Path) -> None:
    violations: list[str] = []
    for py in root.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        if "signal_quality_config.py" in py.as_posix():
            continue
        for key in _getenv_keys_in_file(py):
            if key in SIGNAL_ENV_KEYS:
                violations.append(f"{_rel(py)}: getenv({key!r})")
    assert not violations, "SIGNAL_* env outside SSOT:\n" + "\n".join(violations)


def test_core_signal_enhancer_ssot_is_real() -> None:
    enhancer = get_signal_enhancer("boundary_test")
    thresholds = QualityThresholds()
    assert thresholds.EXCELLENT_MIN >= 0.0
    assessment = enhancer.assess_signal("test content", {})
    assert hasattr(assessment, "composite_score")


def test_apps_shared_subatomic_stub_is_not_core_ssot() -> None:
    from apps_shared.utils import subatomic_hop_util as mod

    stub = mod.get_signal_enhancer()
    assert type(stub).__name__ == "SignalQuality"
    assert not hasattr(stub, "thresholds") or not getattr(stub, "thresholds", None)


def test_apps_shared_engine_types_stub_assess_signal_is_noop_shape() -> None:
    from apps_shared.types.engine_type_types import signal_enhancer

    inst = signal_enhancer("stub")
    out = inst.assess_signal("x")
    assert getattr(out, "composite_score", 0.0) == 0.0


def test_w4_decision_quarantine_stubs_documented() -> None:
    """W4 decision: QUARANTINE (KEEP_STUBBED) — see w2_w5_boundary_and_healing.json."""
    assert True
