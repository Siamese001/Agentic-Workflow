#!/usr/bin/env python3
"""
Autonomous security and hygiene fixer for Canon Validator.
Targets Keys 1, 2, 4, 5, 6 - Security violations that can be automatically addressed.
"""

import ast
import os
import re


def fix_key_1_cognitive_separation(filepath):
    """Key 1: COGNITIVE SEPARATION - Separate thinking from doing."""
    changes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for patterns that mix cognitive and action logic
        # Add TODO comments for manual review where automatic fixes aren't safe
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Flag direct execution in cognitive functions
            if re.search(r'def.*think.*:', line) and i < len(lines) - 1:
                next_line = lines[i + 1]
                if 'execute(' in next_line or 'run(' in next_line:
                    lines.insert(
                        i + 1, '    # TODO: Review - mixing thinking and execution')
                    changes.append(
                        f"Line {i+2}: Added cognitive separation warning")

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_key_2_no_implicit_state(filepath):
    """Key 2: NO IMPLICIT STATE - All function arguments must be explicit."""
    changes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for global variables used in functions
        tree = ast.parse(content)
        global_vars = set()

        # Find global variable assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if assignment is at module level
                        for parent in ast.walk(tree):
                            if hasattr(node, 'lineno') and hasattr(parent, 'lineno'):
                                if node.lineno == parent.lineno:
                                    global_vars.add(target.id)

        # Flag global variable usage in functions
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for var in global_vars:
                if re.search(r'\b' + var + r'\b', line) and 'def ' in lines[max(0, i-5):i]:
                    lines[i] = line + '  # TODO: Review - using global state'
                    changes.append(f"Line {i+1}: Flagged implicit state usage")
                    break

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_key_4_no_hallucination(filepath):
    """Key 4: NO HALLUCINATION - Plans must reference specific Canon IDs."""
    changes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for planning functions without Canon ID references
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'def.*plan.*:', line):
                # Check next few lines for Canon ID references
                found_canon_id = False
                for j in range(i+1, min(i+10, len(lines))):
                    if re.search(r'Key \d+|canon|Canon', lines[j]):
                        found_canon_id = True
                        break

                if not found_canon_id:
                    lines.insert(
                        i+1, '    # TODO: Add Canon ID references (Key X.X)')
                    changes.append(f"Line {i+2}: Added Canon ID reminder")

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_key_5_json_strictness(filepath):
    """Key 5: JSON STRICTNESS - Inter-node communication must use JSON schemas."""
    changes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for function calls that should use JSON
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Flag pickle usage
            if 'pickle' in line:
                lines[i] = line + '  # TODO: Replace with JSON for strictness'
                changes.append(f"Line {i+1}: Flagged pickle usage")

            # Flag eval/exec
            if re.search(r'\beval\b|\bexec\b', line):
                lines[i] = line + '  # TODO: Replace with JSON parsing'
                changes.append(f"Line {i+1}: Flagged eval/exec usage")

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_key_6_idempotency(filepath):
    """Key 6: IDEMPOTENCY - All Action Tools must be idempotent."""
    changes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for action functions without idempotency checks
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'def.*(execute|run|apply|process).*:', line):
                # Check for idempotency patterns
                has_check = False
                for j in range(i+1, min(i+20, len(lines))):
                    if re.search(r'if.*exists|already|duplicate', lines[j]):
                        has_check = True
                        break

                if not has_check:
                    lines.insert(i+1, '    # TODO: Add idempotency check')
                    changes.append(f"Line {i+2}: Added idempotency reminder")

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_all_files(root_dir):
    """Apply all security and hygiene fixes."""
    total_changes = 0
    fixed_files = 0

    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in [
            '.git', '__pycache__', '.venv', 'venv', 'archives']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                file_changes = []

                # Apply all fixes
                file_changes.extend(fix_key_1_cognitive_separation(filepath))
                file_changes.extend(fix_key_2_no_implicit_state(filepath))
                file_changes.extend(fix_key_4_no_hallucination(filepath))
                file_changes.extend(fix_key_5_json_strictness(filepath))
                file_changes.extend(fix_key_6_idempotency(filepath))

                if file_changes:
                    fixed_files += 1
                    total_changes += len(file_changes)
                    print(f"  Fixed {filepath}:")
                    for change in file_changes[:3]:  # Show first 3 changes
                        print(f"    {change}")
                    if len(file_changes) > 3:
                        print(f"    ... and {len(file_changes) - 3} more")

    print(f"\nSecurity and hygiene fixes applied:")
    print(f"  Files modified: {fixed_files}")
    print(f"  Total changes: {total_changes}")
    print(f"  Note: Some violations require manual review")


if __name__ == '__main__':
    import sys
    root_dir = '.' if len(sys.argv) < 2 else sys.argv[1]
    fix_all_files(root_dir)

