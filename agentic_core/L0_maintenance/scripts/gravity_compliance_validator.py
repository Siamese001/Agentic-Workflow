#!/usr/bin/env python3
"""
Sovereign Gravity Compliance Validator (Key 18)
Detects intra-core import waterfall violations per strict layer authority order.
SSOT-aligned with structure_blueprint.py layer ordering.
"""

import re
from pathlib import Path

# [SSOT DERIVED] Layer authority order: Lower index = higher authority (cannot import upward)
# Matches structure_blueprint.py subfolders order for agentic_core
# NAMING FIXED: GRAVITY_LAYERS → gravity_layers
gravity_layers = [
    "L0_maintenance",     # Bedrock
    "config",             # Blueprints
    "utils",              # Core helpers
    "runtime",            # Infrastructure
    "schemas",            # Contracts (if present)
    "L1_cognition",       # Thought
    "L2_execution",       # Action
    "L3_orchestration",   # Management
    "L4_state",           # Persistence
    "L5_safety",          # Shield
    "semantic_memory",    # Long-term context
    "knowledge"           # RAG assets
]

# NAMING FIXED: GravityComplianceValidator → gravity_compliance_validator
class gravity_compliance_validator:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, project_root: Path):
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

    def run(self):
                    
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

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent  # Assumes script in /scripts/
    validator = GravityComplianceValidator(PROJECT_ROOT)
    success = validator.run()
    exit(0 if success else 1)
