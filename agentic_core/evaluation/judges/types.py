"""Unified types for the LLM-as-Judge system.

Provides canonical types shared across all judge components:
- ``JudgeVerdict``      — immutable verdict for one evaluated dimension
- ``JudgeReport``       — aggregated report across multiple dimensions
- ``EvidenceBundle``    — structured evidence from multiple data sources
- ``SourceSnippet``     — source code at ADG-provided coordinates
- ``RubricDefinition``  — configurable evaluation rubric
- ``ScoringCriterion``  — single scoring criterion within a rubric
- ``VerdictOutcome``    — canonical outcome enum (PASS/FAIL/WARN/NEEDS_REVIEW)
- ``ScoringMethod``     — how a rubric is scored (deterministic vs LLM)
- ``EvidenceRequirement`` — what evidence a rubric needs
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class VerdictOutcome(str, Enum):
    """Canonical verdict outcomes."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SKIP = "SKIP"
    ERROR = "ERROR"


class ScoringMethod(str, Enum):
    """How a rubric computes its score."""

    DETERMINISTIC = "deterministic"
    LLM_POINTWISE = "llm_pointwise"
    LLM_PAIRWISE = "llm_pairwise"
    LLM_REFERENCE = "llm_reference"
    HYBRID = "hybrid"


class Severity(str, Enum):
    """Severity classification for rubric violations."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ---------------------------------------------------------------------------
# Evidence types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceSnippet:
    """Source code read at ADG-provided file:line coordinates."""

    file_path: str
    start_line: int
    end_line: int
    content: str
    symbol: str = ""


@dataclass(frozen=True)
class EvidenceItem:
    """Single piece of evidence backing a verdict."""

    evidence_type: str  # "adg_edge", "source_snippet", "runtime_signal", "config"
    key: str  # Identifier (e.g. relation type, signal kind)
    value: str  # Serialized evidence content
    file_path: str = ""
    line_no: int = 0


@dataclass(frozen=True)
class EvidenceBundle:
    """Structured evidence assembled from multiple data sources."""

    target: str  # Module path or evaluation target
    adg_edges: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    source_snippets: tuple[SourceSnippet, ...] = field(default_factory=tuple)
    runtime_signals: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    config_context: dict[str, Any] = field(default_factory=dict)
    adg_digest: str = ""
    module_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def evidence_hash(self) -> str:
        """Deterministic hash of all evidence for provenance."""
        canonical = json.dumps(
            {
                "target": self.target,
                "adg_digest": self.adg_digest,
                "edge_types": sorted(self.adg_edges.keys()),
                "snippet_count": len(self.source_snippets),
                "signal_count": len(self.runtime_signals),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Rubric types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceRequirement:
    """What evidence a rubric needs from the ADG or other sources."""

    evidence_type: str  # "adg_edge", "source_code", "runtime_signal", "config"
    relation: str = ""  # ADG relation type (for adg_edge)
    description: str = ""


@dataclass(frozen=True)
class ScoringCriterion:
    """Single scoring criterion within a rubric."""

    criterion_id: str
    description: str
    weight: float = 1.0
    pass_threshold: float = 1.0
    warn_threshold: float = 0.9


@dataclass(frozen=True)
class RubricDefinition:
    """Configurable evaluation rubric loaded from rubrics.json."""

    rubric_id: str
    dimension: str
    display_name: str
    description: str
    scoring_method: str  # ScoringMethod value
    severity: str  # Severity value
    applies_to: dict[str, Any] = field(default_factory=dict)
    evidence_requirements: tuple[EvidenceRequirement, ...] = field(default_factory=tuple)
    scoring_criteria: tuple[ScoringCriterion, ...] = field(default_factory=tuple)
    deterministic_check: str = ""  # Formula for deterministic evaluation
    score_formula: str = ""  # How to compute the score
    pass_threshold: float = 1.0
    warn_threshold: float = 0.9
    prompt_template: str = ""  # LLM prompt template (for LLM methods)

    @property
    def is_deterministic(self) -> bool:
        return self.scoring_method == ScoringMethod.DETERMINISTIC.value


# ---------------------------------------------------------------------------
# Verdict types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JudgeVerdict:
    """Immutable verdict for one evaluated dimension/rubric."""

    verdict_id: str
    target: str
    dimension: str
    rubric_id: str
    outcome: str  # VerdictOutcome value
    score: float
    reasoning: str
    evidence_items: tuple[EvidenceItem, ...] = field(default_factory=tuple)
    suggestions: tuple[str, ...] = field(default_factory=tuple)
    severity: str = Severity.MEDIUM.value
    adg_digest: str = ""
    provider_id: str = ""
    evidence_hash: str = ""
    created_at: str = ""

    @property
    def passed(self) -> bool:
        return self.outcome in (VerdictOutcome.PASS.value, VerdictOutcome.SKIP.value)

    @property
    def deterministic_digest(self) -> str:
        """Deterministic hash for dedup and provenance."""
        canonical = json.dumps(
            {
                "target": self.target,
                "rubric_id": self.rubric_id,
                "score": self.score,
                "outcome": self.outcome,
                "adg_digest": self.adg_digest,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class JudgeReportRow:
    """One row in the judge report scorecard."""

    dimension: str
    display_name: str
    score: float
    outcome: str
    severity: str
    rubric_id: str
    verdict_count: int = 1


@dataclass
class JudgeReport:
    """Aggregated report from a multi-dimension judge evaluation run."""

    target: str
    verdicts: list[JudgeVerdict] = field(default_factory=list)
    scorecard: list[JudgeReportRow] = field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = True
    adg_digest: str = ""
    created_at: str = ""
    error: str = ""

    @property
    def fail_count(self) -> int:
        return sum(1 for v in self.verdicts if v.outcome == VerdictOutcome.FAIL.value)

    @property
    def warn_count(self) -> int:
        return sum(1 for v in self.verdicts if v.outcome == VerdictOutcome.WARN.value)


# ---------------------------------------------------------------------------
# Judge protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class JudgeProvider(Protocol):
    """Unified protocol for all LLM judge backends."""

    async def judge(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        """Send a judge prompt and return structured response."""
        ...

    @property
    def provider_id(self) -> str: ...

    @property
    def cost_per_eval(self) -> float: ...


__all__ = [
    "EvidenceBundle",
    "EvidenceItem",
    "EvidenceRequirement",
    "JudgeProvider",
    "JudgeReport",
    "JudgeReportRow",
    "JudgeVerdict",
    "RubricDefinition",
    "ScoringCriterion",
    "ScoringMethod",
    "Severity",
    "SourceSnippet",
    "VerdictOutcome",
]
