"""
apps_research Services Layer — Autonomous Research Engine Capabilities.

Discrete service units for source discovery, harvesting, and synthesis.
Aligned with apps_lic services/ pattern.
"""

from __future__ import annotations

from .citation_manager_service import CitationManagerService
from .content_harvester_service import ContentHarvesterService
from .credibility_scorer_service import CredibilityScorerService
from .insight_extractor_service import InsightExtractorService
from .knowledge_integrator_service import KnowledgeIntegratorService
from .repo_signal_service import RepoSignalService
from .report_compiler_service import ReportCompilerService
from .source_discovery_service import SourceDiscoveryService
from .synthesis_engine_service import SynthesisEngineService

__all__ = [
    "CitationManagerService",
    "ContentHarvesterService",
    "CredibilityScorerService",
    "InsightExtractorService",
    "KnowledgeIntegratorService",
    "ReportCompilerService",
    "RepoSignalService",
    "SourceDiscoveryService",
    "SynthesisEngineService",
]
