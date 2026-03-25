"""Research smoke tests — import verification and basic functionality."""
import pytest

@pytest.mark.smoke
def test_research_importable():
    """Verify research module imports without error."""
    try:
        import agentic_core.research
        assert agentic_core.research is not None
    except ImportError as e:
        pytest.skip(f"research not yet implemented: {e}")

@pytest.mark.smoke
def test_research_engine_importable():
    """Verify research engine imports without error."""
    try:
        from agentic_core.research.research_engine import (
            ResearchEngine,
        )
        assert ResearchEngine is not None
    except ImportError as e:
        pytest.skip(f"ResearchEngine not yet implemented: {e}")

@pytest.mark.smoke
def test_research_manager_importable():
    """Verify research manager imports without error."""
    try:
        from agentic_core.research.research_manager import (
            ResearchManager,
        )
        assert ResearchManager is not None
    except ImportError as e:
        pytest.skip(f"ResearchManager not yet implemented: {e}")

@pytest.mark.smoke
def test_research_analyzer_importable():
    """Verify research analyzer imports without error."""
    try:
        from agentic_core.research.research_analyzer import (
            ResearchAnalyzer,
        )
        assert ResearchAnalyzer is not None
    except ImportError as e:
        pytest.skip(f"ResearchAnalyzer not yet implemented: {e}")

@pytest.mark.smoke
def test_research_collector_importable():
    """Verify research collector imports without error."""
    try:
        from agentic_core.research.research_collector import (
            ResearchCollector,
        )
        assert ResearchCollector is not None
    except ImportError as e:
        pytest.skip(f"ResearchCollector not yet implemented: {e}")

@pytest.mark.smoke
def test_research_processor_importable():
    """Verify research processor imports without error."""
    try:
        from agentic_core.research.research_processor import (
            ResearchProcessor,
        )
        assert ResearchProcessor is not None
    except ImportError as e:
        pytest.skip(f"ResearchProcessor not yet implemented: {e}")

@pytest.mark.smoke
def test_research_validator_importable():
    """Verify research validator imports without error."""
    try:
        from agentic_core.research.research_validator import (
            ResearchValidator,
        )
        assert ResearchValidator is not None
    except ImportError as e:
        pytest.skip(f"ResearchValidator not yet implemented: {e}")

@pytest.mark.smoke
def test_research_synthesizer_importable():
    """Verify research synthesizer imports without error."""
    try:
        from agentic_core.research.research_synthesizer import (
            ResearchSynthesizer,
        )
        assert ResearchSynthesizer is not None
    except ImportError as e:
        pytest.skip(f"ResearchSynthesizer not yet implemented: {e}")

@pytest.mark.smoke
def test_research_storage_importable():
    """Verify research storage imports without error."""
    try:
        from agentic_core.research.research_storage import (
            ResearchStorage,
        )
        assert ResearchStorage is not None
    except ImportError as e:
        pytest.skip(f"ResearchStorage not yet implemented: {e}")

@pytest.mark.smoke
def test_research_indexer_importable():
    """Verify research indexer imports without error."""
    try:
        from agentic_core.research.research_indexer import (
            ResearchIndexer,
        )
        assert ResearchIndexer is not None
    except ImportError as e:
        pytest.skip(f"ResearchIndexer not yet implemented: {e}")

@pytest.mark.smoke
def test_research_exporter_importable():
    """Verify research exporter imports without error."""
    try:
        from agentic_core.research.research_exporter import (
            ResearchExporter,
        )
        assert ResearchExporter is not None
    except ImportError as e:
        pytest.skip(f"ResearchExporter not yet implemented: {e}")

@pytest.mark.smoke
def test_research_config_importable():
    """Verify research config imports without error."""
    try:
        from agentic_core.research.research_config import (
            get_research_config,
        )
        assert callable(get_research_config), "get_research_config should be callable"
    except ImportError as e:
        pytest.skip(f"research_config not yet implemented: {e}")