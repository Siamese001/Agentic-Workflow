"""Unit tests for ``ops_scripts/ci/check_dangling_imports.py``.

The gate detects three classes of broken imports:
1. ``from <pkg>.<mod> import <name>`` whose target module does not exist
2. ``import <pkg>.<mod>`` whose target module does not exist
3. ``importlib.import_module("<literal>")`` whose literal arg does not exist

Tests build a tiny synthetic repo on disk, run the gate against it, and assert
on the violation list.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci import check_dangling_imports as gate  # noqa: E402


@pytest.fixture
def synthetic_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build a minimal synthetic repo with one valid package + a few imports."""
    # Use the FIRST production package root so the gate's prefix check accepts it.
    pkg_root = tmp_path / "agentic_core"
    pkg_root.mkdir()
    (pkg_root / "__init__.py").write_text("", encoding="utf-8")

    sub = pkg_root / "subpkg"
    sub.mkdir()
    (sub / "__init__.py").write_text("", encoding="utf-8")
    (sub / "real_module.py").write_text("REAL = 1\n", encoding="utf-8")

    # Patch the gate's REPO_ROOT and SCAN_ROOTS so it scans tmp_path.
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gate, "LOG_DIR", tmp_path / "log")
    monkeypatch.setattr(gate, "LOG_FILE", tmp_path / "log" / "violations.jsonl")
    return tmp_path


def _write(repo: Path, rel: str, body: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body), encoding="utf-8")


class TestModuleResolver:
    def test_resolver_indexes_real_modules(self, synthetic_repo: Path) -> None:
        resolvable = gate.build_module_resolver(synthetic_repo)
        assert "agentic_core" in resolvable
        assert "agentic_core.subpkg" in resolvable
        assert "agentic_core.subpkg.real_module" in resolvable

    def test_resolver_omits_nonexistent(self, synthetic_repo: Path) -> None:
        resolvable = gate.build_module_resolver(synthetic_repo)
        assert "agentic_core.nonexistent" not in resolvable
        assert "agentic_core.subpkg.bogus" not in resolvable


class TestIsInternalModule:
    def test_production_root_match(self) -> None:
        assert gate.is_internal_module("agentic_core")
        assert gate.is_internal_module("agentic_core.L0_routing.config")
        assert gate.is_internal_module("apps_eval.engines.x")

    def test_external_passthrough(self) -> None:
        assert not gate.is_internal_module("os")
        assert not gate.is_internal_module("pathlib")
        assert not gate.is_internal_module("numpy.linalg")
        assert not gate.is_internal_module("requests")


class TestFromImportDetection:
    def test_clean_repo_passes(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/consumer.py",
            """
            from agentic_core.subpkg.real_module import REAL
            x = REAL + 1
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.violations == []

    def test_typo_in_module_path_caught(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/consumer.py",
            """
            from agentic_core.subpkg.bogus_module import REAL
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert len(outcome.violations) == 1
        v = outcome.violations[0]
        assert v.kind == "from_import"
        assert v.target_module == "agentic_core.subpkg.bogus_module"
        assert v.line_no == 2

    def test_external_libraries_not_flagged(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/consumer.py",
            """
            from os.path import join
            from json import loads
            from requests.adapters import HTTPAdapter
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.violations == []


class TestImportDetection:
    def test_typo_in_import_caught(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/consumer.py",
            """
            import agentic_core.subpkg.real_module
            import agentic_core.subpkg.fictional
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        kinds = {(v.target_module, v.kind) for v in outcome.violations}
        assert ("agentic_core.subpkg.fictional", "import") in kinds
        assert ("agentic_core.subpkg.real_module", "import") not in kinds


class TestDynamicImportDetection:
    def test_importlib_literal_caught(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/dynamic_consumer.py",
            """
            import importlib

            def lazy():
                return importlib.import_module("agentic_core.nope.not_here")
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert len(outcome.violations) == 1
        v = outcome.violations[0]
        assert v.kind == "dynamic_import"
        assert v.target_module == "agentic_core.nope.not_here"

    def test_importlib_literal_resolves_passes(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/dynamic_consumer.py",
            """
            import importlib

            def lazy():
                return importlib.import_module("agentic_core.subpkg.real_module")
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.violations == []

    def test_importlib_with_variable_arg_skipped(self, synthetic_repo: Path) -> None:
        # Non-literal args are out of scope (cannot statically validate).
        _write(
            synthetic_repo,
            "agentic_core/dynamic_consumer.py",
            """
            import importlib

            def lazy(name):
                return importlib.import_module(name)
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.violations == []

    def test_dunder_import_literal_caught(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/dynamic_consumer.py",
            """
            def lazy():
                return __import__("agentic_core.bogus")
            """,
        )
        outcome = gate.run_gate(synthetic_repo)
        assert len(outcome.violations) == 1
        assert outcome.violations[0].kind == "dynamic_import"


class TestRegressionCase:
    """The exact pre-existing bug found in the 2026-04-28 RCA: a module-load
    line that imports a typo'd kernel path."""

    def test_seam_path_typo_caught(self, synthetic_repo: Path) -> None:
        # Simulate the actual pre-fix bug: kernel lives at
        # agentic_core.L5_safety.reasoning.core_kernel.classification_kernel
        # but the seam imports the wrong path.
        kernel_dir = synthetic_repo / "agentic_core" / "L5_safety" / "reasoning" / "core_kernel"
        kernel_dir.mkdir(parents=True)
        (kernel_dir / "__init__.py").write_text("", encoding="utf-8")
        (kernel_dir / "classification_kernel.py").write_text("FOO = 1\n", encoding="utf-8")
        # Also create the L5_safety/reasoning intermediate __init__.py
        (synthetic_repo / "agentic_core" / "L5_safety").mkdir(exist_ok=True)
        (synthetic_repo / "agentic_core" / "L5_safety" / "__init__.py").write_text("", encoding="utf-8")
        (synthetic_repo / "agentic_core" / "L5_safety" / "reasoning").mkdir(exist_ok=True)
        (synthetic_repo / "agentic_core" / "L5_safety" / "reasoning" / "__init__.py").write_text(
            "", encoding="utf-8"
        )

        # Now write the buggy seam: imports the WRONG path.
        _write(
            synthetic_repo,
            "agentic_core/L0_routing/enforcement/safety_kernel_seam.py",
            """
            import importlib

            def load():
                return importlib.import_module(
                    "agentic_core.L5_safety.core_kernel.classification_kernel"
                )
            """,
        )
        # Make sure parent dirs are valid packages.
        (synthetic_repo / "agentic_core" / "L0_routing").mkdir(exist_ok=True)
        (synthetic_repo / "agentic_core" / "L0_routing" / "__init__.py").write_text("", encoding="utf-8")
        (synthetic_repo / "agentic_core" / "L0_routing" / "enforcement").mkdir(exist_ok=True)
        (synthetic_repo / "agentic_core" / "L0_routing" / "enforcement" / "__init__.py").write_text(
            "", encoding="utf-8"
        )

        outcome = gate.run_gate(synthetic_repo)
        targets = {v.target_module for v in outcome.violations}
        assert "agentic_core.L5_safety.core_kernel.classification_kernel" in targets


class TestBypass:
    def test_env_bypass_short_circuits(self, synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write(
            synthetic_repo,
            "agentic_core/consumer.py",
            "from agentic_core.totally_fake import X\n",
        )
        monkeypatch.setenv("DANGLING_IMPORT_BYPASS", "1")
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.bypassed is True
        assert outcome.violations == []
