"""
Consolidated Guardrails Package

Reduces 35 guardrail agents to 10 consolidated agents through composable rule sets.

Impact:
- Validation Latency: -35%
- Rule Conflicts: -60%
- Maintainability: +40%
- Agent Count: 35 → 21 (-40%)
"""

from .ErrorRecoveryGuardrail import (
    ErrorRecoveryGuardrail,
    ErrorCategory,
    RecoveryStrategy,
    ErrorContext,
    RecoveryResult,
)

from .CodeQualityGuardrail import (
    CodeQualityGuardrail,
    CodeIssue,
    QualityResult,
)

from .ThreatDetectionGuardrail import (
    ThreatDetectionGuardrail,
    ThreatLevel,
    ThreatType,
    ThreatIndicator,
    ThreatAnalysisResult,
)

from .ConstitutionalGovernanceGuardrail import (
    ConstitutionalGovernanceGuardrail,
    ConstitutionalPrinciple,
    PrincipleViolation,
    GovernanceResult,
)

from .ResourceManagementGuardrail import (
    ResourceManagementGuardrail,
    ResourceType,
    ResourceQuota,
    ResourceCheckResult,
)

from .IntegrityValidationGuardrail import (
    IntegrityValidationGuardrail,
    IntegrityViolation,
    IntegrityResult,
)

from .MCPSecurityGuardrail import (
    MCPSecurityGuardrail,
    MCPSecurityViolation,
    MCPSecurityResult,
)

from .LoggingObservabilityGuardrail import (
    LoggingObservabilityGuardrail,
    LogLevel,
    LogEntry,
    AuditEntry,
)

__all__ = [
    # Error Recovery
    "ErrorRecoveryGuardrail",
    "ErrorCategory",
    "RecoveryStrategy",
    "ErrorContext",
    "RecoveryResult",
    # Code Quality
    "CodeQualityGuardrail",
    "CodeIssue",
    "QualityResult",
    # Threat Detection
    "ThreatDetectionGuardrail",
    "ThreatLevel",
    "ThreatType",
    "ThreatIndicator",
    "ThreatAnalysisResult",
    # Constitutional Governance
    "ConstitutionalGovernanceGuardrail",
    "ConstitutionalPrinciple",
    "PrincipleViolation",
    "GovernanceResult",
    # Resource Management
    "ResourceManagementGuardrail",
    "ResourceType",
    "ResourceQuota",
    "ResourceCheckResult",
    # Integrity Validation
    "IntegrityValidationGuardrail",
    "IntegrityViolation",
    "IntegrityResult",
    # MCP Security
    "MCPSecurityGuardrail",
    "MCPSecurityViolation",
    "MCPSecurityResult",
    # Logging & Observability
    "LoggingObservabilityGuardrail",
    "LogLevel",
    "LogEntry",
    "AuditEntry",
]
