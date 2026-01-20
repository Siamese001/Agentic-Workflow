"""
Pytest Configuration for Dashboard Tests
========================================

Shared fixtures and configuration for all dashboard tests.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def disable_path_shield():
    """Disable path_shield for all dashboard tests - we need real file access."""
    pass

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the validated project root path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def dashboard_dir(project_root) -> Path:
    """Get the dashboard directory path."""
    return project_root / "agentic_core" / "L6_observability" / "dashboards"


@pytest.fixture(scope="session")
def html_file(dashboard_dir) -> Path:
    """Get the dashboard HTML file path."""
    return dashboard_dir / "autonomy_dashboard.html"


@pytest.fixture(scope="session")
def html_content(html_file) -> str:
    """Load the dashboard HTML content."""
    if not html_file.exists():
        pytest.skip(f"Dashboard HTML not found: {html_file}")
    return html_file.read_text(encoding='utf-8')


@pytest.fixture(scope="session")
def agent_discovery_data(project_root) -> List[Dict[str, Any]]:
    """Load agent discovery data."""
    discovery_file = project_root / "agent_discovery_full.json"
    if not discovery_file.exists():
        pytest.skip(f"Agent discovery file not found: {discovery_file}")
    with open(discovery_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def dashboard_data(dashboard_dir) -> List[Dict[str, Any]]:
    """Load dashboard data from dashboard_data.js."""
    data_file = dashboard_dir / "data" / "dashboard_data.js"
    if not data_file.exists():
        pytest.skip(f"Dashboard data file not found: {data_file}")
    
    content = data_file.read_text(encoding='utf-8')
    lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
    content_clean = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
    return json.loads(content_clean)


@pytest.fixture(scope="session")
def js_dir(dashboard_dir) -> Path:
    """Get the JavaScript directory path."""
    return dashboard_dir / "js"


@pytest.fixture(scope="session")
def css_dir(dashboard_dir) -> Path:
    """Get the CSS directory path."""
    return dashboard_dir / "css"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "dashboard: mark test as a dashboard test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (requires browser)"
    )
    config.addinivalue_line(
        "markers", "playwright: mark test as requiring Playwright"
    )
