"""
Phase 3: SSOT Structure Validation
===================================
Verifies agent paths against structure_blueprint.py SSOT definitions.

This module provides:
1. Path validation against SOVEREIGN_TERRITORIES
2. Layer assignment correctness verification (L0-L6)
3. Base agent location compliance (must be in agentic_core/base_agents/)
4. Depth validation per territory
5. Forbidden pattern detection

USAGE:
    from agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer import (
        SSOTStructureValidator
    )
    validator = SSOTStructureValidator()
    result = validator.validate_structure()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    L4_APPROVED_FOLDERS,
    SOVEREIGN_TERRITORIES,
    VARIABLE_DEPTH_SUBFOLDERS,
)
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    AgentInfo,
    RegistryVerifier,
)

# Base agent location requirement
BASE_AGENT_REQUIRED_PATH: Final[str] = "agentic_core/base_agents"

# Layer prefix patterns
LAYER_PATTERNS: Final[dict[str, str]] = {
    "L0": "L0_routing",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}


@dataclass
class StructureViolation:
    """A single structure violation."""

    agent_class: str
    agent_path: str
    violation_type: str
    message: str
    severity: str = "warning"  # warning, error, critical
    suggested_fix: str = ""


@dataclass
class StructureValidationResult:
    """Result of SSOT structure validation."""

    total_agents: int = 0
    compliant_agents: int = 0
    violations: list[StructureViolation] = field(default_factory=list)
    base_agent_violations: list[StructureViolation] = field(default_factory=list)
    layer_violations: list[StructureViolation] = field(default_factory=list)
    depth_violations: list[StructureViolation] = field(default_factory=list)
    territory_violations: list[StructureViolation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage."""
        if self.total_agents == 0:
            return 0.0
        return (self.compliant_agents / self.total_agents) * 100

    @property
    def is_fully_compliant(self) -> bool:
        """Check if all agents are compliant."""
        return len(self.violations) == 0


