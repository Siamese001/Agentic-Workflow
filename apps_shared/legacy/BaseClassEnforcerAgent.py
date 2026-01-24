#!/usr/bin/env python3
"""@deprecated
DEPRECATED: Use CodeStandardsEnforcerAgent instead.

This agent has been consolidated into CodeStandardsEnforcerAgent as part of
Phase 4 consolidation (2026-01-19). This file is retained for backward
compatibility during the transition period.

Migration:
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        CodeStandardsEnforcerAgent,
        get_code_standards_enforcer,
        check_inheritance,
    )
"""

import warnings

warnings.warn(
    "BaseClassEnforcerAgent is deprecated. Use CodeStandardsEnforcerAgent instead.",
    DeprecationWarning,
    stacklevel=2,
)

"""
BaseClassEnforcerAgent - Enforces one-base-class-per-layer best practice.

Best Practice:
- Each agent in L0-L5 layer directories SHOULD inherit from its canonical layer base:
  - L0_maintenance agents → L0MaintenanceBaseAgent
  - L1_cognition agents → L1CognitionBaseAgent
  - L2_execution agents → L2Agent
  - L3_orchestration agents → L3Agent
  - L4_state agents → L4Agent
  - L5_safety agents → L5Agent

- Layer bases already include all required mixins (HealerMixin, MCPHardenedMixin, etc.)
- Inheriting from layer base ensures consistent behavior across all agents

This agent:
1. Scans agent_discovery_full.json for layer agents
2. Reports violations (agents not using canonical layer base)
3. Can auto-heal by updating imports and class definitions (with --execute)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately


import json
import re

    AGENT_DISCOVERY_JSON,
    TESTS_DIR,
)


@dataclass
class BaseClassEnforcerAgent(L5Agent):
    """
    Enforces one-base-class-per-layer inheritance pattern.

    Validates that agents in layer directories inherit from their
    canonical layer base class (L0MaintenanceBaseAgent, L1CognitionBaseAgent, etc.).
    """

    name: str = "BaseClassEnforcerAgent"
    layer: str = "L5"
    project_root: Path = field(default_factory=Path.cwd)

    # Canonical layer bases
    LAYER_BASES: dict[str, str] = field(
        default_factory=lambda: {
            "L0": "L0MaintenanceBaseAgent",
            "L1": "L1CognitionBaseAgent",
            "L2": "L2Agent",
            "L3": "L3Agent",
            "L4": "L4Agent",
            "L5": "L5Agent",
        }
    )

    # Layer directory patterns
    LAYER_PATTERNS: dict[str, str] = field(
        default_factory=lambda: {
            "L0_maintenance": "L0",
            "L1_cognition": "L1",
            "L2_execution": "L2",
            "L3_orchestration": "L3",
            "L4_state": "L4",
            "L5_safety": "L5",
        }
    )

    # Import statement for each layer base
    LAYER_IMPORTS: dict[str, str] = field(
        default_factory=lambda: {
            "L0": "from agentic_core.bases import L0MaintenanceBaseAgent",
            "L1": "from agentic_core.bases import L1CognitionBaseAgent",
            "L2": "from agentic_core.bases import L2Agent",
            "L3": "from agentic_core.bases import L3Agent",
            "L4": "from agentic_core.bases import L4Agent",
            "L5": "from agentic_core.bases import L5Agent",
        }
    )

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)

    def scan_violations(self) -> dict[str, Any]:
        """
        Scan for base class violations.

        Returns:
            Dict with violation summary and details
        """
        discovery_path = self.project_root / AGENT_DISCOVERY_JSON
        if not discovery_path.exists():
            return {"error": f"agent_discovery_full.json not found at {discovery_path}"}

        agents = json.loads(discovery_path.read_text(encoding="utf-8"))

        violations = []
        compliant = []

        for agent in agents:
            layer = agent.get("layer")
            if layer not in self.LAYER_BASES:
                continue

            expected_base = self.LAYER_BASES[layer]
            inheritance = agent.get("inheritance", [])

            if expected_base in inheritance:
                compliant.append(
                    {
                        "class_name": agent.get("class_name"),
                        "path": agent.get("path"),
                        "layer": layer,
                    }
                )
            else:
                violations.append(
                    {
                        "class_name": agent.get("class_name"),
                        "path": agent.get("path"),
                        "layer": layer,
                        "expected_base": expected_base,
                        "current_bases": inheritance[:5],  # First 5
                        "has_healer": "HealerMixin" in inheritance,
                        "has_mcp": "MCPHardenedMixin" in inheritance,
                    }
                )

        return {
            "total_layer_agents": len(violations) + len(compliant),
            "compliant_count": len(compliant),
            "violation_count": len(violations),
            "compliance_rate": round(
                len(compliant) / max(1, len(violations) + len(compliant)) * 100, 1
            ),
            "violations": violations,
            "compliant": compliant,
        }

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, Any]:
        """
        Heal base class violations by updating imports and class definitions.

        Args:
            dry_run: If True, only report what would be changed
            execute: If True, apply changes

        Returns:
            Dict with healing results
        """
        if _call_path is None:
            _call_path = set()

        # Invoke parent healing chain
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )

        scan_result = self.scan_violations()
        if "error" in scan_result:
            return scan_result

        violations = scan_result["violations"]
        healed = []
        failed = []

        for violation in violations:
            file_path = self.project_root / violation["path"]
            if not file_path.exists():
                failed.append({**violation, "reason": "file_not_found"})
                continue

            result = self._heal_single_agent(file_path, violation, dry_run, execute)
            if result.get("healed"):
                healed.append(result)
            else:
                failed.append(result)

        return {
            "dry_run": dry_run,
            "execute": execute,
            "total_violations": len(violations),
            "healed_count": len(healed),
            "failed_count": len(failed),
            "healed": healed if len(healed) <= 10 else healed[:10],
            "failed": failed if len(failed) <= 10 else failed[:10],
        }

    def _heal_single_agent(
        self, file_path: Path, violation: dict, dry_run: bool, execute: bool
    ) -> dict[str, Any]:
        """Heal a single agent file to use correct layer base."""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            layer = violation["layer"]
            expected_base = violation["expected_base"]
            class_name = violation["class_name"]
            layer_import = self.LAYER_IMPORTS[layer]

            # Step 1: Add import if not present
            if layer_import not in content:
                # Find insertion point (after other imports)
                import_pattern = r"^(from\s+\S+\s+import\s+.+|import\s+\S+)$"
                lines = content.split("\n")
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if re.match(import_pattern, line.strip()):
                        last_import_idx = i

                # Insert after last import
                lines.insert(last_import_idx + 1, layer_import)
                content = "\n".join(lines)

            # Step 2: Update class definition to inherit from layer base
            # Pattern: class ClassName(Base1, Base2, ...):
            class_pattern = rf"class\s+{re.escape(class_name)}\s*\(([^)]*)\)\s*:"
            match = re.search(class_pattern, content)

            if match:
                current_bases = match.group(1)
                # Add layer base as first parent if not present
                if expected_base not in current_bases:
                    if current_bases.strip():
                        new_bases = f"{expected_base}, {current_bases}"
                    else:
                        new_bases = expected_base

                    new_class_def = f"class {class_name}({new_bases}):"
                    content = re.sub(class_pattern, new_class_def, content)

            if content != original_content:
                if execute and not dry_run:
                    file_path.write_text(content, encoding="utf-8")

                return {
                    "class_name": class_name,
                    "path": str(violation["path"]),
                    "healed": True,
                    "changes": ["added_import", "updated_inheritance"],
                }

            return {
                "class_name": class_name,
                "path": str(violation["path"]),
                "healed": False,
                "reason": "no_changes_needed_or_pattern_not_matched",
            }

        except Exception as e:
            return {
                "class_name": violation["class_name"],
                "path": str(violation["path"]),
                "healed": False,
                "reason": str(e),
            }

    def validate(self, target: Any = None) -> dict[str, Any]:
        """Validate base class inheritance patterns."""
        result = self.scan_violations()
        result["valid"] = result.get("violation_count", 0) == 0
        return result

    def _run_self_tests(self) -> dict[str, Any]:
        """Self-tests for the enforcer."""
        super()._run_self_tests()

        # Test 1: Layer bases dict is complete
        assert len(self.LAYER_BASES) == 6, "Must have 6 layer bases (L0-L5)"

        # Test 2: Layer patterns match layer bases keys
        for pattern, layer in self.LAYER_PATTERNS.items():
            assert layer in self.LAYER_BASES, f"Pattern {pattern} maps to unknown layer {layer}"

        return {"status": "passed", TESTS_DIR: 2}


def get_base_class_enforcer(project_root: Path = None) -> BaseClassEnforcerAgent:
    """Factory function to get a BaseClassEnforcerAgent instance."""
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent.parent
    return BaseClassEnforcerAgent(project_root=project_root)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Base Class Enforcer Agent")
    parser.add_argument("--scan", action="store_true", help="Scan for violations")
    parser.add_argument("--heal", action="store_true", help="Heal violations (dry-run)")
    parser.add_argument("--execute", action="store_true", help="Execute healing changes")
    args = parser.parse_args()

    enforcer = get_base_class_enforcer()

    if args.scan or (not args.heal):
        result = enforcer.scan_violations()
        print("\n=== Base Class Enforcement Report ===")
        print(f"Total Layer Agents: {result.get('total_layer_agents', 0)}")
        print(f"Compliant: {result.get('compliant_count', 0)}")
        print(f"Violations: {result.get('violation_count', 0)}")
        print(f"Compliance Rate: {result.get('compliance_rate', 0)}%")

        if result.get("violations"):
            print("\nSample Violations:")
            for v in result["violations"][:10]:
                print(f"  {v['class_name']} in {v['layer']}: expected {v['expected_base']}")
                print(f"    current: {v['current_bases']}")

    if args.heal:
        result = enforcer.heal_repository(dry_run=not args.execute, execute=args.execute)
        mode = "EXECUTE" if args.execute else "DRY-RUN"
        print(f"\n=== Base Class Healing ({mode}) ===")
        print(f"Total Violations: {result.get('total_violations', 0)}")
        print(f"Healed: {result.get('healed_count', 0)}")
        print(f"Failed: {result.get('failed_count', 0)}")
