"""
Seam contract tests — verifies all 11 L0 routing seam modules load cleanly
and expose their expected callable interfaces.

G16: Covers all seam files under agentic_core/L0_routing/seams/.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Seam registry: (module_stem, expected_callable_name, callable_type)
# callable_type: "function" or "class"
# ---------------------------------------------------------------------------
SEAM_REGISTRY = [
    ("observability_seam", "load_meta_learning_agent", "function"),
    ("elevator_shaft_seam", "load_context_jit", "function"),
    ("learning_seam", None, None),
    ("safety_enforcement_seam", None, None),
    ("canonical_truth_seam", None, None),
    ("layer_emission_seam", None, None),
    ("redis_decision_cache", None, None),
    ("safety_kernel_seam", None, None),
    ("safety_reasoning_seam", None, None),
    ("safety_validators_seam", None, None),
    ("vigilance_seam", None, None),
]

SEAM_MODULE_PREFIX = "agentic_core.L0_routing.seams."


@pytest.mark.parametrize("stem,_callable,_type", SEAM_REGISTRY)
def test_seam_imports_without_error(stem, _callable, _type):
    """Each seam module must be importable with no ImportError."""
    mod = importlib.import_module(SEAM_MODULE_PREFIX + stem)
    assert mod is not None


@pytest.mark.parametrize(
    "stem,callable_name,callable_type", [(s, c, t) for s, c, t in SEAM_REGISTRY if c is not None]
)
def test_seam_exports_expected_callable(stem, callable_name, callable_type):
    """Each seam with a declared callable must export it."""
    mod = importlib.import_module(SEAM_MODULE_PREFIX + stem)
    assert hasattr(mod, callable_name), f"Seam {stem} missing expected export '{callable_name}'"
    obj = getattr(mod, callable_name)
    if callable_type == "function":
        assert callable(obj), f"{callable_name} must be callable"


# ---------------------------------------------------------------------------
# observability_seam specific contracts
# ---------------------------------------------------------------------------


class TestObservabilitySeam:
    def test_load_meta_learning_agent_returns_class_or_none(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        result = load_meta_learning_agent()
        # Must be a class or None (fail-open)
        assert result is None or (inspect.isclass(result)), f"Expected class or None, got {type(result)}"

    def test_load_meta_learning_agent_returns_meta_learning_client(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        cls = load_meta_learning_agent()
        if cls is not None:
            assert cls.__name__ == "MetaLearningClient"

    def test_load_meta_learning_agent_no_exception_on_repeat_calls(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        r1 = load_meta_learning_agent()
        r2 = load_meta_learning_agent()
        assert r1 is r2 or (r1 is None and r2 is None)


# ---------------------------------------------------------------------------
# elevator_shaft_seam specific contracts
# ---------------------------------------------------------------------------


class TestElevatorShaftSeam:
    def test_load_context_jit_returns_dict(self):
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        result = load_context_jit("intent_001")
        assert isinstance(result, dict)

    def test_load_context_jit_returns_empty_dict(self):
        """Seam is a pure stub — always returns empty dict (no control flow allowed)."""
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        result = load_context_jit("any_intent")
        assert result == {}

    def test_load_context_jit_intent_id_accepted(self):
        """intent_id parameter is accepted without error."""
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        r1 = load_context_jit("intent_a")
        r2 = load_context_jit("intent_b")
        assert r1 == r2 == {}

    def test_load_context_jit_no_control_flow_in_seam(self):
        """Seam must have no If/Try/For/While (enforced by existing invariant test)."""
        import ast

        seam_file = "agentic_core/L0_routing/seams/elevator_shaft_seam.py"
        with open(seam_file, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        forbidden = (ast.If, ast.For, ast.While, ast.Try)
        found = [type(n).__name__ for n in ast.walk(tree) if isinstance(n, forbidden)]
        assert not found, f"Control flow found in seam: {found}"
