"""Comprehensive AST error fixes - handles multiple error types."""
import ast
import re
from pathlib import Path

target_prefixes = ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]
fixed_files = []
skipped_files = []

def try_fix_file(py_file: Path) -> bool:
    """Try to fix AST errors in a file. Returns True if fixed."""
    try:
        content = py_file.read_text(encoding="utf-8")
        original_content = content
        
        # Try parsing first
        try:
            ast.parse(content)
            return False  # Already valid
        except SyntaxError as e:
            pass  # Continue to fixes
        
        # Fix 1: Remove code from docstrings (common pattern)
        content = re.sub(
            r'(class \w+[^:]*:\s+""")\s*#[^\n]*\n\s*super\(\)[^\n]*\n\s*\n',
            r'\1',
            content
        )
        
        # Fix 2: Line continuation character issues - remove trailing backslashes
        content = re.sub(r'\\\s*$', '', content, flags=re.MULTILINE)
        
        # Fix 3: Missing colons in type hints (common in dict literals)
        # This is risky, skip for now
        
        # Try parsing after fixes
        try:
            ast.parse(content)
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                return True
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"Error processing {py_file}: {e}")
        return False

# Process files
for py_file in Path('.').rglob("*.py"):
    rel_path = py_file.relative_to('.')
    if not any(rel_path.parts[0].startswith(prefix) for prefix in target_prefixes):
        continue
    
    try:
        content = py_file.read_text(encoding="utf-8")
        ast.parse(content)
    except SyntaxError:
        if try_fix_file(py_file):
            fixed_files.append(str(py_file))
            print(f"✓ Fixed: {py_file}")
        else:
            skipped_files.append(str(py_file))
            print(f"✗ Skipped (manual review needed): {py_file}")
    except Exception:
        pass

print(f"\n{'='*80}")
print(f"Fixed: {len(fixed_files)} files")
print(f"Skipped: {len(skipped_files)} files (require manual review)")
print(f"{'='*80}")

if skipped_files:
    print("\nFiles requiring manual review:")
    for f in skipped_files[:10]:  # Show first 10
        print(f"  - {f}")
    if len(skipped_files) > 10:
        print(f"  ... and {len(skipped_files) - 10} more")
