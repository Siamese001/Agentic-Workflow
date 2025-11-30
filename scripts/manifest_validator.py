#!/usr/bin/env python3
"""
manifest_validator.py

Filesystem + manifest validator for Agentic-Workflow-10_11.

This script enforces a superset of the structural constraints expressed in:
- windsurf_validation_keys.json
- Agentic Design Pillars (L5 structural + governance expectations)

It validates:

1. Root structure / expected directories
   - agentic_core with L1–L5 subfolders
   - apps/{resume_engine,outreach_engine}/l1..l5
   - tests/ tree with prescribed subfolders
   - data, docs, schemas, runtime, observability, prompt_governance, .github/workflows

2. Exact children constraints
   - No unexpected direct children in key directories (strict allowlists).

3. Hidden / special entries
   - Only .gitignore and .github are allowed hidden entries at root.
   - No other dot-directories/files are permitted.

4. Empty directory policy
   - Zero tolerance for empty directories anywhere in the tree.

5. Depth constraints
   - Maximum directory depth from repo root is 9 levels.

6. Filename policy
   - Max name length: 80 characters (per path component, not full path).
   - Forbidden substrings in names: old, backup, copy, tmp, draft (case-insensitive).

7. Case collision policy
   - Zero tolerance for case-insensitive name collisions within any directory.

8. tests/ extension policy
   - Under tests/, forbidden file extensions:
     .ipynb, .md, .json, .yaml, .yml, .log, .tmp, .bak

9. Optional manifest parity
   - If ci_manifest.json exists at repo root, verify:
     - All listed paths exist
     - No unknown entries appear in manifest

Exit code:
- 0 if all checks pass
- 1 if any violation is found
"""

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable


# =====================================================================
# CONFIG
# =====================================================================

DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)

MAX_DEPTH = 9  # fs.depth.max_depth::9
MAX_NAME_LEN = 80  # fs.filename.max_length::80

FORBIDDEN_SUBSTRINGS = [
    "old",
    "backup",
    "copy",
    "tmp",
    "draft",
]

# tests.forbidden_extension::
FORBIDDEN_TEST_EXTS = {
    ".ipynb",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".log",
    ".tmp",
    ".bak",
}

ALLOWED_ROOT_CHILDREN = {
    "agentic_core",
    "apps",
    "tests",
    "schemas",
    "runtime",
    "observability",
    "prompt_governance",
    "data",
    "docs",
    ".github",
    ".gitignore",
    "ci_reports",         # CI output folder
    "ci_manifest.json",   # optional manifest
    "windsurf_validation_keys.json",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "requirements.txt",
}

# exact_children::agentic_core::
AGENTIC_CORE_CHILDREN = {
    "l1_planning",
    "l2_execution",
    "l3_orchestration",
    "l4_memory",
    "l5_safety",
}

AGENTIC_CORE_L1_CHILDREN = {"planners", "schemas", "utils"}
AGENTIC_CORE_L2_CHILDREN = {"executors", "schemas", "utils"}
AGENTIC_CORE_L3_CHILDREN = {"engines", "framework", "utils"}
AGENTIC_CORE_L4_CHILDREN = {"mappings", "providers", "temporal"}
AGENTIC_CORE_L5_CHILDREN = {"filters", "policies", "validators"}

APPS_CHILDREN = {"resume_engine", "outreach_engine"}
ENGINE_LAYER_CHILDREN = {"l1", "l2", "l3", "l4", "l5"}

TESTS_CHILDREN = {
    "data",
    "e2e",
    "fixtures",
    "integration",
    "l1",
    "l2",
    "l3",
    "l4",
    "l5",
    "regression",
}

TESTS_L1_CHILDREN = {"integration", "unit"}
TESTS_L2_CHILDREN = {"integration", "unit"}
TESTS_L3_CHILDREN = {"orchestration"}
TESTS_L4_CHILDREN = {"memory"}
TESTS_L5_CHILDREN = {"safety"}

GITHUB_CHILDREN = {"workflows"}


@dataclass
class Violation:
    code: str
    message: str
    path: str


# =====================================================================
# UTILS
# =====================================================================

def rel(path: str) -> str:
    """Return path relative to REPO_ROOT for readable messages."""
    try:
        return os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path


