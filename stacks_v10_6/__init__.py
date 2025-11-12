"""Stack-specific agent implementations for v10.6."""

from .models import (
    SpecialistDraftPacket,
    EvidenceClarificationRecord,
    EvidenceBriefRecord,
    EvidenceLiaisonPacket,
    CritiqueFindingRecord,
    CritiquePanelPacket,
)

from .safety import (
    PIISanitizerAgent,
    BiasDetectorAgent,
    PromptInjectionDetectorAgent,
    ConstitutionalReviewerAgent,
)

from .strategy import (
    QueryComplexityClassifier,
    ToTStrategistAgent,
)

from .prompting import PromptEngineerAgent
from .rag import RAG_SearchAgent
from .drafting import (
    StructureLeadAgent,
    NarrativeStylistAgent,
    ComplianceEditorAgent,
    EvidenceLiaisonAgent,
    CritiqueRoutingPanel,
    DraftingGuildCoordinator,
)

from .bullet import (
    BulletEntityExtractionAgent,
    BulletMetricsEnrichmentAgent,
    BulletNarrativeSynthesisAgent,
    BulletEvidenceLinkerAgent,
    BulletConfidenceScoringAgent,
    BulletCoordinatorAgent,
    BulletProvenanceAuditorAgent,
    AsyncBulletGeneratorAgent,
    AsyncBulletCritiqueAgent,
)

from .hil import (
    VirtualReviewerPersonaAgent,
    VirtualReviewerCouncilAgent,
    HILFeedbackSummarizerAgent,
    HILReconciliationAgent,
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent,
)

__all__ = [
    # Models
    "SpecialistDraftPacket",
    "EvidenceClarificationRecord",
    "EvidenceBriefRecord",
    "EvidenceLiaisonPacket",
    "CritiqueFindingRecord",
    "CritiquePanelPacket",
    # Safety
    "PIISanitizerAgent",
    "BiasDetectorAgent",
    "PromptInjectionDetectorAgent",
    "ConstitutionalReviewerAgent",
    # Strategy
    "QueryComplexityClassifier",
    "ToTStrategistAgent",
    # Prompting
    "PromptEngineerAgent",
    # RAG
    "RAG_SearchAgent",
    # Drafting
    "StructureLeadAgent",
    "NarrativeStylistAgent",
    "ComplianceEditorAgent",
    "EvidenceLiaisonAgent",
    "CritiqueRoutingPanel",
    "DraftingGuildCoordinator",
    # Bullet
    "BulletEntityExtractionAgent",
    "BulletMetricsEnrichmentAgent",
    "BulletNarrativeSynthesisAgent",
    "BulletEvidenceLinkerAgent",
    "BulletConfidenceScoringAgent",
    "BulletCoordinatorAgent",
    "BulletProvenanceAuditorAgent",
    "AsyncBulletGeneratorAgent",
    "AsyncBulletCritiqueAgent",
    # HIL
    "VirtualReviewerPersonaAgent",
    "VirtualReviewerCouncilAgent",
    "HILFeedbackSummarizerAgent",
    "HILReconciliationAgent",
    "HILAmbiguityDetectorAgent",
    "HILFeedbackRouterAgent",
]
