"""Wave 1.8 — Token Budget Hard Enforcement Tests.

Tests prove:
1) PASS: budget sufficient → model executes, PASS artifact emitted, remaining correct
2) PRE-CALL FAIL: insufficient budget → model NOT called, TokenBudgetExceeded, FAIL artifact
3) POST-CALL FAIL: model returns more tokens than remaining → TokenBudgetExceeded, FAIL artifact
4) Nested calls: second call consumes remaining budget correctly
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L2_execution.types.token_enforcement_types import (
    TokenBudgetExceeded,
    TokenBudgetStore,
    TokenEnforcementArtifact,
    TokenEnforcementOutcome,
    build_token_enforcement_artifact,
    estimate_prompt_tokens,
    get_token_budget_store,
    set_token_budget_store,
)

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(autouse=True)
def _reset_budget_store():
    """Reset global budget store before/after each test."""
    set_token_budget_store(None)
    yield
    set_token_budget_store(None)


@pytest.fixture()
def gateway():
    """Create a SovereignLLMGateway with mocked provider calls."""
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()

    # Mock config to avoid env var dependencies
    mock_config = MagicMock()
    mock_config.openai_model = "gpt-4o"
    mock_config.anthropic_model = "claude-3.5"
    mock_config.max_audit_log_size = 100
    gw.config  # trigger property; we'll patch it
    return gw


def _run_async(coro):
    """Run async coroutine synchronously for tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# =========================================================================
# Unit tests — TokenBudgetStore
# =========================================================================


class TestTokenBudgetStore:
    """Unit tests for trace-bound budget store."""

    def test_get_or_init_creates_budget(self):
        store = TokenBudgetStore()
        ctx = store.get_or_init("trace-1", 1000)
        assert ctx.trace_id == "trace-1"
        assert ctx.initial_budget == 1000
        assert ctx.remaining_budget == 1000

    def test_get_or_init_returns_existing(self):
        store = TokenBudgetStore()
        ctx1 = store.get_or_init("trace-1", 1000)
        ctx2 = store.get_or_init("trace-1", 9999)
        assert ctx1 is ctx2
        assert ctx2.initial_budget == 1000

    def test_consume_subtracts(self):
        store = TokenBudgetStore()
        store.get_or_init("t1", 500)
        remaining = store.consume("t1", 200)
        assert remaining == 300

    def test_consume_can_go_negative(self):
        store = TokenBudgetStore()
        store.get_or_init("t1", 100)
        remaining = store.consume("t1", 150)
        assert remaining == -50

    def test_consume_missing_trace_raises(self):
        store = TokenBudgetStore()
        with pytest.raises(KeyError, match="No budget for trace_id"):
            store.consume("nonexistent", 10)

    def test_reset_removes_trace(self):
        store = TokenBudgetStore()
        store.get_or_init("t1", 100)
        store.reset("t1")
        ctx = store.get_or_init("t1", 500)
        assert ctx.initial_budget == 500

    def test_separate_traces_independent(self):
        store = TokenBudgetStore()
        store.get_or_init("t1", 1000)
        store.get_or_init("t2", 2000)
        store.consume("t1", 300)
        ctx1 = store.get_or_init("t1", 1000)
        ctx2 = store.get_or_init("t2", 2000)
        assert ctx1.remaining_budget == 700
        assert ctx2.remaining_budget == 2000


# =========================================================================
# Unit tests — Artifact construction
# =========================================================================


class TestArtifactConstruction:
    """TokenEnforcementArtifact construction and validation."""

    def test_pass_artifact(self):
        art = build_token_enforcement_artifact(
            trace_id="t1",
            model="gpt-4o",
            prompt_tokens=100,
            completion_tokens=200,
            remaining_budget=700,
            hard_limit=1000,
            outcome=TokenEnforcementOutcome.PASS,
        )
        assert art.enforcement_mode == "HARD"
        assert art.outcome == TokenEnforcementOutcome.PASS
        assert art.remaining_budget == 700

    def test_fail_artifact(self):
        art = build_token_enforcement_artifact(
            trace_id="t1",
            model="gpt-4o",
            prompt_tokens=500,
            completion_tokens=0,
            remaining_budget=50,
            hard_limit=1000,
            outcome=TokenEnforcementOutcome.FAIL_PRE_CALL,
        )
        assert art.outcome == TokenEnforcementOutcome.FAIL_PRE_CALL

    def test_artifact_is_frozen(self):
        art = build_token_enforcement_artifact(
            trace_id="t1",
            model="m",
            prompt_tokens=0,
            completion_tokens=0,
            remaining_budget=0,
            hard_limit=100,
            outcome=TokenEnforcementOutcome.PASS,
        )
        with pytest.raises(AttributeError):
            art.remaining_budget = 999  # type: ignore[misc]

    def test_non_hard_mode_rejected(self):
        with pytest.raises(ValueError, match="enforcement_mode must be 'HARD'"):
            TokenEnforcementArtifact(
                artifact_id="a1",
                timestamp_utc="2026-01-01T00:00:00Z",
                trace_id="t1",
                model="m",
                prompt_tokens=0,
                completion_tokens=0,
                remaining_budget=0,
                hard_limit=100,
                enforcement_mode="SOFT",
                outcome=TokenEnforcementOutcome.PASS,
            )


