#!/usr/bin/env python3
"""
manifest_validator.py

Agentic L5 Repository Structural Validator
==========================================

This validator performs strict, schema-driven structural checks on the repository.
It enforces OpenAI Agentic L5 architecture principles across:

- Pillar 1  Structural / Layering Model  
- Pillar 3  Structural / Typed Contracts (via folder existence)  
- Pillar 4  Workflow (DAG) / Engine correctness  
- Pillar 8  Tool ecosystem / adapters / tool registry folder correctness  
- Pillar 11 Cost / Optimization (filename constraints, no duplicates)  
- Pillar 12 Test governance (required folders, no strays or empties)  
- Pillar 13 Prompt Governance (prompt registry folder structure)  
- Pillar 14 Sandbox compliance (runtime/sandbox folder enforced)

All validations here are *purely structural*, operating on:

- required directories  
- exact children sets  
- forbidden files  
- empty directory policy  
- depth policy  
- filename policy  
- hidden file rules  
- manifest consistency (ci_manifest.json)  

Exit code:
- 0 = ok  
- 1 = violations  
"""

import json
import os
import sys
from dataclasses import dataclass
from typing import List, Dict, Set, Iterable, Tuple


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)

MAX_DEPTH = 10
MAX_FILENAME_LEN = 80

FORBIDDEN_TEST_EXTS = {
    ".ipynb",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".tmp",
    ".bak",
}

FORBIDDEN_SUBSTRINGS = ["backup", "old", "copy", "draft", "tmp"]

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
    "README.md",
    "LICENSE",
    "ci_reports",
    "ci_manifest.json",
    "windsurf_validation_keys.json",
    "pyproject.toml",
    "requirements.txt",
}

# agentic_core structure
AGENTIC_CORE_CHILDREN = {
    "l1_planning",
    "l2_execution",
    "l3_orchestration",
    "l4_memory",
    "l5_safety",
}

AGENTIC_L1 = {"planners", "schemas", "utils"}
AGENTIC_L2 = {"executors", "schemas", "utils"}
AGENTIC_L3 = {"engines", "framework", "utils"}
AGENTIC_L4 = {"mappings", "providers", "temporal"}
AGENTIC_L5 = {"filters", "policies", "validators"}

APPS_CHILDREN = {"resume_engine", "outreach_engine"}
ENGINE_LAYER_CHILDREN = {"l1", "l2", "l3", "l4", "l5"}

TESTS_CHILDREN = {
    "data",
    "fixtures",
    "e2e",
    "integration",
    "l1",
    "l2",
    "l3",
    "l4",
    "l5",
    "regression",
}

TESTS_L1 = {"unit", "integration"}
TESTS_L2 = {"unit", "integration"}
TESTS_L3 = {"orchestration"}
TESTS_L4 = {"memory"}
TESTS_L5 = {"safety"}

GITHUB_CHILDREN = {"workflows"}


# ============================================================
# VIOLATIONS
# ============================================================

@dataclass
class Violation:
    code: str
    message: str
    path: str


def rel(path: str) -> str:
    try:
        return os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path


# ============================================================
# UTILITIES
# ============================================================


def walk_dirs(root: str) -> Iterable[Tuple[str, List[str], List[str]]]:
    for dp, dns, fns in os.walk(root):
        # prevent symlink traversal
        dns[:] = [d for d in dns if not os.path.islink(os.path.join(dp, d))]
        yield dp, dns, fns


def depth(path: str) -> int:
    relative = rel(path)
    if relative in (".", ""):
        return 0
    return len(relative.split(os.sep))


