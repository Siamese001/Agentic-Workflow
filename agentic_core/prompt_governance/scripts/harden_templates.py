#!/usr/bin/env python3
"""
Template Hardening Automation Script (Phase 4)

Automatically applies standardized headers to all unhardened Jinja templates
in the prompt_governance directory structure.
"""

import os
import re
import sys
import argparse
from pathlib import Path


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
    # Find all {{ variable }} patterns
    required_pattern = r"\{\{\s*([^|}]+?)\s*(?:\|[^}]*)?\}\}"
    required_matches = re.findall(required_pattern, content)
    required_vars = set()

    for var in required_matches:
        # Clean up variable name
        var = var.strip()
        # Skip common non-variable patterns
        if not any(skip in var.lower() for skip in ["if", "for", "end", "else", "elif", "block"]):
            required_vars.add(var)

    # Find {% if variable %} patterns for optional variables
    optional_pattern = r"\{\%\s*if\s+([^%]+?)\s*%\}"
    optional_matches = re.findall(optional_pattern, content)
    optional_vars = set()

    for var in optional_matches:
        var = var.strip()
        # Skip complex conditions
        if " and " not in var and " or " not in var and "not " in var:
            optional_vars.add(var)

    # Find variables with | default filter
    default_pattern = r"\{\{\s*([^|}]+?)\s*\|\s*default"
    default_matches = re.findall(default_pattern, content)
    for var in default_matches:
        var = var.strip()
        optional_vars.add(var)

    return required_vars, optional_vars


def generate_standardized_header(
    required_vars: set[str], optional_vars: set[str], relative_path: str
) -> str:
    """Generate the standardized header for a template."""
    req_list = sorted(list(required_vars)) if required_vars else []
    opt_list = sorted(list(optional_vars)) if optional_vars else []

    header = f"""{{# ============================================================================ #}}
{{# TEMPLATE VALIDATION HEADER (Phase 4 Automation)                             #}}
{{# ============================================================================ #}}
{{# SCHEMA: required_vars=[{", ".join(req_list)}], optional_vars=[{", ".join(opt_list)}] #}}
{{# DESCRIPTION: Auto-migrated template. Please review description. #}}
{{# TERRITORY: {relative_path} #}}
{{# VERSION: v1.0 (Auto) #}}
{{# SECURITY: StrictUndefined enforced #}}
{{# ============================================================================ #}}

"""

    return header


def harden_template(file_path: Path, base_dir: Path, dry_run: bool = True) -> bool:
    """
    Harden a single template file.

    Returns:
        True if file was modified, False if skipped
    """
    try:
        # Read current content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Skip if already hardened
        if is_already_hardened(content):
            return False

        # Extract variables
        required_vars, optional_vars = extract_variables(content)

        # Generate relative path for territory
        relative_path = str(file_path.relative_to(base_dir))

        # Generate header
        header = generate_standardized_header(required_vars, optional_vars, relative_path)

        # New content with header
        new_content = header + content

        # Write or preview
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
    parser.add_argument(
        "--execute", action="store_true", help="Actually write changes (default is dry-run)"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="agentic_core/prompt_governance",
        help="Base directory to scan for templates",
    )

    args = parser.parse_args()

    # Determine base directory
    if os.path.isabs(args.base_dir):
        base_dir = Path(args.base_dir)
    else:
        # Assume relative to current working directory
        cwd = Path.cwd()
        base_dir = cwd / args.base_dir

    if not base_dir.exists():
        print(f"ERROR: Base directory {base_dir} does not exist")
        sys.exit(1)

    print(f"Scanning for Jinja templates in: {base_dir}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print("-" * 60)

    # Find all Jinja files
    jinja_files = find_jinja_files(base_dir)
    print(f"Found {len(jinja_files)} Jinja files")

    # Process files
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