# =========================================================================
# Unit tests — estimate_prompt_tokens
# =========================================================================


class TestEstimateTokens:
    """Token estimation is deterministic."""

    def test_estimate_deterministic(self):
        assert estimate_prompt_tokens("hello world") == estimate_prompt_tokens("hello world")

    def test_estimate_minimum_one(self):
        assert estimate_prompt_tokens("") >= 1

    def test_longer_prompt_more_tokens(self):
        short = estimate_prompt_tokens("hi")
        long = estimate_prompt_tokens("a" * 400)
        assert long > short


# =========================================================================
# Integration — PASS case
# =========================================================================


class TestPassCase:
    """Budget 1000, prompt ~100 tokens, completion 200 → remaining 700, PASS artifact."""

    def test_pass_budget_sufficient(self, gateway):
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        # Stub _call_provider to return controlled token counts
        async def mock_call_provider(prov, prompt, model, temp, max_tok, **kw):
            return {
                "content": "response",
                "tokens": 300,
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "provider": prov,
                "model": model,
            }

        gateway._call_provider = mock_call_provider

        with (
            patch(
                "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
                mock_emit,
            ),
            patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
                return_value=False,
            ),
            patch.object(
                type(gateway),
                "config",
                new_callable=lambda: property(
                    lambda self: MagicMock(
                        openai_model="gpt-4o",
                        anthropic_model="claude-3.5",
                        max_audit_log_size=100,
                    ),
                ),
            ),
        ):
            result = _run_async(
                gateway.generate(
                    prompt="a" * 400,  # ~100 tokens
                    model="gpt-4o",
                    trace_id="trace-pass",
                    token_budget_limit=1000,
                ),
            )

        assert result["content"] == "response"

        # Check artifact emitted
        token_artifacts = [e for e in emitted if e["type"] == "TOKEN_ENFORCEMENT"]
        assert len(token_artifacts) == 1
        art = token_artifacts[0]["artifact"]
        assert art.outcome == TokenEnforcementOutcome.PASS
        assert art.prompt_tokens == 100
        assert art.completion_tokens == 200
        assert art.remaining_budget == 700
        assert art.hard_limit == 1000
        assert art.enforcement_mode == "HARD"


# =========================================================================
# Integration — PRE-CALL FAIL
# =========================================================================


class TestPreCallFail:
    """Remaining 50, estimated prompt 100 → model NOT called, raises, FAIL artifact."""

    def test_pre_call_budget_exceeded(self, gateway):
        emitted = []
        model_called = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        async def mock_call_provider(prov, prompt, model, temp, max_tok, **kw):
            model_called.append(True)
            return {"content": "x", "tokens": 100, "provider": prov, "model": model}

        gateway._call_provider = mock_call_provider

        # Pre-seed budget with only 50 remaining
        store = get_token_budget_store()
        store.get_or_init("trace-pre-fail", 50)

        with (
            patch(
                "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
                mock_emit,
            ),
            patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
                return_value=False,
            ),
            patch.object(
                type(gateway),
                "config",
                new_callable=lambda: property(
                    lambda self: MagicMock(
                        openai_model="gpt-4o",
                        anthropic_model="claude-3.5",
                        max_audit_log_size=100,
                    ),
                ),
            ),
        ):
            with pytest.raises(TokenBudgetExceeded) as exc_info:
                _run_async(
                    gateway.generate(
                        prompt="a" * 400,  # ~100 tokens > 50 remaining
                        model="gpt-4o",
                        trace_id="trace-pre-fail",
                        token_budget_limit=50,
                    ),
                )

        assert exc_info.value.phase == "pre_call"
        assert exc_info.value.remaining == 50
        assert len(model_called) == 0  # model NOT called

        token_artifacts = [e for e in emitted if e["type"] == "TOKEN_ENFORCEMENT"]
        assert len(token_artifacts) == 1
        assert token_artifacts[0]["artifact"].outcome == TokenEnforcementOutcome.FAIL_PRE_CALL


# =========================================================================
# Integration — POST-CALL FAIL
# =========================================================================


