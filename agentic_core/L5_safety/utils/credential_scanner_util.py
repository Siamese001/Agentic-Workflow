"""Credential Scanner Utility - Deterministic credential detection.

This module provides deterministic credential scanning functionality previously
implemented in CredentialScannerAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 9).

Usage:
    from agentic_core.L5_safety.utils.credential_scanner_util import (
        CredentialScanner, CredentialMatch, scan_for_credentials
    )

    # Scan for credentials
    scanner = CredentialScanner()
    results = scanner.scan_for_credentials(Path("."))
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class CredentialMatch:
    """Represents a detected credential in source code."""

    file_path: str
    line_number: int
    line_content: str
    pattern_type: str
    severity: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "line": self.line_number,
            "content": self.line_content[:100],
            "type": self.pattern_type,
            "severity": self.severity,
            "confidence": self.confidence,
        }


@dataclass
class CredentialScanResult:
    """Result of credential scanning."""

    status: str
    total_files_scanned: int
    total_matches: int
    matches: list[CredentialMatch]
    summary: dict[str, Any]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "total_files_scanned": self.total_files_scanned,
            "total_matches": self.total_matches,
            "matches": [m.to_dict() for m in self.matches],
            "summary": self.summary,
            "recommendations": self.recommendations,
        }


# Default credential patterns
DEFAULT_PATTERNS: dict[str, tuple[str, str, float]] = {
    "generic_api_key": (
        "(?i)(api[_-]?key|apikey|api[_-]?secret)\\s*[:=]\\s*[\"']([a-zA-Z0-9_\\-]{20,})[\"']",
        "high",
        0.8,
    ),
    "aws_access_key": ("(?i)(AKIA[0-9A-Z]{16})", "high", 0.95),
    "aws_secret_key": (
        "(?i)(aws[_-]?secret[_-]?access[_-]?key)\\s*[:=]\\s*[\"']([a-zA-Z0-9/+=]{40})[\"']",
        "high",
        0.9,
    ),
    "azure_storage_key": (
        "(?i)(DefaultEndpointsProtocol=https;AccountName=.*?AccountKey=)([a-zA-Z0-9+/=]{88})",
        "high",
        0.95,
    ),
    "gcp_api_key": ("(?i)(AIza[0-9A-Za-z_\\-]{35})", "high", 0.9),
    "github_token": ("(?i)(gh[pousr]_[a-zA-Z0-9]{36,})", "high", 0.95),
    "github_classic_token": (
        "(?i)(github[_-]?token|gh[_-]?token)\\s*[:=]\\s*[\"']([a-f0-9]{40})[\"']",
        "high",
        0.85,
    ),
    "stripe_secret_key": ("(?i)(sk_live_[a-zA-Z0-9]{24,})", "high", 0.95),
    "stripe_restricted_key": ("(?i)(rk_live_[a-zA-Z0-9]{24,})", "high", 0.95),
    "rsa_private_key": ("-----BEGIN RSA PRIVATE KEY-----", "high", 1.0),
    "ssh_private_key": ("-----BEGIN OPENSSH PRIVATE KEY-----", "high", 1.0),
    "pgp_private_key": ("-----BEGIN PGP PRIVATE KEY BLOCK-----", "high", 1.0),
    "generic_secret": (
        "(?i)(secret|password|passwd|pwd)\\s*[:=]\\s*[\"']([^\"']{8,})[\"']",
        "medium",
        0.6,
    ),
    "db_connection_string": (
        "(?i)(mongodb|mysql|postgresql|postgres)://[^:]+:([^@]+)@",
        "high",
        0.85,
    ),
    "oauth_client_secret": (
        "(?i)(client[_-]?secret|oauth[_-]?secret)\\s*[:=]\\s*[\"']([a-zA-Z0-9_\\-]{20,})[\"']",
        "high",
        0.8,
    ),
    "jwt_token": (
        "(?i)(eyJ[a-zA-Z0-9_\\-]+\\.eyJ[a-zA-Z0-9_\\-]+\\.[a-zA-Z0-9_\\-]+)",
        "medium",
        0.7,
    ),
    "slack_token": ("(?i)(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,})", "high", 0.9),
}

# Default scannable extensions
DEFAULT_SCANNABLE_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".sh",
    ".bash",
    ".zsh",
    ".yaml",
    ".yml",
    ".json",
    ".xml",
    ".env",
    ".config",
    ".ini",
    ".toml",
    ".properties",
}

# Default excluded paths
DEFAULT_EXCLUDED_PATHS: set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".sovereign_healing_backup",
    "healing_backups",
    "coverage_html",
    ".pytest_cache",
    ".mypy_cache",
}


def _is_false_positive(line: str, pattern_name: str) -> bool:
    """Check if a match is likely a false positive."""
    if line.strip().startswith("#") or line.strip().startswith("//"):
        return True
    false_positive_markers = [
        "example",
        "placeholder",
        "your_",
        "your-",
        "xxx",
        "yyy",
        "test",
        "mock",
        "fake",
        "dummy",
        "sample",
        "<",
        ">",
    ]
    line_lower = line.lower()
    return any(marker in line_lower for marker in false_positive_markers)


def _generate_summary(matches: list[CredentialMatch]) -> dict[str, Any]:
    """Generate summary statistics."""
    by_severity: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    by_type: dict[str, int] = {}
    for match in matches:
        by_severity[match.severity] = by_severity.get(match.severity, 0) + 1
        by_type[match.pattern_type] = by_type.get(match.pattern_type, 0) + 1
    return {
        "by_severity": by_severity,
        "by_type": by_type,
        "high_confidence_count": sum(1 for m in matches if m.confidence >= 0.9),
    }


def _generate_recommendations(matches: list[CredentialMatch]) -> list[str]:
    """Generate security recommendations based on findings."""
    recommendations: list[str] = []
    if any(m.severity == "high" for m in matches):
        recommendations.append("🚨 HIGH PRIORITY: Remove all hardcoded credentials immediately")
        recommendations.append(
            "Use environment variables or secure secret management (e.g., AWS Secrets Manager, Azure Key Vault)",
        )
    if any("private_key" in m.pattern_type for m in matches):
        recommendations.append(
            "⚠️ Private keys detected - move to secure key storage and rotate compromised keys",
        )
    if any("aws" in m.pattern_type.lower() for m in matches):
        recommendations.append("AWS credentials detected - use IAM roles or AWS SSM Parameter Store")
    if not recommendations:
        recommendations.append("✅ No high-priority credential leaks detected")
    return recommendations


class CredentialScanner:
    """Deterministic credential scanner."""

    def __init__(
        self,
        patterns: dict[str, tuple[str, str, float]] | None = None,
        scannable_extensions: set[str] | None = None,
        excluded_paths: set[str] | None = None,
    ) -> None:
        """Initialize credential scanner.

        Args:
            patterns: Regex patterns for credential detection
            scannable_extensions: File extensions to scan
            excluded_paths: Paths to exclude from scanning
        """
        self.patterns = patterns or DEFAULT_PATTERNS.copy()
        self.scannable_extensions = scannable_extensions or DEFAULT_SCANNABLE_EXTENSIONS.copy()
        self.excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS.copy()
        self.matches: list[CredentialMatch] = []
        # Compile regex patterns once for performance
        self._compiled_patterns: dict[str, tuple[re.Pattern, str, float]] = {
            name: (re.compile(regex), severity, confidence)
            for name, (regex, severity, confidence) in self.patterns.items()
        }

    def _get_scannable_files(self, root_path: Path) -> list[Path]:
        """Get list of files to scan."""
        scannable: list[Path] = []

        if not root_path.exists():
            Logger.warning(f"Root path does not exist: {root_path}")
            return scannable

        for file_path in root_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in self.scannable_extensions:
                continue
            if any(excluded in str(file_path) for excluded in self.excluded_paths):
                continue
            scannable.append(file_path)

        return scannable

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for credentials."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            for line_num, line in enumerate(lines, start=1):
                for pattern_name, (compiled_regex, severity, confidence) in self._compiled_patterns.items():
                    matches = compiled_regex.finditer(line)
                    for _match in matches:
                        if _is_false_positive(line, pattern_name):
                            continue
                        self.matches.append(
                            CredentialMatch(
                                file_path=str(file_path),
                                line_number=line_num,
                                line_content=line.strip(),
                                pattern_type=pattern_name,
                                severity=severity,
                                confidence=confidence,
                            ),
                        )
        except (OSError, UnicodeDecodeError) as e:
            Logger.debug("[CREDENTIAL SCAN] Error scanning %s: %s", file_path, e)

    def scan_for_credentials(
        self,
        target_path: Path | None = None,
        file_patterns: list[str] | None = None,
    ) -> CredentialScanResult:
        """Scan for hardcoded credentials in the codebase.

        Args:
            target_path: Root path to scan (defaults to current directory)
            file_patterns: Optional list of file patterns to scan

        Returns:
            CredentialScanResult with scan results
        """
        if target_path is None:
            target_path = Path.cwd()

        Logger.info(f"[CREDENTIAL SCAN] Starting scan of {target_path}")

        scannable_files = self._get_scannable_files(target_path)
        Logger.info(f"[CREDENTIAL SCAN] Scanning {len(scannable_files)} files")

        self.matches = []
        for file_path in scannable_files:
            self._scan_file(file_path)

        summary = _generate_summary(self.matches)
        recommendations = _generate_recommendations(self.matches)

        Logger.info(f"[CREDENTIAL SCAN] Complete: {len(self.matches)} potential credentials found")

        return CredentialScanResult(
            status="success",
            total_files_scanned=len(scannable_files),
            total_matches=len(self.matches),
            matches=self.matches.copy(),
            summary=summary,
            recommendations=recommendations,
        )


def scan_for_credentials(
    target_path: str | Path | None = None,
    patterns: dict[str, tuple[str, str, float]] | None = None,
) -> CredentialScanResult:
    """Convenience function to scan for credentials.

    Args:
        target_path: Path to scan (defaults to current directory)
        patterns: Optional custom patterns

    Returns:
        CredentialScanResult with scan results
    """
    scanner = CredentialScanner(patterns=patterns)
    return scanner.scan_for_credentials(Path(target_path) if target_path else None)
