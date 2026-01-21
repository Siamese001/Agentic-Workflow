from __future__ import annotations
"""
AnomalyReport - Sovereign Anomaly Detection Schema

Provides standardized anomaly propagation across layers (L2-L5, apps).
Integrates with HealerMixin for audited healing decisions.

Location: agentic_core/schemas/anomaly_report.py
"""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    LOW = "low"           # Cosmetic/drift, auto-heal
    MEDIUM = "medium"     # Functional impairment, local heal
    HIGH = "high"         # Sovereignty risk, escalate
    CRITICAL = "critical" # Immediate shutdown/escalate to L0


@dataclass(frozen=True)
class AnomalyReport:
    """
    Sovereign anomaly report — immutable, auditable structure.

    Emitted by detectors (self-testing, validators, monitors).
    Consumed by HealerMixin._perform_healing().

    Attributes:
        type: Machine-readable anomaly type (e.g., "graph_corruption", "scoring_drift")
        severity: AnomalySeverity level
        description: Human-readable summary
        source: Agent/class name emitting the report
        details: Agent-specific context (e.g., {"graph_nodes": 42})
        timestamp: Auto-timestamp
        provenance_id: MCP chain ID if available
    """
    type: str
    severity: AnomalySeverity
    description: str
    source: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    provenance_id: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.source}: {self.type} — {self.description}"

    def to_dict(self) -> Dict[str, Any]:
        """For MCP auditing / serialization."""
        return {
            "type": self.type,
            "severity": self.severity.value,
            "description": self.description,
            "source": self.source,
            "details": self.details or {},
            "timestamp": self.timestamp,
            "provenance_id": self.provenance_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnomalyReport":
        """Create from dictionary."""
        return cls(
            type=data["type"],
            severity=AnomalySeverity(data["severity"]),
            description=data["description"],
            source=data["source"],
            details=data.get("details"),
            timestamp=data.get("timestamp", time.time()),
            provenance_id=data.get("provenance_id"),
        )


__all__ = ["AnomalyReport", "AnomalySeverity"]
