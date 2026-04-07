"""Fix remaining __init___adg.py files with dangling placeholder code."""
import os

files_to_fix = [
    'tests/unit/agentic_core/L0_routing/engines/test___init___adg.py',
    'tests/unit/agentic_core/L0_routing/meta_control/test___init___adg.py',
    'tests/unit/agentic_core/L0_routing/reasoning/test___init___adg.py',
    'tests/unit/agentic_core/L0_routing/scripts/test_coverage_adg.py',
    'tests/unit/agentic_core/L0_routing/scripts/test_drift_adg.py',
    'tests/unit/agentic_core/L0_routing/utils/test___init___adg.py',
]

# Read the fixed file as template
with open('tests/unit/agentic_core/L0_routing/scripts/test___init___adg.py', 'r', encoding='utf-8') as f:
    template = f.read()

fixed = 0
for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f'Not found: {filepath}')
        continue

    # Get the module path from the file location
    parts = filepath.replace('tests/unit/', '').replace('/', '.').replace('\\', '.').replace('.py', '').split('.')
    module_path = '.'.join(parts[:-1])  # Remove 'test___init___adg' or 'test_coverage_adg'

    # Create new content with correct module path
    new_content = template.replace(
        'agentic_core.L0_routing.scripts.__init__',
        module_path,
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Fixed: {os.path.basename(filepath)}')
    fixed += 1

print(f'\nTotal fixed: {fixed}')
