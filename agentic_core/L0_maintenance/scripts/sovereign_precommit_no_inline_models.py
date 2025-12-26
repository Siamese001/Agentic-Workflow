"""
Sovereign Guard: Block Inline Pydantic Models
Enforces that all Pydantic models must live in core_contracts.py

Usage: Called automatically by pre-commit hook
"""
import ast
import sys
from pathlib import Path

# Files exempt from this check (the SSOT itself)
EXEMPT = {"agentic_core/schemas/models/core_contracts.py"}

class SovereignModelVisitor(ast.NodeVisitor):
    """AST visitor to detect inline Pydantic BaseModel definitions."""
    
    def __init__(self, filename):
        self.filename = filename
        self.violations = []
    
    def visit_ClassDef(self, node):
        """Check if class inherits from BaseModel or Model."""
        for base in node.bases:
            base_name = ""
            
            # Handle direct name (BaseModel)
            if isinstance(base, ast.Name):
                base_name = base.id
            # Handle attribute (pydantic.BaseModel)
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            
            # Detect Pydantic model inheritance
            if base_name in ["BaseModel", "Model"]:
                self.violations.append({
                    "line": node.lineno,
                    "class": node.name,
                    "base": base_name
                })
        
        self.generic_visit(node)

def check_file(filepath):
    """Check a single file for inline Pydantic models."""
    # Normalize path for comparison
    normalized_path = str(Path(filepath)).replace("\\", "/")
    
    # Skip exempt files
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        visitor = SovereignModelVisitor(filepath)
        visitor.visit(tree)
        
        if visitor.violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for violation in visitor.violations:
                print(f"  Line {violation['line']}: class {violation['class']}({violation['base']})")
            print("\n💡 SOLUTION: Migrate this model to:")
            print("   agentic_core/schemas/models/core_contracts.py")
            print("=" * 80)
            return False
        
        return True
    
    except SyntaxError:
        # Skip files with syntax errors (might be in development)
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_inline_models.py <file1> <file2> ...")
        sys.exit(0)
    
    all_passed = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed = False
    
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Inline Pydantic models detected.")
        print("   All models must be centralized in core_contracts.py")
        sys.exit(1)
    
    sys.exit(0)
