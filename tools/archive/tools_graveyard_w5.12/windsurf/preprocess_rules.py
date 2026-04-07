#!/usr/bin/env python3
"""
Windsurf Rules Preprocessor

Expands ${VAR} variables in .windsurf/rules/*.md files using _variables.yaml as SSOT.

Usage:
    python tools/windsurf/preprocess_rules.py --process
    python tools/windsurf/preprocess_rules.py --validate
    python tools/windsurf/preprocess_rules.py --check [--strict]

Modes:
    --process   Expand variables and write to _build/ directory
    --validate  Check that all ${VAR} references in rules are defined in _variables.yaml
    --check     Verify _build/ is up-to-date with source rules (for CI)
    --strict    (with --check) Fail if any variable is undefined

Exit codes:
    0 - Success / All variables valid / _build is fresh
    1 - Validation failed / Undefined variables found / _build is stale
    2 - Configuration error (missing _variables.yaml, etc.)
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml  # type: ignore

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
VARIABLES_FILE = REPO_ROOT / ".windsurf" / "rules" / "_variables.yaml"
RULES_SRC_DIR = REPO_ROOT / ".windsurf" / "rules"
RULES_OUTPUT_FILE = REPO_ROOT / ".windsurf" / "rules" / ".windsurfrules"

# Variable pattern: ${VAR_NAME}
VAR_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')


class VariableLoader:
    """Loads and flattens variables from _variables.yaml."""

    def __init__(self, variables_file: Path):
        self.variables_file = variables_file
        self.variables: Dict[str, str] = {}
        self.metadata: Dict = {}
        self.validation_rules: Dict = {}

    def load(self) -> Dict[str, str]:
        """Load variables from YAML file and flatten nested structures."""
        if not self.variables_file.exists():
            print(f"ERROR: Variables file not found: {self.variables_file}", file=sys.stderr)
            sys.exit(2)

        with open(self.variables_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            print(f"ERROR: Empty variables file: {self.variables_file}", file=sys.stderr)
            sys.exit(2)

        # Extract metadata
        self.metadata = data.get('metadata', {})
        self.validation_rules = data.get('validation', {})

        # Flatten nested variable categories into single dict
        for category in ['paths', 'patterns', 'enforcement', 'references', 'tiers']:
            if category in data:
                for key, value in data[category].items():
                    if isinstance(value, (list, dict)):
                        # Skip complex structures for now
                        continue
                    self.variables[key] = str(value)

        return self.variables

    def validate_variables(self) -> List[str]:
        """Validate that required variables are present and valid."""
        errors = []

        required = self.validation_rules.get('required_variables', [])
        for var in required:
            if var not in self.variables:
                errors.append(f"Required variable '{var}' is not defined")

        return errors


class ConsolidatedRulesProcessor:
    """Processes all rule files and generates consolidated .windsurfrules."""

    def __init__(self, variables: Dict[str, str], src_dir: Path, output_file: Path):
        self.variables = variables
        self.src_dir = src_dir
        self.output_file = output_file

    def find_rule_files(self) -> List[Path]:
        """Find all .md rule files in source directory, ordered by priority."""
        if not self.src_dir.exists():
            return []

        # Priority order: files with 'plan' or 'location' in name first, then alphabetical
        priority_patterns = ['plan', 'location', 'enforcement', 'discipline']
        rules = []
        for f in self.src_dir.iterdir():
            if f.is_file() and f.suffix == '.md' and not f.name.startswith('_'):
                rules.append(f)

        # Sort by priority then name
        def sort_key(path: Path) -> tuple:
            name = path.name.lower()
            priority = 0
            for i, pattern in enumerate(priority_patterns):
                if pattern in name:
                    priority = i + 1
                    break
            return (-priority, name)  # Negative for descending priority

        return sorted(rules, key=sort_key)

    def extract_variables(self, content: str) -> Set[str]:
        """Extract all ${VAR} references from content."""
        return set(VAR_PATTERN.findall(content))

    def expand_variables(self, content: str, strict: bool = True) -> Tuple[str, List[str]]:
        """
        Expand all ${VAR} patterns in content.

        Returns:
            Tuple of (expanded_content, list_of_undefined_vars)
        """
        undefined = []

        def replace_var(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                undefined.append(var_name)
                if strict:
                    return match.group(0)  # Keep original if strict
                else:
                    return f"[[UNDEFINED:{var_name}]]"

        expanded = VAR_PATTERN.sub(replace_var, content)
        return expanded, undefined

    def process_file(self, src_file: Path, strict: bool = True) -> Tuple[str, List[str]]:
        """Process a single rule file."""
        with open(src_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.expand_variables(content, strict)

    def generate_consolidated(self, strict: bool = True) -> Tuple[str, List[str], int]:
        """
        Generate consolidated .windsurfrules from all modular sources.

        Returns:
            Tuple of (consolidated_content, list_of_undefined_vars, processed_count)
        """
        rule_files = self.find_rule_files()

        if not rule_files:
            return "", ["No rule files found"], 0

        parts = []
        all_undefined = []
        processed_count = 0

        # Add auto-generated header
        header = f"""<!--
