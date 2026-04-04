#!/usr/bin/env python3
"""
Simplify config_store.py - Remove repetitive guardian comments and dead code.

Usage:
    python tools/simplify_config_store.py --check   # Dry run
    python tools/simplify_config_store.py --apply   # Apply changes
"""

import argparse
import re
from pathlib import Path


def simplify_file(filepath: Path, dry_run: bool = True) -> dict:
    """Simplify config_store.py by removing repetitive guardian comments."""
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    original_lines = len(content.split('\n'))

    # Remove repetitive guardian: Encoding errors comments (keep max 1 per function)
    # Pattern: # guardian: Encoding errors should specify fallback encoding strategy
    encoding_guardian_pattern = r'# guardian: Encoding errors should specify fallback encoding strategy'

    # Split by function boundaries (lines starting with "def " or "class ")
    sections = []
    current_section = []
    lines = content.split('\n')

    for line in lines:
        if line.startswith('def ') or line.startswith('class ') or line.startswith('# ==='):
            if current_section:
                sections.append(current_section)
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        sections.append(current_section)

    # Process each section - keep only 1 guardian comment per section
    cleaned_sections = []
    for section in sections:
        guardian_count = 0
        cleaned_section = []
        for line in section:
            if re.search(encoding_guardian_pattern, line):
                guardian_count += 1
                if guardian_count == 1:
                    cleaned_section.append(line)
                # Skip subsequent guardian comments
            else:
                cleaned_section.append(line)
        cleaned_sections.append(cleaned_section)

    # Rebuild content
    new_lines = []
    for section in cleaned_sections:
        new_lines.extend(section)

    content = '\n'.join(new_lines)

    # Clean up excess blank lines (more than 2 consecutive)
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    new_line_count = len(content.split('\n'))
    lines_removed = original_lines - new_line_count

    result = {
        'file': str(filepath),
        'original_lines': original_lines,
        'new_lines': new_line_count,
        'lines_removed': lines_removed,
        'changed': content != original_content,
    }

    if not dry_run and result['changed']:
        filepath.write_text(content, encoding='utf-8')

    return result


def main():
    parser = argparse.ArgumentParser(description='Simplify config_store.py')
    parser.add_argument('--check', action='store_true', help='Dry run')
    parser.add_argument('--apply', action='store_true', help='Apply changes')

    args = parser.parse_args()

    if not args.check and not args.apply:
        args.check = True  # Default to dry run

    dry_run = not args.apply

    filepath = Path('agentic_core/L0_routing/meta_control/config_store.py')
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return

    result = simplify_file(filepath, dry_run)

    print(f"\n{'='*60}")
    print(f"Config Store Simplification ({'DRY RUN' if dry_run else 'APPLIED'})")
    print(f"{'='*60}")
    print(f"File: {result['file']}")
    print(f"Original lines: {result['original_lines']}")
    print(f"New lines: {result['new_lines']}")
    print(f"Lines removed: {result['lines_removed']}")
    print(f"Size reduction: {result['lines_removed']/result['original_lines']*100:.1f}%")
    print(f"Changed: {result['changed']}")


if __name__ == '__main__':
    main()
