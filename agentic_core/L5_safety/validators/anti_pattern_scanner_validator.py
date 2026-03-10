"""
Anti-Pattern Scanner

Unified interface for scanning repositories for Phase 2 landmine anti-patterns.
Integrates with Guardian tests and HygieneGuardianAgent for comprehensive
code quality enforcement.

Usage:
    from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

    scanner = AntiPatternScanner(project_root)
    report = scanner.scan_repository()
    print(report.summary())
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternViolation,
    CompositeDetector,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.config_with_logic_validator import (
    ConfigWithLogicDetector,
)
from agentic_core.L5_safety.validators.direct_prompt_compilation_validator import (
    DirectPromptCompilationDetector,
)
from agentic_core.L5_safety.validators.global_mutation_validator import (
    GlobalMutationDetector,
)
from agentic_core.L5_safety.validators.magic_validator import (
    MagicConfigDetector,
)
from agentic_core.L5_safety.validators.path_fragility_validator import (
    PathFragilityDetector,
)
from agentic_core.L5_safety.validators.silent_swallower_validator import (
    SilentSwallowerDetector,
)
from agentic_core.L5_safety.validators.type_erasure_validator import (
    TypeErasureDetector,
)

Logger = logging.getLogger(__name__)


@dataclass
class ScanReport:
    """Report from anti-pattern scanning."""

    project_root: Path
    total_files_scanned: int = 0
    total_violations: int = 0
    violations_by_category: dict[str, int] = field(default_factory=dict)
    files_with_violations: int = 0
    scan_time_ms: float = 0.0
    all_violations: list[AntiPatternViolation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "Anti-Pattern Scan Report",
            "=" * 60,
            f"Project: {self.project_root}",
            f"Files Scanned: {self.total_files_scanned}",
            f"Files with Violations: {self.files_with_violations}",
            f"Total Violations: {self.total_violations}",
            f"Scan Time: {self.scan_time_ms:.2f}ms",
            "",
            "Violations by Category:",
        ]

        for category, count in self.violations_by_category.items():
            status = "🚨" if count > 0 else "✅"
            lines.append(f"  {status} {category}: {count}")

        if self.all_violations:
            lines.append("")
            lines.append("Top Violations:")
            for v in self.all_violations[:10]:
                lines.append(
                    f"  - {v.file_path.name}:{v.line_number} [{v.category.value}] {v.message[:50]}...",
                )

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_root": str(self.project_root),
            "total_files_scanned": self.total_files_scanned,
            "total_violations": self.total_violations,
            "violations_by_category": self.violations_by_category,
            "files_with_violations": self.files_with_violations,
            "scan_time_ms": self.scan_time_ms,
            "violations": [v.to_dict() for v in self.all_violations],
            "errors": self.errors,
        }

    @property
    def passed(self) -> bool:
        """Check if scan passed (no violations)."""
        return self.total_violations == 0


class AntiPatternScanner:
    """
    Unified anti-pattern scanner for repository-wide detection.

    Combines all Phase 2 landmine detectors into a single scanning interface
    with configurable enforcement levels and reporting.
    """

    # Default directories to scan
    DEFAULT_SCAN_DIRS = [
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
    ]

    # Default exclude patterns
    DEFAULT_EXCLUDES = [
        "**/test_*.py",
        "**/*_test.py",
        "**/conftest.py",
        "**/__pycache__/**",
        "**/archives/**",
        "**/.git/**",
    ]

    def __init__(
        self,
        project_root: Path,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        scan_dirs: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ):
        """
        Initialize the anti-pattern scanner.

        Args:
            project_root: Root directory of the project
            enforcement_level: Enforcement level for all detectors
            scan_dirs: Directories to scan (relative to project_root)
            exclude_patterns: Glob patterns to exclude
        """
        self.project_root = Path(project_root).resolve()
        self.enforcement_level = enforcement_level
        self.scan_dirs = scan_dirs or self.DEFAULT_SCAN_DIRS
        self.exclude_patterns = exclude_patterns or self.DEFAULT_EXCLUDES

        # Initialize detectors
        self.composite = CompositeDetector(
            [
                SilentSwallowerDetector(enforcement_level=enforcement_level),
                TypeErasureDetector(enforcement_level=enforcement_level),
                PathFragilityDetector(enforcement_level=enforcement_level),
                MagicConfigDetector(enforcement_level=enforcement_level),
                GlobalMutationDetector(enforcement_level=enforcement_level),
                ConfigWithLogicDetector(enforcement_level=enforcement_level),
                DirectPromptCompilationDetector(enforcement_level=enforcement_level),
            ],
        )

    def scan_repository(self) -> ScanReport:
        """
        Scan the entire repository for anti-patterns.

        Returns:
            ScanReport with all findings
        """
        import time

        start_time = time.time()

        report = ScanReport(project_root=self.project_root)
        all_files = set()
        files_with_violations = set()

        for scan_dir in self.scan_dirs:
            target_dir = self.project_root / scan_dir

            if not target_dir.exists():
                Logger.debug(f"Skipping non-existent directory: {target_dir}")
                continue

            try:
                results = self.composite.scan_directory(
                    target_dir,
                    include_patterns=["**/*.py"],
                    exclude_patterns=self.exclude_patterns,
                )

                for category, category_results in results.items():
                    category_name = category.value

                    if category_name not in report.violations_by_category:
                        report.violations_by_category[category_name] = 0

                    for result in category_results:
                        all_files.add(result.file_path)

                        if result.error:
                            report.errors.append(f"{result.file_path}: {result.error}")

                        if result.has_violations:
                            files_with_violations.add(result.file_path)

                            for violation in result.violations:
                                if not violation.whitelisted:
                                    report.violations_by_category[category_name] += 1
                                    report.total_violations += 1
                                    report.all_violations.append(violation)

            # Error handling - log and continue scanning other directories
            # guardian: allow-silent-swallow
            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                Logger.error(f"Error scanning {target_dir}: {e}")
                report.errors.append(f"Error scanning {target_dir}: {e}")

        report.total_files_scanned = len(all_files)
        report.files_with_violations = len(files_with_violations)
        report.scan_time_ms = (time.time() - start_time) * 1000

        # Sort violations by severity
        report.all_violations.sort(
            key=lambda v: (0 if v.severity == "error" else 1, str(v.file_path), v.line_number),
        )

        return report

    def scan_file(self, file_path: Path) -> list[AntiPatternViolation]:
        """
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of violations found
        """
        violations = []

        results = self.composite.scan_file(file_path)

        for result in results:
            for violation in result.violations:
                if not violation.whitelisted:
                    violations.append(violation)

        return violations

    def scan_changed_files(self, file_paths: list[Path]) -> ScanReport:
        """
        Scan only specific files (for incremental PR checks).

        Args:
            file_paths: List of files to scan

        Returns:
            ScanReport with findings for the specified files
        """
        import time

        start_time = time.time()

        report = ScanReport(project_root=self.project_root)
        files_with_violations = set()

        for category in AntiPatternCategory:
            report.violations_by_category[category.value] = 0

        for file_path in file_paths:
            if not file_path.exists() or not file_path.suffix == ".py":
                continue

            violations = self.scan_file(file_path)

            if violations:
                files_with_violations.add(file_path)

                for violation in violations:
                    category_name = violation.category.value
                    report.violations_by_category[category_name] += 1
                    report.total_violations += 1
                    report.all_violations.append(violation)

        report.total_files_scanned = len(file_paths)
        report.files_with_violations = len(files_with_violations)
        report.scan_time_ms = (time.time() - start_time) * 1000

        return report

    def get_enforcement_action(self, report: ScanReport) -> str:
        """
        Determine the enforcement action based on scan results.

        Args:
            report: Scan report

        Returns:
            Action to take: "pass", "warn", "soft_block", "hard_block"
        """
        if report.passed:
            return "pass"

        if self.enforcement_level == EnforcementLevel.DISABLED:
            return "pass"
        elif self.enforcement_level == EnforcementLevel.WARNING:
            return "warn"
        elif self.enforcement_level == EnforcementLevel.SOFT_BLOCK:
            return "soft_block"
        elif self.enforcement_level == EnforcementLevel.HARD_BLOCK:
            return "hard_block"

        return "warn"


def run_scan(project_root: Path | None = None) -> ScanReport:
    """
    Convenience function to run a full repository scan.

    Args:
        project_root: Optional project root (defaults to current working directory)

    Returns:
        ScanReport with all findings
    """
    if project_root is None:
        project_root = Path.cwd()

    scanner = AntiPatternScanner(project_root)
    return scanner.scan_repository()


__all__ = [
    "AntiPatternScanner",
    "ScanReport",
    "run_scan",
]
