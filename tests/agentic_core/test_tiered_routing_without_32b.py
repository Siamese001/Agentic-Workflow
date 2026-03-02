"""
WAVE 3 — Tiered Local Routing Tests (No 32B).

Validates:
- Local fast (7B) routes correctly for low/medium severity
- Local strong (14B) routes correctly for high severity
- Gemini-2.5-Pro backstop always present for all failure states
- Failure escalation invariants (6 conditions → Gemini)
- No 32B model in any routing path
- No quantized tier introduced
- Gemini-2.5-Pro is never removed from gateway
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    QWEN_7B_MAX_MODEL_LEN,
    QWEN_7B_MODEL_ID,
    QWEN_14B_MODEL_ID,
    TaskClass,
    VLLMFailureType,
    run_preflight_budget_check,
    select_local_tier,
)

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
_BUDGET_TYPES_FILE = _PROJECT_ROOT / "agentic_core" / "L2_execution" / "types" / "vllm_token_budget_types.py"

_SMALL_PROMPT = "Fix the import error in the module."


def _passing_preflight(task_class: str = TaskClass.HEALING_JSON_ARTIFACT.value) -> object:
    """Helper: produce a passing preflight result."""
    return run_preflight_budget_check(
        prompt=_SMALL_PROMPT,
        task_class=task_class,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )


# ---------------------------------------------------------------------------
# Test 1 — Local fast routes correctly (low severity)
# ---------------------------------------------------------------------------


def test_local_fast_routes_correctly_low_severity() -> None:
    """Low severity + passing budget must route to local_fast (7B)."""
    preflight = _passing_preflight()
    decision = select_local_tier(preflight=preflight, severity="low")
    assert decision.tier == "local_fast"
    assert decision.model_id == QWEN_7B_MODEL_ID
    assert decision.failure_type is None


# ---------------------------------------------------------------------------
# Test 2 — Local fast routes correctly (medium severity)
# ---------------------------------------------------------------------------


def test_local_fast_routes_correctly_medium_severity() -> None:
    """Medium severity + passing budget must route to local_fast (7B)."""
    preflight = _passing_preflight()
    decision = select_local_tier(preflight=preflight, severity="medium")
    assert decision.tier == "local_fast"
    assert decision.model_id == QWEN_7B_MODEL_ID
    assert decision.failure_type is None


# ---------------------------------------------------------------------------
# Test 3 — Local strong routes correctly (high severity)
# ---------------------------------------------------------------------------


def test_local_strong_routes_correctly_high_severity() -> None:
    """High severity + passing budget must route to local_strong (14B)."""
    preflight = _passing_preflight()
    decision = select_local_tier(preflight=preflight, severity="high")
    assert decision.tier == "local_strong"
    assert decision.model_id == QWEN_14B_MODEL_ID
    assert decision.failure_type is None


# ---------------------------------------------------------------------------
# Test 4 — Gemini backstop always present: token budget exceeded
# ---------------------------------------------------------------------------


def test_gemini_backstop_token_budget_exceeded() -> None:
    """TOKEN_BUDGET_EXCEEDED must route to Gemini-2.5-Pro."""
    huge_prompt = "x " * 50000
    preflight = run_preflight_budget_check(
        prompt=huge_prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert preflight.token_budget_ok is False
    decision = select_local_tier(preflight=preflight, severity="low")
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED


# ---------------------------------------------------------------------------
# Test 5 — Gemini backstop: circuit breaker open
# ---------------------------------------------------------------------------


def test_gemini_backstop_circuit_breaker_open() -> None:
    """Circuit breaker open must route to Gemini-2.5-Pro."""
    preflight = _passing_preflight()
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        circuit_breaker_open=True,
    )
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN


# ---------------------------------------------------------------------------
# Test 6 — Gemini backstop: queue overflow
# ---------------------------------------------------------------------------


def test_gemini_backstop_queue_overflow() -> None:
    """Queue overflow must route to Gemini-2.5-Pro."""
    preflight = _passing_preflight()
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        queue_overflow=True,
    )
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.QUEUE_OVERFLOW


# ---------------------------------------------------------------------------
# Test 7 — Gemini backstop: GPU health failed
# ---------------------------------------------------------------------------


def test_gemini_backstop_gpu_health_failed() -> None:
    """GPU health failure must route to Gemini-2.5-Pro."""
    preflight = _passing_preflight()
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        gpu_health_failed=True,
    )
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.GPU_HEALTH_FAILED


# ---------------------------------------------------------------------------
# Test 8 — Gemini backstop: schema validation failed
# ---------------------------------------------------------------------------


def test_gemini_backstop_schema_validation_failed() -> None:
    """Schema validation failure must route to Gemini-2.5-Pro."""
    preflight = _passing_preflight()
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        schema_validation_failed=True,
    )
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.SCHEMA_VALIDATION_FAILED


# ---------------------------------------------------------------------------
# Test 9 — Gemini backstop: low confidence
# ---------------------------------------------------------------------------


def test_gemini_backstop_low_confidence() -> None:
    """Low confidence must route to Gemini-2.5-Pro."""
    preflight = _passing_preflight()
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        confidence_below_threshold=True,
    )
    assert decision.tier == "gemini_backstop"
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID
    assert decision.failure_type == VLLMFailureType.LOW_CONFIDENCE


# ---------------------------------------------------------------------------
# Test 10 — Failure escalation invariants: priority order
# ---------------------------------------------------------------------------


def test_failure_escalation_invariants_priority() -> None:
    """Token budget failure takes priority over circuit breaker."""
    huge_prompt = "x " * 50000
    preflight = run_preflight_budget_check(
        prompt=huge_prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    # Both token budget AND circuit breaker failures present
    decision = select_local_tier(
        preflight=preflight,
        severity="low",
        circuit_breaker_open=True,
    )
    # Token budget is checked first → TOKEN_BUDGET_EXCEEDED
    assert decision.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED
    assert decision.tier == "gemini_backstop"


# ---------------------------------------------------------------------------
# Test 11 — Gemini-2.5-Pro is never removed: model ID constant
# ---------------------------------------------------------------------------


def test_gemini_backstop_always_present() -> None:
    """GEMINI_25_PRO_MODEL_ID must be the Gemini-2.5-Pro model."""
    assert GEMINI_25_PRO_MODEL_ID == "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# Test 12 — No 32B model in routing module (AST scan)
# ---------------------------------------------------------------------------


def test_no_32b_model_in_routing_module_ast() -> None:
    """AST scan: no 32B model identifier in vllm_token_budget_types.py."""
    source = _BUDGET_TYPES_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_BUDGET_TYPES_FILE))
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "32b" in node.value.lower() or "32B" in node.value:
                violations.append(f"line {node.lineno}: {node.value!r}")
    assert not violations, "32B model found in routing module:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 13 — No quantized tier in routing module (AST scan)
# ---------------------------------------------------------------------------


def test_no_quantized_tier_in_routing_module_ast() -> None:
    """AST scan: no quantized model markers in vllm_token_budget_types.py."""
    source = _BUDGET_TYPES_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_BUDGET_TYPES_FILE))
    quantized_markers = {"awq", "gptq", "gguf", "int4", "int8", "quantized"}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val_lower = node.value.lower()
            for marker in quantized_markers:
                if marker in val_lower:
                    violations.append(f"line {node.lineno}: {node.value!r} contains {marker!r}")
    assert not violations, "Quantized tier found in routing module:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 14 — No GPU library imports in routing module (AST scan)
# ---------------------------------------------------------------------------


def test_no_gpu_imports_in_routing_module_ast() -> None:
    """AST scan: no torch/vllm/transformers imports in vllm_token_budget_types.py."""
    source = _BUDGET_TYPES_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_BUDGET_TYPES_FILE))
    forbidden_modules = {"torch", "vllm", "transformers", "cuda", "cupy"}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in forbidden_modules:
                        violations.append(f"line {node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in forbidden_modules:
                    violations.append(f"line {node.lineno}: from {node.module} import ...")
    assert not violations, "GPU library imports found in routing module:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 15 — TieredRoutingDecision is frozen (immutable)
# ---------------------------------------------------------------------------


def test_tiered_routing_decision_frozen() -> None:
    """TieredRoutingDecision must be immutable (frozen dataclass)."""
    import dataclasses

    preflight = _passing_preflight()
    decision = select_local_tier(preflight=preflight, severity="low")
    with pytest.raises(dataclasses.FrozenInstanceError):
        decision.tier = "gemini_backstop"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Test 16 — Routing is deterministic across identical inputs
# ---------------------------------------------------------------------------


def test_routing_deterministic_across_runs() -> None:
    """Identical inputs must produce identical routing decisions."""
    preflight = _passing_preflight()
    decisions = [select_local_tier(preflight=preflight, severity="high") for _ in range(5)]
    first = decisions[0]
    for d in decisions[1:]:
        assert d.tier == first.tier
        assert d.model_id == first.model_id
        assert d.reason == first.reason
        assert d.failure_type == first.failure_type


# ---------------------------------------------------------------------------
# Test 17 — Local tier only invoked when token_budget_ok == True
# ---------------------------------------------------------------------------


def test_local_tier_only_when_budget_ok() -> None:
    """Local 7B/14B must only be selected when token_budget_ok is True."""
    preflight = _passing_preflight()
    assert preflight.token_budget_ok is True
    decision = select_local_tier(preflight=preflight, severity="low")
    assert decision.tier in ("local_fast", "local_strong")

    # Failing preflight must never select local tier
    huge_prompt = "x " * 50000
    failing_preflight = run_preflight_budget_check(
        prompt=huge_prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert failing_preflight.token_budget_ok is False
    failing_decision = select_local_tier(preflight=failing_preflight, severity="low")
    assert failing_decision.tier == "gemini_backstop"
    assert failing_decision.model_id == GEMINI_25_PRO_MODEL_ID
