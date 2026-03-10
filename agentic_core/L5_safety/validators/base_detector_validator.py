"""
Base Anti-Pattern Detector Framework

Provides the core infrastructure for AST-based anti-pattern detection
with caching, incremental scanning, and configurable enforcement levels.
"""

import ast
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class EnforcementLevel(str, Enum):
    """Enforcement level for anti-pattern violations."""

    DISABLED = "disabled"  # No enforcement
    WARNING = "warning"  # Log warning, don't block
    SOFT_BLOCK = "soft_block"  # Block PR with override option
    HARD_BLOCK = "hard_block"  # Block PR, no override


class AntiPatternCategory(str, Enum):
    """Categories of anti-patterns."""

    SILENT_SWALLOWER = "silent_swallower"
    TYPE_ERASURE = "type_erasure"
    PATH_FRAGILITY = "path_fragility"
    MAGIC_CONFIGURATION = "magic_configuration"
    GLOBAL_MUTATION = "global_mutation"
    CONFIG_WITH_LOGIC = "config_with_logic"
    DIRECT_PROMPT_COMPILATION = "direct_prompt_compilation"


@dataclass
class AntiPatternViolation:
    """Represents a detected anti-pattern violation."""

    file_path: Path
    line_number: int
    category: AntiPatternCategory
    message: str
    evidence: str
    severity: str = "warning"
    suggested_fix: str | None = None
    whitelisted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "category": self.category.value,
            "message": self.message,
            "evidence": self.evidence,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
            "whitelisted": self.whitelisted,
            "metadata": self.metadata,
        }


@dataclass
class DetectionResult:
    """Result of anti-pattern detection for a file."""

    file_path: Path
    violations: list[AntiPatternViolation] = field(default_factory=list)
    scan_time_ms: float = 0.0
    cached: bool = False
    error: str | None = None

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len([v for v in self.violations if not v.whitelisted]) > 0

    @property
    def violation_count(self) -> int:
        """Count non-whitelisted violations."""
        return len([v for v in self.violations if not v.whitelisted])


