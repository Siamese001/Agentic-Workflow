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

    def test_discover_sources_blank_query_raises(self):
        """G2: _normalize_query raises ValueError on blank input."""
        from apps_research.services.source_discovery_service import SourceDiscoveryService

        service = SourceDiscoveryService()
        with pytest.raises(ValueError, match="must not be blank"):
            service.discover_sources(query="   ")

    def test_discover_sources_max_sources_capped_at_50(self):
        """G3: max_sources > 50 is silently capped to 50."""
        from apps_research.services.source_discovery_service import SourceDiscoveryService, _MAX_SOURCES

        service = SourceDiscoveryService()
        result = service.discover_sources(query="AI governance", max_sources=999)
        assert len(result["sources"]) <= _MAX_SOURCES

    def test_stable_digest_is_deterministic(self):
        """G3 edge: _stable_digest produces same 16-char hex for same input."""
        from apps_research.services.source_discovery_service import _stable_digest

        assert _stable_digest("hello") == _stable_digest("hello")
        assert len(_stable_digest("hello")) == 16
        assert _stable_digest("hello") != _stable_digest("world")

    def test_normalize_seed_urls_filters_invalid_schemes(self):
        """G3 edge: _normalize_seed_urls drops ftp/file URLs, keeps http/https."""
        from apps_research.services.source_discovery_service import _normalize_seed_urls

        urls = ["https://valid.com/page", "ftp://bad.com", "file:///etc/passwd", "http://ok.org"]
        result = _normalize_seed_urls(urls)
        assert result == ["https://valid.com/page", "http://ok.org"]


@pytest.mark.unit
class TestResearchTypesValidation:
    """G4/G5: validators added in hardening pass."""

    def test_source_entry_rejects_invalid_url_scheme(self):
        """G4: SourceEntry.validate_url raises for ftp:// scheme."""
        from pydantic import ValidationError
        from apps_research.types.research_types import SourceEntry

        with pytest.raises(ValidationError, match="url scheme"):
            SourceEntry(source_id="abc123", title="Test", url="ftp://bad.example.com")

    def test_source_entry_accepts_https_url(self):
        """G4 happy: SourceEntry accepts https URL."""
        from apps_research.types.research_types import SourceEntry

        entry = SourceEntry(source_id="abc123", title="Test", url="https://example.com/page")
        assert entry.url == "https://example.com/page"

    def test_source_entry_accepts_empty_url(self):
        """G4 edge: SourceEntry allows empty url (optional field)."""
        from apps_research.types.research_types import SourceEntry

        entry = SourceEntry(source_id="abc123", title="Test", url="")
        assert entry.url == ""

    def test_request_trace_id_rejects_unsafe_chars(self):
        """G5: validate_trace_id raises for spaces/special chars."""
        from pydantic import ValidationError
        from apps_research.types.research_types import ResearchRequest

        with pytest.raises(ValidationError, match="trace_id"):
            ResearchRequest(topic="AI safety", trace_id="bad id with spaces!")

    def test_request_trace_id_accepts_valid_id(self):
        """G5 happy: validate_trace_id accepts hex-like trace ID."""
        from apps_research.types.research_types import ResearchRequest

        req = ResearchRequest(topic="AI safety", trace_id="abc123def456")
        assert req.trace_id == "abc123def456"

    def test_request_comparison_subjects_filters_empty(self):
        """G5 edge: validate_comparison_subjects drops blank entries."""
        from apps_research.types.research_types import ResearchRequest

        req = ResearchRequest(topic="AI safety", comparison_subjects=["GPT-4", "  ", "Claude"])
        assert req.comparison_subjects == ["GPT-4", "Claude"]

    def test_synthesis_engine_service_init(self):
        """Test SynthesisEngineService initialization."""
        from apps_research.services.synthesis_engine_service import SynthesisEngineService

        service = SynthesisEngineService()
        assert service.config == {}
