"""Test isolation for apps_underwriting_ai contract / pipeline tests.

These tests verify deterministic-skeleton invariants (verdict path, rationale
template text, evidence-register growth, feature canonical keys, etc.).
The Qwen-first rationale enrichment activated 2026-05-02 (plan
``apps-underwriting-ai-activation-e8a3c5`` W1 P1.2) is suppressed here so
the contract floor remains assertable byte-for-byte regardless of vLLM
availability on the test machine.

Production callers do NOT set this env var and therefore exercise the
full Qwen-first cascade.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _disable_llm_rationale_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Suppress all LLM-touching rationale paths during the contract suite.

    Covers (1) the Qwen-first primary path activated in
    ``apps-underwriting-ai-activation-e8a3c5`` W1 P1.2 and (2) the
    frontier-pairing telemetry shim activated in W3.3. Both are re-armed
    explicitly by the W3 pairing tests via their own monkeypatch.
    """
    monkeypatch.setenv("APPS_UW_RATIONALE_LLM_DISABLED", "1")
    monkeypatch.delenv("APPS_UW_FRONTIER_PAIRING_ENABLED", raising=False)