class AntiPatternDetector(ABC):
    """
    Abstract base class for anti-pattern detectors.

    Subclasses implement specific detection logic for each anti-pattern category.
    """

    # Cache for parsed ASTs
    _ast_cache: dict[str, tuple[str, ast.Module]] = {}

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        self.enforcement_level = enforcement_level
        self.whitelisted_patterns = whitelisted_patterns or []
        self.whitelisted_files = whitelisted_files or []

    @property
    @abstractmethod
    def category(self) -> AntiPatternCategory:
        """Return the category of anti-pattern this detector handles."""
        pass

    @abstractmethod
    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """
        Detect anti-patterns in the given AST.

        Args:
            file_path: Path to the file being analyzed
            tree: Parsed AST of the file

        Returns:
            List of detected violations
        """
        pass

    def scan_file(self, file_path: Path) -> DetectionResult:
        """
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            DetectionResult with violations and metadata
        """
        import time

        start_time = time.time()

        # Check if file is whitelisted
        if self._is_file_whitelisted(file_path):
            return DetectionResult(
                file_path=file_path,
                violations=[],
                scan_time_ms=0,
                cached=False,
            )

        try:
            # Get AST (with caching)
            tree = self._get_ast(file_path)

            if tree is None:
                return DetectionResult(
                    file_path=file_path,
                    violations=[],
                    scan_time_ms=(time.time() - start_time) * 1000,
                    error="Failed to parse file",
                )

            # Detect violations
            violations = self.detect(file_path, tree)

            # Apply whitelist patterns
            for violation in violations:
                if self._is_violation_whitelisted(violation):
                    violation.whitelisted = True

            scan_time = (time.time() - start_time) * 1000

            return DetectionResult(
                file_path=file_path,
                violations=violations,
                scan_time_ms=scan_time,
            )

        except Exception as e:
            Logger.error(f"Error scanning {file_path}: {e}")
            return DetectionResult(
                file_path=file_path,
                violations=[],
                scan_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    def scan_directory(
        self,
        directory: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[DetectionResult]:
        """
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of DetectionResults
        """
        include_patterns = include_patterns or ["**/*.py"]
        exclude_patterns = exclude_patterns or ["**/test_*.py", "**/__pycache__/**"]

        results = []

        for pattern in include_patterns:
            for file_path in directory.glob(pattern):
                # Skip excluded patterns
                skip = False
                for exclude in exclude_patterns:
                    if file_path.match(exclude):
                        skip = True
                        break

                if skip:
                    continue

                if file_path.is_file():
                    result = self.scan_file(file_path)
                    results.append(result)

        return results

    def _get_ast(self, file_path: Path) -> ast.Module | None:
        """Get AST for file with caching."""
        try:
            content = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.md5(content.encode()).hexdigest()

            cache_key = str(file_path)

            # Check cache
            if cache_key in self._ast_cache:
                cached_hash, cached_tree = self._ast_cache[cache_key]
                if cached_hash == content_hash:
                    return cached_tree

            # Parse and cache
            tree = ast.parse(content, filename=str(file_path))
            self._ast_cache[cache_key] = (content_hash, tree)

            return tree

        except SyntaxError as e:
            Logger.warning(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            Logger.error(f"Error reading {file_path}: {e}")
            return None

    def _is_file_whitelisted(self, file_path: Path) -> bool:
        """Check if file matches whitelist patterns."""
        for pattern in self.whitelisted_files:
            if file_path.match(pattern):
                return True
        return False

    def _is_violation_whitelisted(self, violation: AntiPatternViolation) -> bool:
        """Check if violation matches whitelist patterns."""
        for pattern in self.whitelisted_patterns:
            if pattern in violation.evidence:
                return True
        return False

    def _get_source_line(self, file_path: Path, line_number: int) -> str:
        """Get a specific line from the source file."""
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            if 0 < line_number <= len(lines):
                return lines[line_number - 1].strip()
        except Exception:
            pass
        return ""


class CompositeDetector:
    """
    Combines multiple detectors into a single scanning interface.
    """

    def __init__(self, detectors: list[AntiPatternDetector] | None = None):
        self.detectors = detectors or []

    def add_detector(self, detector: AntiPatternDetector) -> None:
        """Add a detector to the composite."""
        self.detectors.append(detector)

    def scan_file(self, file_path: Path) -> list[DetectionResult]:
        """Scan file with all detectors."""
        results = []
        for detector in self.detectors:
            result = detector.scan_file(file_path)
            results.append(result)
        return results

    def scan_directory(
        self,
        directory: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> dict[AntiPatternCategory, list[DetectionResult]]:
        """Scan directory with all detectors, grouped by category."""
        results: dict[AntiPatternCategory, list[DetectionResult]] = {}

        for detector in self.detectors:
            category_results = detector.scan_directory(directory, include_patterns, exclude_patterns)
            results[detector.category] = category_results

        return results

    def get_summary(self, results: dict[AntiPatternCategory, list[DetectionResult]]) -> dict[str, Any]:
        """Generate summary statistics from scan results."""
        summary = {
            "total_files_scanned": 0,
            "total_violations": 0,
            "violations_by_category": {},
            "files_with_violations": 0,
        }

        all_files = set()
        files_with_violations = set()

        for category, category_results in results.items():
            category_violations = 0

            for result in category_results:
                all_files.add(result.file_path)

                if result.has_violations:
                    files_with_violations.add(result.file_path)
                    category_violations += result.violation_count

            summary["violations_by_category"][category.value] = category_violations
            summary["total_violations"] += category_violations

        summary["total_files_scanned"] = len(all_files)
        summary["files_with_violations"] = len(files_with_violations)

        return summary


__all__ = [
    "AntiPatternCategory",
    "AntiPatternDetector",
    "AntiPatternViolation",
    "CompositeDetector",
    "DetectionResult",
    "EnforcementLevel",
]
