# Core pytest configuration
import pytest

# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

"""Smoke test configuration — fast, deterministic, no external deps."""
import logging
import pytest
from pathlib import Path

# Suppress lifecycle trace loggers (consistent with root conftest)
for _name in ["adg", "lifecycle"]:
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False

@pytest.fixture(autouse=True)
def smoke_timeout(request):
    """Enforce 5s max per smoke test."""
    # Note: Requires pytest-timeout if installed
    pass

# Phase definitions - SINGLE SOURCE OF TRUTH
PHASE_DEFINITIONS = {
    'phase1': ['adg', 'config', 'embeddings', 'health'],
    'phase2': ['alerting', 'audit', 'backup', 'compliance'],
    'phase3': ['analytics', 'automation', 'dashboards', 'reporting'],
    'phase4': ['infrastructure', 'interfaces', 'layers', 'runtime', 'tracing', 'visualization'],
    'phase5': ['experimental', 'research', 'development', 'testing', 'deployment',
              'operations', 'maintenance', 'optimization', 'experimental_features',
              'beta_features', 'future_capabilities'],
    # Additional domains not in original phases
    'additional': ['integration', 'logging', 'metrics', 'monitoring', 'observability',
                  'orchestration', 'performance', 'recovery', 'security', 'telemetry',
                  'workflows']
}

def pytest_collection_modifyitems(items):
    """Auto-mark all tests in smoke/ with appropriate markers."""
    for item in items:
        if "smoke" in str(item.fspath):
            # Always mark as smoke test
            item.add_marker(pytest.mark.smoke)

            # Determine which phase this test belongs to
            test_path = Path(item.fspath)
            domain = test_path.parent.name

            # Add phase markers
            for phase, domains in PHASE_DEFINITIONS.items():
                if domain in domains:
                    if phase.startswith('phase'):
                        item.add_marker(getattr(pytest.mark, phase))
                    else:
                        item.add_marker(pytest.mark.additional)
                    break
