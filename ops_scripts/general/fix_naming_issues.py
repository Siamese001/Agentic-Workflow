"""
Script to fix problematic agent names like pii, ddd, ssot, hop.

Replaces with proper naming: pii_sanitizer, ddd_alignment, ssot_reconciler, hop
"""

import re
from pathlib import Path


def find_files_to_fix() -> list[Path]:
    """Find all Python files that need fixing."""
    patterns = [
        "agentic_core/**/*.py",
        "apps_lic/**/*.py",
        "apps_rg/**/*.py",
        "apps_shared/**/*.py",
        "tests/**/*.py",
        "scripts/**/*.py",
    ]
    files = []
    for pattern in patterns:
        files.extend(Path(".").glob(pattern))
    return files


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
        ("HOP(\\d+)", "HOP\\1"),
        ("hop(\\d+)", "hop\\1"),
    ]


def fix_file_content(content: str) -> str:
    """Apply all replacements to file content."""
    for pattern, replacement in get_replacements():
        content = re.sub(pattern, replacement, content)
    return content


def rename_files_and_directories():
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
    for old_path, new_path in renames:
        old = Path(old_path)
        new = Path(new_path)
        if old.exists() and (not new.exists()):
            print(f"Renaming: {old} -> {new}")
            old.rename(new)


def main():
    """Main function to fix all naming issues."""
    print("Fixing naming issues...")
    print("\n1. Renaming files...")
    rename_files_and_directories()
    print("\n2. Fixing file contents...")
    files = find_files_to_fix()
    fixed_count = 0
    for file_path in files:
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
            fixed_content = fix_file_content(content)
            if content != fixed_content:
                file_path.write_text(fixed_content, encoding="utf-8")
                print(f"Fixed: {file_path}")
                fixed_count += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
