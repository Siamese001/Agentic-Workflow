"""G-2-3 — Healer 10-Step Pipeline Order Enforcement Tests.

Negative tests: reorder, missing, extra, duplicate all raise PermissionError.
Positive test: exact match passes.
Structural tests: single enforcement function, all execution entry points call the gate.
Runtime wiring test: proves the gate is actually called during pipeline execution.
"""

from __future__ import annotations

import pathlib
import re
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.types.v15_types import HEALER_PIPE_ORDER
from agentic_core.L2_execution.enforcement.healer_pipe_order import (
    enforce_healer_pipe_order,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def canonical_steps() -> tuple[str, ...]:
    return HEALER_PIPE_ORDER


@pytest.fixture()
def correct_observed(canonical_steps: tuple[str, ...]) -> list[str]:
    return list(canonical_steps)


# =============================================================================
# NEGATIVE: Reorder violation
# =============================================================================


class TestReorderViolation:
    def test_swap_adjacent_steps_raises(self, canonical_steps, correct_observed):
        """Swap steps 2 and 3 (index 1,2) => PermissionError."""
        correct_observed[1], correct_observed[2] = correct_observed[2], correct_observed[1]
        with pytest.raises(PermissionError, match="HEALER_PIPE_ORDER_VIOLATION") as exc_info:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-reorder")
        msg = str(exc_info.value)
        assert "expected_step=" in msg
        assert "observed_step=" in msg
        assert "step_index=" in msg
        assert "trace_id=trace-reorder" in msg

    def test_swap_first_and_last_raises(self, canonical_steps, correct_observed):
        correct_observed[0], correct_observed[9] = correct_observed[9], correct_observed[0]
        with pytest.raises(PermissionError, match="WRONG_STEP"):
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-swap")

    def test_reverse_order_raises(self, canonical_steps, correct_observed):
        correct_observed.reverse()
        with pytest.raises(PermissionError, match="HEALER_PIPE_ORDER_VIOLATION"):
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-reverse")


# =============================================================================
# NEGATIVE: Missing step violation
# =============================================================================


class TestMissingStepViolation:
    def test_drop_last_step_raises(self, canonical_steps, correct_observed):
        correct_observed.pop()
        with pytest.raises(PermissionError, match="MISSING_STEP") as exc_info:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-missing")
        msg = str(exc_info.value)
        assert "expected_step=commit" in msg
        assert "step_index=9" in msg

    def test_drop_first_step_raises(self, canonical_steps, correct_observed):
        correct_observed.pop(0)
        with pytest.raises(PermissionError, match="HEALER_PIPE_ORDER_VIOLATION"):
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-drop-first")

    def test_drop_middle_step_raises(self, canonical_steps, correct_observed):
        correct_observed.pop(4)
        with pytest.raises(PermissionError, match="HEALER_PIPE_ORDER_VIOLATION"):
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-drop-mid")

    def test_empty_observed_raises(self, canonical_steps):
        with pytest.raises(PermissionError, match="MISSING_STEP"):
            enforce_healer_pipe_order(canonical_steps, [], "trace-empty")


# =============================================================================
# NEGATIVE: Extra step violation
# =============================================================================


class TestExtraStepViolation:
    def test_append_extra_step_raises(self, canonical_steps, correct_observed):
        correct_observed.append("rogue_step")
        with pytest.raises(PermissionError, match="EXTRA_STEP") as exc_info:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-extra")
        msg = str(exc_info.value)
        assert "observed_step=rogue_step" in msg
        assert "step_index=10" in msg

    def test_duplicate_step_raises(self, canonical_steps, correct_observed):
        correct_observed.append(correct_observed[0])
        with pytest.raises(PermissionError, match="EXTRA_STEP"):
            enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-dup")


# =============================================================================
# POSITIVE: Happy path
# =============================================================================


class TestHappyPath:
    def test_exact_match_passes(self, canonical_steps, correct_observed):
        enforce_healer_pipe_order(canonical_steps, correct_observed, "trace-ok")

    def test_exact_match_no_trace_passes(self, canonical_steps, correct_observed):
        enforce_healer_pipe_order(canonical_steps, correct_observed, None)

    def test_canonical_has_10_steps(self, canonical_steps):
        assert len(canonical_steps) == 10


# =============================================================================
# NEGATIVE: Assertion on expected_steps count
# =============================================================================


class TestExpectedStepsContract:
    def test_non_10_expected_raises_assertion(self):
        with pytest.raises(AssertionError, match="exactly 10"):
            enforce_healer_pipe_order(("a", "b"), ["a", "b"], "trace")

    def test_empty_expected_raises_assertion(self):
        with pytest.raises(AssertionError, match="exactly 10"):
            enforce_healer_pipe_order((), [], "trace")


# =============================================================================
# DETERMINISTIC ERROR MESSAGE
# =============================================================================


class TestDeterministicMessage:
    def test_wrong_step_message_fields(self, canonical_steps, correct_observed):
        correct_observed[3] = "INJECTED"
        try:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "t-det")
        except PermissionError as e:
            msg = str(e)
            assert f"expected_step={canonical_steps[3]}" in msg
            assert "observed_step=INJECTED" in msg
            assert "step_index=3" in msg
            assert "trace_id=t-det" in msg

    def test_missing_step_message_fields(self, canonical_steps, correct_observed):
        correct_observed.pop()
        try:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "t-miss")
        except PermissionError as e:
            msg = str(e)
            assert "expected_step=commit" in msg
            assert "observed_step=<absent>" in msg
            assert "step_index=9" in msg

    def test_extra_step_message_fields(self, canonical_steps, correct_observed):
        correct_observed.append("extra")
        try:
            enforce_healer_pipe_order(canonical_steps, correct_observed, "t-extra")
        except PermissionError as e:
            msg = str(e)
            assert "expected_step=<none>" in msg
            assert "observed_step=extra" in msg
            assert "step_index=10" in msg


