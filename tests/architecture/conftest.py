"""
Conftest for tests/architecture/.
Auto-applies the 'architecture' marker to every test in this suite so the
global conftest default-marker filter does not deselect them.
"""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(config, items):
    """Add architecture marker to all tests collected from this directory."""
    arch_marker = pytest.mark.architecture
    for item in items:
        if "architecture" in str(item.fspath):
            item.add_marker(arch_marker)
