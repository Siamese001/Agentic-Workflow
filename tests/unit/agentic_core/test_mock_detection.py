# Ownership: agentic_core / unknown
# -*- coding: utf-8 -*-
"""Test Mock Detection - atomic wrapper."""

from __future__ import annotations

from typing import Any, Dict, List

from shared.models import ValidationResult, ValidationSeverity
from shared.workflow_types import HopStatus, HopCheckpoint


def test_mock_detection(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process test mock detection data."""
    return {"status": "processed", "input_keys": list(data.keys())}


def get_test_mock_detection_config() -> Dict[str, Any]:
    """Get configuration for test_mock_detection."""
    return {"enabled": True, "version": "1.0"}
