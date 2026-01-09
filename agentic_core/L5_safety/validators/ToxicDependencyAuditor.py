#!/usr/bin/env python3
"""
TOXIC DEPENDENCY AUDITOR
-------------------------
L5 Safety Validator designed to identify 'Toxic Hubs' within the core.
Toxicity is defined by high Fan-in (number of inward dependencies).

Logic:
1. Scans all agentic_core modules to build an inverse dependency map.
2. Ranks modules by inward dependency count (Fan-in).
3. Identifies 'High-Risk' modules that would cause massive drift if violated.
4. Feeds priorities to the DynamicSealAgent for targeted remediation.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin


class ToxicDependencyAuditor(MCPHardenedMixin):
    """
    The Risk-Assessor Agent.
    Identifies the most critical components of the Sovereign Architecture.
    """

    def __init__(self, root_dir: str = ".", toxic_threshold: int = 10):
        self.root = Path(root_dir)
        self.threshold = toxic_threshold
        self.dependency_map: Dict[str, Set[str]] = {}  # module -> set of dependents

    def audit_toxicity(self) -> List[Dict]:
        """Builds the fan-in map and identifies toxic hubs."""
        self._build_fan_in_map()
        
        toxic_hubs = []
        for module, dependents in self.dependency_map.items():
            if len(dependents) >= self.threshold:
                toxic_hubs.append({
                    "module": module,
                    "fan_in": len(dependents),
                    "dependents": list(dependents)
                })
        
        # Sort by most toxic (highest fan-in)
        return sorted(toxic_hubs, key=lambda x: x['fan_in'], reverse=True)

    def _build_fan_in_map(self):
        """Walks all python files to see who imports what."""
        for py_file in self.root.glob("agentic_core/**/*.py"):
            current_module = self._get_module_name(py_file)
            imports = self._extract_internal_imports(py_file)
            
            for imp in imports:
                if imp not in self.dependency_map:
                    self.dependency_map[imp] = set()
                self.dependency_map[imp].add(current_module)

    def _extract_internal_imports(self, file_path: Path) -> Set[str]:
        """Uses AST to find internal agentic_core imports."""
        imports = set()
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("agentic_core"):
                        imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("agentic_core"):
                            imports.add(alias.name)
        except Exception:
            pass
        return imports

    def _get_module_name(self, file_path: Path) -> str:
        """Maps file path to standard dot-notation module name."""
        try:
            rel_path = file_path.relative_to(self.root)
            return str(rel_path).replace(".py", "").replace("/", ".").replace("\\", ".")
        except ValueError:
            return ""

    def report(self, toxic_hubs: List[Dict]):
        """Generates a Sovereign Toxicity Report."""
        if not toxic_hubs:
            print(f"✅ TOXICITY CHECK: No modules exceed fan-in threshold ({self.threshold}).")
            return

        print(f"☢️  TOXIC HUB ALERT: {len(toxic_hubs)} modules identified as high-risk.")
        print("-" * 60)
        for hub in toxic_hubs:
            print(f"Module: {hub['module']}")
            print(f"Toxicity Score (Fan-in): {hub['fan_in']}")
            print(f"Impact: A single violation here affects {hub['fan_in']} components.")
            print("-" * 60)


if __name__ == "__main__":
    auditor = ToxicDependencyAuditor()
    hubs = auditor.audit_toxicity()
    auditor.report(hubs)
