#!/usr/bin/env python3
"""
NUCLEAR AUDIT: Comprehensive Agent Technical Status Analysis

Performs deep technical analysis of all agents in agentic_core/ to identify:
1. SovereignBaseAgent inheritance compliance
2. heal() method signature compliance
3. Namespace/structure compliance
4. Import dependency integrity
5. Mixin pattern compliance
6. Abstract vs concrete agent classification

Generated technical status table provides complete visibility into agent health.
"""

import ast
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class AgentTechnicalStatus:
    """Technical status data for a single agent."""

    class_name: str
    file_path: str
    layer: str
    namespace_status: str = "[UNKNOWN]"
    inheritance_status: str = "[UNKNOWN]"
    heal_method_status: str = "[UNKNOWN]"
    import_status: str = "[UNKNOWN]"
    mixin_status: str = "[UNKNOWN]"
    agent_type: str = "[UNKNOWN]"
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    line_count: int = 0
    complexity_score: float = 0.0


class NuclearAuditor:
    """Comprehensive agent technical status auditor."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agentic_core_dir = project_root / "agentic_core"
        self.structure_blueprint = self._load_structure_blueprint()
        self.agent_statuses: list[AgentTechnicalStatus] = []

        # Critical base classes and mixins to check
        self.critical_base_classes = {
            "SovereignBaseAgent",
            "L0MaintenanceBaseAgent",
            "L1CognitionBaseAgent",
            "L2ExecutionBaseAgent",
            "L3OrchestrationBaseAgent",
            "L4StateBaseAgent",
            "L5SafetyBaseAgent",
            "L6ObservabilityBaseAgent",
        }

        self.critical_mixins = {
            "SubatomicTestingMixin",
            "HealerMixin",
            "ValidatorMixin",
            "infrastructure_mixin",
            "ConfigMixin",
            "LLMProviderMixin",
            "EmbeddingMixin",
            "HealingStrategyMixin",
        }

    def _load_structure_blueprint(self) -> dict[str, Any]:
        """Load structure blueprint for namespace validation."""
        try:
            blueprint_path = (
                self.agentic_core_dir / "L5_safety" / "validators" / "structure_blueprint.py"
            )
            if blueprint_path.exists():
                with open(blueprint_path, encoding="utf-8") as f:
                    content = f.read()
                # Parse the SOVEREIGN_TERRITORIES from the file
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (
                                isinstance(target, ast.Name)
                                and target.id == "SOVEREIGN_TERRITORIES"
                            ):
                                return ast.literal_eval(node.value)
        except Exception as e:
            logger.warning(f"Failed to load structure blueprint: {e}")

        return {}

    def audit_all_agents(self) -> list[AgentTechnicalStatus]:
        """Perform comprehensive audit of all agents in agentic_core/."""
        logger.info("Starting nuclear audit of agentic_core/ agents...")

        # Find all Python files in agentic_core
        python_files = list(self.agentic_core_dir.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            try:
                agents = self._analyze_file(file_path)
                self.agent_statuses.extend(agents)
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        logger.info(f"Analyzed {len(self.agent_statuses)} agent classes")
        return self.agent_statuses

    def _analyze_file(self, file_path: Path) -> list[AgentTechnicalStatus]:
        """Analyze a single Python file for agent classes."""
        agents = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    status = self._analyze_agent_class(node, file_path, content)
                    agents.append(status)

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return agents

    def _analyze_agent_class(
        self, class_node: ast.ClassDef, file_path: Path, content: str,
    ) -> AgentTechnicalStatus:
        """Perform detailed analysis of a single agent class."""
        status = AgentTechnicalStatus(
            class_name=class_node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            layer=self._determine_layer(file_path),
            line_count=content.count("\n") + 1,
        )

        # 1. Namespace/Structure Compliance
        status.namespace_status = self._check_namespace_compliance(file_path)

        # 2. Inheritance Analysis
        status.inheritance_status = self._check_inheritance_compliance(class_node)

        # 3. heal() Method Analysis
        status.heal_method_status = self._check_heal_method_compliance(class_node)

        # 4. Import Dependency Analysis
        status.import_status = self._check_import_compliance(content, file_path)

        # 5. Mixin Pattern Analysis
        status.mixin_status = self._check_mixin_compliance(class_node)

        # 6. Agent Type Classification
        status.agent_type = self._classify_agent_type(class_node, content)

        # 7. Calculate complexity score
        status.complexity_score = self._calculate_complexity(class_node, content)

        # 8. Generate violations and recommendations
        self._generate_violations_and_recommendations(status)

        return status

    def _determine_layer(self, file_path: Path) -> str:
        """Determine the architectural layer for a file."""
        path_str = str(file_path)

        layer_mappings = {
            "L0_maintenance": "L0",
            "L1_cognition": "L1",
            "L2_execution": "L2",
            "L3_orchestration": "L3",
            "L4_state": "L4",
            "L5_safety": "L5",
            "L6_observability": "L6",
            "base_agents": "Base",
            "domain": "Domain",
        }

        for pattern, layer in layer_mappings.items():
            if pattern in path_str:
                return layer

        return "Unknown"

    def _check_namespace_compliance(self, file_path: Path) -> str:
        """Check if file location complies with structure blueprint."""
        relative_path = file_path.relative_to(self.project_root)
        path_parts = relative_path.parts

        if len(path_parts) < 2 or path_parts[0] != "agentic_core":
            return "[INVALID] - Outside agentic_core"

        if len(path_parts) >= 3:
            territory = "agentic_core"
            subfolder = path_parts[2]

            # Check if subfolder is valid in structure blueprint
            if territory in self.structure_blueprint:
                valid_subfolders = self.structure_blueprint[territory].get("subfolders", {})
                if isinstance(valid_subfolders, dict) and subfolder in valid_subfolders:
                    return "[VALID]"
                elif isinstance(valid_subfolders, list) and subfolder in valid_subfolders:
                    return "[VALID]"

        return "[INVALID]"

    def _check_inheritance_compliance(self, class_node: ast.ClassDef) -> str:
        """Check inheritance chain for proper base classes."""
        base_classes = []

        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.name)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base))

        # Check for critical base classes
        for critical_base in self.critical_base_classes:
            if critical_base in base_classes:
                return "[VALID]"

        # Check if it inherits from any *Agent class (indicating proper chain)
        for base in base_classes:
            if base.endswith("Agent") or base.endswith("Mixin"):
                return "[PARTIAL]"

        return "[BROKEN] - Missing SovereignBaseAgent inheritance"

    def _check_heal_method_compliance(self, class_node: ast.ClassDef) -> str:
        """Check heal() method signature compliance."""
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == "heal":
                # Check parameters
                args = [arg.arg for arg in node.args.args]

                # Should have 'self' and 'violation: dict' parameters
                if len(args) >= 2 and args[0] == "self":
                    # Check if violation parameter has proper typing
                    if "violation" in args:
                        return "[VALID]"
                    else:
                        return "[INVALID] - Wrong signature"

        return "[MISSING] - No heal() method"

    def _check_import_compliance(self, content: str, file_path: Path) -> str:
        """Check import dependencies for compliance."""
        try:
            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Check for critical imports
            has_sovereign_import = any("SovereignBaseAgent" in imp for imp in imports)
            has_proper_layer_import = any("agentic_core" in imp for imp in imports)

            if has_sovereign_import and has_proper_layer_import:
                return "[VALID]"
            elif has_proper_layer_import:
                return "[PARTIAL]"
            else:
                return "[BROKEN]"

        except Exception:
            return "[ERROR]"

    def _check_mixin_compliance(self, class_node: ast.ClassDef) -> str:
        """Check mixin pattern compliance."""
        base_classes = []

        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.name)

        # Check for critical mixins
        mixin_count = sum(1 for mixin in self.critical_mixins if mixin in base_classes)

        if mixin_count >= 2:  # Should have multiple mixins for proper functionality
            return "[VALID]"
        elif mixin_count >= 1:
            return "[PARTIAL]"
        else:
            return "[MISSING]"

    def _classify_agent_type(self, class_node: ast.ClassDef, content: str) -> str:
        """Classify agent as abstract, concrete, or stub."""
        # Check for abstract methods
        has_abstract = False
        has_pass_only = True

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                has_pass_only = False
                # Check for abstract decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.name in [
                        "abstractmethod",
                        "abc.abstractmethod",
                    ]:
                        has_abstract = True
            elif isinstance(node, ast.Pass):
                continue
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                # Docstring - doesn't count as implementation
                continue
            else:
                has_pass_only = False

        # Check for TODO/FIXME markers
        has_todo = any(marker in content.upper() for marker in ["TODO", "FIXME", "XXX", "HACK"])

        if has_abstract:
            return "Abstract"
        elif has_pass_only or has_todo:
            return "Stub"
        else:
            return "Concrete"

    def _calculate_complexity(self, class_node: ast.ClassDef, content: str) -> float:
        """Calculate complexity score for the agent."""
        # Simple complexity based on:
        # - Number of methods
        # - Number of base classes
        # - Cyclomatic complexity estimation

        method_count = len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
        base_count = len(class_node.bases)

        # Estimate cyclomatic complexity
        complexity_keywords = ["if", "elif", "for", "while", "try", "except", "with"]
        cyclomatic = sum(content.count(keyword) for keyword in complexity_keywords)

        return float(method_count + base_count + cyclomatic * 0.5)

    def _generate_violations_and_recommendations(self, status: AgentTechnicalStatus):
        """Generate violation list and recommendations based on analysis."""
        violations = []
        recommendations = []

        # Inheritance violations
        if "[BROKEN]" in status.inheritance_status:
            violations.append("Missing SovereignBaseAgent inheritance")
            recommendations.append("Add SovereignBaseAgent to class inheritance")

        # heal() method violations
        if "[MISSING]" in status.heal_method_status:
            violations.append("Missing heal() method")
            recommendations.append("Implement heal(self, violation: dict) -> dict method")
        elif "[INVALID]" in status.heal_method_status:
            violations.append("Incorrect heal() method signature")
            recommendations.append("Fix heal() method to match expected signature")

        # Namespace violations
        if "[INVALID]" in status.namespace_status:
            violations.append("Invalid namespace/location")
            recommendations.append("Move agent to proper directory per structure blueprint")

        # Import violations
        if "[BROKEN]" in status.import_status:
            violations.append("Broken import dependencies")
            recommendations.append("Fix import statements and dependencies")

        # Stub agent violations
        if status.agent_type == "Stub":
            violations.append("Agent is incomplete stub")
            recommendations.append("Complete agent implementation or mark as abstract")

        status.violations = violations
        status.recommendations = recommendations

    def generate_technical_status_table(self) -> str:
        """Generate comprehensive technical status table."""
        if not self.agent_statuses:
            return "No agents analyzed"

        # Sort by layer, then by status priority
        def sort_key(status):
            priority_order = {
                "[BROKEN]": 0,
                "[MISSING]": 1,
                "[INVALID]": 2,
                "[PARTIAL]": 3,
                "[VALID]": 4,
            }
            layer_order = {"Base": 0, "L0": 1, "L1": 2, "L2": 3, "L3": 4, "L4": 5, "L5": 6, "L6": 7}

            # Count critical issues
            critical_issues = sum(
                1
                for field in [status.inheritance_status, status.heal_method_status]
                if "[BROKEN]" in field or "[MISSING]" in field
            )

            return (
                critical_issues,
                layer_order.get(status.layer, 99),
                priority_order.get(status.inheritance_status, 99),
            )

        sorted_agents = sorted(self.agent_statuses, key=sort_key)

        # Generate table header
        table = []
        table.append("# NUCLEAR AUDIT REPORT: Agent Technical Status")
        table.append(f"Generated: {datetime.now().isoformat()}")
        table.append(f"Total Agents Analyzed: {len(self.agent_statuses)}")
        table.append("")

        # Summary statistics
        inheritance_broken = sum(
            1 for a in self.agent_statuses if "[BROKEN]" in a.inheritance_status
        )
        heal_missing = sum(1 for a in self.agent_statuses if "[MISSING]" in a.heal_method_status)
        namespace_invalid = sum(1 for a in self.agent_statuses if "[INVALID]" in a.namespace_status)
        stub_agents = sum(1 for a in self.agent_statuses if a.agent_type == "Stub")

        table.append("## Summary Statistics")
        table.append(f"- Broken Inheritance: {inheritance_broken} agents")
        table.append(f"- Missing heal() Method: {heal_missing} agents")
        table.append(f"- Invalid Namespace: {namespace_invalid} agents")
        table.append(f"- Stub/Incomplete Agents: {stub_agents} agents")
        table.append("")

        # Detailed table
        table.append("## Detailed Technical Status")
        table.append("")
        table.append(
            "| Agent | Layer | File | Inheritance | heal() | Namespace | Type | Complexity | Issues |",
        )
        table.append(
            "|-------|-------|------|-------------|--------|-----------|------|------------|--------|",
        )

        for status in sorted_agents:
            issues = len(status.violations)
            if issues > 0:
                issues_str = f"ISSUES {issues}"
            else:
                issues_str = "OK"

            table.append(
                f"| {status.class_name} | {status.layer} | {status.file_path} | "
                f"{status.inheritance_status} | {status.heal_method_status} | "
                f"{status.namespace_status} | {status.agent_type} | "
                f"{status.complexity_score:.1f} | {issues_str} |",
            )

        # Critical issues section
        table.append("")
        table.append("## Critical Issues Requiring Immediate Attention")
        table.append("")

        critical_agents = [
            a
            for a in sorted_agents
            if any(
                "[BROKEN]" in field or "[MISSING]" in field
                for field in [a.inheritance_status, a.heal_method_status]
            )
        ]

        for status in critical_agents:
            table.append(f"### CRITICAL: {status.class_name} ({status.layer})")
            table.append(f"**File:** `{status.file_path}`")
            table.append(f"**Issues:** {', '.join(status.violations)}")
            table.append(f"**Recommendations:** {', '.join(status.recommendations)}")
            table.append("")

        return "\n".join(table)

    def save_report(self, output_path: Path):
        """Save detailed audit report to file."""
        report = self.generate_technical_status_table()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Audit report saved to: {output_path}")


def main():
    """Main execution function."""
    project_root = Path(__file__).parent
    auditor = NuclearAuditor(project_root)

    # Perform comprehensive audit
    logger.info("🚀 Starting nuclear audit...")
    auditor.audit_all_agents()

    # Generate and save report
    report_path = project_root / "NUCLEAR_AUDIT_REPORT.md"
    auditor.save_report(report_path)

    # Print summary
    statuses = auditor.agent_statuses
    total = len(statuses)
    broken = sum(1 for s in statuses if "[BROKEN]" in s.inheritance_status)
    missing_heal = sum(1 for s in statuses if "[MISSING]" in s.heal_method_status)
    valid = sum(
        1
        for s in statuses
        if "[VALID]" in s.inheritance_status and "[VALID]" in s.heal_method_status
    )

    print("\n*** NUCLEAR AUDIT COMPLETE ***")
    print(f"Total Agents: {total}")
    print(f"Broken Inheritance: {broken} ({broken / total * 100:.1f}%)")
    print(f"Missing heal(): {missing_heal} ({missing_heal / total * 100:.1f}%)")
    print(f"Fully Compliant: {valid} ({valid / total * 100:.1f}%)")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
