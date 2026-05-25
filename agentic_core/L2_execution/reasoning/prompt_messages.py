"""PromptMessages IR — structured slot envelope for provider-aware adapters.

Per plan prompt-reception-followups-a7b3c4, phase RH2B.3.

Replaces flat ``(system_string, user_string)`` handoff between
``SlotAssemblyEngine`` and ``SovereignLLMGateway`` with a structured map of
slot-code -> rendered text. Provider adapters (Anthropic / OpenAI / Gemini)
can then project slots onto their native message shapes:

- Anthropic: system slot string + user turns (tool_use via content blocks)
- OpenAI:    role=system + role=user, E0 exemplars as prior user/assistant turns
- Gemini:    systemInstruction + contents[] with role alternation

This module is purely additive: every ``CompiledPromptArtifact`` produced by
``SlotAssemblyEngine`` today still carries ``final_system_string`` /
``final_user_string`` so gateway passthrough is preserved. ``PromptMessages``
is built on top of ``slots_used`` + per-slot content, not alongside it.

The IR contract:

- ``slot_map``: mapping slot_code (S0/I0/D0/C0/E0/M0/H0/U0) -> rendered text.
- ``ordered_slots``: canonical render order (typically the ``slots_used``
  list from the artifact).
- ``exemplars``: optional parsed E0 items as ``(role, text)`` tuples. Adapters
  that want multi-turn exemplar formatting read this instead of the raw E0
  blob.
- ``metadata``: free-form provenance (trace_id, system_version_hash,
  provider_hint).

``from_artifact`` is the single construction entry point so the IR always
derives from an already-signed artifact — callers cannot fabricate slots
independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.compiled_artifact import (
        AuthoritySlot,
        CompiledPromptArtifact,
    )
    from agentic_core.L2_execution.regen.same_authority_thread import (
        SameAuthorityThreadState,
    )


_SYSTEM_SLOT_CODES: tuple[str, ...] = ("S0", "I0", "D0", "C0", "E0", "M0", "H0")
_USER_SLOT_CODES: tuple[str, ...] = ("U0",)


@dataclass(frozen=True)
class PromptMessages:
    """Structured slot envelope consumed by provider-aware adapters.

    Attributes
    ----------
    slot_map : dict[str, str]
        Slot code -> rendered text.
    ordered_slots : tuple[str, ...]
        Canonical slot render order (from ``CompiledPromptArtifact.slots_used``).
    exemplars : tuple[tuple[str, str], ...]
        Optional multi-turn exemplar pairs parsed from E0, as
        ``((role, text), ...)``. Empty when E0 absent or not parseable.
    metadata : dict[str, Any]
        Provenance (``trace_id``, ``system_version_hash``, ``provider_hint``).
    """

    slot_map: dict[str, str] = field(default_factory=dict)
    ordered_slots: tuple[str, ...] = ()
    exemplars: tuple[tuple[str, str], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_artifact(
        cls,
        artifact: CompiledPromptArtifact,
        slots: dict[str, AuthoritySlot] | None = None,
        provider_hint: str | None = None,
    ) -> PromptMessages:
        """Build a ``PromptMessages`` from a signed artifact.

        Parameters
        ----------
        artifact
            Already-signed ``CompiledPromptArtifact``.
        slots
            Optional per-slot-code -> ``AuthoritySlot`` map. When provided,
            ``slot_map`` is keyed by slot code with that slot's ``content``.
            When ``None``, falls back to a two-entry map (``SYSTEM`` /
            ``USER``) sourced from the artifact's flat strings so the IR is
            always constructable even when slots are not retained.
        provider_hint
            Optional provider identifier (``anthropic`` / ``openai`` /
            ``gemini``). Adapters may use this to pick a rendering strategy.
        """
        slot_map: dict[str, str] = {}
        if slots:
            for code, slot in slots.items():
                slot_map[code.upper()] = slot.content
        else:
            # Preserve gateway passthrough: when no per-slot map available,
            # the IR still carries the flat strings under synthetic keys.
            if artifact.final_system_string:
                slot_map["SYSTEM"] = artifact.final_system_string
            if artifact.final_user_string:
                slot_map["USER"] = artifact.final_user_string

        ordered = tuple(code.upper() for code in getattr(artifact, "slots_used", ()) or ())

        exemplars: tuple[tuple[str, str], ...] = ()
        if slots and "E0" in {c.upper() for c in slots}:
            e0_slot = next(v for k, v in slots.items() if k.upper() == "E0")
            exemplars = _parse_exemplar_turns(e0_slot.content)

        metadata: dict[str, Any] = {
            "trace_id": artifact.trace_id,
            "system_version_hash": getattr(artifact, "system_version_hash", ""),
        }
        if provider_hint:
            metadata["provider_hint"] = provider_hint.lower()

        return cls(
            slot_map=slot_map,
            ordered_slots=ordered,
            exemplars=exemplars,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Projections (consumed by provider adapters)
    # ------------------------------------------------------------------

    def system_text(self, separator: str = "\n\n") -> str:
        """Concatenate system-authority slots in canonical order.

        Honors ``ordered_slots`` and includes only codes in
        ``_SYSTEM_SLOT_CODES``. Falls back to the synthetic ``SYSTEM`` key
        used when slots are not retained.
        """
        if "SYSTEM" in self.slot_map and not any(c in self.slot_map for c in _SYSTEM_SLOT_CODES):
            return self.slot_map["SYSTEM"]

        ordered = self.ordered_slots or tuple(self.slot_map)
        parts = [self.slot_map[c] for c in ordered if c in _SYSTEM_SLOT_CODES and c in self.slot_map]
        return separator.join(p for p in parts if p)

    def user_text(self) -> str:
        """Return the U0 user turn text, or the fallback ``USER`` key."""
        if "U0" in self.slot_map:
            return self.slot_map["U0"]
        return self.slot_map.get("USER", "")

    def to_flat(self) -> tuple[str, str]:
        """Compatibility projection: ``(system_string, user_string)``.

        Adapters that have not yet migrated to slot-aware rendering continue
        to call this and see the same flat shape they had pre-RH2B.3.
        """
        return self.system_text(), self.user_text()

    def as_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for logging / telemetry."""
        return {
            "slot_map": dict(self.slot_map),
            "ordered_slots": list(self.ordered_slots),
            "exemplars": [list(pair) for pair in self.exemplars],
            "metadata": dict(self.metadata),
        }

    def append_same_authority_turn(
        self,
        *,
        frozen_compile_ref: str,
        policy_hash: str,
        blueprint_hash: str,
        registry_digest_set: tuple[str, ...],
        replay_key: str,
        provider_lane: str,
        model_lane: str,
        anchor_assistant_content: str,
        delta_user_content: str,
        capability_token: str = "",
        sandbox_envelope: str = "",
        prompt_hash: str = "",
    ) -> "SameAuthorityThreadState":
        """Append REGEN_DELTA user turn under frozen prefix (ADR-085 W1).

        Delegates to :mod:`agentic_core.L2_execution.regen`.
        """
        from agentic_core.L2_execution.regen.prefix_digest import compute_system_prefix_hash
        from agentic_core.L2_execution.regen.same_authority_bundle import SameAuthorityBundle
        from agentic_core.L2_execution.regen.same_authority_thread import (
            SameAuthorityThreadState,
            append_same_authority_turn as _append,
        )

        system_hash = compute_system_prefix_hash(self.system_text())
        bundle = SameAuthorityBundle(
            frozen_compile_ref=frozen_compile_ref,
            system_prefix_hash=system_hash,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            registry_digest_set=registry_digest_set,
            replay_key=replay_key,
            provider_lane=provider_lane,
            model_lane=model_lane,
            capability_token=capability_token,
            sandbox_envelope=sandbox_envelope,
            prompt_hash=prompt_hash or frozen_compile_ref,
        )
        return _append(
            self,
            bundle=bundle,
            anchor_assistant_content=anchor_assistant_content,
            delta_user_content=delta_user_content,
        )


def _parse_exemplar_turns(e0_content: str) -> tuple[tuple[str, str], ...]:
    """Best-effort parse of E0 content into ``(role, text)`` tuples.

    Recognizes the conventional ``USER: ...\\nASSISTANT: ...`` pattern emitted
    by the exemplar bank. Returns an empty tuple for unparseable content so
    callers can treat it as "render E0 as a monolithic block."
    """
    if not e0_content or not isinstance(e0_content, str):
        return ()

    lines = e0_content.splitlines()
    turns: list[tuple[str, str]] = []
    current_role: str | None = None
    current_buf: list[str] = []

    def _flush() -> None:
        if current_role is not None and current_buf:
            turns.append((current_role, "\n".join(current_buf).strip()))

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("USER:"):
            _flush()
            current_role = "user"
            current_buf = [stripped[len("USER:") :].strip()]
        elif stripped.upper().startswith("ASSISTANT:"):
            _flush()
            current_role = "assistant"
            current_buf = [stripped[len("ASSISTANT:") :].strip()]
        else:
            current_buf.append(line)
    _flush()

    return tuple(turns)


__all__ = [
    "PromptMessages",
]
