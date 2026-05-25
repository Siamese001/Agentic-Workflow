"""Same-authority multi-turn thread append under frozen compile prefix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agentic_core.L2_execution.regen.prefix_digest import (
    compute_delta_message_hash,
    compute_slot_prefix_digest,
    compute_system_prefix_hash,
)
from agentic_core.L2_execution.regen.same_authority_bundle import SameAuthorityBundle
from agentic_core.L2_execution.regen.same_authority_errors import (
    EmptyDeltaTurnError,
    FrozenPrefixMutationError,
    SameAuthorityBundleDriftError,
)

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages

_DEVELOPER_SLOT_CODES: frozenset[str] = frozenset({"D0", "DEVELOPER"})
_PREFIX_SLOT_CODES: frozenset[str] = frozenset(
    {"S0", "I0", "D0", "C0", "E0", "M0", "H0", "DEVELOPER", "SYSTEM"},
)
_INITIAL_USER_CODES: frozenset[str] = frozenset({"U0", "USER"})


@dataclass(frozen=True)
class ChatTurn:
    """One chat message for provider ``messages[]`` projection."""

    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class SameAuthorityThreadState:
    """Frozen prefix + anchor assistant + REGEN_DELTA user turn."""

    prefix_slot_snapshot: tuple[tuple[str, str], ...]
    prefix_slot_digest: str
    system_prefix_hash: str
    bundle: SameAuthorityBundle
    initial_user_turn: ChatTurn
    anchor_assistant_turn: ChatTurn
    regen_delta_user_turn: ChatTurn
    delta_message_hash: str

    def to_chat_messages(self) -> list[dict[str, str]]:
        """OpenAI-compatible ``messages[]`` for vLLM chat/completions."""
        out: list[dict[str, str]] = []
        system_parts: list[str] = []
        developer_parts: list[str] = []
        for code, text in self.prefix_slot_snapshot:
            if code in _DEVELOPER_SLOT_CODES:
                if text.strip():
                    developer_parts.append(text)
            elif code in _INITIAL_USER_CODES:
                continue
            elif text.strip():
                system_parts.append(text)
        if system_parts:
            out.append(
                ChatTurn(role="system", content="\n\n".join(system_parts)).as_dict(),
            )
        if developer_parts:
            out.append(
                ChatTurn(role="developer", content="\n\n".join(developer_parts)).as_dict(),
            )
        out.append(self.initial_user_turn.as_dict())
        out.append(self.anchor_assistant_turn.as_dict())
        out.append(self.regen_delta_user_turn.as_dict())
        return out


def _prefix_slot_snapshot(messages: PromptMessages) -> tuple[tuple[str, str], ...]:
    ordered = messages.ordered_slots or tuple(messages.slot_map)
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for code in ordered:
        upper = code.upper()
        if upper in seen:
            continue
        if upper in messages.slot_map and (
            upper in _PREFIX_SLOT_CODES or upper in _INITIAL_USER_CODES
        ):
            pairs.append((upper, messages.slot_map[upper]))
            seen.add(upper)
    for key in sorted(messages.slot_map):
        upper = key.upper()
        if upper not in seen and (
            upper in _PREFIX_SLOT_CODES or upper in _INITIAL_USER_CODES
        ):
            pairs.append((upper, messages.slot_map[upper]))
    return tuple(pairs)


def append_same_authority_turn(
    messages: PromptMessages,
    *,
    bundle: SameAuthorityBundle,
    anchor_assistant_content: str,
    delta_user_content: str,
) -> SameAuthorityThreadState:
    """Append anchor assistant + REGEN_DELTA user turn; prefix slots frozen."""
    delta = (delta_user_content or "").strip()
    if not delta:
        raise EmptyDeltaTurnError("delta_user_content must be non-empty")
    anchor = (anchor_assistant_content or "").strip()
    if not anchor:
        raise EmptyDeltaTurnError("anchor_assistant_content must be non-empty")

    snapshot = _prefix_slot_snapshot(messages)
    slot_digest = compute_slot_prefix_digest(dict(snapshot))
    system_hash = compute_system_prefix_hash(messages.system_text())
    if bundle.system_prefix_hash != system_hash:
        raise FrozenPrefixMutationError(
            "bundle.system_prefix_hash does not match current system prefix",
        )

    user_code = next(
        (c for c, _ in snapshot if c in _INITIAL_USER_CODES),
        "U0",
    )
    user_text = messages.user_text()
    initial_user = ChatTurn(role="user", content=user_text)

    delta_hash = compute_delta_message_hash(delta)
    regen_user = ChatTurn(role="user", content=delta)

    return SameAuthorityThreadState(
        prefix_slot_snapshot=snapshot,
        prefix_slot_digest=slot_digest,
        system_prefix_hash=system_hash,
        bundle=bundle,
        initial_user_turn=initial_user,
        anchor_assistant_turn=ChatTurn(role="assistant", content=anchor),
        regen_delta_user_turn=regen_user,
        delta_message_hash=delta_hash,
    )


def assert_prefix_unchanged(
    state: SameAuthorityThreadState,
    candidate: PromptMessages,
) -> None:
    """NC-1: candidate must not mutate frozen system/developer/user slot snapshot."""
    current = _prefix_slot_snapshot(candidate)
    if current != state.prefix_slot_snapshot:
        raise FrozenPrefixMutationError(
            "slot snapshot changed after same-authority freeze",
        )
    if compute_system_prefix_hash(candidate.system_text()) != state.system_prefix_hash:
        raise FrozenPrefixMutationError(
            "system prefix hash changed after same-authority freeze",
        )


def assert_bundle_unchanged(
    state: SameAuthorityThreadState,
    candidate: SameAuthorityBundle,
) -> None:
    """NC-2: authority bundle fields must not drift across regen."""
    frozen = state.bundle
    checks: list[tuple[str, Any, Any]] = [
        ("frozen_compile_ref", frozen.frozen_compile_ref, candidate.frozen_compile_ref),
        ("policy_hash", frozen.policy_hash, candidate.policy_hash),
        ("blueprint_hash", frozen.blueprint_hash, candidate.blueprint_hash),
        ("registry_digest_set", frozen.registry_digest_set, candidate.registry_digest_set),
        ("replay_key", frozen.replay_key, candidate.replay_key),
        ("provider_lane", frozen.provider_lane, candidate.provider_lane),
        ("model_lane", frozen.model_lane, candidate.model_lane),
        ("capability_token", frozen.capability_token, candidate.capability_token),
        ("sandbox_envelope", frozen.sandbox_envelope, candidate.sandbox_envelope),
        ("prompt_hash", frozen.prompt_hash, candidate.prompt_hash),
        ("system_prefix_hash", frozen.system_prefix_hash, candidate.system_prefix_hash),
    ]
    for field_name, expected, actual in checks:
        if expected != actual:
            raise SameAuthorityBundleDriftError(
                f"{field_name} drifted across same-authority regen",
            )
