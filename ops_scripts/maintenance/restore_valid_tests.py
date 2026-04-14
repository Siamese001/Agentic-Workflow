"""
Identify and restore test files that were incorrectly deleted.

Following STRICT OBSOLESCENCE PROTOCOL:
- Check if the module being tested still exists.
- If the module exists, the test should not have been deleted.
- Restore tests for existing modules.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from tqdm import tqdm


PROJECT_ROOT = get_validated_project_root()
COMMITS = ("2ba9da4df", "8f28b89bd", "2da359262", "f2f260821")
PATTERNS = [
    re.compile(r"from\s+(agentic_core\.[^\s]+)\s+import"),
    re.compile(r"from\s+(apps_lic\.[^\s]+)\s+import"),
    re.compile(r"from\s+(apps_rg\.[^\s]+)\s+import"),
    re.compile(r"from\s+(apps_shared\.[^\s]+)\s+import"),
    re.compile(r"import\s+(agentic_core\.[^\s]+)"),
]


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=check,
    )


def get_deleted_test_files() -> list[tuple[str, str]]:
    deleted: set[tuple[str, str]] = set()
    for commit in COMMITS:
        try:
            result = run_git("diff", "--name-only", "--diff-filter=D", f"{commit}~1", commit)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
        for file_path in result.stdout.splitlines():
            if file_path.endswith(".py") and file_path.startswith("tests/"):
                deleted.add((file_path, commit))
    return sorted(deleted)


def extract_tested_modules(content: str) -> list[str]:
    modules: list[str] = []
    for pattern in PATTERNS:
        modules.extend(pattern.findall(content))
    return sorted(set(modules))


def module_to_path(module: str) -> Path:
    return PROJECT_ROOT / (module.replace(".", "/") + ".py")


def check_module_exists(module: str) -> bool:
    direct_path = module_to_path(module)
    if direct_path.exists():
        return True

    package_path = PROJECT_ROOT / module.replace(".", "/")
    if package_path.is_dir():
        return True

    snake_module = ".".join(re.sub(r"(?<!^)(?=[A-Z])", "_", part).lower() for part in module.split("."))
    return module_to_path(snake_module).exists()


def get_file_content(commit: str, file_path: str) -> str:
    try:
        result = run_git("show", f"{commit}~1:{file_path}")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""
    return result.stdout


def restore_file(file_path: str, commit: str, execute: bool) -> tuple[bool, str]:
    content = get_file_content(commit, file_path)
    if not content:
        return False, "No recoverable content found"

    destination = PROJECT_ROOT / file_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not execute:
        return True, "Dry-run: would restore file"

    try:
        destination.write_text(content, encoding="utf-8")
    except OSError as exc:
        return False, str(exc)
    return True, "Restored"


def analyze_deleted_files() -> dict[str, list[tuple[str, str, list[str] | str]]]:
    deleted_files = get_deleted_test_files()
    should_restore: list[tuple[str, str, list[str]]] = []
    correctly_deleted: list[tuple[str, str, list[str]]] = []
    unclear: list[tuple[str, str, str]] = []

    print(f"Analyzing {len(deleted_files)} deleted test files...")
    for file_path, commit in tqdm(deleted_files, desc="Analyzing deleted tests", unit="file"):
        content = get_file_content(commit, file_path)
        if not content:
            unclear.append((file_path, commit, "Unable to recover deleted test content"))
            continue

        modules = extract_tested_modules(content)
        if not modules:
            unclear.append((file_path, commit, "No clear module imports found"))
            continue

        existing_modules = [module for module in modules if check_module_exists(module)]
        missing_modules = [module for module in modules if module not in existing_modules]

        if existing_modules and not missing_modules:
            should_restore.append((file_path, commit, existing_modules))
        elif missing_modules and not existing_modules:
            correctly_deleted.append((file_path, commit, missing_modules))
        else:
            unclear.append(
                (
                    file_path,
                    commit,
                    f"Mixed module state. Existing: {existing_modules}; Missing: {missing_modules}",
                )
            )

    return {
        "should_restore": should_restore,
        "correctly_deleted": correctly_deleted,
        "unclear": unclear,
    }


def main(execute: bool = False) -> int:
    results = analyze_deleted_files()
    print(f"\nShould restore: {len(results['should_restore'])}")
    print(f"Correctly deleted: {len(results['correctly_deleted'])}")
    print(f"Unclear: {len(results['unclear'])}")

    if results["should_restore"]:
        print("\nRestore candidates:")
        for file_path, commit, modules in results["should_restore"]:
            print(f"  - {file_path} (from {commit}; modules={modules})")

    restored = 0
    failed = 0
    for file_path, commit, _modules in results["should_restore"]:
        ok, message = restore_file(file_path, commit, execute=execute)
        status = "RESTORE" if ok else "FAILED"
        print(f"[{status}] {file_path}: {message}")
        if ok:
            restored += 1
        else:
            failed += 1

    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\nRestore complete ({mode}). Success: {restored}, Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore deleted tests whose target modules still exist.")
    parser.add_argument(
        "--execute", action="store_true", help="Write restored test files to disk. Default is dry-run."
    )
    raise SystemExit(main(execute=parser.parse_args().execute))
