#!/usr/bin/env python3
"""Direct check of Key 29 and Key 30 violations."""

import ast
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).parent
MAX_FUNCTION_LINES = 100
MAX_NESTING_DEPTH = 5

def get_nesting_depth(node: ast.AST, current_depth: int = 0) -> int:
    """Calculate maximum nesting depth of a function."""
    max_depth = current_depth
    
    nesting_nodes = (
        ast.For, ast.AsyncFor, ast.While,
        ast.If, ast.With, ast.AsyncWith,
        ast.Try, ast.ExceptHandler,
        ast.Match, ast.match_case
    )
    
    for child in ast.walk(node):
        if isinstance(child, nesting_nodes):
            child_depth = get_nesting_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
    
    return max_depth

def check_key_29() -> List[str]:
    """Check Key 29 function length violations."""
    violations = []
    
    for py_file in ROOT.rglob("*.py"):
        if "__pycache__" in str(py_file) or "archives" in str(py_file):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, "end_lineno") and node.end_lineno:
                        lines = node.end_lineno - node.lineno + 1
                        if lines > MAX_FUNCTION_LINES:
                            rel_path = py_file.relative_to(ROOT)
                            violations.append(f"{rel_path}:{node.lineno} – {node.name} ({lines} lines)")
        except:
            pass
    
    return violations

def check_key_30() -> List[str]:
    """Check Key 30 nesting depth violations."""
    violations = []
    
    for py_file in ROOT.rglob("*.py"):
        if "__pycache__" in str(py_file) or "archives" in str(py_file):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    depth = get_nesting_depth(node)
                    if depth > MAX_NESTING_DEPTH:
                        rel_path = py_file.relative_to(ROOT)
                        violations.append(f"{rel_path}:{node.lineno} – {node.name} (depth {depth})")
        except:
            pass
    
    return violations

def main():
    """Check both keys and report results."""
    print("\n" + "="*80)
    print("DIRECT KEY 29 AND KEY 30 CHECK")
    print("="*80)
    
    key_29_violations = check_key_29()
    key_30_violations = check_key_30()
    
    print(f"\nKey 29 (Function Length > {MAX_FUNCTION_LINES} lines):")
    if key_29_violations:
        print(f"  ❌ FAILING - {len(key_29_violations)} violations:")
        for v in key_29_violations[:10]:
            print(f"    - {v}")
        if len(key_29_violations) > 10:
            print(f"    ... and {len(key_29_violations) - 10} more")
    else:
        print("  ✅ PASSING - No violations")
    
    print(f"\nKey 30 (Nesting Depth > {MAX_NESTING_DEPTH}):")
    if key_30_violations:
        print(f"  ❌ FAILING - {len(key_30_violations)} violations:")
        for v in key_30_violations[:10]:
            print(f"    - {v}")
        if len(key_30_violations) > 10:
            print(f"    ... and {len(key_30_violations) - 10} more")
    else:
        print("  ✅ PASSING - No violations")
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    if not key_29_violations and not key_30_violations:
        print("🎉 100% COMPLEXITY COMPLIANCE ACHIEVED!")
        print("   - Key 29: PASSING (0 violations)")
        print("   - Key 30: PASSING (0 violations)")
        return 0
    else:
        print(f"⚠️  {len(key_29_violations) + len(key_30_violations)} total violations remaining")
        print(f"   - Key 29: {len(key_29_violations)} violations")
        print(f"   - Key 30: {len(key_30_violations)} violations")
        return 1

if __name__ == "__main__":
    exit(main())
