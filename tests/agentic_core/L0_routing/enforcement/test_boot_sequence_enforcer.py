"""Tests for boot_sequence_enforcer.py module.

This is a minimal module that only emits a trace at import time.
Tests verify the module can be imported and the trace emission occurs.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestBootSequenceEnforcer:
    """Tests for boot_sequence_enforcer module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        # The module executes trace emission at import time
        with patch("agentic_core.L0_routing.enforcement.boot_sequence_enforcer._emit_records_execution_trace") as mock_emit:
            # Re-import to test trace emission
            import importlib
            import sys
            
            # Remove from cache if already imported
            if "agentic_core.L0_routing.enforcement.boot_sequence_enforcer" in sys.modules:
                del sys.modules["agentic_core.L0_routing.enforcement.boot_sequence_enforcer"]
            
            import agentic_core.L0_routing.enforcement.boot_sequence_enforcer
            mock_emit.assert_called_once_with("p0", "evidence", "boot_sequence_enforcer")
