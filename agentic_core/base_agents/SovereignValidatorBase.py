"""SovereignValidatorBase — validator-only base class for E2 Work Order Check.

Per `docs/reference/04_L2_Execute/04_L2_Execute_v2.md` §E2: validators MUST NOT
perform repair. This base exposes validation surface only; calling `heal()` on a
`SovereignValidatorBase` subclass raises `ValidatorCannotHealError`.

This base is ADDITIVE. `SovereignBaseAgent` still works for legacy agents.
New agents that want clean E2/E4 separation subclass `SovereignValidatorBase`
for validators and `SovereignHealerBase` for healers (never both).

Layer authority: L_SHARED (base-class surface).
Plan: `.windsurf/plans/l2-execute-v2-agent-conformance-c8e4f1.md` Wave W1.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentic_core.mixins.validator_mixin import ValidatorMixin


class ValidatorCannotHealError(RuntimeError):
    """Raised when a SovereignValidatorBase subclass attempts to invoke heal logic.

    The L2 Execute v2 contract forbids validators from performing repair. Subclasses
    MUST route repairs to a sibling healer class (SovereignHealerBase).
    """


class SovereignValidatorBase(ValidatorMixin, ABC):
    """Base class for agents whose sole responsibility is the E2 Work Order Check.

    Subclasses MUST:
      * Implement `validate()` returning a `ValidationVerdict`-compatible mapping
      * NOT define any `heal*` method (enforced at runtime via `__init_subclass__`)
      * NOT mutate external state (pure-function validators)

    The E2 contract is: inspect a signed packet, stamp Approved-to-Start or emit
    a sealed rejection. No execution work, no state change.
    """

    __slots__ = ()

    # Forbidden heal method names — subclasses cannot override these.
    _FORBIDDEN_HEAL_METHODS: frozenset[str] = frozenset(
        {"heal", "heal_repository", "_heal", "_heal_repository", "repair", "_repair"}
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for name in cls._FORBIDDEN_HEAL_METHODS:
            if name in cls.__dict__:
                raise TypeError(
                    f"{cls.__name__} inherits from SovereignValidatorBase and "
                    f"cannot define '{name}()'. Move repair logic to a sibling "
                    f"SovereignHealerBase subclass per L2 Execute v2 §E2/§E4."
                )

    @abstractmethod
    def validate(self, packet: Any) -> dict[str, Any]:
        """Run the E2 Work Order Check and return a ValidationVerdict-shaped dict.

        Must return a mapping with at least the keys:
          * ``is_allowed`` (bool) — Approved-to-Start
          * ``reason`` (str) — human-readable verdict
          * ``evidence`` (dict) — structured evidence for sealing

        Must NOT mutate external state. Any detected fault MUST be returned as
        a FAIL verdict, not auto-repaired. Healing is the sibling healer's job.
        """

    def heal(self, *args: Any, **kwargs: Any) -> Any:
        """Explicitly forbidden on SovereignValidatorBase (per L2 Execute v2 §E2)."""
        raise ValidatorCannotHealError(
            f"{type(self).__name__} is a SovereignValidatorBase subclass and "
            f"cannot perform repair. Route the failed packet to the sibling "
            f"SovereignHealerBase subclass per L2 Execute v2 §E4."
        )
