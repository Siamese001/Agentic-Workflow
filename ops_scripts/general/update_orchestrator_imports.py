"""
Phase 1 global search-and-replace for archived legacy orchestrator imports.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from tqdm import tqdm

IMPORT_REPLACEMENTS: dict[str, tuple[str, str]] = {
    "CachedOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "SelfRecoveringOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "IntelligentOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "HardenedWorkflowOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "ConsolidatedOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "OrchestratorAgentAndScopeManagerAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "ScriptsPlanningOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "PilotOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "WorkflowOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "ResumeOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        "CoreOrchestrationAgent",
    ),
    "LicWorkflowOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "OutreachPhase5Orchestrator": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "Phase4OrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "Phase6OrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "Phase7OrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "HOPOrchestratorAgent": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "LicHealingOrchestrator": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "RgHealingOrchestrator": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
    "RgResumeOrchestrator": (
        "agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent",
        "AppWorkflowOrchestratorAgent",
    ),
}

SKIP_PATH_PARTS = {"__pycache__", ".git", ".venv", "venv", "node_modules", "archive", "archives"}


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def find_files_with_imports(root: Path) -> list[Path]:
    """Find all Python files that might have legacy imports."""
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part.lower() in SKIP_PATH_PARTS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def update_imports_in_file(file_path: Path, dry_run: bool = False) -> list[str]:
    """Update legacy imports in a single file."""
    changes: list[str] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return changes

    original_content = content
    for legacy_name, (unified_module, unified_class) in IMPORT_REPLACEMENTS.items():
        pattern = rf"from\s+[\w.]+\s+import\s+{re.escape(legacy_name)}\b"
        if re.search(pattern, content):
            new_import = f"from {unified_module} import {unified_class}"
            content = re.sub(pattern, new_import, content)
            changes.append(f"Updated import: {legacy_name} -> {unified_class}")

        if any(legacy_name in change for change in changes):
            usage_pattern = rf"\b{re.escape(legacy_name)}\b"
            if re.search(usage_pattern, content):
                content = re.sub(usage_pattern, unified_class, content)
                changes.append(f"Updated usage: {legacy_name} -> {unified_class}")

    if content != original_content and not dry_run:
        _atomic_write(file_path, content)
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update legacy orchestrator imports")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args(argv)

    project_root = _resolve_repo_root(args.repo_root)

    print("=" * 70)
    print("Phase 1 Global Search & Replace - Orchestrator Import Updates")
    print("=" * 70)
    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    files = find_files_with_imports(project_root)
    total_changes = 0
    files_modified = 0

    for file_path in tqdm(files, desc="Processing", unit="file"):
        changes = update_imports_in_file(file_path, args.dry_run)
        if not changes:
            continue
        rel_path = file_path.relative_to(project_root)
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
        print("\n✓ ORCHESTRATOR IMPORT UPDATES COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
