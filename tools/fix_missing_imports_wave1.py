"""Batch fix missing lifecycle_trace_contract imports - Wave 1.

Adds missing imports:
- _emit_observes_runtime_state
- _emit_escalates_to_human
- _emit_transcripts_response
- _emit_signs_execution_trace
"""

import os
import re

TARGET_FUNCS = [
    '_emit_observes_runtime_state',
    '_emit_escalates_to_human',
    '_emit_transcripts_response',
    '_emit_signs_execution_trace',
]

IMPORT_PATTERN = re.compile(
    r'from\s+agentic_core\.L_CONTRACTS\.lifecycle_trace_contract\s+import\s*\(([^)]+)\)',
    re.DOTALL
)


def find_missing_imports(filepath):
    """Find which target functions are used but not imported."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []

    # Check if it imports from lifecycle_trace_contract
    match = IMPORT_PATTERN.search(content)
    if not match:
        return []

    import_block = match.group(1)
    used_funcs = []

    for func in TARGET_FUNCS:
        # Check if function is called in the file
        if func + '(' in content or func + ' (' in content:
            # Check if it's in the import block
            if func not in import_block:
                used_funcs.append(func)

    return used_funcs


def fix_file(filepath, missing_funcs):
    """Add missing imports to file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = IMPORT_PATTERN.search(content)
    if not match:
        return False

    old_import = match.group(0)
    import_items = [item.strip() for item in match.group(1).split(',') if item.strip()]

    # Add missing functions in alphabetical order
    for func in missing_funcs:
        if func not in import_items:
            import_items.append(func)

    # Sort and format
    import_items.sort()
    new_import_inner = ',\n'.join(f'    {item}' for item in import_items)
    new_import = f'from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (\n{new_import_inner}\n)'

    # Replace in content
    new_content = content.replace(old_import, new_import)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    root = 'agentic_core'
    fixed_count = 0
    error_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            filepath = os.path.join(dirpath, filename)

            missing = find_missing_imports(filepath)
            if missing:
                try:
                    if fix_file(filepath, missing):
                        fixed_count += 1
                        print(f'Fixed: {filepath} ({len(missing)} imports)')
                except Exception as e:
                    error_count += 1
                    print(f'Error fixing {filepath}: {e}')

    print(f'\nWave 1 Complete: {fixed_count} files fixed, {error_count} errors')


if __name__ == '__main__':
    main()
