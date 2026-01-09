# tests/unit/test_agentic_core_test_check_tests_compliance.py
import pytest
import agentic_core.L5_safety

class TestStructure:
    def test_l5_safety_module_exists(self):
        assert agentic_core.L5_safety is not None
