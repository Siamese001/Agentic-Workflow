#!/usr/bin/env python3
"""
Aggressive Config Store Cleanup - Remove 570+ repetitive guardian comments.
"""

import re
from pathlib import Path


def aggressive_cleanup(filepath: Path, dry_run: bool = True) -> dict:
    """Remove ALL repetitive guardian comments, keeping max 1 per function."""
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    original_lines = len(content.split('\n'))

    # Pattern for the repetitive guardian comment
    guardian_pattern = r'\s*# guardian: Encoding errors should specify fallback encoding strategy'

    # Split content by function definitions (lines starting with "def " at module level)
    lines = content.split('\n')

    result_lines = []
    in_function = False
    function_guardian_found = False
    indentation_level = 0

    for line in lines:
        # Track if we're entering a new function (0-indented def)
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)

        if stripped.startswith('def ') and current_indent == 0:
            in_function = True
            function_guardian_found = False
            indentation_level = current_indent

        # Check for guardian comment
        if 'guardian: Encoding errors should specify fallback encoding strategy' in line:
            if function_guardian_found:
                # Skip this repetitive comment
                continue
            else:
                function_guardian_found = True
                # Keep this first occurrence but clean up the line
                line = re.sub(r'\s*# guardian: Encoding errors should specify fallback encoding strategy\s*$', '', line)

        result_lines.append(line)

    content = '\n'.join(result_lines)

    # Also remove any remaining isolated guardian lines (not attached to code)
    content = re.sub(r'^\s*# guardian: Encoding errors should specify fallback encoding strategy\s*\n', '\n', content, flags=re.MULTILINE)

    # Clean up excess blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Remove trailing whitespace
    content = re.sub(r' +\n', '\n', content)

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
    filepath = Path('agentic_core/L0_routing/meta_control/config_store.py')

    # Dry run first
    result = aggressive_cleanup(filepath, dry_run=True)

    print(f"Config Store Cleanup (DRY RUN)")
    print(f"Original lines: {result['original_lines']}")
    print(f"Would reduce to: {result['new_lines']}")
    print(f"Lines to remove: {result['lines_removed']}")
    print(f"Reduction: {result['lines_removed']/result['original_lines']*100:.1f}%")

    # Apply
    result = aggressive_cleanup(filepath, dry_run=False)
    print(f"\nApplied! Removed {result['lines_removed']} lines")


if __name__ == '__main__':
    main()
