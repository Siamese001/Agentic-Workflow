from __future__ import annotations
#!/usr/bin/env python3
"""
AdvancedDeadCodeAuditorAgent - Sovereign Code Auditor V2.0
Identifies unused imports, functions, classes, and methods across the codebase.
VERSION 2.0 - Hardened with parent-node tracking and class-aware method analysis.
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def add_parents(node, parent=None):
    """Add parent reference to all AST nodes for upward traversal."""
    node.parent = parent
    for child in ast.iter_child_nodes(node):
        add_parents(child, node)


class ASTDeadCodeVisitor(ast.NodeVisitor):
    """
    Enhanced AST visitor that tracks dead code with class-aware method detection.
    """
    
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.imported_names: set[str] = set()
        self.defined_names: set[str] = set()
        self.defined_classes: set[str] = set()
        self.class_methods: Dict[str, Set[str]] = {}
        self.used_methods: Dict[str, Set[str]] = {}
        self.used_names: set[str] = set()
        self.used_classes: set[str] = set()
        self.defined_functions: set[str] = set()
        self.used_functions: set[str] = set()
        self.import_line_numbers: Dict[str, int] = {}
        self.definition_line_numbers: Dict[str, int] = {}
        
    def visit_Import(self, node: ast.Import):
        """Track import statements and their line numbers."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names.add(name)
            self.import_line_numbers[name] = node.lineno
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from-import statements."""
        if node.module:
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                self.imported_names.add(name)
                self.import_line_numbers[name] = node.lineno
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function definitions."""
        self.defined_names.add(node.name)
        self.defined_functions.add(node.name)
        self.definition_line_numbers[node.name] = node.lineno
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Track async function definitions."""
        self.defined_names.add(node.name)
        self.defined_functions.add(node.name)
        self.definition_line_numbers[node.name] = node.lineno
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Track class definitions and their methods."""
        self.defined_names.add(node.name)
        self.defined_classes.add(node.name)
        self.definition_line_numbers[node.name] = node.lineno
        
        # Initialize method tracking for this class
        self.class_methods[node.name] = set()
        self.used_methods[node.name] = set()
        
        # Track all methods in this class
        for body_node in node.body:
            if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.class_methods[node.name].add(body_node.name)
                self.definition_line_numbers[f"{node.name}.{body_node.name}"] = body_node.lineno
                
        self.generic_visit(node)
        
    def visit_Name(self, node: ast.Name):
        """Track name usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call):
        """Track function/method calls."""
        # Track direct function calls
        if isinstance(node.func, ast.Name):
            self.used_functions.add(node.func.id)
        # Track method calls on instances (e.g., instance.method())
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                class_hint = node.func.value.id
                if class_hint in self.defined_classes:
                    self.used_methods.setdefault(class_hint, set()).add(node.func.attr)
        self.generic_visit(node)
        
    # [EXTENSION] Detect self.method / cls.method references
    def visit_Attribute(self, node: ast.Attribute):
        """Track attribute access, especially self.method and cls.method."""
        # Track self.method() and cls.method() calls within class context
        if isinstance(node.value, ast.Name) and node.value.id in {"self", "cls"}:
            # Traverse up to find the enclosing class
            current = node
            while current := getattr(current, 'parent', None):
                if isinstance(current, ast.ClassDef):
                    self.used_methods.setdefault(current.name, set()).add(node.attr)
                    break
        self.generic_visit(node)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class DeadCodeDetectorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Sovereign dead code auditor that identifies unused code across the project.
    Enhanced with class-aware method tracking and parent-node traversal.
    """
    
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.results = {
            "unused_imports": [],
            "unused_functions": [],
            "unused_classes": [],
            "unused_methods": [],
            "dead_files": []
        }
        
    def _find_unused_imports(self, visitor, findings: Dict) -> None:
        """Extract unused imports from visitor."""
        for import_name in visitor.imported_names:
            if import_name not in visitor.used_names:
                findings["unused_imports"].append({
                    "name": import_name,
                    "line": visitor.import_line_numbers.get(import_name, "unknown")
                })

    def _find_unused_functions(self, visitor, findings: Dict) -> None:
        """Extract unused functions from visitor."""
        for func_name in visitor.defined_functions:
            if func_name.startswith("_"):
                continue
            if func_name not in visitor.used_functions and func_name not in visitor.used_names:
                findings["unused_functions"].append({
                    "name": func_name,
                    "line": visitor.definition_line_numbers.get(func_name, "unknown")
                })

    def _find_unused_classes(self, visitor, findings: Dict) -> None:
        """Extract unused classes from visitor."""
        for class_name in visitor.defined_classes:
            if class_name.startswith("_"):
                continue
            if class_name not in visitor.used_classes and class_name not in visitor.used_names:
                findings["unused_classes"].append({
                    "name": class_name,
                    "line": visitor.definition_line_numbers.get(class_name, "unknown")
                })

    def _find_unused_methods(self, visitor, findings: Dict) -> None:
        """Extract unused methods from visitor."""
        for class_name, methods in visitor.class_methods.items():
            used_methods = visitor.used_methods.get(class_name, set())
            for method_name in methods:
                if method_name.startswith("_"):
                    continue
                if method_name not in used_methods and method_name not in visitor.used_names:
                    findings["unused_methods"].append({
                        "class": class_name,
                        "name": method_name,
                        "line": visitor.definition_line_numbers.get(f"{class_name}.{method_name}", "unknown")
                    })

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Python file for dead code."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return {"error": f"Could not read {file_path}: {e}"}
            
        if not content.strip() or file_path.name == "__init__.py":
            return {"skipped": True, "reason": "Empty or __init__ file"}
            
        try:
            tree = ast.parse(content, filename=str(file_path))
            add_parents(tree)
            visitor = ASTDeadCodeVisitor(file_path)
            visitor.visit(tree)
        except SyntaxError as e:
            return {"error": f"Syntax error in {file_path}: {e}"}
            
        findings = {
            "file_path": str(file_path.relative_to(self.project_root)),
            "unused_imports": [],
            "unused_functions": [],
            "unused_classes": [],
            "unused_methods": []
        }
        
        self._find_unused_imports(visitor, findings)
        self._find_unused_functions(visitor, findings)
        self._find_unused_classes(visitor, findings)
        self._find_unused_methods(visitor, findings)
                    
        return findings
        
    def scan_directory(self, directory: Path, recursive: bool = True) -> Dict:
        """
        Scan an entire directory for dead code.
        """
        if not directory.exists():
            return {"error": f"Directory {directory} does not exist"}
            
        # Find all Python files
        if recursive:
            py_files = list(directory.rglob("*.py"))
        else:
            py_files = list(directory.glob("*.py"))
            
        # Filter out __pycache__ and other ignored directories
        py_files = [f for f in py_files if "__pycache__" not in str(f) and ".pytest_cache" not in str(f)]
        
        results = {
            "scanned_files": len(py_files),
            "findings": [],
            "summary": {
                "total_unused_imports": 0,
                "total_unused_functions": 0,
                "total_unused_classes": 0,
                "total_unused_methods": 0
            }
        }
        
        for file_path in py_files:
            finding = self.analyze_file(file_path)
            if "error" in finding:
                results["findings"].append(finding)
            elif "skipped" not in finding:
                results["findings"].append(finding)
                # Update summary
                results["summary"]["total_unused_imports"] += len(finding["unused_imports"])
                results["summary"]["total_unused_functions"] += len(finding["unused_functions"])
                results["summary"]["total_unused_classes"] += len(finding["unused_classes"])
                results["summary"]["total_unused_methods"] += len(finding["unused_methods"])
                
        return results
        
    def generate_report(self, results: Dict) -> str:
        """
        Generate a human-readable report of dead code findings.
        """
        report = []
        report.append("=" * 70)
        report.append(" DEAD CODE DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"Scanned {results.get('scanned_files', 0)} files")
        report.append("")
        
        summary = results.get("summary", {})
        report.append("SUMMARY:")
        report.append(f"  Unused Imports: {summary.get('total_unused_imports', 0)}")
        report.append(f"  Unused Functions: {summary.get('total_unused_functions', 0)}")
        report.append(f"  Unused Classes: {summary.get('total_unused_classes', 0)}")
        report.append(f"  Unused Methods: {summary.get('total_unused_methods', 0)}")
        report.append("")
        
        # Detailed findings
        for finding in results.get("findings", []):
            if "error" in finding:
                report.append(f"ERROR: {finding['error']}")
                continue
                
            file_path = finding.get("file_path", "unknown")
            report.append(f"FILE: {file_path}")
            
            if finding["unused_imports"]:
                report.append("  Unused Imports:")
                for imp in finding["unused_imports"]:
                    report.append(f"    - {imp['name']} (line {imp['line']})")
                    
            if finding["unused_functions"]:
                report.append("  Unused Functions:")
                for func in finding["unused_functions"]:
                    report.append(f"    - {func['name']}() (line {func['line']})")
                    
            if finding["unused_classes"]:
                report.append("  Unused Classes:")
                for cls in finding["unused_classes"]:
                    report.append(f"    - {cls['name']} (line {cls['line']})")
                    
            if finding["unused_methods"]:
                report.append("  Unused Methods:")
                for method in finding["unused_methods"]:
                    report.append(f"    - {method['class']}.{method['name']}() (line {method['line']})")
                    
            report.append("")
            
        return "\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(report)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# CLI Entry Point
def main():
    """Command line interface for the dead code detector."""
    if len(sys.argv) < 2:
        print("Usage: python dead_code_detector_agent.py <directory>")
        sys.exit(1)
        
    target_dir = Path(sys.argv[1])
    if not target_dir.is_absolute():
        target_dir = Path.cwd() / target_dir
        
    detector = DeadCodeDetectorAgent(target_dir)
    results = detector.scan_directory(target_dir)
    print(detector.generate_report(results))


if __name__ == "__main__":
    main()


@timeout(300)
def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """Utils/core extensions - operational only."""
    if _call_path is None:
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

    agent_name = "DeadCodeDetectorAgent"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Utils/core extensions - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)
