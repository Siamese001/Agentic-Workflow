#!/usr/bin/env python3
"""
CI Plan Validator - Comprehensive plan validation for CI/CD
Validates all plans across the repository with strict enforcement.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Token validation constants per §10.2
TOKEN_GREEN_THRESHOLD = 50000
TOKEN_YELLOW_THRESHOLD = 100000
TOKEN_RED_THRESHOLD = 175000

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from tools.validate_plan_format import validate_plan_format

# Try to import token estimator - may not exist in all environments
try:
    from tools.utils.planning.token_estimator import ContextWindowEstimator

    TOKEN_VALIDATOR_AVAILABLE = True
except ImportError:
    TOKEN_VALIDATOR_AVAILABLE = False
    ContextWindowEstimator = None


class CIPlanValidator:
    """Comprehensive CI validator for all plans."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_plans": 0,
            "valid_plans": 0,
            "invalid_plans": 0,
            "plans_with_warnings": 0,
            "failures": [],
            "warnings": [],
            "metrics": {},
        }
        # Initialize token validator if available
        if TOKEN_VALIDATOR_AVAILABLE and ContextWindowEstimator:
            self.token_validator = ContextWindowEstimator()
        else:
            self.token_validator = None

    def find_all_plans(self) -> list[Path]:
        """Find all plan files in the repository."""
        plans = []

        # Search in common plan directories
        plan_dirs = [
            self.repo_root / "docs" / "reports" / "plans",
            self.repo_root / ".windsurf" / "plans",
            Path.home() / ".windsurf" / "plans",  # User plans directory
        ]

        for plan_dir in plan_dirs:
            if plan_dir.exists():
                plans.extend(plan_dir.glob("*.md"))
                # Also search subdirectories
                plans.extend(plan_dir.rglob("*.md"))

        # Remove duplicates and non-plan files
        unique_plans = []
        seen = set()
        for plan in plans:
            if plan.name not in seen and plan.name != "README.md":
                unique_plans.append(plan)
                seen.add(plan.name)

        return sorted(unique_plans)

    def validate_single_plan(self, plan_path: Path) -> dict[str, Any]:
        """Validate a single plan with comprehensive checks."""
        result = {
            "path": str(plan_path),
            "valid": False,
            "issues": [],
            "warnings": [],
            "metrics": {"lines": 0, "sections": 0, "waves": 0, "tokens_estimated": 0},
        }

        try:
            # Basic format validation
            format_result = validate_plan_format(str(plan_path))
            result["valid"] = format_result["valid"]
            result["issues"].extend(format_result["issues"])
            result["warnings"].extend(format_result["warnings"])

            # Read content for additional metrics
            with open(plan_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Calculate metrics
            result["metrics"]["lines"] = len(content.splitlines())
            result["metrics"]["sections"] = content.count("##")

            # Count waves
            wave_matches = content.count("| Wave") + content.count("Wave ")
            result["metrics"]["waves"] = wave_matches

            # Estimate tokens (rough heuristic)
            result["metrics"]["tokens_estimated"] = len(content) // 4

            # Additional validations
            self._validate_plan_content(content, result)

        except Exception as e:
            result["issues"].append(f"Error reading plan: {str(e)}")
            result["valid"] = False

        return result

    def _validate_plan_content(self, content: str, result: dict[str, Any]):
        """Additional content validations including token estimates (§10)."""

        # Check for required sections in CI context
        required_sections = ["## Wave Structure", "## Rules", "## Success Criteria"]

        for section in required_sections:
            if section not in content:
                result["issues"].append(f"Missing required section: {section}")

        # Check for implementation details
        if "## Implementation" not in content and "## Implementation Commands" not in content:
            result["warnings"].append("No implementation section found")

        # Check for evidence
        if "### Evidence" not in content and "### Target" not in content:
            result["warnings"].append("No evidence or target sections")

        # Check for ADG impact if relevant
        if any(keyword in content.lower() for keyword in ["dependency", "import", "module"]):
            if "## ADG Impact" not in content:
                result["warnings"].append("Consider ADG Impact section for dependency changes")

        # §10 TOKEN ESTIMATION VALIDATION — NOW MANDATORY
        if self.token_validator:
            token_result = self.token_validator.validate_plan_tokens(
                Path(result.get("path", "unknown")),
                content,
            )
        else:
            # Fallback if validator not available
            token_result = {
                "wave_table_found": "| Wave" in content or "| Waves" in content,
                "token_estimates_found": "token" in content.lower(),
                "total_tokens": 0,
                "status": "green",
            }
        result["token_validation"] = token_result

        # Hard fail if wave table missing (§10.1)
        if not token_result["wave_table_found"]:
            result["issues"].append("Missing required wave structure table (§10.1)")

        # Hard fail if no token estimates (§10.2)
        if not token_result["token_estimates_found"]:
            result["issues"].append("No token estimates found — must run token estimator (§10.2)")

        # Hard fail if RED status (exceeds 175K tokens)
        if token_result["status"] == "red":
            result["issues"].append(
                f"Token budget exceeded: {token_result['total_tokens']:,} tokens (RED status > 175K). "
                "Plan must be split into smaller waves.",
            )

        # Check wave table format (relaxed for both "Wave" and "Waves")
        if any(marker in content for marker in ["| Waves |", "| Wave |", "| **Wave** |"]):
            # Validate table structure
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if any(marker in line for marker in ["| Waves |", "| Wave |", "| **Wave** |"]):
                    # Check next few lines for proper table format
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if "|" in lines[j] and "---" not in lines[j]:
                            if not any(col.strip() for col in lines[j].split("|")[1:-1]):
                                result["warnings"].append("Empty row in wave table")
                    break

    def validate_all_plans(self) -> dict[str, Any]:
        """Validate all plans in the repository."""
        plans = self.find_all_plans()
        self.results["total_plans"] = len(plans)

        print("=== CI Plan Validation ===")
        print(f"Found {len(plans)} plans to validate")
        print()

        for plan in plans:
            try:
                plan_rel = plan.relative_to(self.repo_root)
            except ValueError:
                # Plan is outside repo (e.g., user plans directory)
                plan_rel = plan
            print(f"Validating: {plan_rel}")
            result = self.validate_single_plan(plan)

            if result["valid"]:
                self.results["valid_plans"] += 1
                print("  Valid")
            else:
                self.results["invalid_plans"] += 1
                print("  Invalid")
                self.results["failures"].append({"plan": str(plan_rel), "issues": result["issues"]})

            if result["warnings"]:
                self.results["plans_with_warnings"] += 1
                print(f"  {len(result['warnings'])} warnings")
                self.results["warnings"].append({"plan": str(plan_rel), "warnings": result["warnings"]})

            # Print key issues
            for issue in result["issues"][:3]:  # Limit output
                print(f"    - {issue}")
            if len(result["issues"]) > 3:
                print(f"    ... and {len(result['issues']) - 3} more")

            # Print token validation info
            if "token_validation" in result:
                tv = result["token_validation"]
                print(f"  Tokens: {tv['total_tokens']:,} ({tv['status'].upper()})")
                print(f"  Wave Table: {'✅' if tv['wave_table_found'] else '❌'}")
                print(f"  Token Estimates: {'✅' if tv['token_estimates_found'] else '❌'}")

            print()

        # Calculate metrics
        self.results["metrics"] = {
            "avg_lines": sum(r["metrics"]["lines"] for r in [self.validate_single_plan(p) for p in plans])
            // len(plans)
            if plans
            else 0,
            "total_waves": sum(r["metrics"]["waves"] for r in [self.validate_single_plan(p) for p in plans]),
            "total_tokens_estimated": sum(
                r["metrics"]["tokens_estimated"] for r in [self.validate_single_plan(p) for p in plans]
            ),
        }

        return self.results

    def generate_report(self) -> str:
        """Generate CI validation report."""
        report = []
        report.append("# CI Plan Validation Report")
        report.append(f"Generated: {self.results['timestamp']}")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"- Total Plans: {self.results['total_plans']}")
        report.append(f"- Valid Plans: {self.results['valid_plans']} ✅")
        report.append(f"- Invalid Plans: {self.results['invalid_plans']} ❌")
        report.append(f"- Plans with Warnings: {self.results['plans_with_warnings']} ⚠️")
        report.append("")

        # Metrics
        report.append("## Metrics")
        report.append(f"- Average Lines per Plan: {self.results['metrics']['avg_lines']:,}")
        report.append(f"- Total Waves: {self.results['metrics']['total_waves']}")
        report.append(f"- Total Estimated Tokens: {self.results['metrics']['total_tokens_estimated']:,}")
        report.append("")

        # Failures
        if self.results["failures"]:
            report.append("## Failures ❌")
            for failure in self.results["failures"]:
                report.append(f"### {failure['plan']}")
                for issue in failure["issues"]:
                    report.append(f"- {issue}")
                report.append("")

        # Warnings
        if self.results["warnings"]:
            report.append("## Warnings ⚠️")
            for warning in self.results["warnings"]:
                report.append(f"### {warning['plan']}")
                for w in warning["warnings"]:
                    report.append(f"- {w}")
                report.append("")

        # Status
        report.append("## Status")
        if self.results["invalid_plans"] == 0:
            report.append("✅ ALL PLANS VALID - CI PASSED")
        else:
            report.append(f"❌ {self.results['invalid_plans']} PLAN(S) INVALID - CI FAILED")

        return "\n".join(report)

    def save_report(self, output_path: str | None = None):
        """Save validation report."""
        if output_path is None:
            # Save report to docs/reports (SSOT location)
            report_path = self.repo_root / "docs" / "reports" / "plan_validation_report.md"
        else:
            report_path = Path(output_path)

        # Ensure directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_report()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        # Also save JSON for programmatic access
        json_path = report_path.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"Report saved to: {report_path}")
        return report_path


def main():
    """Main CI validation entry point."""
    validator = CIPlanValidator()
    results = validator.validate_all_plans()

    # Save report
    report_path = validator.save_report()

    # Print final status
    print("=" * 80)
    print("CI VALIDATION COMPLETE")
    print(f"Valid: {results['valid_plans']}/{results['total_plans']}")
    print(f"Invalid: {results['invalid_plans']}")
    print(f"With Warnings: {results['plans_with_warnings']}")
    print("=" * 80)

    # Exit with error code if any plans are invalid
    if results["invalid_plans"] > 0:
        print(f"\nCI FAILED: {results['invalid_plans']} plan(s) invalid")
        print(f"See report: {report_path}")
        sys.exit(1)
    else:
        print("\nCI PASSED: All plans valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