class TestPostCallFail:
    """Remaining 100, prompt 50 + completion 60 = 110 → remaining -10, raises, FAIL artifact."""

    def test_post_call_budget_exceeded(self, gateway):
        emitted = []

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        async def mock_call_provider(prov, prompt, model, temp, max_tok, **kw):
            return {
                "content": "response",
                "tokens": 110,
                "prompt_tokens": 50,
                "completion_tokens": 60,
                "provider": prov,
                "model": model,
            }

        gateway._call_provider = mock_call_provider

        with (
            patch(
                "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
                mock_emit,
            ),
            patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
                return_value=False,
            ),
            patch.object(
                type(gateway),
                "config",
                new_callable=lambda: property(
                    lambda self: MagicMock(
                        openai_model="gpt-4o",
                        anthropic_model="claude-3.5",
                        max_audit_log_size=100,
                    ),
                ),
            ),
        ):
            with pytest.raises(TokenBudgetExceeded) as exc_info:
                _run_async(
                    gateway.generate(
                        prompt="short",  # ~1 token, passes pre-call gate
                        model="gpt-4o",
                        trace_id="trace-post-fail",
                        token_budget_limit=100,
                    ),
                )

        assert exc_info.value.phase == "post_call"
        assert exc_info.value.remaining == -10

        token_artifacts = [e for e in emitted if e["type"] == "TOKEN_ENFORCEMENT"]
        assert len(token_artifacts) == 1
        assert token_artifacts[0]["artifact"].outcome == TokenEnforcementOutcome.FAIL_POST_CALL
        assert token_artifacts[0]["artifact"].remaining_budget == -10


# =========================================================================
# Integration — Nested calls (budget propagation)
# =========================================================================


class TestNestedCalls:
    """Second call consumes remaining budget from first call correctly."""

    def test_nested_budget_propagation(self, gateway):
        emitted = []
        call_count = [0]

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        async def mock_call_provider(prov, prompt, model, temp, max_tok, **kw):
            call_count[0] += 1
            return {
                "content": f"response-{call_count[0]}",
                "tokens": 300,
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "provider": prov,
                "model": model,
            }

        gateway._call_provider = mock_call_provider

        with (
            patch(
                "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
                mock_emit,
            ),
            patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
                return_value=False,
            ),
            patch.object(
                type(gateway),
                "config",
                new_callable=lambda: property(
                    lambda self: MagicMock(
                        openai_model="gpt-4o",
                        anthropic_model="claude-3.5",
                        max_audit_log_size=100,
                    ),
                ),
            ),
        ):
            # First call: budget 1000, uses 300 → remaining 700
            _run_async(
                gateway.generate(
                    prompt="a" * 400,
                    model="gpt-4o",
                    trace_id="trace-nested",
                    token_budget_limit=1000,
                ),
            )

            # Second call: same trace_id, uses 300 → remaining 400
            _run_async(
                gateway.generate(
                    prompt="a" * 400,
                    model="gpt-4o",
                    trace_id="trace-nested",
                    token_budget_limit=1000,
                ),
            )

        assert call_count[0] == 2

        token_artifacts = [e for e in emitted if e["type"] == "TOKEN_ENFORCEMENT"]
        assert len(token_artifacts) == 2

        # First call: remaining 700
        assert token_artifacts[0]["artifact"].remaining_budget == 700
        assert token_artifacts[0]["artifact"].outcome == TokenEnforcementOutcome.PASS

        # Second call: remaining 400
        assert token_artifacts[1]["artifact"].remaining_budget == 400
        assert token_artifacts[1]["artifact"].outcome == TokenEnforcementOutcome.PASS

    def test_nested_exhaustion(self, gateway):
        """Third call exceeds remaining budget after two calls."""
        emitted = []
        call_count = [0]

        def mock_emit(self_emitter, type_label, artifact):
            emitted.append({"type": type_label, "artifact": artifact})

        async def mock_call_provider(prov, prompt, model, temp, max_tok, **kw):
            call_count[0] += 1
            return {
                "content": f"response-{call_count[0]}",
                "tokens": 400,
                "prompt_tokens": 200,
                "completion_tokens": 200,
                "provider": prov,
                "model": model,
            }

        gateway._call_provider = mock_call_provider

        with (
            patch(
                "agentic_core.L0_maintenance.types.v15_contracts.TelemetryEmitter.emit_typed_artifact",
                mock_emit,
            ),
            patch(
                "agentic_core.L2_execution.enforcement.SovereignLLMGateway.is_v15_enforced",
                return_value=False,
            ),
            patch.object(
                type(gateway),
                "config",
                new_callable=lambda: property(
                    lambda self: MagicMock(
                        openai_model="gpt-4o",
                        anthropic_model="claude-3.5",
                        max_audit_log_size=100,
                    ),
                ),
            ),
        ):
            # Call 1: budget 700, uses 400 → remaining 300
            _run_async(
                gateway.generate(
                    prompt="a" * 40,
                    model="gpt-4o",
                    trace_id="trace-exhaust",
                    token_budget_limit=700,
                ),
            )

            # Call 2: remaining 300, uses 400 → remaining -100 → POST-CALL FAIL
            with pytest.raises(TokenBudgetExceeded) as exc_info:
                _run_async(
                    gateway.generate(
                        prompt="a" * 40,
                        model="gpt-4o",
                        trace_id="trace-exhaust",
                        token_budget_limit=700,
                    ),
                )

        assert exc_info.value.phase == "post_call"
        assert exc_info.value.remaining == -100
