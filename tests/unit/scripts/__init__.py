logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
"""Unit tests for scripts module.

This package contains unit tests for the scripts module, including:
- Logic operations tests
- Data access functionality tests
- Synthesis and validation tests
- Pipeline orchestration tests
- Runtime execution tests

Test Structure:
- Each test module corresponds to a specific scripts submodule
- Tests follow the standard pytest conventions
- Mock objects and fixtures are provided for complex dependencies
"""

import pytest
import logging


# Common test fixtures
@pytest.fixture
def mock_script_context() -> None:
    """Provide a mock script context for testing."""
    return {"runtime": "test", "environment": "unit_test", "debug": True}


# Export test utilities
__all__ = [
    "mock_script_context",
]
