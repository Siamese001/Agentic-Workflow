# tests/unit/test_shared_test_basics.py
import pytest
import agentic_core

class TestStructure:
    def test_agentic_core_exists(self):
        assert agentic_core is not None
