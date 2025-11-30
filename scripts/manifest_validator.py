#!/usr/bin/env python3
"""
manifest_validator.py
Ultra-strict canonical repo structure and filesystem hygiene validator.

Covers:
- Root-level allowlist (no unexpected top-level dirs)
- Forbidden dirs anywhere (cache, .cache, __pycache__, .venv, etc.)
- Depth limits
- Hidden directory/file policy
- Forbidden extensions (log, tmp, bak, zip, exe, dll, etc.)
- Unknown extensions outside a safe text allowlist
- Empty directory detection
- Case-insensitive filename collisions
- Optional manifest.yaml exact match of dirs/files
"""

import os
import sys
import yaml
from collections import defaultdict

# =============================================================================
# CONFIG
# =============================================================================

REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
MANIFEST_PATH = os.path.join(REPO_ROOT, "manifest.yaml")

# Allowed top-level directories (zero-tolerance: anything else is a violation)
ALLOWED_ROOT_DIRS = {
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

# Forbidden directory names anywhere in the tree
FORBIDDEN_DIR_NAMES = {
    "__pycache__",
    ".cache",
    "cache",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "node_modules",
}

# Forbidden file extensions (outside explicit allow zones)
FORBIDDEN_EXTENSIONS = {
    ".log",
    ".tmp",
    ".bak",
    ".swp",
    ".swo",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
}

# Extensions we treat as "text-like" and allowed by default
ALLOWED_TEXT_EXTS = {
    ".py",
    ".txt",
    ".md",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
}

# Hidden dirs/files allowlist
ALLOWED_HIDDEN_DIRS = {".github"}
ALLOWED_HIDDEN_FILES = {".gitignore"}

MAX_DEPTH = 10  # max directory depth from REPO_ROOT (defensive bound)


# =============================================================================
# HELPERS
# =============================================================================

def relpath(path: str) -> str:
    return os.path.relpath(path, REPO_ROOT).replace("\\", "/")


def walk_repo(root: str):
    """Return (dirs, files) as sets of repo-relative paths."""
    dirs = set()
    files = set()
    for dirpath, dirnames, filenames in os.walk(root):
        rdir = relpath(dirpath)
        if rdir != ".":
            dirs.add(rdir)
        for f in filenames:
            rel_file = f"{rdir}/{f}" if rdir != "." else f
            files.add(rel_file)
    return dirs, files


def get_depth(rel: str) -> int:
    if not rel or rel == ".":
        return 0
    return len(rel.split("/"))


def load_manifest(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def flatten_manifest(node, prefix=""):
    expected_dirs = set()
    expected_files = set()

    for entry in node:
        name = entry["name"]
        path = f"{prefix}/{name}" if prefix else name

        if entry["type"] == "directory":
            expected_dirs.add(path)
            children = entry.get("children", [])
            d2, f2 = flatten_manifest(children, path)
            expected_dirs |= d2
            expected_files |= f2
        elif entry["type"] == "file":
            expected_files.add(path)
    return expected_dirs, expected_files


# =============================================================================
# CHECKS
# =============================================================================

def check_root_allowlist(all_dirs, errors):
    root_children = {d.split("/")[0] for d in all_dirs if d}
    unexpected = root_children - ALLOWED_ROOT_DIRS
    missing = ALLOWED_ROOT_DIRS - root_children

    if missing:
        errors.append(f"[ROOT] Missing top-level dirs: {sorted(missing)}")
    if unexpected:
        errors.append(f"[ROOT] Unexpected top-level dirs: {sorted(unexpected)}")


def check_forbidden_dirs(all_dirs, errors):
    for d in all_dirs:
        parts = d.split("/")
        for part in parts:
            if part in FORBIDDEN_DIR_NAMES:
                errors.append(f"[DIR] Forbidden directory name: {d}")
                break


def check_depth_limits(all_dirs, errors):
    for d in all_dirs:
        depth = get_depth(d)
        if depth > MAX_DEPTH:
            errors.append(f"[DEPTH] Directory too deep (> {MAX_DEPTH}): {d}")


def check_hidden_policy(all_dirs, all_files, errors):
    # Hidden dirs
    for d in all_dirs:
        parts = d.split("/")
        for p in parts:
            if p.startswith(".") and p not in ALLOWED_HIDDEN_DIRS:
                errors.append(f"[HIDDEN] Hidden directory not allowed: {d}")
                break

    # Hidden files
    for f in all_files:
        parts = f.split("/")
        fname = parts[-1]
        if fname.startswith(".") and fname not in ALLOWED_HIDDEN_FILES:
            errors.append(f"[HIDDEN] Hidden file not allowed: {f}")


def check_forbidden_and_unknown_extensions(all_files, errors):
    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        # In tests/fixtures or tests/data we may allow extra types
        if f.startswith("tests/fixtures/") or f.startswith("tests/data/"):
            if ext in FORBIDDEN_EXTENSIONS:
                errors.append(f"[EXT] Forbidden extension in fixtures/data: {f}")
            continue

        if ext in FORBIDDEN_EXTENSIONS:
            errors.append(f"[EXT] Forbidden file extension {ext}: {f}")
        elif ext and ext not in ALLOWED_TEXT_EXTS:
            errors.append(f"[EXT] Unknown/unsupported extension {ext}: {f}")


def check_empty_directories(all_dirs, all_files, errors):
    files_by_dir = defaultdict(int)
    for f in all_files:
        d = os.path.dirname(f)
        files_by_dir[d] += 1

    for d in all_dirs:
        if d == "":
            continue
        if files_by_dir[d] == 0:
            # treat directory as non-empty if it has any child dir
            has_child_dir = any(
                child.startswith(d + "/") and child != d for child in all_dirs
            )
            if not has_child_dir:
                errors.append(f"[EMPTY] Directory is empty: {d}")


def check_case_collisions(all_files, errors):
    name_map = defaultdict(list)
    for f in all_files:
        base = os.path.basename(f)
        key = base.lower()
        name_map[key].append(f)
    for key, paths in name_map.items():
        if len(paths) > 1:
            errors.append(f"[CASE] Case-insensitive filename collision: {paths}")


def check_manifest_exact(all_dirs, all_files, errors):
    manifest = load_manifest(MANIFEST_PATH)
    if manifest is None:
        # For strict mode, treat missing manifest as failure
        errors.append(f"[MANIFEST] manifest.yaml missing at {MANIFEST_PATH}")
        return

    expected_dirs, expected_files = flatten_manifest(manifest["root"])

    missing_dirs = expected_dirs - all_dirs
    extra_dirs = all_dirs - expected_dirs
    missing_files = expected_files - all_files
    extra_files = all_files - expected_files

    if missing_dirs:
        errors.append(f"[MANIFEST] Missing directories: {sorted(missing_dirs)}")
    if extra_dirs:
        errors.append(f"[MANIFEST] Unexpected directories: {sorted(extra_dirs)}")
    if missing_files:
        errors.append(f"[MANIFEST] Missing files: {sorted(missing_files)}")
    if extra_files:
        errors.append(f"[MANIFEST] Unexpected files: {sorted(extra_files)}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    all_dirs, all_files = walk_repo(REPO_ROOT)
    errors = []

    check_root_allowlist(all_dirs, errors)
    check_forbidden_dirs(all_dirs, errors)
    check_depth_limits(all_dirs, errors)
    check_hidden_policy(all_dirs, all_files, errors)
    check_forbidden_and_unknown_extensions(all_files, errors)
    check_empty_directories(all_dirs, all_files, errors)
    check_case_collisions(all_files, errors)
    check_manifest_exact(all_dirs, all_files, errors)

    if errors:
        print("\n=== MANIFEST / FS VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Manifest / filesystem validation PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()

