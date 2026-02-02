from __future__ import annotations
#!/usr/bin/env python3
"""
DEPRECATED (2026-01-07): Use GravityValidatorAgent in L5_safety/validators/ instead.

This agent has been consolidated into the unified Gravity system:
- Detection: GravityValidatorAgent (L5_safety/validators/)
- Healing: GravityHealerAgent (L2_execution/tool_registry/)

Sovereign Gravity Compliance Validator (Key 18)
Detects intra-core import waterfall violations per strict layer authority order.
SSOT-aligned with structure_blueprint.py layer ordering.
"""

import re
import warnings
from pathlib import Path

# [SSOT IMPORT] Layer authority from structure_blueprint.py
from agentic_core.config.blueprint_sovereign.structure_blueprint_config import CORE_SUBFOLDER_MAP
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# [SSOT DERIVED] Layer authority order: Lower index = higher authority (cannot import upward)
# Derived from CORE_SUBFOLDER_MAP keys in structure_blueprint.py
gravity_layers = list(CORE_SUBFOLDER_MAP.keys())

# NOT_AN_AGENT — validator utility, not a true agent — excluded from agent discovery
class GravityComplianceValidatorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    '''Brief description of functionality and purpose.'''

    def __init__(self, project_root: Path) -> None:
        warnings.warn(
            "GravityComplianceValidatorAgent is deprecated. Use GravityValidatorAgent from "
            "agentic_core.L5_safety.validators.GravityValidatorAgent instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.root = project_root.resolve()
        self.violations = []

    def get_layer_rank(self, layer_name: str) -> int:
        """Return authority rank: lower = more sovereign"""
        for i, layer in enumerate(GRAVITY_LAYERS):
            if layer in layer_name:
                return i
        return -1  # Unknown = no restriction

    def scan_file(self, file_path: Path):

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        current_rank = self.get_layer_rank(str(file_path))
        if current_rank == -1:
            return

        # Find all agentic_core intra-imports
        imports = re.findall(r"(?:from|import)\s+agentic_core\.(\w+)", content)

        for imported in imports:
            import_rank = self.get_layer_rank(imported)
            if import_rank == -1:
                continue

            # Violation: importing a lower-authority (higher index) layer
            if import_rank > current_rank:
                self.violations.append({
                    "file": file_path.relative_to(self.root),
                    "source_layer": GRAVITY_LAYERS[current_rank],
                    "illegal_import": GRAVITY_LAYERS[import_rank]
                })

    def run(self) -> Dict[str, Any]:

        print("=== GRAVITY COMPLIANCE SCAN ===")
        for py_file in self.root.rglob("*.py"):
            if "agentic_core" in py_file.parts:
                self.scan_file(py_file)

        if not self.violations:
            print("✅ 100% GRAVITY COMPLIANCE ACHIEVED")
            return True

        print(f"🚨 {len(self.violations)} GRAVITY VIOLATIONS DETECTED")
        print(f"{'FILE':<60} {'SOURCE → ILLEGAL TARGET'}")
        print("-" * 90)
        for v in self.violations:
            print(f"{v['file']:<60} {v['source_layer']} → {v['illegal_import']}")
        return False

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent  # Assumes script in /scripts/
    validator = GravityComplianceValidatorAgent(PROJECT_ROOT)
    success = validator.run()
    exit(0 if success else 1)
