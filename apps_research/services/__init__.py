"""
apps_research Services Layer — Autonomous Research Engine Capabilities.

Discrete service units for source discovery, harvesting, and synthesis.
Aligned with apps_lic services/ pattern.
"""

from apps_research.services.source_discovery_service import SourceDiscoveryService
from apps_research.services.content_harvester_service import ContentHarvesterService
from apps_research.services.credibility_scorer_service import CredibilityScorerService
from apps_research.services.insight_extractor_service import InsightExtractorService
from apps_research.services.synthesis_engine_service import SynthesisEngineService
from apps_research.services.citation_manager_service import CitationManagerService
from apps_research.services.knowledge_integrator_service import KnowledgeIntegratorService
from apps_research.services.report_compiler_service import ReportCompilerService

__all__ = [
    "SourceDiscoveryService",
    "ContentHarvesterService",
    "CredibilityScorerService",
    "InsightExtractorService",
    "SynthesisEngineService",
    "CitationManagerService",
    "KnowledgeIntegratorService",
    "ReportCompilerService",
]
