"""
L2 safety contracts — W1 additive types for the L2 best-practices gap plan
(`.windsurf/plans/l2-execute-best-practices-gap-b7c4e2.md`).

Introduces three orthogonal classification axes that every L2 tool invocation
should carry, and a composed ``SafetyProfile`` that attaches them to a
``ToolContract`` without mutating the existing frozen dataclass in
``execution_tool_contract.py``.

Axes:

* ``SideEffectClass``  — what the call touches (READ / WRITE / ACTION / MUTATE_STATE).
* ``Reversibility``    — can the effect be undone, and how easily.
* ``ConsequenceLevel`` — blast-radius band used by the E2 validate-before-execute
                         short-circuit (see ``enforcement/e2_validate_before_execute.py``).

All enums are string-valued for JSON-safe serialization in execution traces
and future Notion / replay writeback.

References:
- Google Vertex AI function calling best practices:
  "validate the function call with the user before executing it" for calls with
  significant consequences.
- codebridge.tech 2026 AI-agent guardrails: permission boundaries + state/recovery.
- Anthropic tool-use best practices: idempotent + parallel-safe markers.

Doctrinal anchor: v33 §4 phase E2 ("mutation type sanity") and §4.1.2 Work
Order Check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

__all__ = [
    "SideEffectClass",
    "Reversibility",
    "ConsequenceLevel",
    "SafetyProfile",
    "register_safety_profile",
    "get_safety_profile",
    "DEFAULT_SAFE_PROFILE",
]


class SideEffectClass(str, Enum):
    """What a tool invocation touches at runtime.

    Ordering matters from safest (READ) to most sensitive (MUTATE_STATE).
    """

    READ = "read"
    WRITE = "write"
    ACTION = "action"
    MUTATE_STATE = "mutate_state"


class Reversibility(str, Enum):
    """How easily a side-effect can be undone."""

    REVERSIBLE = "reversible"
    COMPENSABLE = "compensable"
    IRREVERSIBLE = "irreversible"


class ConsequenceLevel(str, Enum):
    """Blast-radius band used by the E2 validate-before-execute short-circuit."""

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def requires_confirmation(cls, level: "ConsequenceLevel") -> bool:
        """Return True if this level must route through [5] HITL before E3."""
        return level in (cls.HIGH, cls.CRITICAL)


@dataclass(frozen=True, slots=True)
class SafetyProfile:
    """Composed safety metadata for a tool.

    Attached via ``register_safety_profile(tool_name, profile)``. The existing
    ``ToolCapabilityDescriptor`` is not modified — profiles are looked up by
    ``tool_name`` at E2 validation time.
    """

    tool_name: str
    side_effect: SideEffectClass
    reversibility: Reversibility
    consequence: ConsequenceLevel
    parallel_safe: bool = False
    idempotent: bool = False
    thought_signature_required: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "side_effect": self.side_effect.value,
            "reversibility": self.reversibility.value,
            "consequence": self.consequence.value,
            "parallel_safe": self.parallel_safe,
            "idempotent": self.idempotent,
            "thought_signature_required": self.thought_signature_required,
            "notes": self.notes,
        }

    def requires_e2_confirmation(self) -> bool:
        """E2 validate-before-execute gate predicate."""
        return ConsequenceLevel.requires_confirmation(self.consequence) or (
            self.reversibility is Reversibility.IRREVERSIBLE
            and self.side_effect is not SideEffectClass.READ
        )


DEFAULT_SAFE_PROFILE = SafetyProfile(
    tool_name="__default_safe__",
    side_effect=SideEffectClass.READ,
    reversibility=Reversibility.REVERSIBLE,
    consequence=ConsequenceLevel.NEGLIGIBLE,
    parallel_safe=True,
    idempotent=True,
    thought_signature_required=False,
    notes="Default profile applied when a tool has no registered SafetyProfile.",
)


_profile_registry: dict[str, SafetyProfile] = {}


def register_safety_profile(profile: SafetyProfile) -> None:
    """Register a ``SafetyProfile`` for a tool. Overwrites any previous profile."""
    _profile_registry[profile.tool_name] = profile


def get_safety_profile(tool_name: str) -> SafetyProfile:
    """Return the registered profile or ``DEFAULT_SAFE_PROFILE`` if none.

    Default-safe lookup is intentional: tools that have not been classified yet
    are treated as READ/REVERSIBLE/NEGLIGIBLE so the gate stays permissive
    during rollout. Classification is tightened wave by wave.
    """
    return _profile_registry.get(tool_name, DEFAULT_SAFE_PROFILE)


def registered_profile_names() -> list[str]:
    return list(_profile_registry.keys())


def snapshot_registry() -> Mapping[str, SafetyProfile]:
    """Read-only snapshot used by tests and audit probes."""
    return dict(_profile_registry)
