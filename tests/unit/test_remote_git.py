# tests/unit/test_remote_git.py
import pytest
import agentic_core

class TestStructure:
    def test_agentic_core_exists(self):
        assert agentic_core is not None
