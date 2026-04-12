"""
Identify and restore test files that were incorrectly deleted.

Following STRICT OBSOLESCENCE PROTOCOL:
- Check if the module being tested still exists
- If module exists, the test should NOT have been deleted
- Restore tests for existing modules
"""

import re
import subprocess
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

PROJECT_ROOT = Path(__file__).parent


def get_deleted_test_files() -> list:
    """Get all deleted test files from recent commits."""
    commits = ["2ba9da4df", "8f28b89bd", "2da359262", "f2f260821"]
    deleted = set()
    for commit in commits:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=D", f"{commit}~1", commit],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        for f in result.stdout.strip().split("\n"):
            if f.endswith(".py") and f.startswith("tests/"):
                deleted.add((f, commit))
    return list(deleted)


def extract_tested_module(content: str) -> list:
    """Extract the module being tested from import statements."""
    modules = []
    patterns = [
        "from (agentic_core\\.[^\\s]+) import",
        "from (apps_lic\\.[^\\s]+) import",
        "from (apps_rg\\.[^\\s]+) import",
        "from (apps_shared\\.[^\\s]+) import",
        "import (agentic_core\\.[^\\s]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        modules.extend(matches)
    return modules


def module_to_path(module: str) -> Path:
    """Convert module path to file path."""
    path_str = module.replace(".", "/") + ".py"
    return PROJECT_ROOT / path_str


def check_module_exists(module: str) -> bool:
    """Check if a module still exists in the codebase."""
    path = module_to_path(module)
    if path.exists():
        return True
    dir_path = PROJECT_ROOT / module.replace(".", "/")
    if dir_path.is_dir():
        return True
    parts = module.split(".")
    snake_parts = []
    for part in parts:
        snake = re.sub("(?<!^)(?=[A-Z])", "_", part).lower()
        snake_parts.append(snake)
    snake_module = ".".join(snake_parts)
    snake_path = module_to_path(snake_module)
    if snake_path.exists():
        return True
    return False


def get_file_content(commit: str, file_path: str) -> str:
    """Get file content from commit."""
    result = subprocess.run(
        ["git", "show", f"{commit}~1:{file_path}"], capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    return result.stdout


def analyze_deleted_files():
    """Analyze deleted files and identify which should be restored."""
    deleted_files = get_deleted_test_files()
    should_restore = []
    correctly_deleted = []
    unclear = []
    print(f"Analyzing {len(deleted_files)} deleted test files...")
    for file_path, commit in deleted_files:
        content = get_file_content(commit, file_path)
        if not content:
            continue
        modules = extract_tested_module(content)
        if not modules:
            unclear.append((file_path, commit, "No clear module imports found"))
            continue
        existing_modules = []
        missing_modules = []
        for module in modules:
            if check_module_exists(module):
                existing_modules.append(module)
            else:
                missing_modules.append(module)
        if existing_modules and (not missing_modules):
            should_restore.append((file_path, commit, existing_modules))
        elif existing_modules and missing_modules:
            unclear.append(
                (file_path, commit, f"Mixed: exists={existing_modules}, missing={missing_modules}")
            )
        else:
            correctly_deleted.append((file_path, commit, missing_modules))
    return (should_restore, correctly_deleted, unclear)


def main():
    should_restore, correctly_deleted, unclear = analyze_deleted_files()
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print(f"\n### SHOULD BE RESTORED ({len(should_restore)} files)")
    print("These tests were for modules that STILL EXIST:")
    for file_path, commit, modules in should_restore[:50]:
        print(f"  ❌ {file_path}")
        print(f"      Tests: {', '.join(modules[:3])}")
    if len(should_restore) > 50:
        print(f"  ... and {len(should_restore) - 50} more")
    print(f"\n### CORRECTLY DELETED ({len(correctly_deleted)} files)")
    print("These tests were for modules that NO LONGER EXIST:")
    for file_path, commit, modules in correctly_deleted[:20]:
        print(f"  ✅ {file_path}")
    if len(correctly_deleted) > 20:
        print(f"  ... and {len(correctly_deleted) - 20} more")
    print(f"\n### UNCLEAR ({len(unclear)} files)")
    print("These need manual review:")
    for file_path, commit, reason in unclear[:20]:
        print(f"  ⚠️  {file_path}")
        print(f"      Reason: {reason}")
    if len(unclear) > 20:
        print(f"  ... and {len(unclear) - 20} more")
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total analyzed: {len(should_restore) + len(correctly_deleted) + len(unclear)}")
    print(f"Should restore: {len(should_restore)}")
    print(f"Correctly deleted: {len(correctly_deleted)}")
    print(f"Needs review: {len(unclear)}")
    if should_restore:
        print("\n" + "=" * 80)
        print("RESTORE COMMANDS")
        print("=" * 80)
        print("Run these commands to restore incorrectly deleted tests:\n")
        by_commit = {}
        for file_path, commit, modules in should_restore:
            if commit not in by_commit:
                by_commit[commit] = []
            by_commit[commit].append(file_path)
        for commit, files in by_commit.items():
            print(f"# From commit {commit}:")
            for f in files[:10]:
                print(f"git checkout {commit}~1 -- {f}")
            if len(files) > 10:
                print(f"# ... and {len(files) - 10} more files")
            print()
    return should_restore


if __name__ == "__main__":
    should_restore = main()
