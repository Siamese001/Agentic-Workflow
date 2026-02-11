"""CONSOLIDATED: SignatureVerifierAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from agentic_core.L5_safety.reasoning.InspectorExecutor import InspectorExecutor as SignatureVerifierAgent

__all__ = ["SignatureVerifierAgent"]
