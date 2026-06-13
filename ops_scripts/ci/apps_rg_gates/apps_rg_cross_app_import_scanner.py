#!/usr/bin/env python3
"""
DS-5: Cross-App Import Scanner
Verifies apps_rg isolation - no imports from other apps_* packages.
"""
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set


def get_imports_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extract all imports from a Python file."""
    imports = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except SyntaxError as e:
        return [{"error": f"Syntax error: {e}", "file": str(file_path)}]
    except Exception as e:
        return [{"error": f"Parse error: {e}", "file": str(file_path)}]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": alias.name,
                    "file": str(file_path)
                })
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append({
                "type": "from",
                "module": module,
                "names": [a.name for a in node.names],
                "file": str(file_path),
                "level": node.level
            })
    
    return imports


def check_cross_app_imports(repo_root: Path) -> List[Dict[str, Any]]:
    """Check for cross-app imports in apps_rg."""
    violations = []
    
    apps_rg_dir = repo_root / "apps_rg"
    
    # Apps that apps_rg must NOT import from
    forbidden_apps = [
        "apps_lic", "apps_qna", "apps_research", "apps_rfp", 
        "apps_underwriting_ai", "apps_architect", "apps_eval"
    ]
    
    # Find all Python files in apps_rg
    py_files = list(apps_rg_dir.rglob("*.py"))
    
    for py_file in py_files:
        imports = get_imports_from_file(py_file)
        
        for imp in imports:
            module = imp.get("module", "")
            
            # Check if importing from another apps_* package
            for forbidden in forbidden_apps:
                if module.startswith(forbidden) or f".{forbidden}" in module:
                    violations.append({
                        "file": str(py_file.relative_to(repo_root)),
                        "type": "cross_app_import",
                        "severity": "ERROR",
                        "message": f"apps_rg imports from {forbidden}: {module}",
                        "rule": "AG-RGGOV-ISOLATION-1",
                        "import": module
                    })
    
    return violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="apps_rg Cross-App Import Scanner")
    parser.add_argument("--repo-path", default=".", help="Repository root path")
    parser.add_argument("--output-format", choices=["json", "text"], default="text")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_path).resolve()
    violations = check_cross_app_imports(repo_root)
    
    passed = len(violations) == 0
    
    result = {
        "passed": passed,
        "violations": violations,
        "scanner": "apps_rg_cross_app_import_scanner",
        "version": "DS-5.0",
        "scan_scope": "apps_rg/**/*.py"
    }
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Cross-App Import Scanner: {'PASS' if passed else 'FAIL'}")
        print(f"Files scanned: {len(list((repo_root / 'apps_rg').rglob('*.py')))}")
        print(f"Violations: {len(violations)}")
        for v in violations:
            print(f"  - [{v.get('severity', 'ERROR')}] {v.get('file', 'N/A')}: {v.get('message', '')}")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
