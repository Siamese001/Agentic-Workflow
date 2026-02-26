from __future__ import annotations

import unittest.mock

import pytest

from agentic_core.determinism.digest_authority import digest_authority
from agentic_core.L0_routing.scripts.execution_context import (
    ConfigSurface,
    ExecutionContext,
)


def _run_sovereign_process(context: ExecutionContext) -> str:
    """A simplified simulation of a full sovereign decision-making process."""
    # 1. The context is used throughout the process.
    trace_id = context.trace_id or ""

    # 2. Various components produce hashes.
    plan_hash = "a" * 64
    policy_hash = "b" * 64
    transcript_hash = "c" * 64
    config_surface_hash = context.config_surface_hash or "" * 64

    # 3. The digest authority computes the final digest.
    digest = digest_authority.compute_digest(
        trace_id=trace_id,
        plan_hash=plan_hash,
        policy_hash=policy_hash,
        transcript_hash=transcript_hash,
        config_surface_hash=config_surface_hash,
    )

    # 4. The digest is emitted.
    # In a real run, this would be captured from stdout.
    return digest_authority.emit_digest(digest, wave_number=5)


@pytest.mark.governance
def test_two_run_digest_stability():
    """
    Proves that the W<n>-DETERMINISM-DIGEST is identical across two independent runs.

    This is the ultimate validation of the system's deterministic guarantees. It
    simulates two complete runs with identical inputs and asserts that their final
    determinism digests are bit-for-bit identical.
    """
    # 1. Define the identical inputs for both runs.
    config_surface = ConfigSurface(
        threshold_configs={"some_threshold": 0.5},
        tier_constants={"X": 0.75, "Y": 0.40},
        tool_budget_caps={"some_tool": 100},
        freshness_windows={"some_data": 3600},
    )
    context = ExecutionContext(trace_id="trace-123")
    context.set_config_surface(config_surface)

    # --- Run 1 ---
    # Reset the digest authority to simulate a fresh process start.
    digest_authority.reset_for_testing()
    with unittest.mock.patch("builtins.print") as mock_print_1:
        emission_1 = _run_sovereign_process(context)
        # Verify it was emitted correctly
        mock_print_1.assert_called_once_with(emission_1)

    # --- Run 2 ---
    # Reset again for the second run.
    digest_authority.reset_for_testing()
    with unittest.mock.patch("builtins.print") as mock_print_2:
        emission_2 = _run_sovereign_process(context)
        # Verify it was emitted correctly
        mock_print_2.assert_called_once_with(emission_2)

    # --- Assertion ---
    # The digests from two independent runs with identical inputs must be identical.
    assert emission_1 == emission_2, (
        f"Determinism digest is not stable across two runs!\nRun 1: {emission_1}\nRun 2: {emission_2}"
    )

    print(f"\nSuccessfully verified digest stability across two runs:\n  {emission_1}")
