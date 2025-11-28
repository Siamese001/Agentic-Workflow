# File: models.py
# Data Models module for Resume Workflow
# Contains all data structures, enumerations, model classes, and custom exceptions

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set
import copy

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class HopExecutionError(Exception):
    """Raised when a hop fails to execute successfully."""
    pass

class StagingBufferError(Exception):
    """Raised when staging buffer encounters data integrity issues."""
    pass

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects requests."""
    pass

class PhaseTimeoutError(Exception):
    """Raised when a RAG phase execution exceeds timeout."""
    pass

class FactualFailureException(Exception):
    """Raised by Validator when a high-signal factual or strategic check fails, triggering a Slow Loop."""
    pass


# ============================================================================
# ENUMERATIONS
# ============================================================================

# ============================================================================
# IMPORT CUSTOM EXCEPTIONS FROM CENTRALIZED MODULE
# ============================================================================
# Exceptions are defined at the top of this file
# from exceptions import (...) # REMOVED - exceptions defined above

# ============================================================================
# ENUMERATIONS
# ============================================================================

class GateDecision(Enum):
    """Decision outcomes for gate validation."""
    PROCEED = "PROCEED"
    HALT = "HALT"


class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class ResumeSection(Enum):
    """Enumeration of all resume sections."""
    
    K0_NAME = "K.0_Name"
    K0_HEADLINE = "K.0_Headline"
    K0_CONTACT = "K.0_Contact"
    K0_EXECUTIVE_SUMMARY_HEADER = "K.0_Executive_Summary_Header"
    K0_EXPERIENCE_HEADER = "K.0_Experience_Header"
    K0_EDUCATION_HEADER = "K.0_Education_Header"
    K0_CERTIFICATIONS_HEADER = "K.0_Certifications_Header"
    K0_COMPETENCIES_HEADER = "K.0_Competencies_Header"

    K1_EXECUTIVE_SUMMARY = "K.1_Executive_Summary"
    K2_UNIFY_OVERVIEW = "K.2_Unify_Overview"
    K2_UNIFY_BULLETS = "K.2_Unify_Bullets"
    K3_IBM_OVERVIEW = "K.3_IBM_Overview"
    K3_IBM_BULLETS = "K.3_IBM_Bullets"
    K4_TRADERSENSE_NARRATIVE = "K.4_TraderSense_Narrative"
    K5_EY_NARRATIVE = "K.5_EY_Narrative"
    K6_EARLY_CAREER_NARRATIVE = "K.6_Early_Career_Narrative"
    K7_EDUCATION = "K.7_Education"
    K8_CERTIFICATIONS = "K.8_Certifications"
    K9_COMPETENCIES = "K.9_Competencies"
    K10_SKILLS = "K.10_Skills"
    K11_COVER_LETTER = "K.11_Cover_Letter"


class JDEnforcementRule(Enum):
    """Rules for JD enforcement validation."""
    
    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    E3_JD_PARSING_SUCCESS = "JD must parse successfully"
    E4_THEMES_EXTRACTED = "JD-derived themes must be extracted"
    E5_SKILLS_EXTRACTED = "JD-derived skills must be extracted (min 5)"
    E6_JD_TO_THEMATIC = "JD data must flow to ThematicAnalysis"
    E7_THEMATIC_USES_JD = "ThematicAnalysis must use JD data (not mock)"
    E8_ARTIST_RECEIVES_JD = "Artist must receive JD-derived thematic_analysis"
    E9_CONTENT_HAS_JD_KW = "Generated content must contain JD keywords"
    E10_ENRICHMENT_USES_JD = "Enrichment must use JD-derived data"
    E11_VALIDATION_CHECKS_JD = "Validation must check JD keyword presence"
    E12_FILES_CONTAIN_JD = "Output files must contain JD-derived content"
    E13_QA_VERIFIES_JD = "QA report must verify JD usage"
    E14_NO_MOCK_DATA = "No fallback/mock/default data allowed anywhere"
    E15_COMPLETE_AUDIT = "Complete audit trail of JD data flow required"


class BulletProvenance(Enum):
    """Provenance types for resume bullets."""
    Verbatim = "Verbatim"
    Customized = "Customized"
    Synthetic = "Synthetic"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class HopStatus(Enum):
    """Status outcomes for workflow hops."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


# ============================================================================
# DATA MODEL DATACLASSES
# ============================================================================

@dataclass
class ReasoningConfig:
    """Configuration for reasoning strategies (CoT, ToT, Reflexion, Self-Consistency)."""
    cot_min_paths: int = 0
    tot_branches: int = 1
    min_tot_depth: int = 1
    reflexion: bool = False
    max_reflexion_loops: int = 0
    self_consistency: int = 1
    
    # Class-level defaults for different reasoning strategies
    DEFAULT: ClassVar['ReasoningConfig'] = None
    EXECUTIVE_SUMMARY: ClassVar['ReasoningConfig'] = None
    HEADLINE: ClassVar['ReasoningConfig'] = None
    BULLETS: ClassVar['ReasoningConfig'] = None
    NARRATIVE: ClassVar['ReasoningConfig'] = None

