#!/usr/bin/env python3
"""
Paranoid Mode Audit: Sleeping Giant Detection

Identifies agents with high-risk capabilities that are "Armed but Disconnected":
- High Capability: Dangerous imports (shutil, os.remove, ast, subprocess) or mutation methods
- Disconnected Interface: Trivial heal_repository with orphaned substantial methods
- Shadow Execution: __main__ blocks, print() instead of logging
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SleepingGiant:
    """Represents a potentially dangerous agent."""
    file_path: Path
    agent_name: str
    dangerous_imports: list[str] = field(default_factory=list)
    mutation_methods: list[str] = field(default_factory=list)
    heal_repo_lines: int = 0
    heal_repo_is_trivial: bool = False
    orphaned_methods: list[str] = field(default_factory=list)
    has_main_block: bool = False
    uses_print_for_errors: bool = False
    uses_argparse: bool = False
    has_hardcoded_paths: bool = False
    is_zombie_healer: bool = False
    risk_score: str = "Low"
    latent_capability: str = ""
    disconnect_status: str = ""


DANGEROUS_IMPORTS = {
    'shutil': ['rmtree', 'move', 'copy', 'copytree'],
    'os': ['remove', 'unlink', 'rmdir', 'makedirs', 'rename'],
    'subprocess': ['run', 'call', 'Popen', 'check_output'],
}

MUTATION_PATTERNS = [
    r'\.write_text\s*\(',
    r'\.write\s*\(',
    r'open\s*\([^)]*["\']w["\']',
    r'\.unlink\s*\(',
    r'\.rmtree\s*\(',
    r'\.remove\s*\(',
]

EXCLUDED_DIRS = {'__pycache__', '.git', 'archives', 'void_violations', 'node_modules', '.venv', 'venv'}


class AgentAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze agent structure."""

    def __init__(self):
        self.imports: set[str] = set()
        self.dangerous_imports: list[str] = []
        self.classes: dict[str, dict] = {}
        self.current_class: str = None
        self.has_main_block: bool = False
        self.uses_argparse: bool = False
        self.hardcoded_paths: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
            if alias.name in DANGEROUS_IMPORTS:
                self.dangerous_imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)
            base_module = node.module.split('.')[0]
            if base_module in DANGEROUS_IMPORTS:
                for alias in node.names:
                    if alias.name in DANGEROUS_IMPORTS.get(base_module, []):
                        self.dangerous_imports.append(f"{base_module}.{alias.name}")
            if 'argparse' in node.module:
                self.uses_argparse = True
        for alias in node.names:
            if alias.name == 'argparse':
                self.uses_argparse = True
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        self.classes[node.name] = {
            'bases': [self._get_base_name(b) for b in node.bases],
            'methods': {},
            'heal_repository': None,
        }
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.current_class:
            method_info = {
                'name': node.name,
                'lines': node.end_lineno - node.lineno + 1 if node.end_lineno else 1,
                'body': ast.unparse(node) if hasattr(ast, 'unparse') else '',
                'calls': self._get_method_calls(node),
            }
            self.classes[self.current_class]['methods'][node.name] = method_info

            if node.name == 'heal_repository':
                self.classes[self.current_class]['heal_repository'] = method_info
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # Check for hardcoded paths
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id in ('ROOT', 'TARGET', 'PROJECT_ROOT', 'BASE_DIR'):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if '/' in node.value.value or '\\' in node.value.value:
                            self.hardcoded_paths.append(f"{target.id} = {node.value.value}")
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        # Check for if __name__ == "__main__"
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                self.has_main_block = True
        self.generic_visit(node)

    def _get_base_name(self, base) -> str:
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)

    def _get_method_calls(self, node: ast.FunctionDef) -> set[str]:
        """Get all method calls within a function."""
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name) and child.func.value.id == 'self':
                        calls.add(child.func.attr)
        return calls


