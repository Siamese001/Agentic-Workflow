"""SovereignHealerBase — healer-only base class for E4 Fixing Desk.

Per `docs/reference/04_L2_Execute/04_L2_Execute_v2.md` §E4: healers MUST operate
under the same `blueprint_hash`/`policy_hash` snapshot as the originating E2
validation, record `parent_packet_id` + `reason_code`, and increment
`repair_count` against an oscillation threshold.

This base is ADDITIVE. `SovereignBaseAgent` still works for legacy agents.
New agents that want clean E2/E4 separation subclass `SovereignValidatorBase`
for validators and `SovereignHealerBase` for healers (never both).

Layer authority: L_SHARED (base-class surface).
Plan: `.windsurf/plans/l2-execute-v2-agent-conformance-c8e4f1.md` Wave W1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentic_core.mixins.healing_mixin import HealingStrategyMixin


class HealerCannotValidateError(RuntimeError):
    """Raised when a SovereignHealerBase subclass attempts to invoke validation logic.

    The L2 Execute v2 contract forbids healers from performing E2 validation.
    Subclasses MUST route validation to a sibling SovereignValidatorBase class.
    """


class SnapshotBindingError(RuntimeError):
    """Raised when a heal attempt uses a different blueprint/policy snapshot than E2."""


class SovereignHealerBase(HealingStrategyMixin, ABC):
    """Base class for agents whose sole responsibility is the E4 Fixing Desk.

    Subclasses MUST:
      * Implement `heal(request)` returning a `HealResult` (W2)
      * NOT define any `validate*` method (enforced at runtime via `__init_subclass__`)
      * Re-assert `blueprint_hash` / `policy_hash` equality against the originating packet
      * Increment `repair_count` and respect the oscillation threshold

    The E4 contract is: localized repair under the same snapshot, no scope
    expansion, no direct durable commits (those happen in E5 seal + downstream L4).
    """

    __slots__ = ()

    # Max repair attempts per heal request; exceeding this MUST route to NEEDS_HELP.
    MAX_REPAIR_COUNT: int = 3

    _FORBIDDEN_VALIDATE_METHODS: frozenset[str] = frozenset(
        {"validate", "_validate", "validate_repository", "check", "_check"}
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for name in cls._FORBIDDEN_VALIDATE_METHODS:
            if name in cls.__dict__:
                raise TypeError(
                    f"{cls.__name__} inherits from SovereignHealerBase and "
                    f"cannot define '{name}()'. Move validation logic to a "
                    f"sibling SovereignValidatorBase subclass per "
                    f"L2 Execute v2 §E2/§E4."
                )

    @abstractmethod
    def heal(self, heal_request: Any) -> Any:
        """Perform the E4 Fixing Desk repair. MUST return a HealResult (W2 contract)."""

    @staticmethod
    def assert_snapshot_binding(
        heal_blueprint_hash: str,
        heal_policy_hash: str,
        parent_blueprint_hash: str,
        parent_policy_hash: str,
    ) -> None:
        """Enforce L2 Execute v2 §E4 invariant: heal MUST use originating snapshot.

        Raises :class:`SnapshotBindingError` on any mismatch.
        """
        if heal_blueprint_hash != parent_blueprint_hash:
            raise SnapshotBindingError(
                f"blueprint_hash mismatch: heal={heal_blueprint_hash!r} parent={parent_blueprint_hash!r}"
            )
        if heal_policy_hash != parent_policy_hash:
            raise SnapshotBindingError(
                f"policy_hash mismatch: heal={heal_policy_hash!r} parent={parent_policy_hash!r}"
            )

    def validate(self, *args: Any, **kwargs: Any) -> Any:
        """Explicitly forbidden on SovereignHealerBase (per L2 Execute v2 §E4)."""
        raise HealerCannotValidateError(
            f"{type(self).__name__} is a SovereignHealerBase subclass and "
            f"cannot perform validation. Route the packet to the sibling "
            f"SovereignValidatorBase subclass per L2 Execute v2 §E2."
        )
