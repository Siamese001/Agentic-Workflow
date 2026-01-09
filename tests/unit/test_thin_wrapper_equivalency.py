# tests/unit/test_thin_wrapper_equivalency.py
import pytest
import agentic_core

class TestStructure:
    def test_agentic_core_exists(self):
        assert agentic_core is not None
