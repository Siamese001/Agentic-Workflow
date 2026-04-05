"""Fix missing unittest imports in test files."""
import os

count = 0
for root, dirs, files in os.walk(r'tests\unit'):
    for file in files:
        if not file.endswith('.py') or file == 'conftest.py':
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it has unittest.TestCase but no unittest import
        if 'unittest.TestCase' in content and 'import unittest' not in content:
            # Add unittest import after the docstring or at the top
            if content.startswith('"""'):
                # Find end of docstring
                end_doc = content.find('"""', 3) + 3
                new_content = content[:end_doc] + '\nimport unittest\n' + content[end_doc:]
            else:
                new_content = 'import unittest\n' + content

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Fixed: {filepath}')
            count += 1

print(f'Fixed {count} files')