@dataclass
class ValidationResult:
    """Result of a single validation rule."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict = field(default_factory=dict)


@dataclass
class ThematicAnalysis:
    """Thematic analysis derived from job description."""
    primary_theme: Dict = field(default_factory=dict)
    secondary_themes: List[Dict] = field(default_factory=list)
    role_classification: Dict = field(default_factory=dict)
    positioning_directives: Dict = field(default_factory=dict)
    authenticity_patterns: Dict = field(default_factory=dict)
    competitive_intelligence: Any = None
    problem_solution_narratives: Optional[Dict] = None
    signal_quality_score: float = 0.0
    retrieval_method: str = "UNKNOWN"
    retrieval_sources: List[Any] = field(default_factory=list)
    weighting_formula: Optional[Dict] = None
    evidence_log: List[Dict] = field(default_factory=list)


@dataclass
class JDEnforcementResult:
    """Result of a JD enforcement rule check."""
    rule: JDEnforcementRule
    passed: bool
    details: str
    gate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CompetitiveAnalysisConfig:
    """Configuration for competitive analysis."""
    enabled: bool = True
    min_peer_jds: int = 3
    search_pattern: str = '"{role_title}" at "{peer_company}"'
    selection_criteria: List[str] = field(default_factory=lambda: [
        "same_industry", "similar_company_size", "recent_posting_date"
    ])
    table_stakes_threshold: float = 0.8
    differentiator_threshold: float = 0.2


@dataclass
class RAGMission:
    """Mission definition for RAG retrieval."""
    target_company_name: str
    precise_role_title: str
    key_technologies: List[str]
    core_responsibilities: List[str]
    signal_gap_keywords: List[str]
    signal_overlap_keywords: List[str]


@dataclass
class SkillRequirement:
    """A single skill requirement."""
    skill: str
    requirement_type: str
    context: Optional[str] = None
    related_skills: List[str] = field(default_factory=list)


@dataclass
class SkillCluster:
    """A cluster of related skills."""
    cluster_name: str
    skills: List[str]
    representative_skill: str
    confidence: float


@dataclass
class MasterResumeIndex:
    """Index of master resume content for RAG."""
    skill_to_experiences: Dict[str, List[Dict]]
    achievement_catalog: List[Dict]
    domain_vocabularies: Dict[str, List[str]]
    recency_scores: Dict[str, float]
    skill_vectors: Optional[Dict[str, Any]] = None


@dataclass
class RAGEvidence:
    """Evidence from a single RAG iteration."""
    iteration: int
    action: str
    query_or_action: str
    findings_summary: str
    sources_count: int
    confidence_contribution: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGCritique:
    """Critique of RAG results."""
    confidence_score: float
    gaps_identified: List[str]
    refinement_tasks: List[str]
    reasoning: str
    is_sufficient: bool


@dataclass
class RAGState:
    """State tracking for iterative RAG process."""
    phase_name: str
    iteration: int
    evidence_log: List[RAGEvidence] = field(default_factory=list)
    cumulative_result: Optional[Dict[str, Any]] = None
    total_api_calls: int = 0
    critiques: List[RAGCritique] = field(default_factory=list)
    
    def add_evidence(self, evidence: RAGEvidence) -> None:
        """Add evidence to the log."""
        self.evidence_log.append(evidence)
    
    def add_critique(self, critique: RAGCritique) -> None:
        """Add a critique."""
        self.critiques.append(critique)
    
    def get_latest_critique(self) -> Optional[RAGCritique]:
        """Get the most recent critique."""
        return self.critiques[-1] if self.critiques else None


@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence data."""
    peer_jds_analyzed_count: int = 0
    differentiator_keywords: List[str] = field(default_factory=list)
    differentiator_keywords_raw: List[str] = field(default_factory=list)
    differentiator_keywords_weighted: List[Dict] = field(default_factory=list)

    def get_top_differentiators(self, count: int) -> List[str]:
        """Get top N differentiator keywords."""
        return self.differentiator_keywords[:count]


@dataclass
class RetrievalSource:
    """A source used in retrieval."""
    id: str
    type: str
    confidence: float = 0.0
    status: str = "UNKNOWN"
    specific_source: Optional[str] = None


@dataclass
class PartialRAGResult:
    """Partial results from multi-phase RAG process."""
    phase1_result: Optional[Dict[str, Any]] = None
    phase2_result: Optional[Dict[str, Any]] = None
    phase3_result: Optional[Dict[str, Any]] = None
    phase4_result: Optional[Dict[str, Any]] = None

    phase1_success: bool = False
    phase2_success: bool = False
    phase3_success: bool = False
    phase4_success: bool = False

    failure_reasons: List[str] = None

    def __post_init__(self):
        if self.failure_reasons is None:
            self.failure_reasons = []

    @property
    def any_success(self) -> bool:
        """Check if any phase succeeded."""
        return self.phase1_success or self.phase2_success or self.phase3_success or self.phase4_success

    @property
    def full_success(self) -> bool:
        """Check if all phases succeeded."""
        return self.phase1_success and self.phase2_success and self.phase3_success and self.phase4_success

    @property
    def success_rate(self) -> float:
        """Calculate success rate across all phases."""
        successes = sum([self.phase1_success, self.phase2_success, self.phase3_success, self.phase4_success])
        return successes / 4.0


