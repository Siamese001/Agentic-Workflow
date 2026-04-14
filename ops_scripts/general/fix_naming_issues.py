"""
Normalize selected naming inconsistencies like pii, ddd, ssot, and hop.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from tqdm import tqdm

SEARCH_PATTERNS = [
    "agentic_core/**/*.py",
    "apps_lic/**/*.py",
    "apps_rg/**/*.py",
    "apps_shared/**/*.py",
    "tests/**/*.py",
    "scripts/**/*.py",
]


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


def find_files_to_fix(repo_root: Path) -> list[Path]:
    """Find all Python files that need scanning."""
    files: set[Path] = set()
    for pattern in SEARCH_PATTERNS:
        files.update(repo_root.glob(pattern))
    return sorted(files)


def get_replacements() -> list[tuple[str, str]]:
    """Get all replacement patterns."""
    return [
        ("PII_Sanitizer", "PII_Sanitizer"),
        ("pii", "pii"),
        ("PII", "PII"),
        ("pii_sanitizer", "pii_sanitizer"),
        ("PII_Sanitizer", "PII_Sanitizer"),
        ("DDD_Alignment", "DDD_Alignment"),
        ("DDDAlignmentAgent", "DDDAlignmentAgent"),
        ("ddd", "ddd"),
        ("DDD", "DDD"),
        ("ddd_alignment", "ddd_alignment"),
        ("DDD_Alignment", "DDD_Alignment"),
        ("FilesystemSSOTReconcilerAgent", "FilesystemSSOTReconcilerAgent"),
        ("SSOTReconcilerAgent", "SSOTReconcilerAgent"),
        ("ssot", "ssot"),
        ("SSOT", "SSOT"),
        ("filesystem_ssot", "filesystem_ssot"),
        ("Filesystem_SSOT", "Filesystem_SSOT"),
        ("hop", "hop"),
        ("HOP", "HOP"),
        (r"HOP(\d+)", r"HOP\1"),
        (r"hop(\d+)", r"hop\1"),
    ]


def fix_file_content(content: str) -> str:
    """Apply all replacements to file content."""
    for pattern, replacement in get_replacements():
        content = re.sub(pattern, replacement, content)
    return content


def rename_files_and_directories(repo_root: Path, execute: bool) -> int:
    """Rename files and directories with problematic names."""
    renames = [
        (
            "tests/unit/agentic_core/L5_safety/validators/test_ddd_alignment_agent.py",
            "tests/unit/agentic_core/L5_safety/validators/test_ddd_alignment_agent.py",
        ),
        (
            "tests/unit/agentic_core/L5_safety/validators/test_filesystem_ssot_reconciler_agent.py",
            "tests/unit/agentic_core/L5_safety/validators/test_filesystem_ssot_reconciler_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop1_profile_analysis_agent.py",
            "tests/unit/apps_lic/engines/test_hop1_profile_analysis_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop2_research_agent.py",
            "tests/unit/apps_lic/engines/test_hop2_research_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop3_sender_grounding_agent.py",
            "tests/unit/apps_lic/engines/test_hop3_sender_grounding_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop4_routing_agent.py",
            "tests/unit/apps_lic/engines/test_hop4_routing_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop5_generation_agent.py",
            "tests/unit/apps_lic/engines/test_hop5_generation_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop6_validation_agent.py",
            "tests/unit/apps_lic/engines/test_hop6_validation_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop7_gate_decision_agent.py",
            "tests/unit/apps_lic/engines/test_hop7_gate_decision_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop8_q_a_report_agent.py",
            "tests/unit/apps_lic/engines/test_hop8_qa_report_agent.py",
        ),
        (
            "tests/unit/apps_lic/engines/test_hop9_integration_agent.py",
            "tests/unit/apps_lic/engines/test_hop9_integration_agent.py",
        ),
    ]

    rename_count = 0
    for old_path, new_path in renames:
        old = (repo_root / old_path).resolve()
        new = (repo_root / new_path).resolve()
        if old == new:
            continue
        if old.exists() and not new.exists():
            print(f"{'Renaming' if execute else 'Would rename'}: {old} -> {new}")
            if execute:
                new.parent.mkdir(parents=True, exist_ok=True)
                old.rename(new)
            rename_count += 1
    return rename_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fix selected naming inconsistencies across the repository.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--execute", action="store_true", help="Actually write changes. Default is dry-run.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)

    print("Fixing naming issues...")
    if not args.execute:
        print("[DRY RUN] No files will be modified.\n")

    print("\n1. Renaming files...")
    rename_count = rename_files_and_directories(repo_root, execute=args.execute)

    print("\n2. Fixing file contents...")
    files = find_files_to_fix(repo_root)
    fixed_count = 0
    for file_path in tqdm(files, desc="Processing", unit="file"):
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            fixed_content = fix_file_content(content)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Error fixing {file_path}: {exc}")
            continue

        if content != fixed_content:
            if args.execute:
                _atomic_write(file_path, fixed_content)
            print(f"{'Fixed' if args.execute else 'Would fix'}: {file_path}")
            fixed_count += 1

    print(f"\nRenames: {rename_count}")
    print(f"Content updates: {fixed_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
