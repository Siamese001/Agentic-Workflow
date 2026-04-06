"""Test consolidated services for apps_research."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResearchServices:
    """Test apps_research services."""

    def test_citation_manager_service_init(self):
        """Test CitationManagerService initialization."""
        from apps_research.services.citation_manager_service import CitationManagerService

        service = CitationManagerService()
        assert service.config == {}

    def test_content_harvester_service_init(self):
        """Test ContentHarvesterService initialization."""
        from apps_research.services.content_harvester_service import ContentHarvesterService

        service = ContentHarvesterService()
        assert service.config == {}

    def test_credibility_scorer_service_init(self):
        """Test CredibilityScorerService initialization."""
        from apps_research.services.credibility_scorer_service import CredibilityScorerService

        service = CredibilityScorerService()
        assert service.config == {}

    def test_insight_extractor_service_init(self):
        """Test InsightExtractorService initialization."""
        from apps_research.services.insight_extractor_service import InsightExtractorService

        service = InsightExtractorService()
        assert service.config == {}

    def test_knowledge_integrator_service_init(self):
        """Test KnowledgeIntegratorService initialization."""
        from apps_research.services.knowledge_integrator_service import KnowledgeIntegratorService

        service = KnowledgeIntegratorService()
        assert service.config == {}

    @patch("apps_research.services.repo_signal_service.RepoSignalAdapter")
    def test_repo_signal_service_collect(self, mock_adapter):
        """Test RepoSignalService collect."""
        from apps_research.services.repo_signal_service import RepoSignalService

        mock_shared = MagicMock()
        mock_shared.captured_at = "2024-01-01"
        mock_shared.adg = {}
        mock_shared.tests = {}
        mock_shared.ci = {}
        mock_shared.governance = {}
        mock_shared.provenance = {}
        mock_shared.baseline = {}

        mock_adapter.return_value.collect.return_value = mock_shared

        service = RepoSignalService()
        snapshot = service.collect()
        assert snapshot.captured_at == "2024-01-01"

    def test_report_compiler_service_init(self):
        """Test ReportCompilerService initialization."""
        from apps_research.services.report_compiler_service import ReportCompilerService

        service = ReportCompilerService()
        assert service.config == {}

    def test_source_discovery_service_init(self):
        """Test SourceDiscoveryService initialization."""
        from apps_research.services.source_discovery_service import SourceDiscoveryService

        service = SourceDiscoveryService()
        assert service.config == {}

    def test_synthesis_engine_service_init(self):
        """Test SynthesisEngineService initialization."""
        from apps_research.services.synthesis_engine_service import SynthesisEngineService

        service = SynthesisEngineService()
        assert service.config == {}
