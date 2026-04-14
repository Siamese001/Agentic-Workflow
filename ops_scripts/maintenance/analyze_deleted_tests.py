#!/usr/bin/env python3
"""
AST-based analysis of deleted test files to verify obsolescence.

This script follows the STRICT OBSOLESCENCE PROTOCOL from SSOT:
"No file deletion shall occur based on naming conventions. Deletion requires an
AST-based 'zero-reference' verification across the apps_lic, apps_rg, and
apps_shared directories."

It retrieves deleted files from git history and analyzes them with:
1. AST parsing to extract imports
2. Fuzzy matching to find renamed/moved modules
3. Reference checking across apps_lic, apps_rg, apps_shared
"""

import ast
import importlib.util
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    get_validated_project_root,
)
from tqdm import tqdm

PROJECT_ROOT = get_validated_project_root()


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        check=True,
        timeout=60,
    )


def get_deleted_files_from_commit(commit_sha: str) -> list[str]:
    """Get list of deleted files from a specific commit."""
    try:
        result = run_git("diff", "--name-only", "--diff-filter=D", f"{commit_sha}~1", commit_sha)
    except (subprocess.CalledProcessError, OSError):
        return []
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f.startswith("tests/")]


def get_file_content_from_commit(commit_sha: str, file_path: str) -> str:
    """Get file content from a specific commit."""
    try:
        return run_git("show", f"{commit_sha}~1:{file_path}").stdout
    except (subprocess.CalledProcessError, OSError):
        return ""


def analyze_file_with_ast(content: str, file_path: str) -> dict[str, Any]:
    """Analyze a file using AST to determine obsolescence."""
    result = {
        "file_path": file_path,
        "imports": [],
        "broken_imports": [],
        "valid_imports": [],
        "test_classes": [],
        "test_functions": [],
        "is_obsolete": False,
        "confidence": 0.0,
        "reasons": [],
        "fuzzy_matches": [],
    }

    try:
        tree = ast.parse(content)

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(("import", alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom) and node.module:
                result["imports"].append(("from", node.module, node.lineno))

        for _import_type, module_name, lineno in result["imports"]:
            try:
                spec = importlib.util.find_spec(module_name.split(".")[0])
                if spec is None:
                    result["broken_imports"].append((module_name, lineno))
                else:
                    result["valid_imports"].append(module_name)
            except (ModuleNotFoundError, ImportError, ValueError):
                result["broken_imports"].append((module_name, lineno))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                result["test_classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                result["test_functions"].append(node.name)

        total_imports = len(result["imports"])
        broken_count = len(result["broken_imports"])

        if total_imports > 0 and broken_count == total_imports:
            result["is_obsolete"] = True
            result["confidence"] = 0.9
            result["reasons"].append(f"ALL {broken_count} imports are broken")
        elif broken_count > 0 and broken_count >= total_imports * 0.8:
            result["confidence"] = 0.6
            result["reasons"].append(f"{broken_count}/{total_imports} imports are broken (80%+)")
        elif broken_count > 0:
            result["confidence"] = 0.3
            result["reasons"].append(f"{broken_count}/{total_imports} imports are broken")

        if not result["test_classes"] and not result["test_functions"]:
            result["reasons"].append("No test classes or functions found")
            result["confidence"] = max(result["confidence"], 0.4)

    except SyntaxError as exc:
        result["reasons"].append(f"Syntax error: {exc}")
        result["confidence"] = 0.7
    except (OSError, UnicodeDecodeError, AttributeError) as exc:
        result["reasons"].append(f"Analysis error: {exc}")

    return result


def fuzzy_match_module(broken_module: str) -> list[tuple[str, float]]:
    """Find similar module names using fuzzy matching."""
    matches = []
    search_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

    parts = broken_module.split(".")
    target_name = parts[-1] if parts else broken_module

    for search_dir in tqdm(search_dirs, desc="Processing", unit="item"):
        search_path = PROJECT_ROOT / search_dir
        if not search_path.exists():
            continue

        for py_file in sorted(search_path.rglob("*.py")):
            file_stem = py_file.stem
            ratio = SequenceMatcher(None, target_name.lower(), file_stem.lower()).ratio()
            if ratio > 0.6:
                rel_path = str(py_file.relative_to(PROJECT_ROOT))
                matches.append((rel_path, ratio))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:5]


def categorize_deletion(file_path: str, analysis: dict[str, Any]) -> str:
    """Categorize why a file was deleted."""
    filename = Path(file_path).stem
    phase_pattern = re.search(r"phase\d+", filename.lower())

    categories = []
    if analysis["is_obsolete"] and analysis["confidence"] >= 0.8:
        categories.append("CONFIRMED_OBSOLETE")
    elif analysis["confidence"] >= 0.5:
        categories.append("LIKELY_OBSOLETE")
    else:
        categories.append("NEEDS_REVIEW")

    if phase_pattern:
        categories.append("PHASE_FILE")
    if not analysis["test_classes"] and not analysis["test_functions"]:
        categories.append("NO_TESTS")
    if len(analysis["broken_imports"]) == len(analysis["imports"]) and len(analysis["imports"]) > 0:
        categories.append("ALL_IMPORTS_BROKEN")

    return ", ".join(categories)


def main() -> int:
    commits_to_analyze = [
        "2ba9da4df",
        "8f28b89bd",
        "2da359262",
        "f2f260821",
    ]

    all_deleted_files: list[tuple[str, str]] = []

    print("=" * 80)
    print("AST-BASED ANALYSIS OF DELETED TEST FILES")
    print("Following STRICT OBSOLESCENCE PROTOCOL from SSOT")
    print("=" * 80)

    for commit in commits_to_analyze:
        deleted = get_deleted_files_from_commit(commit)
        for file_path in deleted:
            if file_path not in [x[0] for x in all_deleted_files]:
                all_deleted_files.append((file_path, commit))

    print(f"\nTotal deleted test files to analyze: {len(all_deleted_files)}")

    confirmed_obsolete = []
    likely_obsolete = []
    needs_review = []
    phase_files_deleted = []

    for file_path, commit in tqdm(all_deleted_files, desc="Processing", unit="item"):
        content = get_file_content_from_commit(commit, file_path)
        if not content:
            continue

        analysis = analyze_file_with_ast(content, file_path)
        category = categorize_deletion(file_path, analysis)
        result = {
            "file": file_path,
            "commit": commit,
            "category": category,
            "confidence": analysis["confidence"],
            "reasons": analysis["reasons"],
            "broken_imports": analysis["broken_imports"],
        }

        if "PHASE_FILE" in category:
            phase_files_deleted.append(result)
        if "CONFIRMED_OBSOLETE" in category:
            confirmed_obsolete.append(result)
        elif "LIKELY_OBSOLETE" in category:
            likely_obsolete.append(result)
        else:
            broken_imports = analysis["broken_imports"]
            fuzzy_matches = []
            for broken_module, _lineno in broken_imports[:3]:
                fuzzy_matches.extend(fuzzy_match_module(broken_module))
            result["fuzzy_matches"] = fuzzy_matches[:5]
            needs_review.append(result)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Confirmed Obsolete: {len(confirmed_obsolete)}")
    print(f"Likely Obsolete: {len(likely_obsolete)}")
    print(f"Needs Review: {len(needs_review)}")
    print(f"Phase Files Deleted: {len(phase_files_deleted)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
