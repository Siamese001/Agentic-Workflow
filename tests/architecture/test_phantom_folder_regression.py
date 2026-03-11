"""
Regression guard for phantom folder bugs created by healing agents.

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent._heal_depth_violation | SHALLOW depth path | depth_aligned/ created | HARD FAIL — must never exist | test_no_depth_aligned_anywhere |
| HierarchyAgent._heal_depth_violation | DEEP depth path | depth_aligned/ created | HARD FAIL — must never exist | test_no_depth_aligned_in_agentic_core |
| LocationHealerAgent | any healing run | depth_aligned/ spacer created | HARD FAIL — must never exist | test_no_depth_aligned_in_any_territory |
| healing pipeline | any healing run | tests/support/ gains L-layer subdirs | HARD FAIL — support must be flat | test_tests_support_has_no_subdirectories |
| healing pipeline | any healing run | agent file duplicated into phantom subdir | HARD FAIL — no duplicate agents | test_no_agent_file_duplicated_in_subdir |
| healing pipeline | any healing run | depth_aligned duplicate of parent dir | HARD FAIL — content must be unique | test_depth_aligned_not_duplicate_of_parent |

## Bugs being guarded
Bug 1: HierarchyAgent / LocationHealerAgent create `depth_aligned/` spacer directories
        when a file is at the wrong depth. These are semantically meaningless and
        duplicate content from the parent directory.

Bug 2: Healing pipeline creates L-layer subdirectories (`l1_cognition/`, `l2_execution/`,
        `l3_orchestration/`, `l6_observability/`) under `tests/support/`, duplicating
        agent files that already exist at the flat root level.

Both bugs represent the same class of failure: healing agents creating phantom structural
scaffolding rather than actually relocating files correctly.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENT_TERRITORIES = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,
    OPS_SCRIPTS_DIR,
    "docs",
]

# Only used for tests/support/ specific check — NOT for broad territory scan.
# ops_scripts/dev_tools/l0_scripts is a legitimate directory.
L_LAYER_PATTERN = re.compile(r"^l[0-9]_[a-z]+$")


# ===========================================================================
# Bug 1: depth_aligned/ phantom folders
# ===========================================================================


@pytest.mark.architecture
class TestDepthAlignedRegression:
    def _all_depth_aligned_dirs(self) -> list[Path]:
        violations = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("*"):
                if d.is_dir() and d.name == "depth_aligned":
                    violations.append(d)
        return violations

    def test_no_depth_aligned_anywhere(self):
        """depth_aligned/ must not exist anywhere in any canonical territory.

        This directory name is a semantically meaningless spacer invented by
        HierarchyAgent / LocationHealerAgent to satisfy depth counters. It is
        a known healing bug. Any occurrence = regression.
        """
        violations = self._all_depth_aligned_dirs()
        if violations:
            rel = [str(d.relative_to(REPO_ROOT)) for d in violations]
            pytest.fail(
                f"HEALING BUG REGRESSION: {len(violations)} phantom depth_aligned/ "
                f"director(y/ies) found — these must never be created:\n  " + "\n  ".join(rel)
            )

    def test_no_depth_aligned_in_agentic_core(self):
        """Specific guard: agentic_core/ must never contain depth_aligned/."""
        ac = REPO_ROOT / AGENTIC_CORE_DIR
        if not ac.exists():
            pytest.fail("agentic_core not present")
        violations = [d for d in ac.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside agentic_core/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_no_depth_aligned_in_tests(self):
        """Specific guard: tests/ must never contain depth_aligned/."""
        t = REPO_ROOT / TESTS_DIR
        if not t.exists():
            pytest.fail("tests/ not present")
        violations = [d for d in t.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside tests/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_no_depth_aligned_in_system_learning(self):
        """Specific guard: system_learning/ must never contain depth_aligned/."""
        sl = REPO_ROOT / SYSTEM_LEARNING_DIR
        if not sl.exists():
            pytest.fail("system_learning not present")
        violations = [d for d in sl.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside system_learning/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_depth_aligned_not_in_sovereign_territories_blueprint(self):
        """depth_aligned must not be declared as a canonical subfolder in the blueprint.

        Guards against the healing agent updating SOVEREIGN_TERRITORIES to
        legitimise the phantom folder structure.
        """
        try:
            from agentic_core.L5_safety.config.structure_blueprint import (
                get_all_territories,
            )
        except ImportError:
            pytest.fail("get_all_territories not importable")

        def _walk(obj: object, path: str = "") -> list[str]:
            found = []
            if hasattr(obj, "items"):
                for k, v in obj.items():
                    if k == "depth_aligned":
                        found.append(f"{path}.{k}")
                    found.extend(_walk(v, f"{path}.{k}"))
            return found

        violations = _walk(get_all_territories())
        assert not violations, (
            "depth_aligned declared as canonical subfolder in get_all_territories(): "
            + ", ".join(violations)
            + " — this is forbidden."
        )

    def test_depth_aligned_not_duplicate_of_parent(self):
        """depth_aligned/ content must not be a duplicate of its parent directory.

        When the bug fires, depth_aligned/ contains byte-for-byte copies of parent
        files. This test catches partial regression where the folder exists but
        the duplication only covers some files.
        """
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("depth_aligned"):
                if not d.is_dir():
                    continue
                parent = d.parent
                parent_files = {f.name for f in parent.iterdir() if f.is_file()}
                da_files = {f.name for f in d.iterdir() if f.is_file()}
                overlap = parent_files & da_files
                assert not overlap, (
                    f"depth_aligned/ at {d.relative_to(REPO_ROOT)} duplicates "
                    f"{len(overlap)} file(s) from its parent: {sorted(overlap)}"
                )


# ===========================================================================
# Bug 2: tests/support/ phantom L-layer subdirectories
# ===========================================================================


@pytest.mark.architecture
class TestTestsSupportFlatStructure:
    def _support_subdirs(self) -> list[Path]:
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            return []
        return [d for d in support.iterdir() if d.is_dir() and d.name != "__pycache__"]

    def test_tests_support_has_no_subdirectories(self):
        """tests/support/ must be a flat directory with no subdirectories.

        Healing agents have incorrectly created L-layer subdirectories (l1_cognition/,
        l2_execution/, etc.) under tests/support/ and duplicated agent files into them.
        tests/support/ holds flat test-only infrastructure agents — no hierarchy allowed.
        """
        subdirs = self._support_subdirs()
        if subdirs:
            rel = [str(d.relative_to(REPO_ROOT)) for d in subdirs]
            pytest.fail(
                f"HEALING BUG REGRESSION: {len(subdirs)} phantom subdirector(y/ies) found "
                f"under tests/support/ — this directory must be flat:\n  " + "\n  ".join(rel)
            )

    def test_tests_support_has_no_l_layer_subdirectories(self):
        """tests/support/ must not contain any L-layer subdirectory names.

        Pattern: l[0-9]_<name> (e.g. l1_cognition, l6_observability).
        These are phantom folders created by a misbehaving healing run.
        """
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")
        violations = [d for d in support.iterdir() if d.is_dir() and L_LAYER_PATTERN.match(d.name)]
        assert not violations, "L-layer phantom subdirectories found under tests/support/: " + ", ".join(
            d.name for d in violations
        )

    def test_tests_support_no_agent_duplication(self):
        """Agent files in tests/support/ must not also exist in any subdirectory.

        When the bug fires, every agent at tests/support/FooAgent.py is also
        duplicated into tests/support/l1_cognition/FooAgent.py (or similar).
        """
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")

        root_agents = {f.name for f in support.iterdir() if f.is_file() and f.suffix == ".py"}
        subdirs = [d for d in support.iterdir() if d.is_dir() and d.name != "__pycache__"]

        for subdir in subdirs:
            sub_files = {f.name for f in subdir.iterdir() if f.is_file() and f.suffix == ".py"}
            duplicates = root_agents & sub_files
            assert not duplicates, (
                f"Agent file(s) duplicated between tests/support/ and "
                f"tests/support/{subdir.name}/: {sorted(duplicates)}"
            )

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "l0_routing",
            "l1_cognition",
            "l2_execution",
            "l3_orchestration",
            "l4_memory",
            "l5_safety",
            "l6_observability",
            "depth_aligned",
            "_quarantine",
        ],
    )
    def test_tests_support_specific_forbidden_subdirs_absent(self, forbidden_name):
        """Each known-bad subdirectory name must not exist under tests/support/."""
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")
        bad = support / forbidden_name
        assert not bad.exists(), (
            f"Forbidden subdirectory tests/support/{forbidden_name}/ exists — "
            "created by a misbehaving healing run. Remove it."
        )


# ===========================================================================
# Bug 3: phantom subdirectory duplication across all territories
# ===========================================================================


@pytest.mark.architecture
class TestPhantomSubdirDuplication:
    # ONLY depth_aligned is universally forbidden.
    # _quarantine is canonical under tests/. l0_scripts is legitimate ops tooling.
    FORBIDDEN_SUBDIR_NAMES = frozenset({"depth_aligned"})

    def _is_forbidden(self, name: str) -> bool:
        return name in self.FORBIDDEN_SUBDIR_NAMES

    def test_no_depth_aligned_subdirs_in_any_territory(self):
        """No canonical territory may contain depth_aligned/ subdirs.

        This is the exhaustive scan across all territories that catches any healing
        agent creating phantom depth_aligned/ structure anywhere in the repo.
        """
        violations: list[str] = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("*"):
                if d.is_dir() and self._is_forbidden(d.name) and "__pycache__" not in d.parts:
                    violations.append(str(d.relative_to(REPO_ROOT)))

        assert not violations, (
            f"REGRESSION: {len(violations)} forbidden depth_aligned/ directory(ies) found:\n  "
            + "\n  ".join(sorted(violations))
        )

    def test_no_file_exists_in_both_parent_and_depth_aligned_subdir(self):
        """Files must not be duplicated between a directory and a depth_aligned/ child.

        When the healing bug fires, a directory gains a depth_aligned/ child that
        contains byte-for-byte copies of the parent's files.
        """
        violations: list[str] = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("depth_aligned"):
                if not d.is_dir() or "__pycache__" in d.parts:
                    continue
                parent = d.parent
                parent_files = {f.name for f in parent.iterdir() if f.is_file()}
                child_files = {f.name for f in d.iterdir() if f.is_file()}
                dupes = parent_files & child_files
                for dup in sorted(dupes):
                    violations.append(f"{d.relative_to(REPO_ROOT)}/{dup}")

        assert not violations, (
            f"REGRESSION: {len(violations)} file(s) duplicated in depth_aligned/ subdir:\n  "
            + "\n  ".join(violations)
        )

    def test_git_index_has_no_depth_aligned_paths(self):
        """Ensure no depth_aligned/ directories are tracked by git.

        Catches cases where phantom dirs were committed but deleted on disk —
        they would resurface on the next `git checkout` or clone.
        """
        import subprocess

        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        tracked = result.stdout.splitlines()
        violations = [f for f in tracked if "depth_aligned" in Path(f).parts]
        assert not violations, (
            f"REGRESSION: {len(violations)} depth_aligned/ path(s) tracked in git index:\n  "
            + "\n  ".join(sorted(violations)[:40])
        )

    def test_git_index_has_no_tests_support_l_layer_subdirs(self):
        """Ensure no L-layer subdirs of tests/support/ are tracked in git.

        Catches the phantom tests/support/l1_cognition/, l6_observability/ etc.
        even if already deleted on disk (git index would restore them on checkout).
        """
        import subprocess

        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        tracked = result.stdout.splitlines()
        violations = [
            f
            for f in tracked
            if f.startswith("tests/support/")
            and len(Path(f).parts) > 2
            and L_LAYER_PATTERN.match(Path(f).parts[2])
        ]
        assert not violations, (
            f"REGRESSION: {len(violations)} phantom tests/support/L-layer path(s) in git:\n  "
            + "\n  ".join(sorted(violations)[:40])
        )
