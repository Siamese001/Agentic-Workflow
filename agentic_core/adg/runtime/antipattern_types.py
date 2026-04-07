"""Anti-pattern type definitions — pure data structures only.

Zero side effects on import. No lifecycle trace imports. This module defines
the domain model for anti-pattern detection and tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AntipatternSeverity(str, Enum):
    """Severity of a detected anti-pattern."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AntipatternCategory(str, Enum):
    """Canonical anti-pattern categories matching ADG static scanner edge kinds."""

    # Original static scanner patterns
    SILENT_EXCEPTION_SWALLOW = "silent_exception_swallow"
    BLOCKING_CALL_IN_ASYNC = "blocking_call_in_async"
    GLOBAL_STATE_MUTATION = "global_state_mutation"
    RETRY_WITHOUT_BACKOFF = "retry_without_backoff"
    BARE_EXCEPT = "bare_except"
    MUTABLE_DEFAULT_ARG = "mutable_default_arg"
    STAR_IMPORT_USE = "star_import_use"
    HARDCODED_SECRET = "hardcoded_secret"
    HARDCODED_PATH = "hardcoded_path"
    DEAD_CODE = "dead_code"
    OVERLY_BROAD_CATCH = "overly_broad_catch"
    BROAD_EXCEPTION_CATCH = "broad_exception_catch"
    LOG_AND_SWALLOW = "log_and_swallow"
    RETURN_NONE_SWALLOW = "return_none_swallow"

    # MCP-specific anti-patterns (P2 additions)
    SECRET_IN_EDITOR_CONFIG = "secret_in_editor_config"
    UNPINNED_MCP_PACKAGE = "unpinned_mcp_package"
    DEFAULT_LOCAL_DB_CREDENTIALS = "default_local_db_credentials"
    OVERBROAD_FILESYSTEM_ROOT = "overbroad_filesystem_root"
    REDUNDANT_CAPABILITY_OVERLAP = "redundant_capability_overlap"
    REMOTE_MCP_WITHOUT_EXPLICIT_MODE = "remote_mcp_without_explicit_mode"
    MACHINE_SPECIFIC_ABSOLUTE_EXECUTABLE_PATH = "machine_specific_absolute_executable_path"
    PLACEHOLDER_VALUE_IN_LIVE_CONFIG = "placeholder_value_in_live_config"
    NETWORK_TOOL_WITHOUT_EGRESS_POLICY = "network_tool_without_egress_policy"
    MIXED_MUTATION_AND_EXFILTRATION_SURFACE = "mixed_mutation_and_exfiltration_surface"
    IMPORT_TIME_SIDE_EFFECT = "import_time_side_effect"
    READ_ACCESSOR_WITH_SIDE_EFFECT = "read_accessor_with_side_effect"
    NONDETERMINISTIC_ID_GENERATION = "nondeterministic_id_generation"
    DOMAIN_MODEL_COUPLED_TO_TELEMETRY = "domain_model_coupled_to_telemetry"
    SUPPRESSION_WITHOUT_REASON = "suppression_without_reason"
    UNBOUNDED_REGISTRY_GROWTH = "unbounded_registry_growth"
    EXACT_MATCH_ONLY_CLASSIFIER = "exact_match_only_classifier"


_SEVERITY_MAP: dict[AntipatternCategory, AntipatternSeverity] = {
    # Original static scanner patterns
    AntipatternCategory.HARDCODED_SECRET: AntipatternSeverity.CRITICAL,
    AntipatternCategory.HARDCODED_PATH: AntipatternSeverity.HIGH,
    AntipatternCategory.GLOBAL_STATE_MUTATION: AntipatternSeverity.MEDIUM,
    AntipatternCategory.SILENT_EXCEPTION_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.BLOCKING_CALL_IN_ASYNC: AntipatternSeverity.HIGH,
    AntipatternCategory.RETRY_WITHOUT_BACKOFF: AntipatternSeverity.MEDIUM,
    AntipatternCategory.BARE_EXCEPT: AntipatternSeverity.MEDIUM,
    AntipatternCategory.OVERLY_BROAD_CATCH: AntipatternSeverity.MEDIUM,
    AntipatternCategory.BROAD_EXCEPTION_CATCH: AntipatternSeverity.HIGH,
    AntipatternCategory.LOG_AND_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.RETURN_NONE_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.MUTABLE_DEFAULT_ARG: AntipatternSeverity.LOW,
    AntipatternCategory.STAR_IMPORT_USE: AntipatternSeverity.LOW,
    AntipatternCategory.DEAD_CODE: AntipatternSeverity.INFO,
    # MCP-specific patterns
    AntipatternCategory.SECRET_IN_EDITOR_CONFIG: AntipatternSeverity.CRITICAL,
    AntipatternCategory.DEFAULT_LOCAL_DB_CREDENTIALS: AntipatternSeverity.CRITICAL,
    AntipatternCategory.MIXED_MUTATION_AND_EXFILTRATION_SURFACE: AntipatternSeverity.CRITICAL,
    AntipatternCategory.IMPORT_TIME_SIDE_EFFECT: AntipatternSeverity.CRITICAL,
    AntipatternCategory.NONDETERMINISTIC_ID_GENERATION: AntipatternSeverity.CRITICAL,
    AntipatternCategory.UNPINNED_MCP_PACKAGE: AntipatternSeverity.HIGH,
    AntipatternCategory.OVERBROAD_FILESYSTEM_ROOT: AntipatternSeverity.HIGH,
    AntipatternCategory.NETWORK_TOOL_WITHOUT_EGRESS_POLICY: AntipatternSeverity.HIGH,
    AntipatternCategory.READ_ACCESSOR_WITH_SIDE_EFFECT: AntipatternSeverity.HIGH,
    AntipatternCategory.DOMAIN_MODEL_COUPLED_TO_TELEMETRY: AntipatternSeverity.HIGH,
    AntipatternCategory.REDUNDANT_CAPABILITY_OVERLAP: AntipatternSeverity.MEDIUM,
    AntipatternCategory.REMOTE_MCP_WITHOUT_EXPLICIT_MODE: AntipatternSeverity.MEDIUM,
    AntipatternCategory.MACHINE_SPECIFIC_ABSOLUTE_EXECUTABLE_PATH: AntipatternSeverity.MEDIUM,
    AntipatternCategory.SUPPRESSION_WITHOUT_REASON: AntipatternSeverity.MEDIUM,
    AntipatternCategory.UNBOUNDED_REGISTRY_GROWTH: AntipatternSeverity.MEDIUM,
    AntipatternCategory.PLACEHOLDER_VALUE_IN_LIVE_CONFIG: AntipatternSeverity.LOW,
    AntipatternCategory.EXACT_MATCH_ONLY_CLASSIFIER: AntipatternSeverity.LOW,
}


