"""
Tests for HealContext trace_id and execution_mode (E1 + E10).

Per .windsurfrules §1.1: Zero-tolerance testing - all changed logic tested.
Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
Per hostile audit Section E1: trace_id threads through all artifacts and HealContext.
Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate modes.
"""

import argparse
import re

import pytest


def test_heal_context_trace_id_format():
    """
    PASS: trace_id follows format SSOT-YYYYMMDD-HHMMSS-{8hex}.
    FAIL: trace_id has wrong format or missing components.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must be unique and traceable.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    # Verify trace_id format: SSOT-YYYYMMDD-HHMMSS-{8hex}
    pattern = r"^SSOT-\d{8}-\d{6}-[0-9a-f]{8}$"
    assert re.match(pattern, ctx.trace_id), f"trace_id format invalid: {ctx.trace_id}"

    # Verify trace_id components
    parts = ctx.trace_id.split("-")
    assert len(parts) == 4, f"trace_id should have 4 parts, got {len(parts)}"
    assert parts[0] == "SSOT", "trace_id should start with SSOT"
    assert len(parts[1]) == 8, "timestamp date should be 8 digits"
    assert len(parts[2]) == 6, "timestamp time should be 6 digits"
    assert len(parts[3]) == 8, "uuid fragment should be 8 hex chars"


def test_heal_context_trace_id_uniqueness():
    """
    PASS: Multiple HealContext instances generate different trace_ids.
    FAIL: trace_ids collide or are identical.

    Per .windsurfrules §1.7: Deterministic decision surfaces must not collapse.
    Per hostile audit Section E1: trace_id must be unique per run.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)

    # Generate multiple trace_ids
    trace_ids = set()
    for _ in range(10):
        ctx = HealContext.from_args(args)
        trace_ids.add(ctx.trace_id)

    # All trace_ids should be unique
    assert len(trace_ids) == 10, "trace_ids should be unique across instances"


def test_heal_context_execution_mode_scan():
    """
    PASS: execution_mode='scan' when heal=False and validate=False.
    FAIL: Wrong execution_mode for scan-only mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "scan", f"Expected 'scan', got '{ctx.execution_mode}'"
    assert ctx.heal is False
    assert ctx.auto_approve is False


def test_heal_context_execution_mode_heal():
    """
    PASS: execution_mode='heal' when heal=True.
    FAIL: Wrong execution_mode for heal mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "heal", f"Expected 'heal', got '{ctx.execution_mode}'"
    assert ctx.heal is True
    assert ctx.auto_approve is True


def test_heal_context_execution_mode_validate():
    """
    PASS: execution_mode='validate' when validate=True.
    FAIL: Wrong execution_mode for validate mode.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=True)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "validate", f"Expected 'validate', got '{ctx.execution_mode}'"


def test_heal_context_execution_mode_validate_overrides_heal():
    """
    PASS: execution_mode='validate' when both validate=True and heal=True.
    FAIL: validate doesn't take precedence over heal.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E10: validate mode has highest priority.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=True)
    ctx = HealContext.from_args(args)

    assert ctx.execution_mode == "validate", "validate should override heal"


def test_heal_context_immutability():
    """
    PASS: HealContext is frozen and cannot be mutated.
    FAIL: HealContext fields can be modified after creation.

    Per .windsurfrules §1.8: Fail-closed - invalid preconditions must block operation.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=False, validate=False)
    ctx = HealContext.from_args(args)

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        ctx.heal = True

    with pytest.raises(Exception):
        ctx.trace_id = "modified"

    with pytest.raises(Exception):
        ctx.execution_mode = "modified"


def test_heal_context_trace_id_correlation():
    """
    PASS: trace_id is consistent within a single HealContext instance.
    FAIL: trace_id changes or is unstable.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must be stable for correlation.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    # Access trace_id multiple times
    trace_id_1 = ctx.trace_id
    trace_id_2 = ctx.trace_id
    trace_id_3 = ctx.trace_id

    assert trace_id_1 == trace_id_2 == trace_id_3, "trace_id must be stable"


def test_heal_context_all_fields_present():
    """
    PASS: HealContext has all required fields (heal, auto_approve, telemetry, meta_learning, trace_id, execution_mode).
    FAIL: Missing required fields.

    Per .windsurfrules §1.5: Edge cases - missing field.
    Per hostile audit Section E1+E10: All fields must be present.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import HealContext

    args = argparse.Namespace(heal=True, validate=False)
    ctx = HealContext.from_args(args)

    # Verify all fields exist
    assert hasattr(ctx, "heal")
    assert hasattr(ctx, "auto_approve")
    assert hasattr(ctx, "enable_telemetry")
    assert hasattr(ctx, "enable_meta_learning")
    assert hasattr(ctx, "trace_id")
    assert hasattr(ctx, "execution_mode")

    # Verify types
    assert isinstance(ctx.heal, bool)
    assert isinstance(ctx.auto_approve, bool)
    assert isinstance(ctx.enable_telemetry, bool)
    assert isinstance(ctx.enable_meta_learning, bool)
    assert isinstance(ctx.trace_id, str)
    assert isinstance(ctx.execution_mode, str)

    # Verify trace_id is not empty
    assert len(ctx.trace_id) > 0, "trace_id must not be empty"

    # Verify execution_mode is valid
    assert ctx.execution_mode in ["scan", "heal", "validate"], f"Invalid execution_mode: {ctx.execution_mode}"
