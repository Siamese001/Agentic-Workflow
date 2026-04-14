"""
Apply heuristic filtering to pascal_case_audit_log.txt, queue safe renames, and update imports.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
from tqdm import tqdm

_emit_writes_through("p1", "remediate_naming_audit", "uwg_governed_write")
_emit_writes_through("p1", "remediate_naming_audit", "uwg_governed_write_2")
_emit_pulls_context("p1", "remediate_naming_audit", "context_retrieval")
_emit_pulls_context("p1", "remediate_naming_audit", "context_retrieval_2")
emit_determinism_digest("trace_remediate_naming_audit", "remediate_naming_audit_dispatch")
emit_determinism_digest("trace_remediate_naming_audit", "remediate_naming_audit_complete")
_emit_validated_by_safety_plane("p1", "remediate_naming_audit", "safety_validation")

VERB_PATTERN = re.compile(
    r"^(Fix|Run|Test|Analyze|Update|Manage|Utilities|Check|Archive|Restore|Generate|Fetch|Find|Load|Perform|"
    r"Query|Refactor|Verify|Convert|Calculate|Execute|Invoke|Measure|Monitor|Parse|Process|Register|Resolve|"
    r"Validate|Watch|Write)(?=[A-Z])"
)
PROTECTED_SUFFIXES = (
    "Agent.py",
    "Orchestrator.py",
    "Validator.py",
    "Factory.py",
    "Registry.py",
    "Engine.py",
    "Model.py",
    "schema.py",
    "Config.py",
    "Exception.py",
    "Error.py",
    "Client.py",
    "Service.py",
    "Manager.py",
)
DEFAULT_AUDIT_LOG = "pascal_case_audit_log.txt"
DEFAULT_SKIPPED_LOG = "remediation_skipped.log"


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
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    stage_one = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stage_one).lower()


def get_files_from_log(root_dir: Path, audit_log: Path) -> list[Path]:
    if not audit_log.exists():
        raise FileNotFoundError(f"Audit log not found at {audit_log}")

    lines = [line.strip() for line in audit_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    files: list[Path] = []

    for line in tqdm(lines, desc="Processing", unit="line"):
        clean_path = line.split("]", 1)[-1].strip() if "]" in line else line
        candidate = (root_dir / clean_path.replace("\\", "/")).resolve()
        if candidate.exists():
            files.append(candidate)
    return files


def update_imports(root_dir: Path, renames: list[tuple[Path, Path]], execute: bool) -> int:
    """Scan codebase to update imports for renamed files."""
    print("\n[Phase 2] Updating Imports (Safe Regex)...")
    rename_map = {old_path.stem: new_path.stem for old_path, new_path in renames}
    count = 0

    for root, dirs, files in tqdm(os.walk(root_dir), desc="Processing", unit="dir"):
        dirs[:] = [directory for directory in dirs if directory not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            file_path = Path(root) / file_name
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue

            original_content = content
            for old, new in rename_map.items():
                if old in content:
                    content = re.sub(rf"\b{re.escape(old)}\b", new, content)

            if content != original_content:
                if execute:
                    _atomic_write(file_path, content)
                count += 1

    print(f"  {'Modified' if execute else 'Would modify'} {count} files with import updates.")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply safe naming remediations from pascal_case_audit_log.txt.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--audit-log", help="Path to the pascal_case audit log.")
    parser.add_argument(
        "--execute", action="store_true", help="Actually run git mv and file writes. Default is dry-run."
    )
    args = parser.parse_args(argv)

    root_dir = _resolve_repo_root(args.repo_root)
    audit_log = (
        Path(args.audit_log).expanduser().resolve() if args.audit_log else root_dir / DEFAULT_AUDIT_LOG
    )
    skipped_log = root_dir / DEFAULT_SKIPPED_LOG

    print(f"[*] Starting remediation based on {audit_log.name}")
    if not args.execute:
        print("[DRY RUN] No files will be modified.\n")

    try:
        targets = get_files_from_log(root_dir, audit_log)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(f"[*] Loaded {len(targets)} verified existing files.")
    rename_queue: list[tuple[Path, Path]] = []
    skipped: list[tuple[str, str]] = []

    for file_path in tqdm(targets, desc="Processing", unit="file"):
        name = file_path.name
        stem = file_path.stem

        if name.endswith(PROTECTED_SUFFIXES):
            skipped.append((name, "Protected suffix"))
            continue

        if VERB_PATTERN.match(stem):
            new_path = file_path.with_name(to_snake_case(stem) + ".py")
            rename_queue.append((file_path, new_path))
            continue

        skipped.append((name, "No safe rename pattern match"))

    print(f"\n[Analysis] Renaming {len(rename_queue)} files. Skipping {len(skipped)}.")
    if not rename_queue:
        print("No safe renames found.")
        _atomic_write(skipped_log, "\n".join(f"{name}: {reason}" for name, reason in skipped) + "\n")
        return 0

    print("\n[Phase 1] Executing Git Moves...")
    success_count = 0
    successful_renames: list[tuple[Path, Path]] = []

    for old_path, new_path in tqdm(rename_queue, desc="Processing", unit="rename"):
        if new_path.exists():
            print(f"  [SKIP] Target exists: {new_path.name}")
            continue

        if args.execute:
            result = subprocess.run(
                ["git", "mv", str(old_path), str(new_path)],
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(f"  [ERROR] Git mv failed for {old_path.name}: {result.stderr.strip()}")
                continue
            print(f"  [OK-GIT] {old_path.name} -> {new_path.name}")
        else:
            print(f"  [DRY-RUN] {old_path.name} -> {new_path.name}")

        success_count += 1
        successful_renames.append((old_path, new_path))

    if successful_renames:
        update_imports(root_dir, successful_renames, execute=args.execute)

    _atomic_write(skipped_log, "\n".join(f"{name}: {reason}" for name, reason in skipped) + "\n")
    print("\n[*] Skipped log written.")
    print(f"[*] Successful rename operations: {success_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
