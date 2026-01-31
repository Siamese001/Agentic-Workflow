#!/usr/bin/env python3
"""
Nuclear Audit: Comprehensive Agent Analysis for agentic_core/

Scans all agents in agentic_core/ and generates technical status table with:
- Agent Name (Full Class Name)
- Inheritance (SovereignBaseAgent verification)
- Mixin Verification (SubatomicTestingMixin, HealingStrategyMixin imports)
- heal() Signature (violation: dict parameter check)
- Primary Dependencies (agents/SDKs called)
- Namespace (SSOT folder verification)
- Status (Ready, Broken Import, Signature Mismatch, Stub)
"""

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

# Import SSOT for namespace validation
from agentic_core.L5_safety.validators.structure_blueprint import (
    CORE_SUBFOLDER_MAP,
    L4_APPROVED_FOLDERS,
    SOVEREIGN_TERRITORIES,
)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@dataclass
class AgentAuditResult:
    """Results from auditing a single agent."""

    agent_name: str
    file_path: str
    inheritance: str
    has_subatomic_testing: bool
    has_healing_strategy: bool
    heal_signature: str
    dependencies: list[str]
    namespace: str
    namespace_valid: bool
    status: str
    issues: list[str]


class NuclearAuditAgent:
    """Performs comprehensive nuclear audit of all agents."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agentic_core_dir = project_root / "agentic_core"

        # Load structure blueprint for namespace validation
        self.structure_blueprint = self._load_structure_blueprint()

        # Results storage
        self.results: list[AgentAuditResult] = []

    def _load_structure_blueprint(self) -> dict:
        """Load structure blueprint for namespace validation."""
        # Return the SSOT from structure_blueprint.py
        return CORE_SUBFOLDER_MAP

    def _find_agent_files(self) -> list[Path]:
        """Find all Python files containing agent classes."""
        agent_files = []
        for py_file in self.agentic_core_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Quick check for agent-like content
                if "class" in content and ("Agent" in content or "Mixin" in content):
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if node.name.endswith("Agent") or "Mixin" in node.name:
                                agent_files.append(py_file)
                                break
            except Exception as e:
                logger.warning(f"Failed to parse {py_file}: {e}")

        return sorted(set(agent_files))

    def _is_agent_class(self, node: ast.ClassDef) -> bool:
        """Determine if class is an agent (not Protocol/Mixin)."""
        # Exclude Protocols
        if any(base.id == "Protocol" for base in node.bases if isinstance(base, ast.Name)):
            return False

        # Exclude Mixins (by naming convention)
        if node.name.endswith("Mixin"):
            return False

        # Include only classes ending with 'Agent' or 'BaseAgent'
        return node.name.endswith("Agent") or node.name.endswith("BaseAgent")

    def _validate_namespace(self, file_path: Path, class_name: str) -> tuple[str, bool]:
        """Validate agent namespace against SSOT."""
        # Get relative path from project root
        rel_path = file_path.relative_to(self.project_root)
        parts = rel_path.parts

        # Normalize path to use forward slashes
        namespace_str = str(Path(*parts[:-1])).replace("\\", "/")

        # Constitutional check: Base agents MUST be in agentic_core/base_agents/
        if class_name.endswith("BaseAgent"):
            expected = "agentic_core/base_agents"
            is_valid = namespace_str == expected
            return namespace_str, is_valid

        # Check against SOVEREIGN_TERRITORIES
        if len(parts) >= 2 and parts[0] == "agentic_core":
            if len(parts) >= 3:
                layer_folder = parts[2]
                subfolder = parts[3] if len(parts) > 3 else None

                # Check if layer is in CORE_SUBFOLDER_MAP
                if layer_folder in self.structure_blueprint:
                    valid_subfolders = self.structure_blueprint[layer_folder]
                    if subfolder is None or subfolder in valid_subfolders:
                        return namespace_str, True
                    else:
                        # Check if it's an L4 approved folder
                        full_path = f"agentic_core/{layer_folder}/{subfolder}"
                        if full_path in L4_APPROVED_FOLDERS:
                            return namespace_str, True
                        return namespace_str, False
                else:
                    return namespace_str, False
            else:
                return namespace_str, False
        else:
            # Not in agentic_core - check other territories
            if parts[0] in SOVEREIGN_TERRITORIES:
                return namespace_str, True
            return namespace_str, False

    def _check_inheritance(self, node: ast.ClassDef) -> dict:
        """Check inheritance chain."""
        # Special case: SovereignBaseAgent is the root
        if node.name == "SovereignBaseAgent":
            return {"status": "ROOT", "message": "Root of inheritance hierarchy"}

        # Extract inheritance chain
        inheritance_chain = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance_chain.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance_chain.append(ast.unparse(base))

        # Check for SovereignBaseAgent inheritance
        has_sovereign = any("SovereignBaseAgent" in base for base in inheritance_chain)

        if has_sovereign:
            return {
                "status": "VALID",
                "chain": inheritance_chain,
                "message": "Valid SovereignBaseAgent inheritance",
            }
        else:
            return {
                "status": "BROKEN",
                "chain": inheritance_chain,
                "message": "Missing SovereignBaseAgent inheritance",
            }

    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef) -> AgentAuditResult:
        """Analyze a single agent class."""
        class_name = class_node.name
        rel_path = file_path.relative_to(self.project_root)

        # Initialize result
        result = AgentAuditResult(
            agent_name=class_name,
            file_path=str(rel_path),
            inheritance="Unknown",
            has_subatomic_testing=False,
            has_healing_strategy=False,
            heal_signature="Not found",
            dependencies=[],
            namespace=str(rel_path.parent),
            namespace_valid=False,
            status="Ready",
            issues=[],
        )

        # Analyze inheritance using new helper
        inheritance_result = self._check_inheritance(class_node)
        result.inheritance = ", ".join(inheritance_result.get("chain", []))

        if inheritance_result["status"] == "BROKEN":
            result.issues.append("Missing SovereignBaseAgent inheritance")
            result.status = "Broken Import"
        elif inheritance_result["status"] == "ROOT":
            # SovereignBaseAgent itself - don't flag as broken
            pass

        # Check for mixin imports
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            result.has_subatomic_testing = "SubatomicTestingMixin" in content
            result.has_healing_strategy = "HealingStrategyMixin" in content

            # Analyze heal() method signature
            heal_methods = [
                node
                for node in class_node.body
                if isinstance(node, ast.FunctionDef) and node.name == "heal"
            ]
            if heal_methods:
                heal_method = heal_methods[0]
                args = [arg.arg for arg in heal_method.args.args]
                if (
                    "violation" in args and "dict" in str(heal_method.args.args[1])
                    if len(heal_method.args.args) > 1
                    else False
                ):
                    result.heal_signature = "heal(self, violation: dict)"
                else:
                    result.heal_signature = f"heal({', '.join(args)})"
                    if "violation" not in args:
                        result.issues.append("heal() method missing 'violation: dict' parameter")
                        result.status = "Signature Mismatch"
            elif (
                inheritance_result["status"] == "VALID"
            ):  # Should have heal method if inheriting from SovereignBaseAgent
                result.issues.append("Missing heal() method")
                result.status = "Signature Mismatch"

            # Extract dependencies
            imports = re.findall(r"from\s+([^\s]+)\s+import|import\s+([^\s]+)", content)
            for import_match in imports:
                module = import_match[0] or import_match[1]
                if "Agent" in module or any(x in module for x in ["sdk", "api", "external"]):
                    result.dependencies.append(module)

        except Exception as e:
            result.issues.append(f"File analysis error: {e}")
            result.status = "Broken Import"

        # Validate namespace using new helper
        namespace, namespace_valid = self._validate_namespace(file_path, class_name)
        result.namespace = namespace
        result.namespace_valid = namespace_valid

        if not namespace_valid:
            result.issues.append(f"Invalid namespace: {namespace}")
            if result.status == "Ready":
                result.status = "Signature Mismatch"

        # Check for stub status
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if "TODO" in content or "FIXME" in content or "STUB" in content.upper():
                if result.status == "Ready":
                    result.status = "Stub"
                    result.issues.append("Contains TODO/FIXME/STUB markers")

            # Check for pass-only methods
            if re.search(r"def\s+\w+\s*\([^)]*\)\s*:\s*pass", content):
                if result.status == "Ready":
                    result.status = "Stub"
                    result.issues.append("Contains pass-only methods")

        except Exception:
            pass

        return result

    def run_audit(self) -> list[AgentAuditResult]:
        """Run comprehensive nuclear audit."""
        print("Starting Nuclear Audit of agentic_core/...")

        agent_files = self._find_agent_files()
        print(f"Found {len(agent_files)} agent files to analyze")

        for file_path in agent_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Exclude Protocols and Mixins from audit
                        if self._is_agent_class(node):
                            result = self._analyze_class(file_path, node)
                            self.results.append(result)

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        print(f"Analyzed {len(self.results)} agent classes")
        return self.results

    def generate_markdown_table(self) -> str:
        """Generate comprehensive markdown status table."""
        if not self.results:
            return "No results found."

        # Sort by status (priority first) then by namespace
        priority_order = {"Broken Import": 0, "Signature Mismatch": 1, "Stub": 2, "Ready": 3}
        sorted_results = sorted(
            self.results, key=lambda x: (priority_order.get(x.status, 4), x.namespace, x.agent_name)
        )

        # Generate table header
        table = [
            "# Nuclear Audit Results: agentic_core/ Agent Technical Status\n",
            "Generated comprehensive analysis of all agents in agentic_core/ directory.\n",
            "## Summary Statistics\n",
            f"- **Total Agents**: {len(self.results)}",
            f"- **Ready**: {len([r for r in self.results if r.status == 'Ready'])}",
            f"- **Broken Import**: {len([r for r in self.results if r.status == 'Broken Import'])}",
            f"- **Signature Mismatch**: "
            f"{len([r for r in self.results if r.status == 'Signature Mismatch'])}",
            f"- **Stub**: {len([r for r in self.results if r.status == 'Stub'])}",
            "",
            "## Detailed Technical Status Table\n",
            "| Agent Name | Inheritance | Mixin Verification | "
            "heal() Signature | Primary Dependencies | Namespace | Status | Issues |",
            "|------------|-------------|-------------------|------------------|-------------------|----------|--------|---------|",
        ]

        # Generate table rows
        for result in sorted_results:
            # Format mixins
            mixins = []
            if result.has_subatomic_testing:
                mixins.append("[OK] SubatomicTesting")
            if result.has_healing_strategy:
                mixins.append("[OK] HealingStrategy")
            mixins_str = ", ".join(mixins) if mixins else "[MISSING]"

            # Format dependencies
            deps_str = ", ".join(result.dependencies[:3])  # Limit to first 3
            if len(result.dependencies) > 3:
                deps_str += f" (+{len(result.dependencies) - 3})"

            # Format namespace with validation indicator
            namespace_str = (
                f"{result.namespace} {'[OK]' if result.namespace_valid else '[INVALID]'}"
            )

            # Format status with indicator
            status_indicator = {
                "Ready": "[OK]",
                "Broken Import": "[CRITICAL]",
                "Signature Mismatch": "[WARNING]",
                "Stub": "[INFO]",
            }
            status_str = f"{status_indicator.get(result.status, '[UNKNOWN]')} {result.status}"

            # Highlight problematic rows
            row_prefix = "**" if result.status in ["Broken Import", "Signature Mismatch"] else ""
            row_suffix = "**" if result.status in ["Broken Import", "Signature Mismatch"] else ""

            issues_str = "; ".join(result.issues[:2])  # Limit to first 2 issues
            if len(result.issues) > 2:
                issues_str += f" (+{len(result.issues) - 2})"

            table.append(
                f"| {row_prefix}{result.agent_name}{row_suffix} | "
                f"{result.inheritance} | "
                f"{mixins_str} | "
                f"{result.heal_signature} | "
                f"{deps_str} | "
                f"{namespace_str} | "
                f"{status_str} | "
                f"{issues_str} |"
            )

        # Add high-priority remediation section
        problematic = [
            r for r in self.results if r.status in ["Broken Import", "Signature Mismatch"]
        ]
        if problematic:
            table.extend(
                [
                    "",
                    "## High-Priority Remediation Targets",
                    "",
                    "The following agents require immediate attention:",
                    "",
                ]
            )

            for result in problematic:
                table.extend(
                    [
                        f"### **{result.agent_name}** ({result.status})",
                        f"- **File**: `{result.file_path}`",
                        f"- **Issues**: {'; '.join(result.issues)}",
                        f"- **Inheritance**: {result.inheritance}",
                        f"- **Namespace**: {result.namespace}",
                        "",
                    ]
                )

        return "\n".join(table)


def main():
    """Main entry point for nuclear audit."""
    project_root = Path.cwd()

    # Verify we're in the right directory
    if not (project_root / "agentic_core").exists():
        print("Error: Must be run from project root with agentic_core/ directory")
        return

    # Run audit
    auditor = NuclearAuditAgent(project_root)
    results = auditor.run_audit()

    # Generate and save report
    report = auditor.generate_markdown_table()

    # Save to file
    report_file = project_root / "NUCLEAR_AUDIT_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Nuclear audit complete! Report saved to: {report_file}")

    # Print summary
    broken = len([r for r in results if r.status == "Broken Import"])
    mismatch = len([r for r in results if r.status == "Signature Mismatch"])

    if broken > 0 or mismatch > 0:
        print(
            f"Found {broken} broken imports and {mismatch} "
            f"signature mismatches - immediate attention required!"
        )
    else:
        print("All agents passed basic validation!")


if __name__ == "__main__":
    main()
