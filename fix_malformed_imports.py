"""Fix malformed import statements with embedded configuration constants."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Pattern to match the malformed import block
MALFORMED_PATTERN = re.compile(
    r'(from\s+[\w.]+\s+import\s+\(\s*\n)'
    r'MAX_RETRIES\s*=\s*3\s*\n'
    r'DEFAULT_SLEEP\s*=\s*[\d.]+\s*\n'
    r'THRESHOLD\s*=\s*[\d.]+\s*\n'
    r'BUFFER_SIZE\s*=\s*\d+\s*\n'
    r'(?:BATCH_SIZE\s*=\s*\d+\s*\n)?'
    r'(?:MAX_DEPTH\s*=\s*\d+\s*\n)?'
    r'(?:MAX_FILES\s*=\s*\d+\s*\n)?'
    r'(?:DEFAULT_TIMEOUT\s*=\s*\d+.*\n)?'
    r'#\s*Configuration constants\s*\n'
    r'\s*\n',
    re.MULTILINE
)

def fix_file(py_file: Path) -> bool:
    """Fix malformed imports in a single file. Returns True if changes made."""
    try:
        content = py_file.read_text(encoding='utf-8')
    except Exception:
        return False

    if 'MAX_RETRIES = 3' not in content:
        return False

    # Replace the malformed pattern with just the import statement start
    new_content = MALFORMED_PATTERN.sub(r'\1', content)

    if new_content != content:
        py_file.write_text(new_content, encoding='utf-8')
        return True

    return False

def main():
    fixed_count = 0

    # Scan all Python files in the repository
    for py_file in ROOT.rglob('*.py'):
        if '.git' in py_file.parts:
            continue

        if fix_file(py_file):
            fixed_count += 1
            print(f"Fixed: {py_file.relative_to(ROOT)}")

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
