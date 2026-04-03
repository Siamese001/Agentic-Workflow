#!/usr/bin/env python3
"""
ADG Layer Boundary Checker — Check layer sovereignty using ADG layer metadata

Replaces AST + glob + regex patterns with ADG-powered queries for better performance
and accuracy in detecting layer boundary violations and import sovereignty issues.

Usage:
    python tools/adg/adg_layer_boundary_checker.py
    python tools/adg/adg_layer_boundary_checker.py --directory agentic_core
    python tools/adg/adg_layer_boundary_checker.py --file path/to/file.py
    python tools/adg/adg_layer_boundary_checker.py --layer L1
"""

import argparse
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

# Try to import ADG Query Bridge
try:
    from adg_query_bridge import ADGQueryBridge, FileMatch, Node
    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable: {e}")
    ADG_AVAILABLE = False


class LayerViolation:
    """Represents a layer boundary violation found by the checker."""

    def __init__(self, file_path: str, line_number: int, source_layer: str,
                 target_layer: str, import_module: str, violation_type: str,
                 message: str = ""):
        self.file_path = file_path
        self.line_number = line_number
        self.source_layer = source_layer
        self.target_layer = target_layer
        self.import_module = import_module
        self.violation_type = violation_type
        self.message = message

    def __repr__(self):
        return f"LayerViolation({self.file_path}:{self.line_number} - {self.source_layer}→{self.target_layer} [{self.violation_type}])"


