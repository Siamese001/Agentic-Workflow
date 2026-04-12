"""Clean up corrupted test files - remove stray code outside function bodies."""

import os
import re


def clean_test_file(filepath):
    """Remove stray code blocks from test files."""
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Pattern 1: Remove stray triple-quoted strings at module level after test functions
    # These look like: """Test X runtime behavior.""" followed by # Arrange/# Act blocks
    pattern1 = r'"""Test [^"]+ runtime behavior\."""\s*# Arrange\s*# TODO:[^#]*# Act[^#]*(?:# TODO:[^#]*)*(?:result = None.*?assert.*)?'

    # Pattern 2: Remove stray # Arrange/# Act blocks at module level
    pattern2 = r"\n# Arrange\n# TODO: Set up test data\ninput_data = \{\}[^#]*# Act[^#]*(?:result = None.*?assert.*?)?"

    # Pattern 3: Remove stray runtime_context blocks
    pattern3 = r"\n# Arrange\n# TODO: Set up execution parameters\ninput_data = \{\}[^#]*# Act[^#]*(?:result = None.*?assert.*?)?"

    original = content
    content = re.sub(pattern1, "", content, flags=re.DOTALL)
    content = re.sub(pattern2, "", content, flags=re.DOTALL)
    content = re.sub(pattern3, "", content, flags=re.DOTALL)

    # Pattern 4: Remove multiple consecutive empty lines
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned: {filepath}")
        return True
    return False


# Find and clean all _adg.py test files
count = 0
for root, dirs, files in os.walk(r"tests\unit"):
    for file in files:
        if not file.endswith(".py"):
            continue
        filepath = os.path.join(root, file)
        if clean_test_file(filepath):
            count += 1

print(f"Cleaned {count} files")
