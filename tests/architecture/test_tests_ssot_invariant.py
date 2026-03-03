"""
Invariant: every folder under tests/ must be declared in the SSOT territory.
Guards against healing-pipeline drift that creates undeclared test subfolders.

AST-based where possible; filesystem scan for the subfolder audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_blueprint_test_subfolders() -> set[str]:
    """Read declared test subfolders directly from SOVEREIGN_TERRITORIES via import."""
    from agentic_core.L5_safety.config.structure_blueprint.territories import (
        SOVEREIGN_TERRITORIES,
    )

    raw = SOVEREIGN_TERRITORIES.get("tests", {}).get("subfolders", {})
    return set(raw.keys()) if hasattr(raw, "keys") else set()


_NON_PACKAGE_DIRS: frozenset[str] = frozenset({"__pycache__"})


def _get_disk_test_subfolders() -> set[str]:
    return {d.name for d in TESTS_DIR.iterdir() if d.is_dir() and d.name not in _NON_PACKAGE_DIRS}


# ---------------------------------------------------------------------------
# Invariant tests
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=False,
    reason=(
        "Pre-migration: tests/agentic_core, tests/apps_* still exist at the wrong "
        "level. Will pass after Phase D migration moves them under tests/unit/."
    ),
)
def test_all_disk_subfolders_declared_in_ssot():
    """Every folder on disk under tests/ must be in _constants.py SSOT."""
    declared = _get_blueprint_test_subfolders()
    on_disk = _get_disk_test_subfolders()
    undeclared = on_disk - declared
    assert not undeclared, (
        f"tests/ subfolders exist on disk but are NOT declared in the SSOT "
        f"(_constants.py tests territory): {sorted(undeclared)}\n"
        f"Add them to the 'subfolders' dict of the 'tests' territory in "
        f"agentic_core/L5_safety/config/structure_blueprint/_constants.py"
    )


@pytest.mark.xfail(
    strict=False,
    reason=(
        "Pre-migration: healing pipeline placed agentic_core/apps_* directly under "
        "tests/ instead of tests/unit/. Will pass after Phase D migration."
    ),
)
def test_no_source_mirror_at_tests_root():
    """Source-mirrored test folders must NOT appear directly under tests/.

    They belong under tests/unit/<source_root>/, not tests/<source_root>/.
    The healing pipeline previously created tests/agentic_core/ etc. at the
    wrong level; this test prevents regression once migration is complete.
    """
    from agentic_core.L5_safety.config.structure_blueprint import TEST_MIRROR_ROOTS

    on_disk = _get_disk_test_subfolders()
    misplaced = on_disk & TEST_MIRROR_ROOTS
    assert not misplaced, (
        f"Source-mirror roots found directly under tests/ (wrong level): {sorted(misplaced)}\n"
        f"These must live under tests/unit/<name>/, not tests/<name>/.\n"
        f"Run the migration script: tools/mirror_tests.py"
    )


def test_tests_l2_subfolder_map_matches_ssot():
    """derived.py TESTS_L2_SUBFOLDER_MAP keys must equal the SSOT declared subfolders."""
    from agentic_core.L5_safety.config.structure_blueprint import TESTS_L2_SUBFOLDER_MAP

    declared = _get_blueprint_test_subfolders()
    derived_keys = set(TESTS_L2_SUBFOLDER_MAP.keys())
    diff = derived_keys.symmetric_difference(declared)
    assert not diff, (
        f"TESTS_L2_SUBFOLDER_MAP in derived.py diverged from SSOT territory.\n"
        f"Symmetric diff: {sorted(diff)}\n"
        f"This should not happen — derived.py reads from the territory."
    )


def test_canonical_location_map_keys_in_mirror_roots():
    """TEST_CANONICAL_LOCATION_MAP keys must be a subset of TEST_MIRROR_ROOTS."""
    from agentic_core.L5_safety.config.structure_blueprint import (
        TEST_CANONICAL_LOCATION_MAP,
        TEST_MIRROR_ROOTS,
    )

    extra = set(TEST_CANONICAL_LOCATION_MAP.keys()) - TEST_MIRROR_ROOTS - {"system_learning"}
    assert not extra, f"TEST_CANONICAL_LOCATION_MAP has keys not in TEST_MIRROR_ROOTS: {extra}"


def test_get_canonical_test_path_agentic_core():
    """get_canonical_test_path routes agentic_core sources to tests/unit/agentic_core/."""
    from agentic_core.L5_safety.config.structure_blueprint import get_canonical_test_path

    src = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning" / "FooAgent.py"
    result = get_canonical_test_path(src, REPO_ROOT)
    expected = REPO_ROOT / "tests" / "unit" / "agentic_core" / "L5_safety" / "reasoning" / "test_FooAgent.py"
    assert result == expected, f"Expected {expected}, got {result}"


def test_get_canonical_test_path_apps_rg():
    """get_canonical_test_path routes apps_rg sources to tests/unit/apps_rg/."""
    from agentic_core.L5_safety.config.structure_blueprint import get_canonical_test_path

    src = REPO_ROOT / "apps_rg" / "engines" / "BarEngine.py"
    result = get_canonical_test_path(src, REPO_ROOT)
    expected = REPO_ROOT / "tests" / "unit" / "apps_rg" / "engines" / "test_BarEngine.py"
    assert result == expected, f"Expected {expected}, got {result}"


def test_align_tests_structure_util_imports_from_ssot():
    """align_tests_structure_util.py must NOT define its own TESTS_L2_SUBFOLDER_MAP literal.

    It must import from the SSOT blueprint package.
    Uses AST parsing — no string grep.
    """
    util_path = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "align_tests_structure_util.py"
    source = util_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(util_path))

    # Check: no module-level dict assignment named TESTS_L2_SUBFOLDER_MAP
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TESTS_L2_SUBFOLDER_MAP":
                    if isinstance(node.value, ast.Dict):
                        pytest.fail(
                            "align_tests_structure_util.py defines its own "
                            "TESTS_L2_SUBFOLDER_MAP literal dict. "
                            "It must import from the SSOT blueprint package instead."
                        )

    # Check: has an import from structure_blueprint for TESTS_L2_SUBFOLDER_MAP
    has_ssot_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "structure_blueprint" in module:
                names = [alias.name for alias in node.names]
                if "TESTS_L2_SUBFOLDER_MAP" in names:
                    has_ssot_import = True
                    break

    assert has_ssot_import, (
        "align_tests_structure_util.py does not import TESTS_L2_SUBFOLDER_MAP "
        "from structure_blueprint. It must use the SSOT constant."
    )


def test_test_generator_agent_no_hardcoded_tests_path():
    """TestGeneratorAgent must not hardcode 'tests/autogen' — must use SSOT constant.

    Uses AST parsing.
    """
    agent_path = REPO_ROOT / "agentic_core" / "L5_safety" / "reasoning" / "TestGeneratorAgent.py"
    source = agent_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(agent_path))

    hardcoded = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in ("tests/autogen", "tests\\autogen"):
                hardcoded.append(node.value)

    assert not hardcoded, (
        f"TestGeneratorAgent.py contains hardcoded test path(s): {hardcoded}. "
        f"Use TESTS_AUTOGEN_DIR from the SSOT blueprint package."
    )
