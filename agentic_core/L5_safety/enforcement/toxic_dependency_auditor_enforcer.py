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

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
)


class ToxicDependencyAuditor(SovereignBaseAgent):
    """
    The Risk-Assessor Agent.
    Identifies the most critical components of the Sovereign Architecture.
    """

    def __init__(self, root_dir: str = ".", toxic_threshold: int = 10):
        self.root = Path(root_dir)
        self.threshold = toxic_threshold
        self.dependency_map: dict[str, set[str]] = {}  # module -> set of dependents

    def audit_toxicity(self, coverage_data: dict[str, float] = None) -> list[dict]:
        """Builds the fan-in map and identifies toxic hubs with coverage weighting.

        Args:
            coverage_data: Optional dict mapping module paths to coverage percentages (0.0-1.0)

        Returns:
            List of toxic hubs sorted by systemic risk score
        """
        self._build_fan_in_map()

        toxic_hubs = []
        for module, dependents in self.dependency_map.items():
            if len(dependents) >= self.threshold:
                # Calculate base toxicity score (fan-in)
                fan_in = len(dependents)

                # Apply coverage weighting if available
                coverage_weight = 1.0
                if coverage_data and module in coverage_data:
                    # Lower coverage = higher risk
                    # Coverage 0% = 2.0x multiplier, 100% = 1.0x multiplier
                    coverage_pct = coverage_data[module]
                    coverage_weight = 2.0 - coverage_pct

                # Systemic risk = fan_in * coverage_weight
                systemic_risk = fan_in * coverage_weight

                toxic_hubs.append(
                    {
                        "module": module,
                        "fan_in": fan_in,
                        "coverage": coverage_data.get(module, 0.0) if coverage_data else None,
                        "coverage_weight": coverage_weight,
                        "systemic_risk": systemic_risk,
                        "dependents": list(dependents),
                    },
                )

        # Sort by systemic risk (highest first)
        return sorted(toxic_hubs, key=lambda x: x["systemic_risk"], reverse=True)

    def _build_fan_in_map(self):
        """Walks all python files to see who imports what."""
        # Operation Zero: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(self.root / AGENTIC_CORE_DIR):
            current_module = self._get_module_name(py_file)
            imports = self._extract_internal_imports(py_file)

            for imp in imports:
                if imp not in self.dependency_map:
                    self.dependency_map[imp] = set()
                self.dependency_map[imp].add(current_module)

    def _extract_internal_imports(self, file_path: Path) -> set[str]:
        """Uses AST to find internal agentic_core imports."""
        imports = set()
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith(AGENTIC_CORE_DIR):
                        imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(AGENTIC_CORE_DIR):
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

    def report(self, toxic_hubs: list[dict]):
        """Generates a Sovereign Toxicity Report with coverage weighting."""
        if not toxic_hubs:
            print(f"✅ TOXICITY CHECK: No modules exceed fan-in threshold ({self.threshold}).")
            return

        print(f"☢️  TOXIC HUB ALERT: {len(toxic_hubs)} modules identified as high-risk.")
        print("-" * 60)
        for hub in toxic_hubs:
            print(f"Module: {hub['module']}")
            print(f"Fan-in (Dependencies): {hub['fan_in']}")

            if hub.get("coverage") is not None:
                coverage_pct = hub["coverage"] * 100
                print(f"Coverage: {coverage_pct:.1f}%")
                print(f"Coverage Weight: {hub['coverage_weight']:.2f}x")
                print(f"Systemic Risk Score: {hub['systemic_risk']:.1f}")
            else:
                print(f"Toxicity Score: {hub['fan_in']}")

            print(f"Impact: A single violation here affects {hub['fan_in']} components.")
            print("-" * 60)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Toxic dependency auditor is detection-only
        toxic_hubs = self.audit_toxicity()
        return {
            "violations_found": len(toxic_hubs),
            "violations_fixed": 0,
            "errors": 0,
            "skipped": len(toxic_hubs),
            "reason": "Toxic dependencies require architectural refactoring",
        }

    def heal(self, violation: dict) -> dict:
        """Heal toxic dependency violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (toxic_hub, high_fan_in)
                - module: Module with high fan-in
                - fan_in: Number of dependencies

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Toxic dependencies require architectural refactoring",
        }


if __name__ == "__main__":
    auditor = ToxicDependencyAuditor()
    hubs = auditor.audit_toxicity()
    auditor.report(hubs)
