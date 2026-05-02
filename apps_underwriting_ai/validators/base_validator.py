"""Validator base contract for apps_underwriting_ai decision packets.

Skeleton-stage scope: deterministic, document-driven gate checks.
Jurisdictional-regulatory validators are deferred (plan scope boundary).

Every validator returns a :class:`ValidationResult`. Composites (e.g.
:class:`DecisionPacketValidator`) return a list of results, one per
sub-validator, preserving the order in which sub-validators ran.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """Single validator verdict.

    Attributes:
        validator: Short identifier for the validator that produced this.
        passed: ``True`` if the gate passes; ``False`` means a violation
            must be recorded in ``DecisionPacket.gate_violations``.
        severity: One of ``"info"``, ``"warning"``, ``"error"``. Only
            ``"error"`` forces the assembler to surface the violation.
        message: Human-readable rationale (never PII-bearing).
        context: Structured diagnostic payload (dict of scalars).
    """

    validator: str
    passed: bool
    severity: str = "error"
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.severity not in ("info", "warning", "error"):
            raise ValueError(
                f"severity must be info/warning/error, got {self.severity!r}"
            )


class BaseValidator:
    """Abstract base. Subclasses override :meth:`validate`.

    Subclasses set :attr:`name` (short identifier used in
    :attr:`ValidationResult.validator`). Concrete validators MUST be
    stateless at the instance level.
    """

    name: str = ""

    def validate(self, **kwargs: Any) -> ValidationResult:
        """Run the validator. Subclass-specific kwargs.

        Returns:
            A :class:`ValidationResult`.
        """
        raise NotImplementedError("subclass must override validate()")
