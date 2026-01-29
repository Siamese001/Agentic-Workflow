#!/usr/bin/env python3
"""
Test Structure Auto-Fix Script

Moves misplaced test files to their correct locations based on the
Depth-3 SSOT (Single Source of Truth) requirements.

Rules:
1. Test files in tests/unit/ should be under agentic_core/, apps_rg/, apps_lic/, or apps_shared/
2. Test files in tests/integration/ should be under the same domain structure
3. Attempts to determine correct location by analyzing test content
"""

import ast
import shutil
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = PROJECT_ROOT / "tests"

def analyze_test_imports(file_path: Path) -> Optional[str]:
    """Analyze test file to determine which domain it belongs to based on imports."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("agentic_core"):
                        return "agentic_core"
                    elif alias.name.startswith("apps_rg"):
                        return "apps_rg"
                    elif alias.name.startswith("apps_lic"):
                        return "apps_lic"
                    elif alias.name.startswith("apps_shared"):
                        return "apps_shared"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module.startswith("agentic_core"):
                        return "agentic_core"
                    elif node.module.startswith("apps_rg"):
                        return "apps_rg"
                    elif node.module.startswith("apps_lic"):
                        return "apps_lic"
                    elif node.module.startswith("apps_shared"):
                        return "apps_shared"
    except Exception:
        pass
    
    return None

def fix_test_structure():
    """Move misplaced test files to correct locations."""
    print("[AUTO-FIX] Moving misplaced test files to correct locations...")
    
    moved_count = 0
    error_count = 0
    
    # Process both unit and integration tests
    for test_type in ["unit", "integration"]:
        test_dir = TESTS_ROOT / test_type
        if not test_dir.exists():
            continue
            
        print(f"\n--- Processing {test_type} tests ---")
        
        for item in test_dir.iterdir():
            if item.is_file() and item.name.startswith("test_") and item.name.endswith(".py"):
                # Skip allowed files
                if item.name in {"__init__.py", "conftest.py"}:
                    continue
                    
                # Determine target domain
                domain = analyze_test_imports(item)
                if not domain:
                    # Default to agentic_core if we can't determine
                    domain = "agentic_core"
                    print(f"  [WARNING] Could not determine domain for {item.name}, defaulting to {domain}")
                
                # Create target directory
                target_dir = test_dir / domain
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Move file
                target_path = target_dir / item.name
                try:
                    shutil.move(str(item), str(target_path))
                    print(f"  [MOVED] {item.name} -> {test_type}/{domain}/")
                    moved_count += 1
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    error_count += 1
    
    print(f"\n[AUTO-FIX] Complete: {moved_count} files moved, {error_count} errors")
    return moved_count, error_count

if __name__ == "__main__":
    fix_test_structure()
