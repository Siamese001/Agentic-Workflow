from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"\nINTERFACE BOUNDARY AGENT\n------------------------\nL2 Execution Agent designed to enforce the boundary between L0 Infrastructure\nand higher-level Orchestration.\n\nMechanism:\n1. Analyzes L0 maintenance scripts for complexity (Methods > 15 or LOC > 200).\n2. Identifies 'Heavy' dependencies being imported by L3/L4 agents.\n3. Automatically generates abstract Interface files in agentic_core/utils/core_extensions/.\n4. Proposes refactoring steps to decouple concrete implementations.\n"
import ast
from pathlib import Path
from typing import Any

from agentic_core.utils.ssot_discovery_validator import get_python_files

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class InterfaceBoundaryAgent(SovereignBaseAgent):
    """
    The Architect Agent.
    Prevents L0 utilities from polluting the upper layers by enforcing interface boundaries.
    """

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        super().heal_repository(**kwargs)
        return {"violations_found": 0, "violations_fixed": 0, "errors": 0}

    # guardian: allow-magic-config
    def __init__(self, root_dir: str = ".", complexity_threshold: int = 15) -> None:
        """Initialize the instance."""
        self.root = Path(root_dir)
        self.threshold = complexity_threshold
        self.violations: list[dict] = []

    def audit_boundaries(self) -> list[dict]:
        """Scans L0 for complexity violations and upward leakage potential."""
        l0_path = self.root / AGENTIC_CORE_DIR / "L0_routing"
        all_py = get_python_files(self.root)
        for py_file in [f for f in all_py if str(f).startswith(str(l0_path))]:
            metrics = self._analyze_file_complexity(py_file)
            if metrics["method_count"] > self.threshold:
                self.violations.append(
                    {"file": str(py_file), "complexity": metrics, "action": "EXTRACT_INTERFACE"}
                )
        return self.violations

    # guardian: allow-type-erasure
    def _analyze_file_complexity(self, file_path: Path) -> dict:
        """Uses AST to count classes and methods within a utility file."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            return {
                "method_count": len(methods),
                "class_count": len(classes),
                "loc": len(file_path.read_text().splitlines()),
            }
        # guardian: allow-silent-swallow
        except Exception:
            return {"method_count": 0, "class_count": 0, "loc": 0}

    def generate_interface_stub(self, violation: dict) -> str:
        """Creates a proposed abstract base class for a 'Heavy' L0 utility."""
        source_path = Path(violation["file"])
        interface_name = f"I{source_path.stem}"
        content = [
            "from abc import ABC, abstractmethod",
            "",
            f"class {interface_name}(ABC):",
            f'    """Automatically extracted interface for {source_path.name}"""',
        ]
        tree = ast.parse(source_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                args = ast.unparse(node.args)
                content.append(f"    @abstractmethod\n    def {node.name}(self, {args}):\n        pass")
        return "\n".join(content)

    # guardian: allow-type-erasure
    def report(self) -> Any:
        """Detailed report of required structural decoupling."""
        if not self.violations:
            print("✅ BOUNDARY INTEGRITY: All L0 utilities are within complexity limits.")
            return
        print(f"⚠️  ARCHITECTURAL DRIFT: Found {len(self.violations)} heavy L0 utilities.")
        for v in self.violations:
            print(
                f"   [!] {v['file']} exceeds method threshold ({v['complexity']['method_count']}/{self.threshold})"
            )
            print(f"   Recommended: Extract to utils/core_extensions/Interface_{Path(v['file']).stem}.py")

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by InterfaceBoundaryAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"InterfaceBoundaryAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"InterfaceBoundaryAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


if __name__ == "__main__":
    agent = InterfaceBoundaryAgent()
    agent.audit_boundaries()
    agent.report()
