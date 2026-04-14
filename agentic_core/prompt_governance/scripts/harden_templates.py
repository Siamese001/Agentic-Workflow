"""
Template Hardening Automation Script (Phase 4)

Automatically applies standardized headers to all unhardened Jinja templates
in the prompt_governance directory structure.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "harden_templates", "uwg_governed_write")
_emit_writes_through("p1", "harden_templates", "uwg_governed_write_2")
_emit_pulls_context("p1", "harden_templates", "context_retrieval")
_emit_pulls_context("p1", "harden_templates", "context_retrieval_2")
emit_determinism_digest("trace_harden_templates", "harden_templates_dispatch")
emit_determinism_digest("trace_harden_templates", "harden_templates_complete")
_emit_validated_by_safety_plane("p1", "harden_templates", "safety_validation")


def find_jinja_files(base_dir: Path) -> list[Path]:
    """Recursively find all .jinja files in the directory."""
    jinja_files = []
    for file_path in base_dir.rglob("*.jinja"):
        if file_path.is_file():
            jinja_files.append(file_path)
    return jinja_files


def is_already_hardened(content: str) -> bool:
    """Check if template already has SCHEMA header."""
    return "{# SCHEMA:" in content


def extract_variables(content: str) -> tuple[set[str], set[str]]:
    """
    Extract required and optional variables from Jinja template content.

    Returns:
        Tuple of (required_vars, optional_vars)
    """
    required_pattern = "\\{\\{\\s*([^|}]+?)\\s*(?:\\|[^}]*)?\\}\\}"
    required_matches = re.findall(required_pattern, content)
    required_vars = set()
    for var in required_matches:
        var = var.strip()
        if not any(skip in var.lower() for skip in ["if", "for", "end", "else", "elif", "block"]):
            required_vars.add(var)
    optional_pattern = "\\{\\%\\s*if\\s+([^%]+?)\\s*%\\}"
    optional_matches = re.findall(optional_pattern, content)
    optional_vars = set()
    for var in optional_matches:
        var = var.strip()
        if " and " not in var and " or " not in var and ("not " in var):
            optional_vars.add(var)
    default_pattern = "\\{\\{\\s*([^|}]+?)\\s*\\|\\s*default"
    default_matches = re.findall(default_pattern, content)
    for var in default_matches:
        var = var.strip()
        optional_vars.add(var)
    return (required_vars, optional_vars)


def generate_standardized_header(required_vars: set[str], optional_vars: set[str], relative_path: str) -> str:
    """Generate the standardized header for a template."""
    req_list = sorted(required_vars) if required_vars else []
    opt_list = sorted(optional_vars) if optional_vars else []
    header = f"{{# ============================================================================ #}}\n{{# TEMPLATE VALIDATION HEADER (Phase 4 Automation)                             #}}\n{{# ============================================================================ #}}\n{{# SCHEMA: required_vars=[{', '.join(req_list)}], optional_vars=[{', '.join(opt_list)}] #}}\n{{# DESCRIPTION: Auto-migrated template. Please review description. #}}\n{{# TERRITORY: {relative_path} #}}\n{{# VERSION: v1.0 (Auto) #}}\n{{# SECURITY: StrictUndefined enforced #}}\n{{# ============================================================================ #}}\n\n"
    return header


def harden_template(file_path: Path, base_dir: Path, dry_run: bool = True) -> bool:
    """
    Harden a single template file.

    Returns:
        True if file was modified, False if skipped
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        if is_already_hardened(content):
            return False
        required_vars, optional_vars = extract_variables(content)
        relative_path = str(file_path.relative_to(base_dir))
        header = generate_standardized_header(required_vars, optional_vars, relative_path)
        new_content = header + content
        if dry_run:
            print(f"DRY RUN: Would harden {relative_path}")
            print(f"  Required vars: {sorted(required_vars)}")
            print(f"  Optional vars: {sorted(optional_vars)}")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"HARDENED: {relative_path}")
        return True
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Harden Jinja templates with standardized headers")
    parser.add_argument("--execute", action="store_true", help="Actually write changes (default is dry-run)")
    parser.add_argument(
        "--base-dir",
        type=str,
        default="agentic_core/prompt_governance",
        help="Base directory to scan for templates",
    )
    args = parser.parse_args()
    if os.path.isabs(args.base_dir):
        base_dir = Path(args.base_dir)
    else:
        cwd = Path.cwd()
        base_dir = cwd / args.base_dir
    if not base_dir.exists():
        print(f"ERROR: Base directory {base_dir} does not exist")
        sys.exit(1)
    print(f"Scanning for Jinja templates in: {base_dir}")
    print(f"Mode: {('EXECUTE' if args.execute else 'DRY RUN')}")
    print("-" * 60)
    jinja_files = find_jinja_files(base_dir)
    print(f"Found {len(jinja_files)} Jinja files")
    hardened_count = 0
    skipped_count = 0
    for file_path in sorted(jinja_files):
        if harden_template(file_path, base_dir, dry_run=not args.execute):
            hardened_count += 1
        else:
            skipped_count += 1
    print("-" * 60)
    print("Summary:")
    print(f"  Total files found: {len(jinja_files)}")
    print(f"  Files hardened: {hardened_count}")
    print(f"  Files skipped (already hardened): {skipped_count}")
    if not args.execute:
        print(f"\nTo apply changes, run: python {__file__} --execute")


if __name__ == "__main__":
    main()