# =============================================================================
# STRUCTURAL: Single enforcement function
# =============================================================================


class TestStructural:
    def test_single_enforce_definition(self):
        """Exactly one file in agentic_core defines enforce_healer_pipe_order."""
        pat = re.compile(r"def enforce_healer_pipe_order\b")
        hits = []
        for p in pathlib.Path("agentic_core").rglob("*.py"):
            content = p.read_text(encoding="utf-8", errors="ignore")
            if pat.search(content):
                hits.append(str(p))
        assert len(hits) == 1, f"Expected 1 definition, found {len(hits)}: {hits}"
        assert "healer_pipe_order" in hits[0]

    def test_gateway_calls_enforce(self):
        """v15_execution_gateway.py must call enforce_healer_pipe_order."""
        gw_path = pathlib.Path("agentic_core/L0_routing/enforcement/v15_execution_gateway.py")
        assert gw_path.exists(), f"Gateway not found: {gw_path}"
        content = gw_path.read_text(encoding="utf-8", errors="ignore")
        assert "enforce_healer_pipe_order" in content, (
            "v15_execution_gateway.py does not call enforce_healer_pipe_order"
        )
        assert "import" in content and "enforce_healer_pipe_order" in content


# =============================================================================
# RUNTIME WIRING: prove gate is actually called during pipeline execution
# =============================================================================


class TestRuntimeWiring:
    def test_gate_called_if_wiring_intact(self):
        """Prove enforce_healer_pipe_order is called during gateway execution.

        Mocks all pipeline dependencies so _execute_inner completes to the
        enforce call. A spy on enforce records the invocation.
        """
        import hashlib
        from unittest.mock import MagicMock

        from agentic_core.L0_routing.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        # Build a valid SurgicalManifest
        ast_snippet = "print('hello')"
        manifest_hash = hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest()
        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id="corr-1",
            node_id="node-1",
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="canonical",
            fix_constraint=FixConstraint.STRICT,
            manifest_hash=manifest_hash,
            change_history=("init",),
            provenance_chain=("source",),
        )

        call_log: list[dict] = []

        def spy_enforce(expected_steps, observed_steps, trace_id=None):
            call_log.append(
                {
                    "expected": expected_steps,
                    "observed": list(observed_steps),
                    "trace_id": trace_id,
                }
            )

        gw_mod = "agentic_core.L0_routing.enforcement.v15_execution_gateway"
        with (
            patch(f"{gw_mod}.enforce_healer_pipe_order", side_effect=spy_enforce),
            patch(f"{gw_mod}.validate_execution_input", return_value=manifest),
            patch(f"{gw_mod}.validate_manifest_emission"),
            patch(f"{gw_mod}.dedupe_sha256", return_value="fake-hash"),
            patch(f"{gw_mod}.create_boundary_snapshot", return_value=MagicMock(trace_id="snap")),
            patch(f"{gw_mod}.GuardrailGuard") as mock_guardrail_cls,
        ):
            mock_guardrail_cls.return_value.enforce_all.return_value = True

            from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
                V15ExecutionGateway,
            )

            gw = V15ExecutionGateway()

            def fake_heal(m):
                return {"errors": 0, "status": "ok"}

            def fake_state_hash():
                return ("fs-hash", "git-hash", "mem-hash")

            try:
                gw.execute(manifest, heal_fn=fake_heal, state_hash_fn=fake_state_hash, trace_id="wiring-test")
            except Exception:
                pass

        assert len(call_log) >= 1, (
            "enforce_healer_pipe_order was NOT called during gateway execution — gate wiring is broken"
        )
        assert call_log[0]["trace_id"] == "wiring-test"
        assert call_log[0]["observed"] == list(HEALER_PIPE_ORDER)

    def test_gate_removal_causes_test_failure(self):
        """Prove that if we replace enforce with a no-op, the structural test
        still catches it (the function must exist in the source)."""
        gw_path = pathlib.Path("agentic_core/L0_routing/enforcement/v15_execution_gateway.py")
        content = gw_path.read_text(encoding="utf-8", errors="ignore")
        assert "enforce_healer_pipe_order(HEALER_PIPE_ORDER, observed_steps" in content, (
            "The enforce_healer_pipe_order call site was removed from the gateway"
        )
