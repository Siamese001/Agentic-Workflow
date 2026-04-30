"""W3 boundary leak contract tests for apps_shared.adapters facades.

Locks in the W3 invariants:
1. ``apps_shared.adapters.system_learning_facade`` exports the 6 system_learning
   symbols apps may consume.
2. ``apps_shared.adapters.rg_orchestrator_facade`` exports ``RgResumeOrchestrator``.
3. Both facades use PEP 562 ``__getattr__`` lazy resolution \u2014 module-level
   import does NOT eagerly pull in the upstream peer.
4. NO file under ``apps_eval/`` or ``apps_lic/`` imports directly from
   ``system_learning`` or ``apps_rg`` \u2014 all cross-tree imports MUST go
   through the apps_shared facades.

This is the regression suite for ADG hotspots G5, G6, G7 (see plan
``apps-runtime-first-principles-e6ba58``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]


# ---------------------------------------------------------------------------
# Facade export contract
# ---------------------------------------------------------------------------


def test_system_learning_facade_exports_expected_symbols() -> None:
    """W3.2/W3.3: system_learning_facade must re-export the 6 documented symbols."""
    from apps_shared.adapters import system_learning_facade

    expected = {
        "get_sl_memory_bridge",
        "get_process_bus",
        "MetaLearningChangePackage",
        "MetaLearningBus",
        "get_current_adapter",
        "seal_step",
    }
    assert expected.issubset(set(system_learning_facade.__all__))
    # Each symbol must resolve via the lazy __getattr__ path.
    for name in expected:
        assert hasattr(system_learning_facade, name), f"{name} not resolvable"


def test_rg_orchestrator_facade_exports_expected_symbol() -> None:
    """W3.1: rg_orchestrator_facade must re-export RgResumeOrchestrator."""
    from apps_shared.adapters import rg_orchestrator_facade

    assert "RgResumeOrchestrator" in rg_orchestrator_facade.__all__
    assert hasattr(rg_orchestrator_facade, "RgResumeOrchestrator")


def test_system_learning_facade_unknown_attr_raises_attribute_error() -> None:
    """W3.2/W3.3: facade must raise AttributeError (not ImportError) for unknown names."""
    from apps_shared.adapters import system_learning_facade

    with pytest.raises(AttributeError):
        _ = system_learning_facade.does_not_exist  # type: ignore[attr-defined]


def test_rg_orchestrator_facade_unknown_attr_raises_attribute_error() -> None:
    """W3.1: facade must raise AttributeError (not ImportError) for unknown names."""
    from apps_shared.adapters import rg_orchestrator_facade

    with pytest.raises(AttributeError):
        _ = rg_orchestrator_facade.does_not_exist  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Lazy-resolution contract \u2014 module load must NOT eagerly import upstream
# ---------------------------------------------------------------------------


def test_system_learning_facade_uses_pep562_getattr() -> None:
    """W3.2/W3.3: facade must use PEP 562 ``__getattr__`` rather than top-level imports."""
    from apps_shared.adapters import system_learning_facade

    # PEP 562 contract: module defines __getattr__ at module scope.
    assert hasattr(system_learning_facade, "__getattr__")
    # The lazy-symbols mapping is the SSOT for re-exports.
    assert hasattr(system_learning_facade, "_LAZY_SYMBOLS")
    assert isinstance(system_learning_facade._LAZY_SYMBOLS, dict)


def test_rg_orchestrator_facade_uses_pep562_getattr() -> None:
    """W3.1: facade must use PEP 562 ``__getattr__`` rather than top-level imports."""
    from apps_shared.adapters import rg_orchestrator_facade

    assert hasattr(rg_orchestrator_facade, "__getattr__")
    assert hasattr(rg_orchestrator_facade, "_LAZY_SYMBOLS")


def test_system_learning_facade_module_source_has_no_top_level_upstream_import() -> None:
    """W3.2/W3.3: facade source must not eagerly import system_learning at module top.

    Source-level scan because once a lazy symbol is resolved it caches into
    globals(); a runtime check would falsely detect the cached entry.
    """
    facade_path = REPO_ROOT / "apps_shared" / "adapters" / "system_learning_facade.py"
    src = facade_path.read_text(encoding="utf-8")
    # Top-level imports start at column 0 (no leading whitespace). Any
    # ``from system_learning`` at column 0 violates the lazy contract.
    for line in src.splitlines():
        if line.startswith("from system_learning") or line.startswith("import system_learning"):
            pytest.fail(f"Top-level system_learning import in facade: {line!r}")


def test_rg_orchestrator_facade_module_source_has_no_top_level_upstream_import() -> None:
    """W3.1: facade source must not eagerly import apps_rg at module top."""
    facade_path = REPO_ROOT / "apps_shared" / "adapters" / "rg_orchestrator_facade.py"
    src = facade_path.read_text(encoding="utf-8")
    for line in src.splitlines():
        if line.startswith("from apps_rg") or line.startswith("import apps_rg"):
            pytest.fail(f"Top-level apps_rg import in facade: {line!r}")


# ---------------------------------------------------------------------------
# Boundary-leak invariant \u2014 NO direct cross-tree imports outside the facades
# ---------------------------------------------------------------------------


_DIRECT_SYSTEM_LEARNING_IMPORT = re.compile(
    r"^\s*(?:from\s+system_learning(?:\.|\s+import)|import\s+system_learning)",
    re.MULTILINE,
)
_DIRECT_APPS_RG_IMPORT = re.compile(
    r"^\s*(?:from\s+apps_rg(?:\.|\s+import)|import\s+apps_rg)",
    re.MULTILINE,
)


def _scan_tree_for_direct_imports(app_root: Path, pattern: re.Pattern[str]) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    for py in app_root.rglob("*.py"):
        # Ignore __pycache__ and our own facade tests.
        if "__pycache__" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in pattern.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            hits.append((py.relative_to(REPO_ROOT), line_no, m.group(0).strip()))
    return hits


def test_apps_eval_has_no_direct_system_learning_imports() -> None:
    """W3.2: apps_eval/ must route all system_learning access through the facade."""
    hits = _scan_tree_for_direct_imports(
        REPO_ROOT / "apps_eval", _DIRECT_SYSTEM_LEARNING_IMPORT
    )
    assert not hits, (
        f"Direct system_learning imports in apps_eval (must use "
        f"apps_shared.adapters.system_learning_facade):\n"
        + "\n".join(f"  {p}:{ln}  {snippet}" for p, ln, snippet in hits)
    )


def test_apps_eval_has_no_direct_apps_rg_imports() -> None:
    """W3.1: apps_eval/ must route apps_rg access through the facade."""
    hits = _scan_tree_for_direct_imports(REPO_ROOT / "apps_eval", _DIRECT_APPS_RG_IMPORT)
    assert not hits, (
        f"Direct apps_rg imports in apps_eval (must use "
        f"apps_shared.adapters.rg_orchestrator_facade):\n"
        + "\n".join(f"  {p}:{ln}  {snippet}" for p, ln, snippet in hits)
    )


def test_apps_lic_has_no_direct_system_learning_imports() -> None:
    """W3.3: apps_lic/ must route all system_learning access through the facade."""
    hits = _scan_tree_for_direct_imports(
        REPO_ROOT / "apps_lic", _DIRECT_SYSTEM_LEARNING_IMPORT
    )
    assert not hits, (
        f"Direct system_learning imports in apps_lic (must use "
        f"apps_shared.adapters.system_learning_facade):\n"
        + "\n".join(f"  {p}:{ln}  {snippet}" for p, ln, snippet in hits)
    )


# ---------------------------------------------------------------------------
# Sanity \u2014 the touched source files still parse and resolve
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "apps_eval.engines.scenario_runner",
        "apps_eval.engines.regression_detector",
        "apps_eval.integrations.meta_bus_publisher",
        "apps_lic.engines.control_plane",
        pytest.param(
            "apps_lic.engines.lic_spine_adapter",
            marks=pytest.mark.xfail(
                reason=(
                    "Pre-existing broken import at line 115: "
                    "'from apps_shared.spine.base_spine_adapter import BaseSpineAdapter' "
                    "references a module that does not exist anywhere in the tree. "
                    "Unrelated to W3 (W3 edit is at line 20). Tracked separately."
                ),
                strict=True,
                raises=ModuleNotFoundError,
            ),
        ),
        "apps_lic.reasoning.HOPPipelineExecutor",
    ],
)
def test_touched_modules_still_importable(module_path: str) -> None:
    """W3 sanity: every file we modified must still be importable.

    The lic_spine_adapter case is marked xfail(strict=True) because the file
    has a separate pre-existing broken import at line 115 unrelated to W3.
    Once that pre-existing issue is fixed, the xfail will turn into XPASSED
    and pytest will fail \u2014 forcing the marker to be removed (intentional).
    """
    import importlib

    importlib.import_module(module_path)
