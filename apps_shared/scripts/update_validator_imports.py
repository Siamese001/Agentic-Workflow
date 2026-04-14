"""
update_validator_imports.py - Phase 2 Global Search & Replace

Updates all imports of archived legacy validators to use the new unified agents.

Mapping:
- SyntaxValidatorAgent, CanonValidatorAgent, CanonAstValidatorAgent,
  AsyncBlockingValidatorAgent, PrintStatementValidatorAgent
  -> CodeValidatorAgent

- GravityValidatorAgent, HygieneValidatorAgent, HygieneValidatorAgent,
  AgentRegistryValidatorAgent, CognitiveContractValidatorAgent
  -> StructureValidatorAgent

- ContactValidatorAgent, ContentCleanlinessValidatorAgent, MessageDiversityValidator
  -> AppContentValidatorAgent

Usage:
    python scripts/update_validator_imports.py --dry-run
    python scripts/update_validator_imports.py
"""

import argparse
import re
import sys
from pathlib import Path
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
IMPORT_REPLACEMENTS: dict[str, tuple[str, str]] = {
    "SyntaxValidatorAgent": ("agentic_core.L5_safety.unified.CodeValidatorAgent", "CodeValidatorAgent"),
    "CanonValidatorAgent": ("agentic_core.L5_safety.unified.CodeValidatorAgent", "CodeValidatorAgent"),
    "CanonAstValidatorAgent": ("agentic_core.L5_safety.unified.CodeValidatorAgent", "CodeValidatorAgent"),
    "AsyncBlockingValidatorAgent": (
        "agentic_core.L5_safety.unified.CodeValidatorAgent",
        "CodeValidatorAgent",
    ),
    "PrintStatementValidatorAgent": (
        "agentic_core.L5_safety.unified.CodeValidatorAgent",
        "CodeValidatorAgent",
    ),
    "GravityValidatorAgent": (
        "agentic_core.L5_safety.unified.StructureValidatorAgent",
        "StructureValidatorAgent",
    ),
    "HygieneValidatorAgent": (
        "agentic_core.L5_safety.unified.StructureValidatorAgent",
        "StructureValidatorAgent",
    ),
    "AgentRegistryValidatorAgent": (
        "agentic_core.L5_safety.unified.StructureValidatorAgent",
        "StructureValidatorAgent",
    ),
    "CognitiveContractValidatorAgent": (
        "agentic_core.L5_safety.unified.StructureValidatorAgent",
        "StructureValidatorAgent",
    ),
    "ContactValidatorAgent": (
        "apps_lic.shared.validation.AppContentValidatorAgent",
        "AppContentValidatorAgent",
    ),
    "ContentCleanlinessValidatorAgent": (
        "apps_lic.shared.validation.AppContentValidatorAgent",
        "AppContentValidatorAgent",
    ),
    "MessageDiversityValidator": (
        "apps_lic.shared.validation.AppContentValidatorAgent",
        "AppContentValidatorAgent",
    ),
}


def find_files_with_imports(root: Path) -> list[Path]:
    """Find all Python files that might have legacy imports."""
    files = []
    for path in root.rglob("*.py"):
        path_str = str(path).lower()
        if "archive" in path_str:
            continue
        if "unified" in path_str and "test" not in path_str:
            continue
        if "__pycache__" in path_str:
            continue
        files.append(path)
    return files


def update_imports_in_file(file_path: Path, dry_run: bool = False) -> list[str]:
    """Update legacy imports in a single file."""
    changes = []
    try:
        content = file_path.read_text(encoding="utf-8")
    # guardian: allow-silent-swallow
    except Exception:
        return changes
    original_content = content
    for legacy_name, (unified_module, unified_class) in tqdm(
        IMPORT_REPLACEMENTS.items(), desc="Processing", unit="item"
    ):
        pattern1 = f"from\\s+[\\w.]+\\s+import\\s+{legacy_name}\\b"
        if re.search(pattern1, content):
            new_import = f"from {unified_module} import {unified_class}"
            content = re.sub(pattern1, new_import, content)
            changes.append(f"Updated import: {legacy_name} -> {unified_class}")
        pattern2 = f"import\\s+[\\w.]+\\.{legacy_name}\\b"
        if re.search(pattern2, content):
            changes.append(f"Found module import of {legacy_name} (manual update needed)")
        if any(legacy_name in c for c in changes):
            usage_pattern = f"\\b{legacy_name}\\b"
            if re.search(usage_pattern, content):
                content = re.sub(usage_pattern, unified_class, content)
                changes.append(f"Updated usage: {legacy_name} -> {unified_class}")
    if content != original_content and (not dry_run):
        file_path.write_text(content, encoding="utf-8")
    return changes


def main():
    parser = argparse.ArgumentParser(description="Update legacy validator imports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()
    print("=" * 70)
    print("Phase 2 Global Search & Replace - Import Updates")
    print("=" * 70)
    if args.dry_run:
        print("\n[DRY RUN MODE]\n")
    files = find_files_with_imports(PROJECT_ROOT)
    total_changes = 0
    files_modified = 0
    for file_path in files:
        changes = update_imports_in_file(file_path, args.dry_run)
        if changes:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"\n{rel_path}:")
            for change in changes:
                print(f"  - {change}")
            total_changes += len(changes)
            files_modified += 1
    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Files scanned:  {len(files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total changes:  {total_changes}")
    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ IMPORT UPDATES COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
