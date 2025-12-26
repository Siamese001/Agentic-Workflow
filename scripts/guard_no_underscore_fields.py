"""
Sovereign Guard: Block underscore-prefixed fields in SSOT models.
Session 6 - Permanent Defense Installation
"""
import ast
import sys
from pathlib import Path

def check_ssot(filepath: Path) -> bool:
    """Check for underscore-prefixed fields in core_contracts.py"""
    if "core_contracts.py" not in str(filepath):
        return True
    
    tree = ast.parse(filepath.read_text(encoding='utf-8'))
    violations = []
    
    for node in ast.walk(tree):
        # Check Pydantic Fields (annotated assignments)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.startswith("_") and not node.target.id.startswith("__"):
                violations.append((node.lineno, node.target.id))
        # Check Dataclass Fields (regular assignments)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.startswith("_") and not t.id.startswith("__"):
                    violations.append((node.lineno, t.id))

    if violations:
        print("\n" + "="*70)
        print("❌ SOVEREIGN GUARD VIOLATION: Underscore Fields Detected")
        print("="*70)
        for line, field in violations:
            print(f"[ERROR] Line {line}: Field '{field}' violates public API contract")
        print("\nUnderscore-prefixed fields are forbidden in SSOT models.")
        print("Use standard snake_case field names instead.")
        print("="*70 + "\n")
        return False
    
    print("✅ Sovereign Guard: No underscore field violations detected")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python guard_no_underscore_fields.py <file1> [file2 ...]")
        sys.exit(1)
    
    all_passed = all(check_ssot(Path(f)) for f in sys.argv[1:])
    sys.exit(0 if all_passed else 1)
