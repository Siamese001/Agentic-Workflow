"""
DDD Alignment Guardian - Sovereign Edition (December 29, 2025)
Detects violations of Domain-Driven Design tactical patterns:
- Anemic Domain Models (data holders without behavior)
- God Classes (excessive responsibilities)
- Mutable Value Objects
- Service layer bloat indicators
- Aggregate root misuse patterns
"""

import ast
from pathlib import Path
from typing import List, Tuple, Dict

def get_ddd_violations_detailed(root_path: str) -> List[Dict]:
    """
    [NEW] Detailed DDD violation detector — structured output for L0 healing/forensics.
    
    Returns:
        List of dicts with keys: file, line, type, description, severity
    """
    violations: List[Dict] = []
    root = Path(root_path)
    # [ROBUSTNESS] Handle case where root path doesn't exist
    if not root.exists():
        return violations

    python_files = list(root.rglob("*.py"))
    
    if not python_files:
        return violations
    
    for py_file in python_files:
        try:
            relative_path = py_file.relative_to(root)
        except ValueError:
            # Handle edge case where file is not relative to root (symlinks etc)
            relative_path = py_file.name

        # Skip tests, migrations, and private modules
        # [SOVEREIGN FILTER] Adjusted to catch more valid code while skipping infrastructure
        if any(skip in str(relative_path) for skip in ["tests", "migrations", "__pycache__", ".venv", "venv"]) or py_file.name.startswith("_"):
            continue
        
        try:
            code = py_file.read_text(encoding="utf-8", errors="ignore") # [ROBUSTNESS] Ignore encoding errors
            tree = ast.parse(code, filename=str(py_file))
        except SyntaxError as e:
            violations.append({
                "file": str(relative_path),
                "line": 1,
                "type": "Parse Error",
                "description": f"Invalid syntax: {e}",
                "severity": "LOW"
            })
            continue
        except Exception as e:
            violations.append({
                "file": str(relative_path),
                "line": 1,
                "type": "Read Error",
                "description": f"Failed to read/parse: {e}",
                "severity": "LOW"
            })
            continue
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            
            # Extract class body analysis
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")]
            attrs = [n for n in node.body if isinstance(n, ast.Assign)]
            # Also count type-annotated attributes (e.g. x: int) common in Pydantic/DataClasses
            ann_attrs = [n for n in node.body if isinstance(n, ast.AnnAssign)]
            total_methods = len(methods)
            total_attrs = len(attrs) + len(ann_attrs)
            
            # 1. Anemic Domain Model Detection
            # High attributes + low behavior = likely DTO/anemic entity
            if total_attrs >= 6 and total_methods <= 2:
                # Basic check to avoid flagging Pydantic models in 'schemas' folder if structure allows
                if "schemas" not in str(relative_path):
                    violations.append({
                        "file": str(relative_path),
                        "line": node.lineno,
                        "type": "Anemic Domain Model",
                        "description": f"Class '{node.name}' has {total_attrs} attributes but only {total_methods} behaviors — probable data holder without domain logic",
                        "severity": "HIGH"
                    })
            
            # 2. God Class Detection
            # Excessive methods indicate SRP violation
            if total_methods > 25:
                violations.append({
                    "file": str(relative_path),
                    "line": node.lineno,
                    "type": "God Class",
                    "description": f"Class '{node.name}' has {total_methods} methods — potential violation of Single Responsibility Principle",
                    "severity": "MEDIUM"
                })
            
            # 3. Mutable Value Object Detection
            # Value Objects must be immutable — no setters or mutable ops
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)
            
            # [HEURISTIC] Check for naming conventions like "ValueObject" or "VO"
            if any(vo_indicator in bases for vo_indicator in ["ValueObject", "VO", "Immutable"]) or "ValueObject" in node.name:
                setters_or_mutators = [m for m in methods if m.name.startswith(("set_", "update_", "add_", "remove_")) or "mutat" in m.name.lower()]
                if setters_or_mutators:
                    violations.append({
                        "file": str(relative_path),
                        "line": node.lineno,
                        "type": "Mutable Value Object",
                        "description": f"Value Object '{node.name}' contains mutating methods ({[m.name for m in setters_or_mutators]}) — VOs must be immutable",
                        "severity": "CRITICAL"
                    })
            
            # 4. Service Layer Bloat (heuristic)
            # Services should orchestrate, not contain domain logic
            if node.name.endswith("Service") or node.name.endswith("Manager"):
                complex_methods = 0
                for method in methods:
                    # Rough complexity: nested loops, conditionals, long body
                    # Count flow control statements
                    method_complexity = len([n for n in ast.walk(method) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
                    if method_complexity > 8: # Slightly relaxed threshold
                        complex_methods += 1
                
                if complex_methods > 5:
                    violations.append({
                        "file": str(relative_path),
                        "line": node.lineno,
                        "type": "Fat Service",
                        "description": f"Service '{node.name}' has {complex_methods} complex methods — likely containing domain logic instead of orchestration",
                        "severity": "MEDIUM"
                    })
    
    return violations


def validate_ddd_alignment(root_path: str) -> Tuple[float, List[str]]:
    """
    Existing Auditor-compatible validator — simple score + string issues.
    Used directly by Sovereign Auditor v3.1.
    """
    detailed_violations = get_ddd_violations_detailed(root_path)
    
    # Scoring: 5 points per violation, clamped to 0-100
    base_score = 100.0
    penalty_per_violation = 5.0
    
    # [SOVEREIGN SCORING] Critical violations hit harder
    critical_count = sum(1 for v in detailed_violations if v['severity'] == 'CRITICAL')
    penalty_per_violation += (critical_count * 10.0) # Bonus penalty for criticals

    score = max(0.0, base_score - len(detailed_violations) * penalty_per_violation)
    
    # Format issues as strings for Auditor consumption
    issues: List[str] = []
    for v in detailed_violations:
        line_info = f"line {v['line']}" if v['line'] > 0 else ""
        issues.append(f"{v['file']}:{line_info} [{v['severity']}] {v['type']}: {v['description']}")
    
    return score, issues