class SSOTStructureValidator:
    """Validates agent structure against SSOT definitions."""

    def __init__(self, project_root: Path | None = None):
        """Initialize validator with project root."""
        self.verifier = RegistryVerifier(project_root)
        self.project_root = self.verifier.project_root

    def _normalize_path(self, path: str) -> str:
        """Normalize path separators to forward slashes."""
        return path.replace("\\", "/")

    def _get_territory(self, path: str) -> str | None:
        """Get the territory for a given path."""
        normalized = self._normalize_path(path)
        parts = normalized.split("/")

        if not parts:
            return None

        first_part = parts[0]

        # Check against known territories
        if first_part in SOVEREIGN_TERRITORIES:
            return first_part

        return None

    def _get_expected_depth(self, territory: str) -> int:
        """Get expected depth for a territory."""
        if territory not in SOVEREIGN_TERRITORIES:
            return 2  # Default depth

        territory_def = SOVEREIGN_TERRITORIES[territory]
        return territory_def.get("depth", 2)

    def _get_actual_depth(self, path: str) -> int:
        """Get actual depth of a file path."""
        normalized = self._normalize_path(path)
        parts = [p for p in normalized.split("/") if p]
        return len(parts)

    def _is_base_agent(self, class_name: str) -> bool:
        """Check if class name indicates a base agent."""
        return class_name.endswith("BaseAgent")

    def _is_in_variable_depth_folder(self, path: str) -> bool:
        """Check if path is in a variable depth folder."""
        normalized = self._normalize_path(path)
        parts = normalized.split("/")

        for part in parts:
            if part in VARIABLE_DEPTH_SUBFOLDERS:
                return True
        return False

    def _is_in_l4_approved_folder(self, path: str) -> bool:
        """Check if path is in an L4 approved folder."""
        normalized = self._normalize_path(path)

        for approved in L4_APPROVED_FOLDERS:
            if normalized.startswith(approved):
                return True
        return False

    def _validate_base_agent_location(self, agent: AgentInfo) -> StructureViolation | None:
        """Validate that base agents are in the correct location."""
        if not self._is_base_agent(agent.class_name):
            return None

        normalized = self._normalize_path(agent.relative_path)

        if not normalized.startswith(BASE_AGENT_REQUIRED_PATH):
            return StructureViolation(
                agent_class=agent.class_name,
                agent_path=agent.relative_path,
                violation_type="base_agent_location",
                message=f"Base agent must be in {BASE_AGENT_REQUIRED_PATH}/",
                severity="critical",
                suggested_fix=f"Move to {BASE_AGENT_REQUIRED_PATH}/{agent.class_name}.py",
            )
        return None

    def _validate_layer_assignment(self, agent: AgentInfo) -> StructureViolation | None:
        """Validate that agent layer matches its path."""
        normalized = self._normalize_path(agent.relative_path)

        # Skip non-agentic_core agents
        if not normalized.startswith(AGENTIC_CORE_DIR):
            return None

        # Extract layer from path
        parts = normalized.split("/")
        if len(parts) < 2:
            return None

        path_layer = None
        for layer_prefix, layer_dir in LAYER_PATTERNS.items():
            if layer_dir in parts:
                path_layer = layer_prefix
                break

        # Check if agent.layer matches path layer
        if path_layer and agent.layer != path_layer:
            # Only flag if agent has a layer assigned
            if agent.layer not in ["Unknown", "Root", path_layer]:
                return StructureViolation(
                    agent_class=agent.class_name,
                    agent_path=agent.relative_path,
                    violation_type="layer_mismatch",
                    message=f"Agent layer '{agent.layer}' doesn't match path layer '{path_layer}'",
                    severity="warning",
                    suggested_fix=f"Update agent layer to '{path_layer}'",
                )
        return None

    def _validate_depth(self, agent: AgentInfo) -> StructureViolation | None:
        """Validate path depth against territory requirements."""
        normalized = self._normalize_path(agent.relative_path)
        territory = self._get_territory(normalized)

        if not territory:
            return None

        expected_depth = self._get_expected_depth(territory)
        actual_depth = self._get_actual_depth(normalized)

        # Allow variable depth folders
        if self._is_in_variable_depth_folder(normalized):
            return None

        # Allow L4 approved folders
        if self._is_in_l4_approved_folder(normalized):
            return None

        # Check if depth exceeds expected
        if actual_depth > expected_depth + 1:
            return StructureViolation(
                agent_class=agent.class_name,
                agent_path=agent.relative_path,
                violation_type="depth_violation",
                message=f"Path depth {actual_depth} exceeds territory max {expected_depth + 1}",
                severity="warning",
                suggested_fix="Consider restructuring to reduce nesting depth",
            )
        return None

    def _validate_territory(self, agent: AgentInfo) -> StructureViolation | None:
        """Validate agent is in a recognized territory."""
        normalized = self._normalize_path(agent.relative_path)
        territory = self._get_territory(normalized)

        if not territory:
            # Check if it's a root-level file
            parts = normalized.split("/")
            if len(parts) == 1:
                return StructureViolation(
                    agent_class=agent.class_name,
                    agent_path=agent.relative_path,
                    violation_type="root_file",
                    message="Agent file at repository root - should be in a territory",
                    severity="error",
                    suggested_fix="Move to appropriate territory (e.g., agentic_core/)",
                )

            # Unknown territory
            first_part = parts[0] if parts else "unknown"
            return StructureViolation(
                agent_class=agent.class_name,
                agent_path=agent.relative_path,
                violation_type="unknown_territory",
                message=f"Path starts with unrecognized territory: {first_part}",
                severity="warning",
                suggested_fix="Move to a recognized territory",
            )
        return None

    def _validate_forbidden_patterns(self, agent: AgentInfo) -> StructureViolation | None:
        """Check for forbidden patterns in path."""
        normalized = self._normalize_path(agent.relative_path)
        territory = self._get_territory(normalized)

        if not territory or territory not in SOVEREIGN_TERRITORIES:
            return None

        territory_def = SOVEREIGN_TERRITORIES[territory]
        forbidden = territory_def.get("forbidden_patterns", [])

        for pattern in forbidden:
            if pattern in normalized:
                return StructureViolation(
                    agent_class=agent.class_name,
                    agent_path=agent.relative_path,
                    violation_type="forbidden_pattern",
                    message=f"Path contains forbidden pattern: {pattern}",
                    severity="error",
                    suggested_fix=f"Remove or rename to avoid pattern: {pattern}",
                )
        return None

    def validate_agent(self, agent: AgentInfo) -> list[StructureViolation]:
        """Validate a single agent against all SSOT rules."""
        violations = []

        # Run all validations
        base_violation = self._validate_base_agent_location(agent)
        if base_violation:
            violations.append(base_violation)

        layer_violation = self._validate_layer_assignment(agent)
        if layer_violation:
            violations.append(layer_violation)

        depth_violation = self._validate_depth(agent)
        if depth_violation:
            violations.append(depth_violation)

        territory_violation = self._validate_territory(agent)
        if territory_violation:
            violations.append(territory_violation)

        forbidden_violation = self._validate_forbidden_patterns(agent)
        if forbidden_violation:
            violations.append(forbidden_violation)

        return violations

    def validate_structure(self) -> StructureValidationResult:
        """Perform full SSOT structure validation."""
        result = StructureValidationResult()

        # Get all agents
        agents = self.verifier.scan_filesystem()
        result.total_agents = len(agents)

        # Validate each agent
        for agent in agents:
            agent_violations = self.validate_agent(agent)

            if agent_violations:
                result.violations.extend(agent_violations)

                # Categorize violations
                for v in agent_violations:
                    if v.violation_type == "base_agent_location":
                        result.base_agent_violations.append(v)
                    elif v.violation_type == "layer_mismatch":
                        result.layer_violations.append(v)
                    elif v.violation_type == "depth_violation":
                        result.depth_violations.append(v)
                    elif v.violation_type in ["root_file", "unknown_territory"]:
                        result.territory_violations.append(v)
            else:
                result.compliant_agents += 1

        return result

    def generate_report(self, result: StructureValidationResult) -> str:
        """Generate markdown report from validation result."""
        lines = [
            "# Phase 3: SSOT Structure Validation Report",
            "",
            "## Summary",
            "",
            f"- **Total Agents:** {result.total_agents}",
            f"- **Compliant Agents:** {result.compliant_agents}",
            f"- **Compliance:** {result.compliance_percentage:.1f}%",
            f"- **Total Violations:** {len(result.violations)}",
            "",
            "### Violation Breakdown",
            "",
            "| Category | Count |",
            "|----------|-------|",
            f"| Base Agent Location | {len(result.base_agent_violations)} |",
            f"| Layer Mismatch | {len(result.layer_violations)} |",
            f"| Depth Violations | {len(result.depth_violations)} |",
            f"| Territory Violations | {len(result.territory_violations)} |",
            "",
        ]

        # Critical violations (base agent location)
        if result.base_agent_violations:
            lines.extend(
                [
                    "## Critical: Base Agent Location Violations",
                    "",
                    "| Agent | Current Path | Suggested Fix |",
                    "|-------|--------------|---------------|",
                ],
            )
            for v in result.base_agent_violations:
                lines.append(f"| {v.agent_class} | {v.agent_path} | {v.suggested_fix} |")
            lines.append("")

        # Territory violations
        if result.territory_violations:
            lines.extend(
                [
                    "## Territory Violations",
                    "",
                    "| Agent | Path | Issue |",
                    "|-------|------|-------|",
                ],
            )
            for v in result.territory_violations[:20]:
                lines.append(f"| {v.agent_class} | {v.agent_path} | {v.message} |")
            if len(result.territory_violations) > 20:
                remaining = len(result.territory_violations) - 20
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")

        # Layer violations
        if result.layer_violations:
            lines.extend(
                [
                    "## Layer Assignment Violations",
                    "",
                    "| Agent | Path | Issue |",
                    "|-------|------|-------|",
                ],
            )
            for v in result.layer_violations[:20]:
                lines.append(f"| {v.agent_class} | {v.agent_path} | {v.message} |")
            if len(result.layer_violations) > 20:
                remaining = len(result.layer_violations) - 20
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")

        # Depth violations
        if result.depth_violations:
            lines.extend(
                [
                    "## Depth Violations",
                    "",
                    "| Agent | Path | Issue |",
                    "|-------|------|-------|",
                ],
            )
            for v in result.depth_violations[:20]:
                lines.append(f"| {v.agent_class} | {v.agent_path} | {v.message} |")
            if len(result.depth_violations) > 20:
                remaining = len(result.depth_violations) - 20
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")

        return "\n".join(lines)


def run_structure_validation() -> StructureValidationResult:
    """Run SSOT structure validation and return result."""
    validator = SSOTStructureValidator()
    return validator.validate_structure()


if __name__ == "__main__":
    validator = SSOTStructureValidator()
    result = validator.validate_structure()
    report = validator.generate_report(result)
    print(report)
