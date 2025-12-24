"""
Fix imports after moving files to P1_core subdirectories.
Updates all references to moved files throughout the codebase.
"""
import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")

# Map of old import paths to new paths
IMPORT_REWRITES = {
    # L3_orchestration moves
    r"from \.fission_executor import": "from .P1_core.fission_executor import",
}

def fix_imports():
    """Fix all imports referencing moved files."""
    print("[*] FIXING IMPORTS AFTER FILE MOVES...")
    fixed = 0
    
    for py_file in ROOT.rglob("*.py"):
        if "venv" in str(py_file) or ".git" in str(py_file):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            original = content
            
            # Apply all rewrites
            for old_pattern, new_path in IMPORT_REWRITES.items():
                content = re.sub(old_pattern, new_path, content)
            
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f"  [✓] Fixed: {py_file.relative_to(ROOT)}")
                fixed += 1
        except Exception as e:
            pass
    
    print(f"\n[OK] Fixed {fixed} import statements")

if __name__ == "__main__":
    fix_imports()