def analyze_file(file_path: Path) -> SleepingGiant | None:
    """Analyze a single file for Sleeping Giant patterns."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return None

    # Quick filter - must be an Agent file
    if 'Agent' not in file_path.name and 'class' not in content:
        return None

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    analyzer = AgentAnalyzer()
    analyzer.visit(tree)

    # Check for mutation patterns in raw content
    mutation_methods = []
    for pattern in MUTATION_PATTERNS:
        if re.search(pattern, content):
            mutation_methods.append(pattern.replace('\\', '').replace('s*', '').replace('(', ''))

    # Check for print() usage for errors
    uses_print_for_errors = bool(re.search(r'print\s*\(\s*["\'].*(?:error|Error|ERROR|fail|Fail|FAIL)', content))

    # Find agent classes
    for class_name, class_info in analyzer.classes.items():
        if not class_name.endswith('Agent'):
            continue

        # Check if it inherits from HealerMixin or has heal_repository
        has_healer = 'HealerMixin' in class_info['bases'] or 'heal_repository' in class_info['methods']
        if not has_healer:
            continue

        giant = SleepingGiant(
            file_path=file_path,
            agent_name=class_name,
            dangerous_imports=analyzer.dangerous_imports,
            mutation_methods=mutation_methods,
            has_main_block=analyzer.has_main_block,
            uses_print_for_errors=uses_print_for_errors,
            uses_argparse=analyzer.uses_argparse,
            has_hardcoded_paths=len(analyzer.hardcoded_paths) > 0,
        )

        # Analyze heal_repository
        heal_repo = class_info.get('heal_repository')
        if heal_repo:
            giant.heal_repo_lines = heal_repo['lines']
            body = heal_repo['body']

            # Check if trivial
            is_trivial = (
                heal_repo['lines'] <= 6 or
                'return {' in body and ('skipped' in body or 'violations' in body) or
                body.strip().endswith('pass') or
                'return super().heal_repository' in body
            )
            giant.heal_repo_is_trivial = is_trivial

            # Check for zombie healer
            if 'return super().heal_repository' in body or body.strip().endswith('pass'):
                giant.is_zombie_healer = True

            # Find orphaned methods
            heal_calls = heal_repo['calls']
            substantial_methods = [
                name for name, info in class_info['methods'].items()
                if name not in ('__init__', '__post_init__', 'heal_repository', '__str__', '__repr__')
                and info['lines'] > 5
                and name not in heal_calls
            ]
            giant.orphaned_methods = substantial_methods

        # Calculate risk
        risk_factors = 0
        capabilities = []

        if giant.dangerous_imports:
            risk_factors += 2
            capabilities.append(f"Imports: {', '.join(giant.dangerous_imports)}")
        if giant.mutation_methods:
            risk_factors += 2
            capabilities.append(f"Mutations: {', '.join(giant.mutation_methods[:3])}")
        if giant.heal_repo_is_trivial and giant.orphaned_methods:
            risk_factors += 3
        if giant.has_main_block:
            risk_factors += 1
        if giant.uses_argparse:
            risk_factors += 1
        if giant.has_hardcoded_paths:
            risk_factors += 1
        if giant.is_zombie_healer:
            risk_factors += 2

        if risk_factors >= 6:
            giant.risk_score = "CRITICAL"
        elif risk_factors >= 4:
            giant.risk_score = "High"
        elif risk_factors >= 2:
            giant.risk_score = "Medium"
        else:
            giant.risk_score = "Low"

        giant.latent_capability = "; ".join(capabilities) if capabilities else "None detected"

        if giant.orphaned_methods:
            giant.disconnect_status = f"Orphaned: {', '.join(giant.orphaned_methods[:5])}"
        elif giant.is_zombie_healer:
            giant.disconnect_status = "Zombie: heal_repository delegates to super() only"
        else:
            giant.disconnect_status = "Connected"

        # Only return if there's actual risk
        if risk_factors >= 2 or giant.orphaned_methods:
            return giant

    return None


def main():
    root = Path(__file__).parent.parent / "agentic_core"

    print("=" * 80)
    print("PARANOID MODE AUDIT: Sleeping Giant Detection")
    print("=" * 80)
    print()

    giants: list[SleepingGiant] = []

    for file_path in root.rglob("*.py"):
        if any(excluded in file_path.parts for excluded in EXCLUDED_DIRS):
            continue

        giant = analyze_file(file_path)
        if giant:
            giants.append(giant)

    # Sort by risk
    risk_order = {"CRITICAL": 0, "High": 1, "Medium": 2, "Low": 3}
    giants.sort(key=lambda g: (risk_order.get(g.risk_score, 4), -len(g.orphaned_methods)))

    # Print Risk Matrix
    print("RISK MATRIX: Sleeping Giants")
    print("-" * 80)
    print(f"{'Agent Name':<40} {'Risk':<10} {'Orphaned Methods':<5} {'Capabilities'}")
    print("-" * 80)

    critical_giants = []
    high_giants = []

    for giant in giants:
        if giant.risk_score in ("CRITICAL", "High"):
            print(f"{giant.agent_name:<40} {giant.risk_score:<10} {len(giant.orphaned_methods):<5} {giant.latent_capability[:40]}")
            if giant.risk_score == "CRITICAL":
                critical_giants.append(giant)
            else:
                high_giants.append(giant)

    print()
    print("=" * 80)
    print("DETAILED ANALYSIS: Critical & High Risk Giants")
    print("=" * 80)

    for giant in (critical_giants + high_giants)[:10]:
        print()
        print(f"🔴 {giant.agent_name}")
        print(f"   File: {giant.file_path.relative_to(root.parent)}")
        print(f"   Risk Score: {giant.risk_score}")
        print(f"   Latent Capability: {giant.latent_capability}")
        print(f"   Disconnect Status: {giant.disconnect_status}")
        print(f"   heal_repository lines: {giant.heal_repo_lines} (Trivial: {giant.heal_repo_is_trivial})")
        if giant.orphaned_methods:
            print(f"   Orphaned Methods: {', '.join(giant.orphaned_methods[:10])}")
        if giant.has_main_block:
            print("   ⚠️  Has __main__ block (CLI Giant)")
        if giant.uses_argparse:
            print("   ⚠️  Uses argparse (CLI Giant)")
        if giant.has_hardcoded_paths:
            print("   ⚠️  Has hardcoded paths")
        if giant.is_zombie_healer:
            print("   ⚠️  Zombie Healer (delegates to super only)")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Sleeping Giants Found: {len(giants)}")
    print(f"  CRITICAL: {len(critical_giants)}")
    print(f"  High: {len(high_giants)}")
    print(f"  Medium: {len([g for g in giants if g.risk_score == 'Medium'])}")
    print(f"  Low: {len([g for g in giants if g.risk_score == 'Low'])}")

    # Return data for further processing
    return giants, critical_giants, high_giants


if __name__ == "__main__":
    main()