class ADGLayerBoundaryChecker:
    """Checker for layer boundary violations using ADG."""

    def __init__(self, repo_root: str | None = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.bridge = ADGQueryBridge() if ADG_AVAILABLE else None

        # Layer sovereignty rules (L1 must NOT import L2+, etc.)
        self.layer_rules = {
            "L1": ["L2", "L3", "L4", "L5", "L6"],
            "L2": ["L5", "L6"],
            "L3": ["L5", "L6"],
            # L4 can import from higher layers
            # L5 can import from L6
            # L6 is the highest layer
        }

        # Apps layers that should not import directly from L* layers
        self.apps_prefixes = ["apps_lic", "apps_rg", "apps_shared", "apps_eval", "apps_exec", "apps_research", "apps_rfp"]
        self.l_layer_prefix = "L"

    def check_file(self, file_path: str) -> List[LayerViolation]:
        """Check layer boundaries in a specific file."""
        violations = []
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return [LayerViolation(file_path, 0, "", "", "", "file_not_found", f"File not found: {file_path}")]

        try:
            if ADG_AVAILABLE:
                violations = self._check_file_with_adg(file_path_obj)
            else:
                violations = self._check_file_with_ast_fallback(file_path_obj)
        except Exception as e:
            violations.append(LayerViolation(
                file_path=str(file_path_obj.relative_to(self.repo_root)),
                line_number=0,
                source_layer="",
                target_layer="",
                import_module="",
                violation_type="check_error",
                message=f"Failed to check layer boundaries: {e}"
            ))

        return violations

    def _check_file_with_adg(self, file_path: Path) -> List[LayerViolation]:
        """Check file layer boundaries using ADG."""
        violations = []
        rel_path = str(file_path.relative_to(self.repo_root))

        try:
            # Determine source layer
            source_layer = self._determine_layer_from_path(rel_path)
            if not source_layer:
                return violations  # Not in a layer we care about

            # Extract imports from the file
            imports = self._extract_imports_ast(file_path)

            for import_info in imports:
                module_name = import_info.get("module", "")
                line_num = import_info.get("line", 0)

                if not module_name:
                    continue

                # Get target layer from ADG
                target_layer = self._get_module_layer_from_adg(module_name)

                if target_layer:
                    violations.extend(self._check_layer_violation(
                        source_layer, target_layer, module_name, line_num, rel_path
                    ))
                else:
                    # Module not found in ADG, check if it's a layer violation by pattern
                    violations.extend(self._check_pattern_violation(
                        source_layer, module_name, line_num, rel_path
                    ))

        except Exception as e:
            warnings.warn(f"ADG check failed for {rel_path}, falling back to AST: {e}")
            violations = self._check_file_with_ast_fallback(file_path)

        return violations

    def _determine_layer_from_path(self, file_path: str) -> Optional[str]:
        """Determine the layer from a file path."""
        parts = file_path.split('/')

        # Check for L0-L6 layers
        for i, part in enumerate(parts):
            if part.startswith("L") and len(part) == 2 and part[1].isdigit():
                return part

        # Check for apps_* layers
        for part in parts:
            if part.startswith("apps_"):
                return part

        return None

    def _extract_imports_ast(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract imports using AST parsing."""
        import ast

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append({
                            "type": "from",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })

            return imports
        except SyntaxError:
            return []

    def _get_module_layer_from_adg(self, module_name: str) -> Optional[str]:
        """Get the layer for a module using ADG."""
        if not ADG_AVAILABLE:
            return None

        try:
            # Search for the module in each layer
            for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
                nodes = self.bridge.nodes_in_layer(layer)
                for node in nodes:
                    if (module_name in node.label or
                        module_name in str(node.file_path) or
                        node.label.endswith(module_name)):
                        return layer
        except Exception:
            pass

        return None

    def _check_layer_violation(self, source_layer: str, target_layer: str,
                              module_name: str, line_num: int, file_path: str) -> List[LayerViolation]:
        """Check if an import violates layer sovereignty rules."""
        violations = []

        # Check layer inversion for agentic_core layers
        if source_layer in self.layer_rules:
            forbidden_layers = self.layer_rules[source_layer]
            for forbidden_layer in forbidden_layers:
                if (target_layer == forbidden_layer or
                    target_layer.startswith(forbidden_layer + ".")):
                    violations.append(LayerViolation(
                        file_path=file_path,
                        line_number=line_num,
                        source_layer=source_layer,
                        target_layer=target_layer,
                        import_module=module_name,
                        violation_type="layer_inversion",
                        message=f"Layer inversion: {source_layer} imports from {target_layer}"
                    ))

        # Check apps_* direct L* imports
        if source_layer in self.apps_prefixes:
            if target_layer.startswith(self.l_layer_prefix):
                violations.append(LayerViolation(
                    file_path=file_path,
                    line_number=line_num,
                    source_layer=source_layer,
                    target_layer=target_layer,
                    import_module=module_name,
                    violation_type="apps_direct_l_import",
                    message=f"Apps layer {source_layer} directly imports from {target_layer} (use agentic_core.interfaces shims)"
                ))

        return violations

    def _check_pattern_violation(self, source_layer: str, module_name: str,
                                line_num: int, file_path: str) -> List[LayerViolation]:
        """Check for violations based on module name patterns when ADG lookup fails."""
        violations = []

        # Check if module name suggests a layer
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if module_name.startswith(layer + "."):
                violations.extend(self._check_layer_violation(
                    source_layer, layer, module_name, line_num, file_path
                ))
                break

        return violations

    def _check_file_with_ast_fallback(self, file_path: Path) -> List[LayerViolation]:
        """Check file layer boundaries using AST fallback when ADG is unavailable."""
        violations = []
        rel_path = str(file_path.relative_to(self.repo_root))

        try:
            source_layer = self._determine_layer_from_path(rel_path)
            if not source_layer:
                return violations

            imports = self._extract_imports_ast(file_path)

            for import_info in imports:
                module_name = import_info.get("module", "")
                line_num = import_info.get("line", 0)

                if not module_name:
                    continue

                # Check violations based on patterns only
                violations.extend(self._check_pattern_violation(
                    source_layer, module_name, line_num, rel_path
                ))

        except Exception as e:
            violations.append(LayerViolation(
                file_path=rel_path,
                line_number=0,
                source_layer="",
                target_layer="",
                import_module="",
                violation_type="check_error",
                message=f"Failed to check layer boundaries: {e}"
            ))

        return violations

    def check_directory(self, directory: str) -> List[LayerViolation]:
        """Check layer boundaries in all Python files in a directory."""
        violations = []
        dir_path = self.repo_root / directory

        if not dir_path.exists():
            return [LayerViolation(directory, 0, "", "", "", "directory_not_found", f"Directory not found: {directory}")]

        for py_file in dir_path.rglob("*.py"):
            file_violations = self.check_file(str(py_file))
            violations.extend(file_violations)

        return violations

    def check_layer(self, layer: str) -> List[LayerViolation]:
        """Check all files in a specific layer for boundary violations."""
        violations = []

        if not ADG_AVAILABLE:
            return [LayerViolation(layer, 0, "", "", "", "adg_unavailable", "ADG not available for layer checking")]

        try:
            # Get all nodes in the specified layer
            nodes = self.bridge.nodes_in_layer(layer)

            for node in nodes:
                if node.file_path:
                    file_violations = self.check_file(str(self.repo_root / node.file_path))
                    # Filter violations that involve this layer
                    layer_violations = [v for v in file_violations if v.source_layer == layer]
                    violations.extend(layer_violations)

        except Exception as e:
            violations.append(LayerViolation(
                file_path=layer,
                line_number=0,
                source_layer=layer,
                target_layer="",
                import_module="",
                violation_type="check_error",
                message=f"Failed to check layer {layer}: {e}"
            ))

        return violations

    def get_layer_summary(self) -> Dict[str, Any]:
        """Get a summary of layer information."""
        if not ADG_AVAILABLE:
            return {"error": "ADG not available"}

        try:
            summary = {
                "layers": {},
                "total_files": 0,
                "total_violations": 0
            }

            # Get basic statistics from ADG
            for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
                nodes = self.bridge.nodes_in_layer(layer)
                summary["layers"][layer] = {
                    "node_count": len(nodes),
                    "files": len(set(node.file_path for node in nodes if node.file_path))
                }
                summary["total_files"] += summary["layers"][layer]["files"]

            return summary

        except Exception as e:
            return {"error": f"Failed to get layer summary: {e}"}


def main():
    """Main entry point for the ADG layer boundary checker."""
    parser = argparse.ArgumentParser(description="ADG Layer Boundary Checker")
    parser.add_argument("--file", help="Specific file to check")
    parser.add_argument("--directory", help="Directory to check")
    parser.add_argument("--layer", help="Layer to check (L0-L6)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--summary", action="store_true", help="Show layer summary")

    args = parser.parse_args()

    checker = ADGLayerBoundaryChecker()
    violations = []

    if args.summary:
        summary = checker.get_layer_summary()
        import json
        print(json.dumps(summary, indent=2))
        return

    if args.file:
        violations = checker.check_file(args.file)
    elif args.directory:
        violations = checker.check_directory(args.directory)
    elif args.layer:
        violations = checker.check_layer(args.layer)
    else:
        # Check entire repository
        violations = checker.check_directory(".")

    if args.format == "json":
        import json
        output = [
            {
                "file_path": v.file_path,
                "line_number": v.line_number,
                "source_layer": v.source_layer,
                "target_layer": v.target_layer,
                "import_module": v.import_module,
                "violation_type": v.violation_type,
                "message": v.message
            }
            for v in violations
        ]
        print(json.dumps(output, indent=2))
    else:
        print(f"ADG Layer Boundary Checker Results")
        print(f"=================================")
        print(f"Found {len(violations)} layer boundary violations")
        print()

        # Group violations by type
        by_type = {}
        by_source_layer = {}

        for v in violations:
            if v.violation_type not in by_type:
                by_type[v.violation_type] = []
            by_type[v.violation_type].append(v)

            if v.source_layer not in by_source_layer:
                by_source_layer[v.source_layer] = []
            by_source_layer[v.source_layer].append(v)

        # Show violations by source layer
        for source_layer, layer_violations in sorted(by_source_layer.items()):
            if not source_layer:
                continue
            print(f"{source_layer} violations:")
            for v in sorted(layer_violations, key=lambda x: (x.file_path, x.line_number)):
                print(f"  {v.file_path}:{v.line_number} - {v.import_module}")
                print(f"    → {v.target_layer} ({v.violation_type})")
                if v.message:
                    print(f"    {v.message}")
            print()

        if not violations:
            print("✅ No layer boundary violations found")
        else:
            print("Summary by violation type:")
            for violation_type, type_violations in sorted(by_type.items()):
                print(f"  {violation_type}: {len(type_violations)}")

            print("\nRecommendations:")
            print("1. Use agentic_core.interfaces shims for cross-layer imports")
            print("2. Consider dependency injection to break layer coupling")
            print("3. Review architecture for proper layer separation")


if __name__ == "__main__":
    main()
