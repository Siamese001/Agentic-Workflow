from __future__ import annotations

"""
CredentialScannerAgent - Detects hardcoded credentials in source code

Risk 4: Hardcoded Credential Detection
Scans the codebase for potential security leaks including:
- API Keys
- Secret Tokens
- Private Keys
- Hardcoded Passwords
- AWS/Azure/GCP credentials

Uses FileCache for efficient scanning (Opportunity #3 integration).
"""


import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import subatomic_testing_mixin
from agentic_core.utils.file_cache import FileCache

logger = logging.getLogger(__name__)


@dataclass
class CredentialMatch:
    """Represents a detected credential in source code."""

    file_path: str
    line_number: int
    line_content: str
    pattern_type: str
    severity: str  # "high", "medium", "low"
    confidence: float  # 0.0 to 1.0


@dataclass
class CredentialScannerAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    L5 Safety Agent for detecting hardcoded credentials.

    Implements comprehensive regex patterns to identify:
    - API keys (generic, AWS, Azure, GCP, GitHub, Stripe, etc.)
    - Secret tokens and access tokens
    - Private keys (RSA, SSH, PGP)
    - Hardcoded passwords
    - Database connection strings
    - OAuth secrets

    Uses FileCache for efficient repository scanning.
    """

    # Credential detection patterns
    PATTERNS: dict[str, tuple[str, str, float]] = field(
        default_factory=lambda: {
            # Format: pattern_name: (regex, severity, confidence)
            # Generic API Keys
            "generic_api_key": (
                r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                "high",
                0.8,
            ),
            # AWS Credentials
            "aws_access_key": (r"(?i)(AKIA[0-9A-Z]{16})", "high", 0.95),
            "aws_secret_key": (
                r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']',
                "high",
                0.9,
            ),
            # Azure Credentials
            "azure_storage_key": (
                r"(?i)(DefaultEndpointsProtocol=https;AccountName=.*?AccountKey=)([a-zA-Z0-9+/=]{88})",
                "high",
                0.95,
            ),
            # GCP Credentials
            "gcp_api_key": (r"(?i)(AIza[0-9A-Za-z_\-]{35})", "high", 0.9),
            # GitHub Tokens
            "github_token": (r"(?i)(gh[pousr]_[a-zA-Z0-9]{36,})", "high", 0.95),
            "github_classic_token": (
                r'(?i)(github[_-]?token|gh[_-]?token)\s*[:=]\s*["\']([a-f0-9]{40})["\']',
                "high",
                0.85,
            ),
            # Stripe Keys
            "stripe_secret_key": (r"(?i)(sk_live_[a-zA-Z0-9]{24,})", "high", 0.95),
            "stripe_restricted_key": (r"(?i)(rk_live_[a-zA-Z0-9]{24,})", "high", 0.95),
            # Private Keys
            "rsa_private_key": (r"-----BEGIN RSA PRIVATE KEY-----", "high", 1.0),
            "ssh_private_key": (r"-----BEGIN OPENSSH PRIVATE KEY-----", "high", 1.0),
            "pgp_private_key": (r"-----BEGIN PGP PRIVATE KEY BLOCK-----", "high", 1.0),
            # Generic Secrets
            "generic_secret": (
                r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
                "medium",
                0.6,
            ),
            # Database Connection Strings
            "db_connection_string": (
                r"(?i)(mongodb|mysql|postgresql|postgres)://[^:]+:([^@]+)@",
                "high",
                0.85,
            ),
            # OAuth Secrets
            "oauth_client_secret": (
                r'(?i)(client[_-]?secret|oauth[_-]?secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                "high",
                0.8,
            ),
            # JWT Tokens
            "jwt_token": (
                r"(?i)(eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)",
                "medium",
                0.7,
            ),
            # Slack Tokens
            "slack_token": (
                r"(?i)(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,})",
                "high",
                0.9,
            ),
        }
    )

    # File extensions to scan
    SCANNABLE_EXTENSIONS: set[str] = field(
        default_factory=lambda: {
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
    )

    # Paths to exclude from scanning
    EXCLUDED_PATHS: set[str] = field(
        default_factory=lambda: {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "archives",
            ".sovereign_healing_backup",
            "healing_backups",
            "coverage_html",
            ".pytest_cache",
            ".mypy_cache",
        }
    )

    def __post_init__(self):
        """Initialize the credential scanner."""
        super().__post_init__()
        self.file_cache: FileCache | None = None
        self.matches: list[CredentialMatch] = []

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for CredentialScannerAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        try:
            violation.get("type", "")
            file_path = violation.get("file")

            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }

            # CredentialScannerAgent healing logic
            return {
                "status": "manual_required",
                "details": "CredentialScannerAgent requires manual review for healing",
                "artifacts": [],
                "errors": [],
            }

        except Exception as e:
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    def scan_for_credentials(
        self, target_path: Path | None = None, file_patterns: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Scan for hardcoded credentials in the codebase.

        Args:
            target_path: Root path to scan (defaults to project root)
            file_patterns: Optional list of file patterns to scan

        Returns:
            Dict with scan results including matches, summary, and recommendations
        """
        if target_path is None:
            from agentic_core.L5_safety.validators.structure_blueprint_config import (
                get_validated_project_root,
            )

            target_path = get_validated_project_root()

        logger.info(f"[CREDENTIAL SCAN] Starting scan of {target_path}")

        # Initialize FileCache for efficient scanning
        if self.file_cache is None:
            self.file_cache = FileCache(project_root=target_path)

        # Get all scannable files
        scannable_files = self._get_scannable_files(target_path)
        logger.info(f"[CREDENTIAL SCAN] Scanning {len(scannable_files)} files")

        # Scan each file
        self.matches = []
        for file_path in scannable_files:
            self._scan_file(file_path)

        # Generate summary
        summary = self._generate_summary()

        logger.info(f"[CREDENTIAL SCAN] Complete: {len(self.matches)} potential credentials found")

        return {
            "status": "success",
            "total_files_scanned": len(scannable_files),
            "total_matches": len(self.matches),
            "matches": [self._match_to_dict(m) for m in self.matches],
            "summary": summary,
            "recommendations": self._generate_recommendations(),
        }

    def _get_scannable_files(self, root_path: Path) -> list[Path]:
        """Get list of files to scan using FileCache."""
        if self.file_cache is None:
            return []

        all_files = self.file_cache.get_all_files()

        scannable = []
        for file_path in all_files:
            # Check extension
            if file_path.suffix not in self.SCANNABLE_EXTENSIONS:
                continue

            # Check excluded paths
            if any(excluded in str(file_path) for excluded in self.EXCLUDED_PATHS):
                continue

            scannable.append(file_path)

        return scannable

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for credentials."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, start=1):
                for pattern_name, (regex, severity, confidence) in self.PATTERNS.items():
                    matches = re.finditer(regex, line)
                    for _match in matches:
                        # Skip false positives
                        if self._is_false_positive(line, pattern_name):
                            continue

                        self.matches.append(
                            CredentialMatch(
                                file_path=str(file_path),
                                line_number=line_num,
                                line_content=line.strip(),
                                pattern_type=pattern_name,
                                severity=severity,
                                confidence=confidence,
                            )
                        )
        except Exception as e:
            logger.debug(f"[CREDENTIAL SCAN] Error scanning {file_path}: {e}")

    def _is_false_positive(self, line: str, pattern_name: str) -> bool:
        """Check if a match is likely a false positive."""
        # Skip comments
        if line.strip().startswith("#") or line.strip().startswith("//"):
            return True

        # Skip example/placeholder values
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

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        by_severity = {"high": 0, "medium": 0, "low": 0}
        by_type = {}

        for match in self.matches:
            by_severity[match.severity] += 1
            by_type[match.pattern_type] = by_type.get(match.pattern_type, 0) + 1

        return {
            "by_severity": by_severity,
            "by_type": by_type,
            "high_confidence_count": sum(1 for m in self.matches if m.confidence >= 0.9),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        if any(m.severity == "high" for m in self.matches):
            recommendations.append("🚨 HIGH PRIORITY: Remove all hardcoded credentials immediately")
            recommendations.append(
                "Use environment variables or secure secret management (e.g., AWS Secrets Manager, Azure Key Vault)"
            )

        if any("private_key" in m.pattern_type for m in self.matches):
            recommendations.append(
                "⚠️ Private keys detected - move to secure key storage and rotate compromised keys"
            )

        if any("aws" in m.pattern_type.lower() for m in self.matches):
            recommendations.append("AWS credentials detected - use IAM roles or AWS SSM Parameter Store")

        if not recommendations:
            recommendations.append("✅ No high-priority credential leaks detected")

        return recommendations

    def _match_to_dict(self, match: CredentialMatch) -> dict[str, Any]:
        """Convert CredentialMatch to dictionary."""
        return {
            "file": match.file_path,
            "line": match.line_number,
            "content": match.line_content[:100],  # Truncate for safety
            "type": match.pattern_type,
            "severity": match.severity,
            "confidence": match.confidence,
        }

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Scan repository for hardcoded credentials and report findings.

        Scans Python files for hardcoded API keys, passwords, tokens, and
        other sensitive credentials. Credential violations require manual
        review and cannot be auto-fixed for safety reasons.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed credential report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository(dry_run=dry_run, execute=execute, **kwargs)

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)

        try:
            self.logger.info(f"[{agent_name}] Scanning for hardcoded credentials...")

            scan_results = self.scan_for_credentials()
            violations_found = scan_results.get("total_matches", 0)

            if violations_found > 0:
                self.logger.warning(f"  Found {violations_found} potential credential leaks")

                if execute and not dry_run:
                    # Generate credential report (we don't auto-fix for safety)
                    import json

                    report_path = Path(self.project_root) / "logs" / "credential_scan_report.json"
                    report_path.parent.mkdir(parents=True, exist_ok=True)

                    report = {
                        "scan_date": str(Path(__file__).stat().st_mtime),
                        "total_violations": violations_found,
                        "summary": scan_results.get("summary", {}),
                        "note": "Credential violations require manual review - DO NOT auto-fix",
                    }

                    with open(report_path, "w", encoding="utf-8") as f:
                        json.dump(report, f, indent=2)

                    self.logger.info(f"  Generated credential report: {report_path}")

            else:
                self.logger.info("  No credential leaks detected")

            self.logger.info(
                f"[{agent_name}] Complete: {violations_found} potential leaks (manual review required)"
            )

            return {
                "violations_found": violations_found,
                "violations_fixed": 0,  # Never auto-fix credentials for safety
                "errors": 0,
                "skipped": violations_found,  # All skipped because manual review required
                "agent": agent_name,
                "dry_run": dry_run,
                "note": "Credential violations require manual review",
            }

        finally:
            _call_path.discard(agent_name)
