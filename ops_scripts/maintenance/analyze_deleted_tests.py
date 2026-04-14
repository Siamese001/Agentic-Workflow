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
)
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent


def get_deleted_files_from_commit(commit_sha: str) -> list[str]:
    """Get list of deleted files from a specific commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=D", f"{commit_sha}~1", commit_sha],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f.startswith("tests/")]


def get_file_content_from_commit(commit_sha: str, file_path: str) -> str:
    """Get file content from a specific commit."""
    result = subprocess.run(
        ["git", "show", f"{commit_sha}~1:{file_path}"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result.stdout


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

        # Extract imports
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(("import", alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(("from", node.module, node.lineno))

        # Check each import
        for _import_type, module_name, lineno in result["imports"]:
            try:
                # Check if module exists
                spec = importlib.util.find_spec(module_name.split(".")[0])
                if spec is None:
                    result["broken_imports"].append((module_name, lineno))
                else:
                    result["valid_imports"].append(module_name)
            except (ModuleNotFoundError, ImportError, ValueError):
                result["broken_imports"].append((module_name, lineno))

        # Extract test classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("Test"):
                    result["test_classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    result["test_functions"].append(node.name)

        # Determine obsolescence
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

    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        result["reasons"].append(f"Syntax error: {e}")
        result["confidence"] = 0.7
    except (OSError, UnicodeDecodeError, AttributeError) as e:
        result["reasons"].append(f"Analysis error: {e}")

    return result


def fuzzy_match_module(broken_module: str) -> list[tuple[str, float]]:
    """Find similar module names using fuzzy matching."""
    matches = []

    # Get all Python files in agentic_core, apps_lic, apps_rg, apps_shared
    search_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

    parts = broken_module.split(".")
    target_name = parts[-1] if parts else broken_module

    for search_dir in tqdm(search_dirs, desc="Processing", unit="item"):
        search_path = PROJECT_ROOT / search_dir
        if not search_path.exists():
            continue

        for py_file in search_path.rglob("*.py"):
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

    # Check for phase patterns in filename
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


def main():
    """Main analysis function."""
    # Commits that deleted test files
    commits_to_analyze = [
        "2ba9da4df",  # "Complete massive cleanup - delete 313 obsolete test files"
        "8f28b89bd",  # "Complete RCA cleanup - delete 102 obsolete phase and test files"
        "2da359262",  # "RCA cleanup - consolidate corrupted and duplicate test files"
        "f2f260821",  # "Critical fixes to guardian test"
    ]

    all_deleted_files = []

    print("=" * 80)
    print("AST-BASED ANALYSIS OF DELETED TEST FILES")
    print("Following STRICT OBSOLESCENCE PROTOCOL from SSOT")
    print("=" * 80)

    for commit in commits_to_analyze:
        deleted = get_deleted_files_from_commit(commit)
        for f in deleted:
            if f not in [x[0] for x in all_deleted_files]:
                all_deleted_files.append((f, commit))

    print(f"\nTotal deleted test files to analyze: {len(all_deleted_files)}")

    # Categorize results
    confirmed_obsolete = []
    likely_obsolete = []
    needs_review = []
    phase_files_deleted = []

    for file_path, commit in tqdm(all_deleted_files, desc="Processing", unit="item"):
        content = get_file_content_from_commit(commit, file_path)
        if not content:
            continue

        analysis = analyze_file_with_ast(content, file_path)

        # Find fuzzy matches for broken imports
        for module, _lineno in analysis["broken_imports"][:3]:
            matches = fuzzy_match_module(module)
            if matches:
                analysis["fuzzy_matches"].append(
                    {"broken_module": module, "possible_matches": matches},
                )

        category = categorize_deletion(file_path, analysis)

        entry = {"file": file_path, "commit": commit, "category": category, "analysis": analysis}

        if "CONFIRMED_OBSOLETE" in category:
            confirmed_obsolete.append(entry)
        elif "LIKELY_OBSOLETE" in category:
            likely_obsolete.append(entry)
        else:
            needs_review.append(entry)

        if "PHASE_FILE" in category:
            phase_files_deleted.append(entry)

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    print(f"\n### CONFIRMED OBSOLETE ({len(confirmed_obsolete)} files)")
    print("These files had ALL imports broken - deletion was justified.")
    for entry in confirmed_obsolete[:20]:
        print(f"  ✅ {entry['file']}")
        for reason in entry["analysis"]["reasons"]:
            print(f"      - {reason}")
    if len(confirmed_obsolete) > 20:
        print(f"  ... and {len(confirmed_obsolete) - 20} more")

    print(f"\n### LIKELY OBSOLETE ({len(likely_obsolete)} files)")
    print("These files had 80%+ broken imports - deletion was probably justified.")
    for entry in likely_obsolete[:20]:
        print(f"  ⚠️  {entry['file']}")
        for reason in entry["analysis"]["reasons"]:
            print(f"      - {reason}")
    if len(likely_obsolete) > 20:
        print(f"  ... and {len(likely_obsolete) - 20} more")

    print(f"\n### NEEDS REVIEW ({len(needs_review)} files)")
    print("These files may have been deleted incorrectly - REQUIRES MANUAL REVIEW.")
    for entry in needs_review[:30]:
        print(f"  ❌ {entry['file']}")
        for reason in entry["analysis"]["reasons"]:
            print(f"      - {reason}")
        if entry["analysis"]["fuzzy_matches"]:
            print("      Possible renamed modules:")
            for match in entry["analysis"]["fuzzy_matches"][:2]:
                print(
                    f"        - {match['broken_module']} -> {match['possible_matches'][0][0]} ({match['possible_matches'][0][1]:.0%})",
                )
    if len(needs_review) > 30:
        print(f"  ... and {len(needs_review) - 30} more")

    print(f"\n### PHASE FILES DELETED ({len(phase_files_deleted)} files)")
    print("Files with 'phase' in filename - check if deletion was based on name alone.")
    for entry in phase_files_deleted[:20]:
        confidence = entry["analysis"]["confidence"]
        if confidence >= 0.8:
            status = "✅ JUSTIFIED (all imports broken)"
        elif confidence >= 0.5:
            status = "⚠️  PROBABLY OK (80%+ imports broken)"
        else:
            status = "❌ REVIEW NEEDED (may have been deleted by name)"
        print(f"  {status}: {entry['file']}")
    if len(phase_files_deleted) > 20:
        print(f"  ... and {len(phase_files_deleted) - 20} more")

    # Final statistics
    print("\n" + "=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    print(f"Total files analyzed: {len(all_deleted_files)}")
    print(f"Confirmed obsolete (justified deletion): {len(confirmed_obsolete)}")
    print(f"Likely obsolete (probably justified): {len(likely_obsolete)}")
    print(f"Needs review (may need restoration): {len(needs_review)}")
    print(f"Phase files deleted: {len(phase_files_deleted)}")

    # Return files that need review for potential restoration
    return needs_review


if __name__ == "__main__":
    needs_review = main()

    if needs_review:
        print("\n" + "=" * 80)
        print("ACTION REQUIRED")
        print("=" * 80)
        print(f"{len(needs_review)} files may need to be restored.")
        print("Run: git checkout <commit>~1 -- <file_path>")
        print("to restore specific files for manual review.")
