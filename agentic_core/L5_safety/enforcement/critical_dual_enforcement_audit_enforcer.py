"""
CRITICAL Dual Enforcement Guarantee (REQ-416)

Ensures every CRITICAL requirement has >=2 enforcement layers including at least
one runtime (except ENFORCEMENT_CLASS=STRUCTURAL which requires >=1 CI/AST layer).
CI MUST read ENFORCEMENT_LAYERS and ENFORCEMENT_CLASS metadata per requirement
and fail if audit conditions unmet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR

Logger = logging.getLogger(__name__)

# Enforcement layer types
EnforcementLayer = Literal["AST", "Runtime", "CI", "Schema", "Signature", "Replay"]

# Enforcement classes
EnforcementClass = Literal["STRUCTURAL", "EXECUTION_PATH"]  # guardian: allow-magic-configuration

# Minimum enforcement layers required
# guardian: allow-magic-configuration
MIN_ENFORCEMENT_LAYERS = 2  # Minimum enforcement layers for CRITICAL requirements
MIN_STRUCTURAL_LAYERS = 1


@dataclass(frozen=True)
class RequirementMetadata:
    """Metadata for a requirement from the requirements document."""

    req_id: str
    domain: str
    requirement: str
    enforcement: str
    severity: str
    enforcement_layers: list[EnforcementLayer]
    enforcement_class: EnforcementClass


class DualEnforcementViolation(Exception):
    """Raised when dual enforcement guarantee is violated."""

    pass


class CriticalDualEnforcementAuditor:
    """Audits CRITICAL requirements for dual enforcement compliance (REQ-416)."""

    def __init__(self, requirements_path: Path | None = None):
        """Initialize the auditor.

        Args:
            requirements_path: Path to requirements document
        """
        if requirements_path is None:
            # Calculate path from agentic_core/L5_safety/enforcement/ to docs/reports/plans/
            self.requirements_path = (
                Path(__file__).resolve().parents[3]
                / "docs"
                / REPORTS_DIR
                / "plans"
                / "Agentic Master Requirements.md"
            )
        else:
            self.requirements_path = requirements_path

    def parse_requirements_metadata(self) -> dict[str, RequirementMetadata]:
        """Parse requirements from the markdown document.

        Returns:
            Dictionary mapping REQ-ID to RequirementMetadata
        """
        requirements = {}

        try:
            content = self.requirements_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Find the requirements table
            in_table = False
            for i, line in enumerate(lines):
                # Look for table header
                if (
                    "| Req ID | Domain | Requirement | Enforcement | Severity | ENFORCEMENT_LAYERS | ENFORCEMENT_CLASS |"
                    in line
                ):
                    in_table = True
                    continue

                if not in_table:
                    continue

                # Skip table header separator
                if "|--------" in line:
                    continue

                # Skip empty lines
                if not line.strip():
                    continue

                # Parse requirement row
                if line.startswith("| REQ-"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]  # Remove empty first/last

                    if len(parts) >= 7:
                        req_id = parts[0]
                        domain = parts[1]
                        requirement = parts[2]
                        enforcement = parts[3]
                        severity = parts[4]
                        layers_str = parts[5]
                        class_str = parts[6]

                        # Parse enforcement layers
                        enforcement_layers = []
                        if layers_str:
                            layers = [l.strip() for l in layers_str.split(",")]
                            for layer in layers:
                                layer = layer.strip()
                                if layer in ["AST", "Runtime", "CI", "Schema", "Signature", "Replay"]:
                                    enforcement_layers.append(layer)

                        # Parse enforcement class
                        enforcement_class = "EXECUTION_PATH"  # Default
                        if "STRUCTURAL" in class_str:
                            enforcement_class = "STRUCTURAL"

                        requirements[req_id] = RequirementMetadata(
                            req_id=req_id,
                            domain=domain,
                            requirement=requirement,
                            enforcement=enforcement,
                            severity=severity,
                            enforcement_layers=enforcement_layers,
                            enforcement_class=enforcement_class,
                        )

        except Exception as e:
            Logger.error(f"Failed to parse requirements: {e}")
            raise

        return requirements

    def audit_critical_requirements(self) -> dict[str, list[str]]:
        """Audit all CRITICAL requirements for dual enforcement compliance.

        Returns:
            Dictionary with "violations" and "warnings" keys containing lists of issues
        """
        requirements = self.parse_requirements_metadata()
        violations = []
        warnings = []

        for req_id, metadata in requirements.items():
            if metadata.severity != "CRITICAL":
                continue

            # Check enforcement layers count
            layer_count = len(metadata.enforcement_layers)

            if metadata.enforcement_class == "STRUCTURAL":
                # STRUCTURAL requirements need at least 1 CI/AST layer
                has_ci_or_ast = any(layer in ["CI", "AST"] for layer in metadata.enforcement_layers)
                if not has_ci_or_ast:
                    violations.append(
                        f"{req_id}: STRUCTURAL class requires at least 1 CI or AST layer, "
                        f"found: {metadata.enforcement_layers}"
                    )
                elif layer_count < MIN_STRUCTURAL_LAYERS:
                    warnings.append(
                        f"{req_id}: STRUCTURAL class has only {layer_count} enforcement layer(s), "
                        f"recommended minimum: {MIN_STRUCTURAL_LAYERS}"
                    )
            else:
                # EXECUTION_PATH requirements need at least 2 layers with 1 runtime
                has_runtime = "Runtime" in metadata.enforcement_layers

                if layer_count < MIN_ENFORCEMENT_LAYERS:
                    violations.append(
                        f"{req_id}: CRITICAL requires >=2 enforcement layers, "
                        f"found {layer_count}: {metadata.enforcement_layers}"
                    )
                elif not has_runtime:
                    violations.append(
                        f"{req_id}: CRITICAL requires at least 1 Runtime enforcement layer, "
                        f"found: {metadata.enforcement_layers}"
                    )

        return {"violations": violations, "warnings": warnings}

    def generate_audit_report(self) -> str:
        """Generate a comprehensive audit report.

        Returns:
            Formatted audit report as string
        """
        audit_results = self.audit_critical_requirements()

        report = []
        report.append("# CRITICAL Dual Enforcement Audit Report (REQ-416)")
        report.append("")
        report.append(f"Requirements file: {self.requirements_path}")
        report.append("")

        if audit_results["violations"]:
            report.append("## VIOLATIONS")
            report.append("")
            for violation in audit_results["violations"]:
                report.append(f"- **VIOLATION**: {violation}")
            report.append("")
        else:
            report.append("## VIOLATIONS")
            report.append("")
            report.append("✅ No violations found.")
            report.append("")

        if audit_results["warnings"]:
            report.append("## WARNINGS")
            report.append("")
            for warning in audit_results["warnings"]:
                report.append(f"- **WARNING**: {warning}")
            report.append("")
        else:
            report.append("## WARNINGS")
            report.append("")
            report.append("✅ No warnings found.")
            report.append("")

        # Summary
        requirements = self.parse_requirements_metadata()
        critical_count = sum(1 for r in requirements.values() if r.severity == "CRITICAL")

        report.append("## SUMMARY")
        report.append("")
        report.append(f"- Total requirements: {len(requirements)}")
        report.append(f"- CRITICAL requirements: {critical_count}")
        report.append(f"- Violations: {len(audit_results['violations'])}")
        report.append(f"- Warnings: {len(audit_results['warnings'])}")
        report.append("")

        if not audit_results["violations"]:
            report.append("✅ All CRITICAL requirements satisfy dual enforcement guarantee (REQ-416).")
        else:
            report.append("❌ Dual enforcement guarantee violations detected (REQ-416).")

        return "\n".join(report)

    def save_audit_report(self, output_path: Path) -> Path:
        """Save audit report to file.

        Args:
            output_path: Path to save the report

        Returns:
            Path to the saved report
        """
        report = self.generate_audit_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        Logger.info(f"Dual enforcement audit report saved to {output_path}")
        return output_path

    def run_ci_audit(self) -> int:
        """Run CI audit and return exit code.

        Returns:
            0 if no violations, 1 if violations found
        """
        audit_results = self.audit_critical_requirements()

        if audit_results["violations"]:
            Logger.error("CRITICAL Dual Enforcement violations detected (REQ-416):")
            for violation in audit_results["violations"]:
                Logger.error(f"  - {violation}")
            return 1

        Logger.info("✅ All CRITICAL requirements satisfy dual enforcement guarantee (REQ-416)")

        if audit_results["warnings"]:
            Logger.warning("Dual enforcement warnings:")
            for warning in audit_results["warnings"]:
                Logger.warning(f"  - {warning}")

        return 0


def run_dual_enforcement_audit() -> int:
    """Run the dual enforcement audit as a CLI command.

    Returns:
        Exit code (0 for success, 1 for violations)
    """
    auditor = CriticalDualEnforcementAuditor()
    return auditor.run_ci_audit()


def test_dual_enforcement_audit() -> bool:
    """Test the dual enforcement auditor.

    Returns:
        True if audit works correctly, False otherwise
    """
    try:
        auditor = CriticalDualEnforcementAuditor()
        requirements = auditor.parse_requirements_metadata()

        # Check that we parsed some requirements
        if not requirements:
            Logger.error("No requirements parsed")
            return False

        # Check that we have CRITICAL requirements
        critical_count = sum(1 for r in requirements.values() if r.severity == "CRITICAL")
        if critical_count == 0:
            Logger.error("No CRITICAL requirements found")
            return False

        # Run audit
        auditor.audit_critical_requirements()

        # Audit should complete without errors
        return True

    except Exception as e:
        Logger.error(f"Dual enforcement audit test failed: {e}")
        return False
