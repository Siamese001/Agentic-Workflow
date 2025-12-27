"""Identify all test files with syntax errors."""
import py_compile
import sys
from pathlib import Path

def check_syntax(filepath):
    """Check if a Python file has syntax errors."""
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """Find all test files with syntax errors."""
    test_dirs = [
        Path('tests/core'),
        Path('tests/integration'),
        Path('tests/unit'),
        Path('tests/e2e'),
    ]
    
    broken_files = []
    working_files = []
    
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue
            
        for test_file in test_dir.glob('test_*.py'):
            is_valid, error = check_syntax(test_file)
            
            if is_valid:
                working_files.append(test_file)
                print(f"OK {test_file}")
            else:
                broken_files.append((test_file, error))
                print(f"FAIL {test_file}")
                if error:
                    err_msg = error.split('Sorry:')[1] if 'Sorry:' in error else error[:100]
                    print(f"   Error: {err_msg}".encode('ascii', 'ignore').decode('ascii'))
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Working: {len(working_files)}")
    print(f"  Broken: {len(broken_files)}")
    print(f"{'='*60}")
    
    if broken_files:
        print("\nBroken files:")
        for filepath, _ in broken_files:
            print(f"  - {filepath}")
    
    return len(broken_files)

if __name__ == '__main__':
    sys.exit(main())
