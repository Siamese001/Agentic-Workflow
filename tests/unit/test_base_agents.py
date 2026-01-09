# tests/unit/test_base_agents.py
import pytest
import agentic_core

class TestStructure:
    def test_agentic_core_exists(self):
        assert agentic_core is not None
