"""G-16-9: Constitutional authority invariants for System Learning.

System Learning has ZERO execution authority. It may only:
  - READ from L4 audit surfaces
  - WRITE immutable versioned artifacts to L4 versioned store
  - EMIT ChangePackage proposals through governance flow

FORBIDDEN at all times:
  - EXECUTE: invoking any work contract or agent
  - ACTIVATE: directly updating activation pointers
  - WRITE to audit surfaces (audit logs are append-only by L6)
  - Side-channel activation (bypassing governance flow)
"""

from __future__ import annotations

from dataclasses import dataclass


class AuthorityViolation(Exception):
    """Raised when System Learning attempts a forbidden operation.

    Fail-closed: any ambiguous operation raises this exception.
    """


_FORBIDDEN_MODES: frozenset[str] = frozenset({"EXECUTE", "ACTIVATE"})
_AUDIT_WRITE_OPERATIONS: frozenset[str] = frozenset(
    {"write_audit", "append_audit", "delete_audit", "mutate_audit", "overwrite_audit", "patch_audit"},
)
_SIDE_CHANNEL_OPERATIONS: frozenset[str] = frozenset(
    {
        "update_activation_pointer",
        "set_active_version",
        "activate_change_package",
        "flip_pointer",
        "swap_active",
        "direct_activate",
    },
)


@dataclass(frozen=True)
class AuthorityContext:
    """Describes a single operation attempted by System Learning.

    Fields
    ------
    caller_layer : str
        Identifier of the calling subsystem (e.g., "agentic_core.L6_system_learning.engines.rca").
    operation : str
        Canonical operation name (e.g., "read_audit_slice", "write_change_package").
    target : str
        Target resource or surface (e.g., "l4_audit", "l4_versioned_store").
    mode : str
        Access mode: one of "READ", "WRITE", "EXECUTE", "ACTIVATE".
    """

    caller_layer: str
    operation: str
    target: str
    mode: str


def assert_zero_execution_authority(ctx: AuthorityContext) -> None:
    """Fail-closed: raise AuthorityViolation if ctx.mode is EXECUTE or ACTIVATE.

    System Learning has zero execution authority. It cannot execute work
    contracts or directly activate change packages.

    Parameters
    ----------
    ctx : AuthorityContext
        The operation context to validate.

    Raises
    ------
    AuthorityViolation
        If ctx.mode is "EXECUTE" or "ACTIVATE".
    """
    if ctx.mode in _FORBIDDEN_MODES:
        raise AuthorityViolation(
            f"AUTHORITY_VIOLATION:ZERO_EXECUTION_AUTHORITY|caller={ctx.caller_layer}|operation={ctx.operation}|target={ctx.target}|mode={ctx.mode}|forbidden_modes={sorted(_FORBIDDEN_MODES)}",
        )


def assert_read_only_audit_access(ctx: AuthorityContext) -> None:
    """Fail-closed: raise AuthorityViolation for any write to audit surfaces.

    Audit logs are append-only and managed exclusively by L6 observability.
    System Learning may only READ from audit surfaces.

    Parameters
    ----------
    ctx : AuthorityContext
        The operation context to validate.

    Raises
    ------
    AuthorityViolation
        If ctx.mode is not "READ" when targeting audit surfaces, or if
        ctx.operation is a known audit-write operation.
    """
    if ctx.operation in _AUDIT_WRITE_OPERATIONS:
        raise AuthorityViolation(
            f"AUTHORITY_VIOLATION:AUDIT_WRITE_FORBIDDEN|caller={ctx.caller_layer}|operation={ctx.operation}|target={ctx.target}|mode={ctx.mode}",
        )
    if "audit" in ctx.target.lower() and ctx.mode != "READ":
        raise AuthorityViolation(
            f"AUTHORITY_VIOLATION:AUDIT_SURFACE_NON_READ|caller={ctx.caller_layer}|operation={ctx.operation}|target={ctx.target}|mode={ctx.mode}|required_mode=READ",
        )


def assert_no_side_channel_activation(ctx: AuthorityContext) -> None:
    """Fail-closed: raise AuthorityViolation for side-channel activation attempts.

    Activation of change packages MUST route through the governance flow
    (Proposal → Evaluation → Approval → Decision → L5 Validation → Pointer Update).
    Direct pointer updates or side-channel activations are forbidden.

    Parameters
    ----------
    ctx : AuthorityContext
        The operation context to validate.

    Raises
    ------
    AuthorityViolation
        If ctx.operation resembles a direct pointer update or activation.
    """
    if ctx.operation in _SIDE_CHANNEL_OPERATIONS:
        raise AuthorityViolation(
            f"AUTHORITY_VIOLATION:SIDE_CHANNEL_ACTIVATION_FORBIDDEN|caller={ctx.caller_layer}|operation={ctx.operation}|target={ctx.target}|mode={ctx.mode}|required_path=governance_flow",
        )
    if ctx.mode == "ACTIVATE":
        raise AuthorityViolation(
            f"AUTHORITY_VIOLATION:DIRECT_ACTIVATE_FORBIDDEN|caller={ctx.caller_layer}|operation={ctx.operation}|target={ctx.target}|mode={ctx.mode}",
        )
