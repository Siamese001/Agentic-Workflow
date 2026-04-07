"""G-16-16: Delta enforcement for System Learning config surface changes.

Pure functions for validating proposed config changes against constraints:
  - Bounds enforcement
  - Max delta per cycle enforcement
  - Type validation
  - Forbidden surface rejection

All functions are deterministic, side-effect free, and fail-closed.
"""

from __future__ import annotations

from system_learning.constraints.config_surfaces import (
    ALLOWED_SURFACES,
    FORBIDDEN_SURFACES,
    L0_ROUTING_CONSTRAINTS,
    L0_ROUTING_INT_CONSTRAINTS,
    L1_MODEL_POINTER_CONSTRAINTS,
    L5_POLICY_INT_CONSTRAINTS,
    RAG_CONSTRAINTS,
    FloatConstraint,
    IntConstraint,
    PointerConstraint,
)

# =============================================================================
# Exceptions
# =============================================================================


class ConstraintViolation(Exception):
    """Raised when a proposed config change violates constraints."""


class ForbiddenSurface(ConstraintViolation):
    """Raised when attempting to modify a forbidden surface."""


class UnknownSurface(ConstraintViolation):
    """Raised when attempting to modify an unknown/unallowlisted surface."""


class BoundsViolation(ConstraintViolation):
    """Raised when a value is outside allowed bounds."""


class DeltaViolation(ConstraintViolation):
    """Raised when a delta exceeds max_delta_per_cycle."""


class TypeViolation(ConstraintViolation):
    """Raised when a value has incorrect type."""


class PointerViolation(ConstraintViolation):
    """Raised when a pointer value is not in allowlist."""


# =============================================================================
# Constraint Lookup
# =============================================================================


def _get_constraint(
    surface_name: str,
) -> FloatConstraint | IntConstraint | PointerConstraint:
    """Get the constraint for a surface.

    Parameters
    ----------
    surface_name : str
        The config surface name.

    Returns
    -------
    FloatConstraint | IntConstraint | PointerConstraint
        The constraint for the surface.

    Raises
    ------
    ForbiddenSurface
        If surface is in FORBIDDEN_SURFACES.
    UnknownSurface
        If surface is not in ALLOWED_SURFACES.
    """
    if surface_name in FORBIDDEN_SURFACES:
        raise ForbiddenSurface(f"FORBIDDEN_SURFACE: {surface_name!r} is immutable and cannot be optimized")

    if surface_name not in ALLOWED_SURFACES:
        raise UnknownSurface(f"UNKNOWN_SURFACE: {surface_name!r} is not in allowlist")

    # Lookup constraint
    if surface_name in L0_ROUTING_CONSTRAINTS:
        return L0_ROUTING_CONSTRAINTS[surface_name]
    if surface_name in L0_ROUTING_INT_CONSTRAINTS:
        return L0_ROUTING_INT_CONSTRAINTS[surface_name]
    if surface_name in RAG_CONSTRAINTS:
        return RAG_CONSTRAINTS[surface_name]
    if surface_name in L1_MODEL_POINTER_CONSTRAINTS:
        return L1_MODEL_POINTER_CONSTRAINTS[surface_name]
    if surface_name in L5_POLICY_INT_CONSTRAINTS:
        return L5_POLICY_INT_CONSTRAINTS[surface_name]

    # Should never reach here if ALLOWED_SURFACES is correct
    raise UnknownSurface(f"CONSTRAINT_LOOKUP_FAILED: {surface_name!r} in allowlist but no constraint found")


# =============================================================================
# Validation Functions
# =============================================================================


def validate_surface_change(
    surface_name: str,
    old_value: float | int | str,
    new_value: float | int | str,
) -> None:
    """Validate a proposed config surface change.

    Enforces:
      - Surface is allowlisted (not forbidden, not unknown)
      - Type matches constraint type
      - Value is within bounds
      - Delta is within max_delta_per_cycle
      - Pointer values are in allowlist

    Parameters
    ----------
    surface_name : str
        The config surface name.
    old_value : float | int | str
        The current value.
    new_value : float | int | str
        The proposed new value.

    Raises
    ------
    ForbiddenSurface
        If surface is forbidden.
    UnknownSurface
        If surface is not allowlisted.
    TypeViolation
        If value type does not match constraint type.
    BoundsViolation
        If value is outside bounds.
    DeltaViolation
        If delta exceeds max_delta_per_cycle.
    PointerViolation
        If pointer value is not in allowlist.
    """
    constraint = _get_constraint(surface_name)

    # Float constraint validation
    if isinstance(constraint, FloatConstraint):
        if not isinstance(old_value, (float, int)):
            raise TypeViolation(
                f"TYPE_VIOLATION: {surface_name!r} old_value must be float, got {type(old_value).__name__}",
            )
        if not isinstance(new_value, (float, int)):
            raise TypeViolation(
                f"TYPE_VIOLATION: {surface_name!r} new_value must be float, got {type(new_value).__name__}",
            )

        old_float = float(old_value)
        new_float = float(new_value)

        # Bounds check
        if not (constraint.min_value <= new_float <= constraint.max_value):
            raise BoundsViolation(
                f"BOUNDS_VIOLATION: {surface_name!r} new_value {new_float} "
                f"outside bounds [{constraint.min_value}, {constraint.max_value}]",
            )

        # Delta check
        delta = abs(new_float - old_float)
        if delta > constraint.max_delta_per_cycle:
            raise DeltaViolation(
                f"DELTA_VIOLATION: {surface_name!r} delta {delta:.4f} "
                f"exceeds max_delta_per_cycle {constraint.max_delta_per_cycle}",
            )

    # Int constraint validation
    elif isinstance(constraint, IntConstraint):
        if not isinstance(old_value, int):
            raise TypeViolation(
                f"TYPE_VIOLATION: {surface_name!r} old_value must be int, got {type(old_value).__name__}",
            )
        if not isinstance(new_value, int):
            raise TypeViolation(
                f"TYPE_VIOLATION: {surface_name!r} new_value must be int, got {type(new_value).__name__}",
            )

        # Bounds check
        if not (constraint.min_value <= new_value <= constraint.max_value):
            raise BoundsViolation(
                f"BOUNDS_VIOLATION: {surface_name!r} new_value {new_value} "
                f"outside bounds [{constraint.min_value}, {constraint.max_value}]",
            )

        # Delta check
        delta = abs(new_value - old_value)
        if delta > constraint.max_delta_per_cycle:
            raise DeltaViolation(
                f"DELTA_VIOLATION: {surface_name!r} delta {delta} "
                f"exceeds max_delta_per_cycle {constraint.max_delta_per_cycle}",
            )

    # Pointer constraint validation
    elif isinstance(constraint, PointerConstraint):
        if not isinstance(new_value, str):
            raise TypeViolation(
                f"TYPE_VIOLATION: {surface_name!r} new_value must be str, got {type(new_value).__name__}",
            )

        # Allowlist check
        if new_value not in constraint.allowlist:
            raise PointerViolation(
                f"POINTER_VIOLATION: {surface_name!r} new_value {new_value!r} "
                f"not in allowlist {sorted(constraint.allowlist)}",
            )

    else:
        # Should never reach here
        raise ConstraintViolation(f"UNKNOWN_CONSTRAINT_TYPE: {type(constraint).__name__}")
