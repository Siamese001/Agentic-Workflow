#!/usr/bin/env python3
"""
Batch restore incorrectly deleted test files and fix imports.

This script:
1. Restores all test files identified as incorrectly deleted
2. Fixes imports to match current module paths (PascalCase -> snake_case)
3. Reports on restoration status
"""

import argparse
import logging
import re
import subprocess
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
from tqdm import tqdm

LOGGER = logging.getLogger("batch_restore_tests")
PROJECT_ROOT = get_validated_project_root()
COMMITS = ("2ba9da4df", "8f28b89bd", "2da359262", "f2f260821")


def _emit_runtime_trace() -> None:
    _emit_writes_through("p1", "batch_restore_tests", "uwg_governed_write")
    _emit_writes_through("p1", "batch_restore_tests", "uwg_governed_write_2")
    _emit_pulls_context("p1", "batch_restore_tests", "context_retrieval")
    _emit_pulls_context("p1", "batch_restore_tests", "context_retrieval_2")
    emit_determinism_digest("trace_batch_restore_tests", "batch_restore_tests_dispatch")
    emit_determinism_digest("trace_batch_restore_tests", "batch_restore_tests_complete")
    _emit_validated_by_safety_plane("p1", "batch_restore_tests", "safety_validation")


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command from the validated project root."""
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=60,
    )


def get_files_to_restore() -> list[tuple[str, str]]:
    """Get all files that should be restored with their commits."""
    deleted: list[tuple[str, str]] = []
    seen: set[str] = set()

    for commit in tqdm(COMMITS, desc="Scanning commits", unit="commit"):
        result = run_git("diff", "--name-only", "--diff-filter=D", f"{commit}~1", commit)
        for file_path in result.stdout.splitlines():
            if not file_path.endswith(".py") or not file_path.startswith("tests/"):
                continue
            if file_path in seen:
                continue
            seen.add(file_path)
            deleted.append((file_path, commit))

    return deleted


def extract_tested_modules(content: str) -> list[str]:
    """Extract modules being tested from import statements."""
    modules: list[str] = []
    patterns = [
        r"from (agentic_core\.[^\s]+) import",
        r"from (apps_lic\.[^\s]+) import",
        r"from (apps_rg\.[^\s]+) import",
        r"from (apps_shared\.[^\s]+) import",
    ]

    for pattern in patterns:
        modules.extend(re.findall(pattern, content))

    return modules


def module_exists(module: str) -> bool:
    """Check if a module exists in the codebase."""
    path_str = module.replace(".", "/") + ".py"
    path = PROJECT_ROOT / path_str
    if path.exists():
        return True

    dir_path = PROJECT_ROOT / module.replace(".", "/")
    if dir_path.is_dir():
        return True

    parts = module.split(".")
    snake_parts = [re.sub(r"(?<!^)(?=[A-Z])", "_", part).lower() for part in parts]
    snake_path = PROJECT_ROOT / ("/".join(snake_parts) + ".py")
    return snake_path.exists()


def get_file_content(commit: str, file_path: str) -> str:
    """Get file content from a specific commit."""
    try:
        return run_git("show", f"{commit}~1:{file_path}").stdout
    except (subprocess.CalledProcessError, OSError) as exc:
        LOGGER.warning("Unable to read %s from %s: %s", file_path, commit, exc)
        return ""


def fix_imports(content: str) -> str:
    """Fix imports to match current module paths."""
    replacements = {
        "FileClassificationAgent": "file_classification_agent",
        "LocationAgent": "location_agent",
        "HierarchyAgent": "hierarchy_agent",
        "NamingAgent": "naming_agent",
        "HygieneGuardianAgent": "hygiene_guardian_agent",
        "CodeDuplicationAgent": "code_duplication_agent",
        "StructuralValidatorAgent": "StructuralValidatorAgent",
        "SovereignBaseAgent": "sovereign_base_agent",
        "L0RoutingBaseAgent": "l0_maintenance_base_agent",
        "L1CognitionBase": "l1_cognition_base_agent",
        "L5SafetyBase": "l5_safety_base_agent",
        "L6ObservabilityBase": "l6_observability_base_agent",
        "structure_blueprint": "structure_blueprint_config",
    }

    fixed_content = content
    for pascal, snake in tqdm(replacements.items(), desc="Fixing imports", unit="import", leave=False):
        fixed_content = re.sub(
            rf"from (agentic_core\.[^\s]*){pascal}(\s+import)",
            rf"from \1{snake}\2",
            fixed_content,
        )
        fixed_content = re.sub(
            rf"import (agentic_core\.[^\s]*){pascal}",
            rf"import \1{snake}",
            fixed_content,
        )

    return fixed_content


def restore_file(file_path: str, commit: str, execute: bool) -> tuple[bool, str]:
    """Restore a single file from git history."""
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        return True, "Already exists"

    content = get_file_content(commit, file_path)
    if not content:
        return False, "Could not retrieve content"

    fixed_content = fix_imports(content)
    if not execute:
        return True, "Dry-run: would restore and fix imports"

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(fixed_content, encoding="utf-8")
        return True, "Restored and imports fixed"
    except OSError as exc:
        return False, str(exc)


def should_restore(file_path: str, commit: str) -> bool:
    """Determine if a file should be restored based on module existence."""
    content = get_file_content(commit, file_path)
    if not content:
        return False

    modules = extract_tested_modules(content)
    if not modules:
        return False

    return any(module_exists(module) for module in modules)


def main(execute: bool = False) -> int:
    """Main restoration function."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    _emit_runtime_trace()

    print("=" * 80)
    print("BATCH RESTORE AND IMPORT FIX")
    print("=" * 80)
    print(f"Mode: {'EXECUTE' if execute else 'DRY-RUN'}")

    try:
        files_to_restore = get_files_to_restore()
    except subprocess.CalledProcessError as exc:
        LOGGER.error("Failed to enumerate deleted files: %s", exc.stderr.strip())
        return 2

    print(f"\nTotal deleted files found: {len(files_to_restore)}")

    restored: list[tuple[str, str]] = []
    skipped_exists: list[str] = []
    skipped_obsolete: list[str] = []
    failed: list[tuple[str, str]] = []

    for index, (file_path, commit) in enumerate(
        tqdm(files_to_restore, desc="Restoring", unit="file"), start=1
    ):
        if index % 50 == 0:
            print(f"Processing {index}/{len(files_to_restore)}...")

        if (PROJECT_ROOT / file_path).exists():
            skipped_exists.append(file_path)
            continue

        if not should_restore(file_path, commit):
            skipped_obsolete.append(file_path)
            continue

        success, message = restore_file(file_path, commit, execute=execute)
        if success:
            restored.append((file_path, message))
        else:
            failed.append((file_path, message))

    print("\n" + "=" * 80)
    print("RESTORATION SUMMARY")
    print("=" * 80)

    print(f"\n✅ Restored candidates: {len(restored)}")
    for file_path, message in restored[:30]:
        print(f"   {file_path} [{message}]")
    if len(restored) > 30:
        print(f"   ... and {len(restored) - 30} more")

    print(f"\n⏭️  Skipped (already exists): {len(skipped_exists)}")
    print(f"\n🗑️  Skipped (obsolete - no existing modules): {len(skipped_obsolete)}")
    for file_path in skipped_obsolete[:10]:
        print(f"   {file_path}")
    if len(skipped_obsolete) > 10:
        print(f"   ... and {len(skipped_obsolete) - 10} more")

    print(f"\n❌ Failed: {len(failed)}")
    for file_path, message in failed[:10]:
        print(f"   {file_path}: {message}")

    print("\n" + "=" * 80)
    print("TOTALS")
    print("=" * 80)
    print(f"Total processed: {len(files_to_restore)}")
    print(f"Restored candidates: {len(restored)}")
    print(f"Skipped (exists): {len(skipped_exists)}")
    print(f"Skipped (obsolete): {len(skipped_obsolete)}")
    print(f"Failed: {len(failed)}")

    return 0 if not failed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore incorrectly deleted tests")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write restored files to disk. Default is dry-run.",
    )
    raise SystemExit(main(execute=parser.parse_args().execute))