def walk_tree(root: str) -> Iterable[Tuple[str, List[str], List[str]]]:
    """Wrapper over os.walk to avoid following symlinks."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Do not follow symlinks
        dirnames[:] = [d for d in dirnames if not os.path.islink(os.path.join(dirpath, d))]
        yield dirpath, dirnames, filenames


def depth_of(path: str) -> int:
    """Compute depth (number of path segments) from REPO_ROOT."""
    rel_path = rel(path)
    if rel_path in (".", ""):
        return 0
    parts = [p for p in rel_path.split(os.sep) if p]
    return len(parts)


def load_manifest(root: str) -> Dict[str, List[str]]:
    """Load optional manifest file if present, else return empty."""
    manifest_path = os.path.join(root, "ci_manifest.json")
    if not os.path.exists(manifest_path):
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        # Manifest is best-effort – structural failure is handled as violation later
        return {}


# =====================================================================
# CHECKS
# =====================================================================

def check_root_structure(violations: List[Violation]) -> None:
    root_children = set(os.listdir(REPO_ROOT))

    # Hidden handling & allowed root set
    for name in root_children:
        full = os.path.join(REPO_ROOT, name)
        if name.startswith("."):
            # Allowed: .gitignore and .github
            if name not in {".gitignore", ".github"}:
                violations.append(
                    Violation(
                        code="HIDDEN_ROOT_FORBIDDEN",
                        message=f"Unexpected hidden root entry: {name}",
                        path=rel(full),
                    )
                )

        # Check that root children are whitelisted
        if name not in ALLOWED_ROOT_CHILDREN:
            violations.append(
                Violation(
                    code="ROOT_CHILD_UNEXPECTED",
                    message=f"Unexpected root entry: {name}",
                    path=rel(full),
                )
            )

    # Required root children (structural presence)
    required = {
        "agentic_core",
        "apps",
        "tests",
        "schemas",
        "runtime",
        "observability",
        "prompt_governance",
        "data",
        "docs",
        ".github",
    }
    for req in required:
        if req not in root_children:
            violations.append(
                Violation(
                    code="ROOT_CHILD_MISSING",
                    message=f"Missing required root entry: {req}",
                    path=rel(REPO_ROOT),
                )
            )


def check_exact_children(
    root: str,
    subpath: str,
    expected_children: Set[str],
    violations: List[Violation],
    code_prefix: str,
) -> None:
    target = os.path.join(root, subpath)
    if not os.path.isdir(target):
        violations.append(
            Violation(
                code=f"{code_prefix}_MISSING_DIR",
                message=f"Expected directory missing: {subpath}",
                path=rel(target),
            )
        )
        return

    actual = set(os.listdir(target))
    # Filter out common noise directories
    actual_clean = {a for a in actual if a not in {".gitkeep", "__pycache__"}}

    # Missing
    for exp in expected_children:
        if exp not in actual_clean:
            violations.append(
                Violation(
                    code=f"{code_prefix}_MISSING_CHILD",
                    message=f"Missing child '{exp}' in {subpath}",
                    path=rel(target),
                )
            )
    # Unexpected
    for ch in actual_clean:
        if ch not in expected_children:
            violations.append(
                Violation(
                    code=f"{code_prefix}_UNEXPECTED_CHILD",
                    message=f"Unexpected child '{ch}' in {subpath}",
                    path=rel(os.path.join(target, ch)),
                )
            )


def check_structural_expectations(violations: List[Violation]) -> None:
    # agentic_core
    check_exact_children(
        REPO_ROOT,
        "agentic_core",
        AGENTIC_CORE_CHILDREN,
        violations,
        "AGENTIC_CORE",
    )

    check_exact_children(
        REPO_ROOT,
        os.path.join("agentic_core", "l1_planning"),
        AGENTIC_CORE_L1_CHILDREN,
        violations,
        "L1_PLANNING",
    )
    check_exact_children(
        REPO_ROOT,
        os.path.join("agentic_core", "l2_execution"),
        AGENTIC_CORE_L2_CHILDREN,
        violations,
        "L2_EXECUTION",
    )
    check_exact_children(
        REPO_ROOT,
        os.path.join("agentic_core", "l3_orchestration"),
        AGENTIC_CORE_L3_CHILDREN,
        violations,
        "L3_ORCHESTRATION",
    )
    check_exact_children(
        REPO_ROOT,
        os.path.join("agentic_core", "l4_memory"),
        AGENTIC_CORE_L4_CHILDREN,
        violations,
        "L4_MEMORY",
    )
    check_exact_children(
        REPO_ROOT,
        os.path.join("agentic_core", "l5_safety"),
        AGENTIC_CORE_L5_CHILDREN,
        violations,
        "L5_SAFETY",
    )

    # apps
    check_exact_children(REPO_ROOT, "apps", APPS_CHILDREN, violations, "APPS")

    for engine in ("resume_engine", "outreach_engine"):
        check_exact_children(
            REPO_ROOT,
            os.path.join("apps", engine),
            ENGINE_LAYER_CHILDREN,
            violations,
            f"APPS_{engine.upper()}",
        )
        for layer in ENGINE_LAYER_CHILDREN:
            # allow empty here structurally; emptiness is checked elsewhere
            engine_layer_dir = os.path.join(REPO_ROOT, "apps", engine, layer)
            if not os.path.isdir(engine_layer_dir):
                violations.append(
                    Violation(
                        code="ENGINE_LAYER_MISSING_DIR",
                        message=f"Missing {engine}/{layer} directory",
                        path=rel(engine_layer_dir),
                    )
                )

    # tests
    check_exact_children(REPO_ROOT, "tests", TESTS_CHILDREN, violations, "TESTS")
    check_exact_children(
        REPO_ROOT, os.path.join("tests", "l1"), TESTS_L1_CHILDREN, violations, "TESTS_L1"
    )
    check_exact_children(
        REPO_ROOT, os.path.join("tests", "l2"), TESTS_L2_CHILDREN, violations, "TESTS_L2"
    )
    check_exact_children(
        REPO_ROOT, os.path.join("tests", "l3"), TESTS_L3_CHILDREN, violations, "TESTS_L3"
    )
    check_exact_children(
        REPO_ROOT, os.path.join("tests", "l4"), TESTS_L4_CHILDREN, violations, "TESTS_L4"
    )
    check_exact_children(
        REPO_ROOT, os.path.join("tests", "l5"), TESTS_L5_CHILDREN, violations, "TESTS_L5"
    )

    # .github
    check_exact_children(REPO_ROOT, ".github", GITHUB_CHILDREN, violations, "GITHUB")


def check_empty_directories(violations: List[Violation]) -> None:
    for dirpath, dirnames, filenames in walk_tree(REPO_ROOT):
        # ignore repo root emptiness (not expected anyway) and .git
        rel_d = rel(dirpath)
        if rel_d == ".":
            continue
        # ignore common noise
        dirnames_clean = [d for d in dirnames if d not in {"__pycache__"}]
        if not dirnames_clean and not filenames:
            violations.append(
                Violation(
                    code="EMPTY_DIRECTORY",
                    message="Empty directory not allowed",
                    path=rel_d,
                )
            )


def check_depth(violations: List[Violation]) -> None:
    for dirpath, dirnames, filenames in walk_tree(REPO_ROOT):
        d = depth_of(dirpath)
        if d > MAX_DEPTH:
            violations.append(
                Violation(
                    code="DEPTH_EXCEEDED",
                    message=f"Directory depth {d} exceeds MAX_DEPTH={MAX_DEPTH}",
                    path=rel(dirpath),
                )
            )


def check_case_collisions(violations: List[Violation]) -> None:
    for dirpath, dirnames, filenames in walk_tree(REPO_ROOT):
        # Check directories + files
        names = dirnames + filenames
        lower_map: Dict[str, List[str]] = {}
        for name in names:
            lower_map.setdefault(name.lower(), []).append(name)

        for lower, originals in lower_map.items():
            if len(originals) > 1:
                violations.append(
                    Violation(
                        code="CASE_COLLISION",
                        message=f"Case-insensitive name collision: {originals}",
                        path=rel(dirpath),
                    )
                )


def check_filename_policy(violations: List[Violation]) -> None:
    forbidden_lower = [s.lower() for s in FORBIDDEN_SUBSTRINGS]

    for dirpath, dirnames, filenames in walk_tree(REPO_ROOT):
        for name in dirnames + filenames:
            full_path = os.path.join(dirpath, name)
            rel_p = rel(full_path)
            # Name length
            if len(name) > MAX_NAME_LEN:
                violations.append(
                    Violation(
                        code="NAME_TOO_LONG",
                        message=f"Name exceeds {MAX_NAME_LEN} chars: {name}",
                        path=rel_p,
                    )
                )

            # Forbidden substrings
            lower_name = name.lower()
            for sub in forbidden_lower:
                if sub in lower_name:
                    violations.append(
                        Violation(
                            code="NAME_FORBIDDEN_SUBSTRING",
                            message=f"Name contains forbidden substring '{sub}': {name}",
                            path=rel_p,
                        )
                    )


def check_tests_extensions(violations: List[Violation]) -> None:
    tests_root = os.path.join(REPO_ROOT, "tests")
    if not os.path.isdir(tests_root):
        violations.append(
            Violation(
                code="TESTS_DIR_MISSING",
                message="tests/ directory is missing",
                path=rel(tests_root),
            )
        )
        return

    for dirpath, _, filenames in walk_tree(tests_root):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            _, ext = os.path.splitext(fn)
            if ext.lower() in FORBIDDEN_TEST_EXTS:
                violations.append(
                    Violation(
                        code="TESTS_FORBIDDEN_EXTENSION",
                        message=f"Forbidden test file extension '{ext}'",
                        path=rel(full),
                    )
                )


def check_manifest_parity(violations: List[Violation]) -> None:
    """
    If ci_manifest.json exists, ensure:
    - It is valid JSON mapping "files" / "dirs" -> list[str]
    - Every listed path exists
    - No extraneous keys are present
    """
    manifest_path = os.path.join(REPO_ROOT, "ci_manifest.json")
    if not os.path.exists(manifest_path):
        return

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        violations.append(
            Violation(
                code="MANIFEST_INVALID_JSON",
                message=f"ci_manifest.json is not valid JSON ({e})",
                path=rel(manifest_path),
            )
        )
        return

    if not isinstance(data, dict):
        violations.append(
            Violation(
                code="MANIFEST_INVALID_TYPE",
                message="ci_manifest.json root must be a JSON object",
                path=rel(manifest_path),
            )
        )
        return

    allowed_keys = {"files", "dirs"}
    for key in data.keys():
        if key not in allowed_keys:
            violations.append(
                Violation(
                    code="MANIFEST_UNEXPECTED_KEY",
                    message=f"Unexpected key in manifest: {key}",
                    path=rel(manifest_path),
                )
            )

    files = data.get("files", [])
    dirs = data.get("dirs", [])

    if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
        violations.append(
            Violation(
                code="MANIFEST_FILES_INVALID",
                message='"files" must be a list of strings',
                path=rel(manifest_path),
            )
        )
    if not isinstance(dirs, list) or not all(isinstance(p, str) for p in dirs):
        violations.append(
            Violation(
                code="MANIFEST_DIRS_INVALID",
                message='"dirs" must be a list of strings',
                path=rel(manifest_path),
            )
        )

    for fpath in files:
        full = os.path.join(REPO_ROOT, fpath)
        if not os.path.isfile(full):
            violations.append(
                Violation(
                    code="MANIFEST_FILE_MISSING",
                    message=f"Manifest file missing in repo: {fpath}",
                    path=rel(full),
                )
            )

    for dpath in dirs:
        full = os.path.join(REPO_ROOT, dpath)
        if not os.path.isdir(full):
            violations.append(
                Violation(
                    code="MANIFEST_DIR_MISSING",
                    message=f"Manifest directory missing in repo: {dpath}",
                    path=rel(full),
                )
            )


# =====================================================================
# MAIN
# =====================================================================

def main() -> None:
    violations: List[Violation] = []

    if not os.path.isdir(REPO_ROOT):
        print(f"[manifest_validator] ERROR: REPO_ROOT does not exist: {REPO_ROOT}")
        sys.exit(1)

    # 1. Root & structural expectations
    check_root_structure(violations)
    check_structural_expectations(violations)

    # 2. Empty directories
    check_empty_directories(violations)

    # 3. Depth
    check_depth(violations)

    # 4. Case collision
    check_case_collisions(violations)

    # 5. Filename policy
    check_filename_policy(violations)

    # 6. tests/ forbidden extensions
    check_tests_extensions(violations)

    # 7. Manifest parity
    check_manifest_parity(violations)

    if not violations:
        print("[manifest_validator] OK: All structural checks passed.")
        sys.exit(0)

    print("[manifest_validator] FAIL: Violations detected.")
    for v in violations:
        print(f"[{v.code}] {v.message} :: {v.path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
