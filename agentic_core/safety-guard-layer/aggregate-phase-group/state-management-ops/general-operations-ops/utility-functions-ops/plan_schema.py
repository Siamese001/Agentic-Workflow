from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum

class RouteType(Enum):
    CONNECTION_REQ = "CONNECTION_REQ"
    SHORT_NEW = "SHORT_NEW"
    LONG_NEW = "LONG_NEW"
    FOLLOW_UP = "FOLLOW_UP"
    INMAIL = "INMAIL"

class RecipientType(Enum):
    HIRING_MANAGER = "HIRING_MANAGER"
    RECRUITER = "RECRUITER"
    SENIOR_TA = "SENIOR_TA"
    EXECUTIVE = "EXECUTIVE"
    C_LEVEL = "C_LEVEL"

@dataclass
class RoutingPlan:
    route: RouteType
    conditions: Dict[str, Any]
    constraints: Dict[str, Any]

@dataclass
class RetrievalPlan:
    hyde_enabled: bool
    hyde_trigger: str
    web_search_calls: int
    internal_sources: List[str]
    reranking_model: str
    reranking_threshold: float
    self_rag_max_hops: int
    episodic_memory_enabled: bool
    knowledge_graph_enabled: bool
    few_shot_enabled: bool

@dataclass
class InsightPlan:
    signal_weights: Dict[str, float]
    min_signal_threshold: float
    per_claim_min_confidence: float
    aggregate_min_confidence: float
    confidence_enforcement: str

@dataclass
class KNodePlan:
    hop_order: List[Dict[str, Any]]
    assembly_policy: str
    validation_gates: List[Dict[str, str]]

@dataclass
class TonePlan:
    archetype_mappings: Dict[str, Dict[str, Any]]
    language_adaptation: Dict[str, Any]

@dataclass
class CTAPlan:
    archetype_styles: Dict[str, Dict[str, Any]]
    date_window_rules: Dict[str, Any]

@dataclass
class ConstraintPlan:
    forbidden_verbs: List[str]
    filler_patterns: List[str]
    placeholder_patterns: List[str]
    word_count_tolerance: float
    ascii_rules: Dict[str, bool]

@dataclass
class ValidatorPlan:
    error_codes: Dict[str, Dict[str, Any]]
    severity_thresholds: Dict[str, bool]
    master_gate: Dict[str, Any]

@dataclass
class FamilyPlan:
    archetype_templates: Dict[str, Dict[str, Any]]
    signature_formats: Dict[str, Dict[str, Any]]

@dataclass
class ScenarioPlan:
    entity_grounding: Dict[str, Any]
    team_whitelist: Dict[str, Any]
    generation_constraints: Dict[str, Any]

@dataclass
class SeniorityPlan:
    taxonomy: Dict[str, Any]
    classification_rules: Dict[str, Any]
    default_archetype: str
    default_confidence: float

@dataclass
class TemplatePlan:
    cta_templates: Dict[str, Any]
    system_prompt: Dict[str, Any]
    greeting_templates: Dict[str, Any]

@dataclass
class MissionPlan:
    sender_structure: Dict[str, Any]
    recipient_structure: Dict[str, Any]
    job_description_structure: Dict[str, Any]
    message_context_structure: Dict[str, Any]

@dataclass
class LICPlan:
    routing: RoutingPlan
    parameters: Dict[str, Any]
    retrieval: RetrievalPlan
    insights: InsightPlan
    k_nodes: KNodePlan
    constraints: ConstraintPlan
    tone: TonePlan
    cta: CTAPlan
    validators: ValidatorPlan
    families: FamilyPlan
    scenarios: ScenarioPlan
    seniority: SeniorityPlan
    templates: TemplatePlan
    mission: MissionPlan
