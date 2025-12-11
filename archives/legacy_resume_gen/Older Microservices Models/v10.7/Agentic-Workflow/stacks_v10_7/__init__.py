"""Stack-specific agent implementations for v10.7."""




# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.prompting import PromptEngineerAgent  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.rag import RAG_SearchAgent  # INVALID: Cannot import from path with hyphens



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
