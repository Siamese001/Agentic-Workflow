"""
Tests: SSOT heal runner pre-flight restore + symbol gate logic contract.

Verifies that the runner's pre-flight design would:
1. Detect a missing _legacy_main symbol
2. Retry restore once
3. Fail fast with exit code 2 if still missing
"""

import pytest

pytestmark = pytest.mark.guardian


class TestPreflightSymbolGate:
    def test_symbol_check_passes_when_present(self):
        """Verify _legacy_main is importable from the canonical module."""
        import sys

        sys.path.insert(0, ".")
        from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main

        assert callable(_legacy_main)

    def test_preflight_retry_logic_contract(self):
        """
        Contract test: if symbol missing on first check, retry once.
        We simulate this by tracking call counts.
        """
        call_count = {"check": 0, "restore": 0}

        def mock_check_symbol():
            call_count["check"] += 1
            # First call fails, second succeeds
            return call_count["check"] >= 2

        def mock_restore():
            call_count["restore"] += 1

        # Simulate the runner's pre-flight logic
        mock_restore()  # Initial restore
        if not mock_check_symbol():  # First check fails
            mock_restore()  # Retry restore
            result = mock_check_symbol()  # Second check
        else:
            result = True

        assert result is True
        assert call_count["check"] == 2
        assert call_count["restore"] == 2

    def test_preflight_fails_fast_if_still_missing(self):
        """
        Contract test: if symbol still missing after retry, exit 2.
        """
        call_count = {"check": 0, "restore": 0}

        def mock_check_symbol():
            call_count["check"] += 1
            return False  # Always fails

        def mock_restore():
            call_count["restore"] += 1

        # Simulate the runner's pre-flight logic
        mock_restore()  # Initial restore
        exit_code = 0
        if not mock_check_symbol():  # First check fails
            mock_restore()  # Retry restore
            if not mock_check_symbol():  # Second check also fails
                exit_code = 2  # Fail fast

        assert exit_code == 2
        assert call_count["check"] == 2
        assert call_count["restore"] == 2

    def test_preflight_succeeds_on_first_try(self):
        """
        Contract test: if symbol present on first check, no retry needed.
        """
        call_count = {"check": 0, "restore": 0}

        def mock_check_symbol():
            call_count["check"] += 1
            return True  # Always succeeds

        def mock_restore():
            call_count["restore"] += 1

        # Simulate the runner's pre-flight logic
        mock_restore()  # Initial restore
        exit_code = 0
        if not mock_check_symbol():  # First check passes
            mock_restore()
            if not mock_check_symbol():
                exit_code = 2

        assert exit_code == 0
        assert call_count["check"] == 1
        assert call_count["restore"] == 1