AUTO-GENERATED FILE - DO NOT EDIT DIRECTLY
Source: .windsurf/rules/*.md
Generated by: tools/windsurf/preprocess_rules.py
Variables expanded from: .windsurf/rules/_variables.yaml
Timestamp: {Path(__file__).stat().st_mtime if Path(__file__).exists() else 'N/A'}
-->

---

# Agentic Workflow — Sovereign Architecture Rules (Consolidated)

> ⛔ **CONSTITUTIONAL FLOOR — READ FIRST**
> This file is auto-generated from modular rule sources in `.windsurf/rules/*.md`.
> DO NOT EDIT THIS FILE DIRECTLY. Edit the source files and regenerate.

---

"""
        parts.append(header)

        for rule_file in rule_files:
            try:
                content, undefined = self.process_file(rule_file, strict)

                if undefined and strict:
                    all_undefined.extend([f"{rule_file.name}: {u}" for u in undefined])
                    continue

                # Add file separator
                separator = f"\n\n<!-- SOURCE: {rule_file.name} -->\n\n"
                parts.append(separator)
                parts.append(content)
                processed_count += 1

            except Exception as e:  # noqa: BLE001
                all_undefined.append(f"{rule_file.name}: {str(e)}")

        consolidated = "".join(parts)
        return consolidated, all_undefined, processed_count

    def write_consolidated(self, content: str) -> Path:
        """Write consolidated content to output file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return self.output_file


class Validator:
    """Validates that all variables in rules are defined."""

    def __init__(self, variables: Dict[str, str], src_dir: Path):
        self.variables = variables
        self.src_dir = src_dir
        self.processor = ConsolidatedRulesProcessor(variables, src_dir, Path())

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate all rule files.

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        rule_files = self.processor.find_rule_files()

        if not rule_files:
            errors.append(f"No rule files found in {self.src_dir}")
            return False, errors

        all_undefined = set()
        file_undefined: Dict[str, Set[str]] = {}

        for rule_file in rule_files:
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()

            undefined = self.processor.extract_variables(content)
            undefined.discard('')  # Remove empty if any

            # Filter to only those not in our variables
            missing = undefined - set(self.variables.keys())

            if missing:
                file_undefined[rule_file.name] = missing
                all_undefined.update(missing)

        if all_undefined:
            errors.append(f"\nUndefined variables found in {len(file_undefined)} file(s):")
            for fname, missing in sorted(file_undefined.items()):
                errors.append(f"  {fname}: {', '.join(sorted(missing))}")
            errors.append(f"\nTotal undefined: {len(all_undefined)}")
            errors.append(f"Add these to: {VARIABLES_FILE}")
            return False, errors

        return True, [f"✓ All variables valid across {len(rule_files)} rule files"]


def cmd_process(args):
    """Process mode: expand variables and write consolidated .windsurfrules."""
    loader = VariableLoader(VARIABLES_FILE)
    variables = loader.load()

    # Validate variables first
    var_errors = loader.validate_variables()
    if var_errors:
        print("ERROR: Variable validation failed:", file=sys.stderr)
        for err in var_errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    processor = ConsolidatedRulesProcessor(variables, RULES_SRC_DIR, RULES_OUTPUT_FILE)

    content, undefined, processed_count = processor.generate_consolidated(strict=args.strict)

    if undefined and args.strict:
        print("ERROR: Undefined variables found:", file=sys.stderr)
        for u in undefined:
            print(f"  - {u}", file=sys.stderr)
        return 1

    output_file = processor.write_consolidated(content)
    print(f"✓ Generated consolidated rules: {output_file.relative_to(REPO_ROOT)}")
    print(f"✓ Processed {processed_count} rule file(s)")

    if undefined:
        print("\nWarnings (undefined variables, non-strict mode):")
        for u in undefined:
            print(f"  - {u}")

    return 0


def cmd_validate(_args: argparse.Namespace) -> int:
    """Validate mode: check all ${VAR} references are defined."""
    loader = VariableLoader(VARIABLES_FILE)
    variables = loader.load()

    validator = Validator(variables, RULES_SRC_DIR)
    is_valid, messages = validator.validate()

    for msg in messages:
        print(msg)

    return 0 if is_valid else 1


def cmd_check(_args: argparse.Namespace) -> int:
    """Check mode: verify .windsurfrules is up-to-date (for CI)."""
    loader = VariableLoader(VARIABLES_FILE)
    variables = loader.load()

    processor = ConsolidatedRulesProcessor(variables, RULES_SRC_DIR, RULES_OUTPUT_FILE)

    # Generate what the content should be
    expected_content, undefined, _ = processor.generate_consolidated(strict=True)

    # Strip header from expected content (find first <!-- SOURCE: -->)
    source_marker = "<!-- SOURCE:"
    marker_pos = expected_content.find(source_marker)
    if marker_pos != -1:
        expected_content = expected_content[marker_pos:]

    expected_hash = hashlib.md5(expected_content.encode('utf-8')).hexdigest()

    # Read current output file (skipping header if auto-generated)
    if not RULES_OUTPUT_FILE.exists():
        print(f"✗ Missing: {RULES_OUTPUT_FILE.relative_to(REPO_ROOT)}")
        print("  Run: python tools/windsurf/preprocess_rules.py --process")
        return 1

    with open(RULES_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        actual_content = f.read()

    # Remove auto-generated header for comparison (find first <!-- SOURCE: -->)
    source_marker = "<!-- SOURCE:"
    marker_pos = actual_content.find(source_marker)
    if marker_pos != -1:
        # Strip everything before the first source marker
        actual_content = actual_content[marker_pos:]
    elif actual_content.startswith("<!--\nAUTO-GENERATED"):
        # Fallback: strip HTML comment header only
        header_end = actual_content.find("-->")
        if header_end != -1:
            nl_pos = actual_content.find("\n", header_end)
            if nl_pos != -1:
                actual_content = actual_content[nl_pos + 1:].lstrip()

    actual_hash = hashlib.md5(actual_content.encode('utf-8')).hexdigest()

    if expected_hash != actual_hash:
        print(f"✗ Stale: {RULES_OUTPUT_FILE.name} (source changed, rebuild needed)")
        print("  Run: python tools/windsurf/preprocess_rules.py --process")
        return 1
    else:
        print(f"✓ Fresh: {RULES_OUTPUT_FILE.name}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess Windsurf rules - expand variables from _variables.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --process          # Generate consolidated .windsurfrules
  %(prog)s --validate        # Check all ${VAR} references are defined
  %(prog)s --check           # Verify .windsurfrules is up-to-date
  %(prog)s --process --strict  # Fail on undefined variables
        """,
    )

    parser.add_argument(
        '--process',
        action='store_true',
        help='Expand variables and generate consolidated .windsurfrules',
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate that all ${VAR} references are defined in _variables.yaml',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check that .windsurfrules is up-to-date with sources (for CI)',
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail if undefined variables are found',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output',
    )

    args = parser.parse_args()

    if not (args.process or args.validate or args.check):
        parser.print_help()
        return 2

    if args.validate:
        return cmd_validate(args)
    elif args.check:
        return cmd_check(args)
    elif args.process:
        return cmd_process(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
