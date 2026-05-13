"""Backward-compatibility shim — re-exports UnderwritingEngine from _legacy.

The canonical execution path is the agentic_core dispatch chain via
apps_underwriting_ai/runtime/dispatch/underwriting_dispatch.py.

This shim preserves the contract surface expected by test_contract.py and
test_outputs.py (UnderwritingEngine.run → UnderwritingResult) without
restoring the parallel pipeline.

Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W4.
"""
from __future__ import annotations

from apps_underwriting_ai.engines._legacy.underwriting_engine import UnderwritingEngine

__all__ = ["UnderwritingEngine"]