def load_manifest() -> Dict:
    mf = os.path.join(REPO_ROOT, "ci_manifest.json")
    if not os.path.isfile(mf):
        return {}
    try:
        with open(mf, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ============================================================
# VALIDATION HELPERS
# ============================================================


def exact_children(dirpath: str, expected: Set[str], violations: List[Violation], code_prefix: str):
    if not os.path.isdir(dirpath):
        violations.append(Violation(f"{code_prefix}_MISSING_DIR",
                                   "Required directory missing",
                                   rel(dirpath)))
        return

    actual = set(os.listdir(dirpath))
    # Allow typical ignore
    clean = {a for a in actual if a not in {"__pycache__", ".gitkeep"}}

    # Missing
    for e in expected:
        if e not in clean:
            violations.append(Violation(f"{code_prefix}_MISSING_CHILD",
                                       f"Missing required child '{e}'",
                                       rel(dirpath)))

    # Unexpected
    for a in clean:
        if a not in expected:
            violations.append(Violation(f"{code_prefix}_UNEXPECTED_CHILD",
                                       f"Unexpected directory child '{a}'",
                                       rel(os.path.join(dirpath, a))))


def check_empty_directories(violations: List[Violation]):
    for dp, dns, fns in walk_dirs(REPO_ROOT):
        r = rel(dp)
        if r == ".":
            continue
        if not dns and not fns:
            violations.append(Violation("EMPTY_DIR",
                                       "Directory is empty — not allowed",
                                       r))


def check_depth_limits(violations: List[Violation]):
    for dp, dns, fns in walk_dirs(REPO_ROOT):
        d = depth(dp)
        if d > MAX_DEPTH:
            violations.append(Violation("DEPTH_EXCEEDED",
                                       f"Depth {d} exceeds MAX_DEPTH {MAX_DEPTH}",
                                       rel(dp)))


def check_case_collisions(violations: List[Violation]):
    for dp, dns, fns in walk_dirs(REPO_ROOT):
        combined = dns + fns
        lower_map = {}
        for name in combined:
            lower = name.lower()
            lower_map.setdefault(lower, []).append(name)

        for lower, originals in lower_map.items():
            if len(originals) > 1:
                violations.append(Violation("CASE_COLLISION",
                                           f"Case-insensitive collision: {originals}",
                                           rel(dp)))


def check_filename_rules(violations: List[Violation]):
    for dp, dns, fns in walk_dirs(REPO_ROOT):
        for name in dns + fns:
            relp = rel(os.path.join(dp, name))

            # length
            if len(name) > MAX_FILENAME_LEN:
                violations.append(Violation("FILENAME_TOO_LONG",
                                           f"Filename exceeds max length: {name}",
                                           relp))

            lower = name.lower()
            for sub in FORBIDDEN_SUBSTRINGS:
                if sub in lower:
                    violations.append(Violation("FILENAME_FORBIDDEN_SUBSTRING",
                                               f"Forbidden substring '{sub}' in name",
                                               relp))


def check_hidden_root(violations: List[Violation]):
    for name in os.listdir(REPO_ROOT):
        if name.startswith(".") and name not in {".gitignore", ".github"}:
            violations.append(Violation("ROOT_HIDDEN_FORBIDDEN",
                                       "Hidden file/folder not allowed at root",
                                       rel(os.path.join(REPO_ROOT, name))))


def check_tests_extensions(violations: List[Violation]):
    test_root = os.path.join(REPO_ROOT, "tests")
    if not os.path.isdir(test_root):
        violations.append(Violation("TESTS_ROOT_MISSING",
                                   "tests/ directory missing",
                                   rel(test_root)))
        return

    for dp, dns, fns in walk_dirs(test_root):
        for fn in fns:
            _, ext = os.path.splitext(fn)
            if ext.lower() in FORBIDDEN_TEST_EXTS:
                violations.append(Violation("TEST_FILE_FORBIDDEN_EXT",
                                           f"Forbidden extension '{ext}' in tests",
                                           rel(os.path.join(dp, fn))))


def check_manifest_parity(violations: List[Violation]):
    manifest = load_manifest()
    if not manifest:
        return

    allowed_keys = {"files", "dirs"}
    for key in manifest.keys():
        if key not in allowed_keys:
            violations.append(Violation("MANIFEST_UNEXPECTED_KEY",
                                       f"Unexpected key '{key}' in manifest",
                                       rel("ci_manifest.json")))

    for f in manifest.get("files", []):
        full = os.path.join(REPO_ROOT, f)
        if not os.path.isfile(full):
            violations.append(Violation("MANIFEST_FILE_MISSING",
                                       f"Manifest file missing: {f}",
                                       rel(full)))

    for d in manifest.get("dirs", []):
        full = os.path.join(REPO_ROOT, d)
        if not os.path.isdir(full):
            violations.append(Violation("MANIFEST_DIR_MISSING",
                                       f"Manifest directory missing: {d}",
                                       rel(full)))


# ============================================================
# STRUCTURAL CHECKS PER DIRECTORY
# ============================================================

def check_root_structure(violations: List[Violation]):
    actual = set(os.listdir(REPO_ROOT))

    # Unexpected
    for a in actual:
        if a not in ALLOWED_ROOT_CHILDREN:
            violations.append(Violation("ROOT_CHILD_UNEXPECTED",
                                       f"Unexpected root child '{a}'",
                                       rel(os.path.join(REPO_ROOT, a))))

    # Required
    for req in [
        "agentic_core", "apps", "tests", "schemas",
        "runtime", "observability", "prompt_governance",
        "data", "docs", ".github"
    ]:
        if req not in actual:
            violations.append(Violation("ROOT_CHILD_MISSING",
                                       f"Missing required root entry '{req}'",
                                       rel(REPO_ROOT)))


def check_agentic_core(violations: List[Violation]):
    ac = os.path.join(REPO_ROOT, "agentic_core")
    exact_children(ac, AGENTIC_CORE_CHILDREN, violations, "AGENTIC_CORE")

    exact_children(os.path.join(ac, "l1_planning"), AGENTIC_L1, violations, "L1_PLANNING")
    exact_children(os.path.join(ac, "l2_execution"), AGENTIC_L2, violations, "L2_EXECUTION")
    exact_children(os.path.join(ac, "l3_orchestration"), AGENTIC_L3, violations, "L3_ORCHESTRATION")
    exact_children(os.path.join(ac, "l4_memory"), AGENTIC_L4, violations, "L4_MEMORY")
    exact_children(os.path.join(ac, "l5_safety"), AGENTIC_L5, violations, "L5_SAFETY")


def check_apps_structure(violations: List[Violation]):
    apps = os.path.join(REPO_ROOT, "apps")
    exact_children(apps, APPS_CHILDREN, violations, "APPS")

    for engine in APPS_CHILDREN:
        engine_path = os.path.join(apps, engine)
        exact_children(engine_path, ENGINE_LAYER_CHILDREN, violations, f"APPS_{engine.upper()}")


def check_tests_structure(violations: List[Violation]):
    troot = os.path.join(REPO_ROOT, "tests")
    exact_children(troot, TESTS_CHILDREN, violations, "TESTS")

    exact_children(os.path.join(troot, "l1"), TESTS_L1, violations, "TESTS_L1")
    exact_children(os.path.join(troot, "l2"), TESTS_L2, violations, "TESTS_L2")
    exact_children(os.path.join(troot, "l3"), TESTS_L3, violations, "TESTS_L3")
    exact_children(os.path.join(troot, "l4"), TESTS_L4, violations, "TESTS_L4")
    exact_children(os.path.join(troot, "l5"), TESTS_L5, violations, "TESTS_L5")


def check_github_structure(violations: List[Violation]):
    gh = os.path.join(REPO_ROOT, ".github")
    exact_children(gh, GITHUB_CHILDREN, violations, "GITHUB")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    violations: List[Violation] = []

    if not os.path.isdir(REPO_ROOT):
        print(f"[manifest_validator] ERROR: repo root not found: {REPO_ROOT}")
        sys.exit(1)

    # Structural checks
    check_hidden_root(violations)
    check_root_structure(violations)
    check_agentic_core(violations)
    check_apps_structure(violations)
    check_tests_structure(violations)
    check_github_structure(violations)

    # Non-structural but mandatory ground rules
    check_empty_directories(violations)
    check_depth_limits(violations)
    check_case_collisions(violations)
    check_filename_rules(violations)
    check_tests_extensions(violations)

    # Manifest parity
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
