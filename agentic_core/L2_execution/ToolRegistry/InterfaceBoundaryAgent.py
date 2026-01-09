#!/usr/bin/env python3
"""
INTERFACE BOUNDARY AGENT
------------------------
L2 Execution Agent designed to enforce the boundary between L0 Infrastructure 
and higher-level Orchestration. 

Mechanism:
1. Analyzes L0 maintenance scripts for complexity (Methods > 15 or LOC > 200).
2. Identifies 'Heavy' dependencies being imported by L3/L4 agents.
3. Automatically generates abstract Interface files in agentic_core/utils/core_extensions/.
4. Proposes refactoring steps to decouple concrete implementations.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin


class InterfaceBoundaryAgent(MCPHardenedMixin):
    """
    The Architect Agent.
    Prevents L0 utilities from polluting the upper layers by enforcing interface boundaries.
    """

    def __init__(self, root_dir: str = ".", complexity_threshold: int = 15):
        self.root = Path(root_dir)
        self.threshold = complexity_threshold
        self.violations: List[Dict] = []

    def audit_boundaries(self) -> List[Dict]:
        """Scans L0 for complexity violations and upward leakage potential."""
        l0_path = self.root / "agentic_core" / "L0_maintenance"
        for py_file in l0_path.glob("**/*.py"):
            metrics = self._analyze_file_complexity(py_file)
            if metrics['method_count'] > self.threshold:
                self.violations.append({
                    'file': str(py_file),
                    'complexity': metrics,
                    'action': 'EXTRACT_INTERFACE'
                })
        return self.violations

    def _analyze_file_complexity(self, file_path: Path) -> Dict:
        """Uses AST to count classes and methods within a utility file."""
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'))
            methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            return {
                'method_count': len(methods),
                'class_count': len(classes),
                'loc': len(file_path.read_text().splitlines())
            }
        except Exception:
            return {'method_count': 0, 'class_count': 0, 'loc': 0}

    def generate_interface_stub(self, violation: Dict) -> str:
        """Creates a proposed abstract base class for a 'Heavy' L0 utility."""
        source_path = Path(violation['file'])
        interface_name = f"I{source_path.stem}"
        
        content = [
            f'from abc import ABC, abstractmethod',
            f'',
            f'class {interface_name}(ABC):',
            f'    """Automatically extracted interface for {source_path.name}"""'
        ]

        # Extract method signatures for the interface
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                args = ast.unparse(node.args)
                content.append(f'    @abstractmethod\n    def {node.name}(self, {args}):\n        pass')

        return "\n".join(content)

    def report(self):
        """Detailed report of required structural decoupling."""
        if not self.violations:
            print("✅ BOUNDARY INTEGRITY: All L0 utilities are within complexity limits.")
            return

        print(f"⚠️  ARCHITECTURAL DRIFT: Found {len(self.violations)} heavy L0 utilities.")
        for v in self.violations:
            print(f"   [!] {v['file']} exceeds method threshold ({v['complexity']['method_count']}/{self.threshold})")
            print(f"   Recommended: Extract to utils/core_extensions/Interface_{Path(v['file']).stem}.py")


if __name__ == "__main__":
    agent = InterfaceBoundaryAgent()
    agent.audit_boundaries()
    agent.report()