@dataclass
class SuppressionRecord:
    """Record of a suppression decision with audit trail."""

    reason: str
    reviewer: str = ""
    ticket: str = ""
    suppressed_at: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "reviewer": self.reviewer,
            "ticket": self.ticket,
            "suppressed_at": self.suppressed_at,
        }


def _compute_fingerprint(
    run_id: str,
    source_file: str,
    line_start: int,
    symbol: str,
    category: AntipatternCategory,
) -> str:
    """Compute stable fingerprint for an anti-pattern occurrence.

    Uses SHA-256 hash of stable inputs to ensure deterministic IDs across
    runs. No UUID generation or wall-clock dependence.
    """
    import hashlib

    fingerprint_input = f"{run_id}:{source_file}:{line_start}:{symbol}:{category.value}"
    return hashlib.sha256(fingerprint_input.encode()).hexdigest()


@dataclass
class AntipatternRecord:
    """A single anti-pattern occurrence with forensic metadata.

    Schema version 2.0 introduces stable fingerprinting and expanded
    forensic fields for governed RCA and promotion tracking.
    """

    schema_version: str = "2.0"
    fingerprint: str = ""
    record_id: str = ""
    category: AntipatternCategory = AntipatternCategory.SILENT_EXCEPTION_SWALLOW
    severity: AntipatternSeverity = AntipatternSeverity.MEDIUM
    source_file: str = ""
    line_start: int = 0
    line_end: int = 0
    column_start: int = 0
    symbol: str = ""
    rule_id: str = ""
    scanner: str = ""
    evidence_hash: str = ""
    suppression: SuppressionRecord | None = None
    remediation_status: str = "open"
    agent_id: str = ""
    run_id: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        """Compute fingerprint and record_id after initialization."""
        if not self.fingerprint:
            self.fingerprint = _compute_fingerprint(
                self.run_id,
                self.source_file,
                self.line_start,
                self.symbol,
                self.category,
            )
        if not self.record_id:
            # Use first 12 chars of fingerprint as record_id (deterministic)
            self.record_id = f"apr-{self.fingerprint[:12]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "fingerprint": self.fingerprint,
            "record_id": self.record_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "symbol": self.symbol,
            "rule_id": self.rule_id,
            "scanner": self.scanner,
            "evidence_hash": self.evidence_hash,
            "suppression": self.suppression.to_dict() if self.suppression else None,
            "remediation_status": self.remediation_status,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "description": self.description,
        }


@dataclass
class AntipatternRegistryReport:
    """Aggregated anti-pattern report for a run.

    Pure data structure with zero side effects. All @property accessors
    are pure computation functions.
    """

    agent_id: str
    run_id: str
    records: list[AntipatternRecord] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def critical_count(self) -> int:
        return sum(1 for r in self.records if r.severity == AntipatternSeverity.CRITICAL)

    @property
    def suppressed_count(self) -> int:
        return sum(1 for r in self.records if r.suppression is not None)

    @property
    def active_count(self) -> int:
        return sum(1 for r in self.records if r.suppression is None)

    @property
    def by_category(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self.records:
            result[r.category.value] = result.get(r.category.value, 0) + 1
        return result

    @property
    def by_severity(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self.records:
            result[r.severity.value] = result.get(r.severity.value, 0) + 1
        return result

    @property
    def affected_files(self) -> set[str]:
        return {r.source_file for r in self.records if r.source_file}

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_count": self.total_count,
            "critical_count": self.critical_count,
            "suppressed_count": self.suppressed_count,
            "active_count": self.active_count,
            "affected_file_count": len(self.affected_files),
            "by_category": self.by_category,
            "by_severity": self.by_severity,
        }