@dataclass
class RAGTelemetry:
    """Telemetry data for RAG operations."""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    full_success: bool = False
    partial_success: bool = False
    success_rate: float = 0.0

    phase1_attempts: int = 0
    phase1_success: bool = False
    phase1_duration_seconds: float = 0.0

    phase2_attempts: int = 0
    phase2_success: bool = False
    phase2_duration_seconds: float = 0.0

    phase3_attempts: int = 0
    phase3_success: bool = False
    phase3_duration_seconds: float = 0.0

    phase4_attempts: int = 0
    phase4_success: bool = False
    phase4_duration_seconds: float = 0.0

    total_api_calls: int = 0
    failed_api_calls: int = 0
    total_search_calls: int = 0

    errors: List[str] = field(default_factory=list)
    circuit_breaker_triggered: bool = False

    total_duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry to dictionary format."""
        return {
            "timestamp": self.timestamp,
            "success": {
                "full": self.full_success,
                "partial": self.partial_success,
                "rate": self.success_rate
            },
            "phases": {
                "phase1": {
                    "attempts": self.phase1_attempts,
                    "success": self.phase1_success,
                    "duration": self.phase1_duration_seconds
                },
                "phase2": {
                    "attempts": self.phase2_attempts,
                    "success": self.phase2_success,
                    "duration": self.phase2_duration_seconds
                },
                "phase3": {
                    "attempts": self.phase3_attempts,
                    "success": self.phase3_success,
                    "duration": self.phase3_duration_seconds
                },
                "phase4": {
                    "attempts": self.phase4_attempts,
                    "success": self.phase4_success,
                    "duration": self.phase4_duration_seconds
                }
            },
            "api": {
                "total_calls": self.total_api_calls,
                "failed_calls": self.failed_api_calls,
                "search_calls": self.total_search_calls
            },
            "errors": self.errors,
            "circuit_breaker": self.circuit_breaker_triggered,
            "total_duration": self.total_duration_seconds
        }


@dataclass
class HopCheckpoint:
    """Checkpoint data for a single workflow hop."""
    hop_id: str
    hop_name: str
    status: HopStatus
    timestamp_start: str
    timestamp_end: str
    output_hash: Optional[str] = None
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

# ============================================================================
# CORE DATA STRUCTURES (MOVED FROM WORKFLOW)
# ============================================================================

class ImmutableStagingBuffer:
    """
    A write-once, read-many buffer that can be locked.
    This class is now correctly centralized in models.py.
    """
    def __init__(self):
        self._data = {}
        self._locked = False
        self._lock_timestamp = None

    def set(self, key: str, value: Any):
        """Sets a key-value pair, raising an error if locked."""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a value by key, returning a deep copy to maintain immutability."""
        value = self._data.get(key, default)
        # Return deep copy to prevent external modifications
        if value is not None and value is not default:
            return copy.deepcopy(value)
        return value

    def lock(self):
        """Locks the buffer, preventing further writes."""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()

    def is_locked(self) -> bool:
        """Checks if the buffer is locked."""
        return self._locked

    def unlock(self):
        """Unlocks the buffer to allow modifications in the next phase."""
        if self._locked:
            self._locked = False
            self._lock_timestamp = None

    @property
    def data(self) -> Dict:
        """Returns a deep copy of the buffer's data."""
        return copy.deepcopy(self._data)


# ============================================================================
# INITIALIZE REASONING CONFIG CLASS VARIABLES
# ============================================================================

# Initialize class-level ReasoningConfig instances
ReasoningConfig.DEFAULT = ReasoningConfig(
    cot_min_paths=0,
    tot_branches=1,
    min_tot_depth=1,
    reflexion=False,
    max_reflexion_loops=0,
    self_consistency=1
)

ReasoningConfig.EXECUTIVE_SUMMARY = ReasoningConfig(
    cot_min_paths=3,
    tot_branches=3,
    min_tot_depth=2,
    reflexion=True,
    max_reflexion_loops=2,
    self_consistency=3
)

ReasoningConfig.HEADLINE = ReasoningConfig(
    cot_min_paths=2,
    tot_branches=2,
    min_tot_depth=2,
    reflexion=False,
    max_reflexion_loops=0,
    self_consistency=2
)

ReasoningConfig.BULLETS = ReasoningConfig(
    cot_min_paths=2,
    tot_branches=2,
    min_tot_depth=1,
    reflexion=False,
    max_reflexion_loops=0,
    self_consistency=2
)

ReasoningConfig.NARRATIVE = ReasoningConfig(
    cot_min_paths=2,
    tot_branches=2,
    min_tot_depth=2,
    reflexion=True,
    max_reflexion_loops=1,
    self_consistency=2
)
