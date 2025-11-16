"""Layer-4 state adapter responsible for applying typed patches."""

from __future__ import annotations

import copy
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, Mapping, MutableMapping

from pydantic import BaseModel, ConfigDict

from core_v10_7 import (
    A2AMessage,
    EphemeralState,
    EpisodicMemory,
    MainGraphState,
    MemoryState,
    SemanticMemoryRef,
)


class StatePatch(BaseModel):
    resume: dict | None = None
    strategy: dict | None = None
    rag: dict | None = None
    bullets: dict | None = None
    drafting: dict | None = None
    qa: dict | None = None
    artifacts: dict | None = None
    safety_report: dict | None = None
    policy_decision: dict | None = None
    constitutional_review: dict | None = None
    memory: MemoryState | None = None
    ephemeral: EphemeralState | None = None
    extra: dict | None = None

    model_config = ConfigDict(extra="allow")


class StateAdapterStack:
    """L4 Memory & State: the ONLY component allowed to mutate workflow state."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    def apply_patch(
        self, state_dict: Dict[str, Any], patch: Dict[str, Any] | StatePatch
    ) -> Dict[str, Any]:
        """Apply a schema-validated patch to the workflow state."""

        if not isinstance(state_dict, MutableMapping):
            state_dict = {}

        patch_obj: StatePatch
        if isinstance(patch, StatePatch):
            patch_obj = patch
        elif isinstance(patch, Mapping):
            patch_obj = StatePatch(**patch)
        else:
            return copy.deepcopy(state_dict)

        typed_state = MainGraphState.from_dict(copy.deepcopy(state_dict))
        merged_dict = typed_state.to_dict()

        for key in patch_obj.model_fields:
            if key == "extra":
                continue
            value = getattr(patch_obj, key)
            if value is None:
                continue
            if hasattr(value, "model_dump") and callable(value.model_dump):
                merged_dict[key] = self._normalize_patch(value.model_dump())
            elif isinstance(value, Mapping):
                existing = merged_dict.get(key, {})
                merged_dict[key] = self._deep_merge(
                    dict(existing) if isinstance(existing, Mapping) else {},
                    self._normalize_patch(value),
                )
            else:
                merged_dict[key] = copy.deepcopy(value)

        extra = getattr(patch_obj, "model_extra", None) or getattr(
            patch_obj, "__pydantic_extra__", {}
        )
        if patch_obj.extra:
            extra = self._deep_merge(extra, self._normalize_patch(patch_obj.extra))
        if extra:
            merged_dict = self._deep_merge(merged_dict, self._normalize_patch(extra))

        validated_state = MainGraphState.from_dict(merged_dict)

        wrapper_cls = type(
            "StateWrapper",
            (dict,),
            {
                "__getattr__": lambda self, key: self.get(key),
            },
        )

        return wrapper_cls(validated_state.to_dict())

    def _normalize_patch(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {k: self._normalize_patch(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_patch(v) for v in value]
        if hasattr(value, "model_dump") and callable(value.model_dump):
            return self._normalize_patch(value.model_dump())
        if is_dataclass(value):
            return self._normalize_patch(asdict(value))
        return copy.deepcopy(value)

    def _deep_merge(self, base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        for key, patch_value in patch.items():
            if isinstance(patch_value, Mapping):
                existing = base.get(key)
                if not isinstance(existing, Mapping):
                    existing = {}
                base[key] = self._deep_merge(dict(existing), dict(patch_value))
            elif isinstance(patch_value, list):
                base[key] = copy.deepcopy(patch_value)
            else:
                base[key] = patch_value
        return base


def patch_memory(
    *,
    conversation: Iterable[dict] | None = None,
    agent_notes: Iterable[str] | None = None,
    vector_store_ids: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
) -> StatePatch:
    """Build a memory-focused state patch with explicit replacements."""

    episodic = None
    semantic = None

    if conversation is not None or agent_notes is not None:
        episodic = EpisodicMemory(
            conversation=list(conversation or []),
            agent_notes=list(agent_notes or []),
        )
    if vector_store_ids is not None or tags is not None:
        semantic = SemanticMemoryRef(
            vector_store_ids=list(vector_store_ids or []),
            tags=list(tags or []),
        )

    if episodic is None and semantic is None:
        return StatePatch()

    memory = MemoryState()
    if episodic is not None:
        memory.episodic = episodic
    if semantic is not None:
        memory.semantic = semantic

    return StatePatch(memory=memory)


def patch_ephemeral_events(
    *,
    events: Iterable[Any] | None = None,
    debug_traces: Iterable[str] | None = None,
    last_node: str | None = None,
) -> StatePatch:
    """Build a patch targeting ephemeral execution metadata."""

    if events is None and debug_traces is None and last_node is None:
        return StatePatch()

    ephemeral = EphemeralState()
    if events is not None:
        ephemeral.events = list(events)
    if debug_traces is not None:
        ephemeral.debug_traces = list(debug_traces)
    if last_node is not None:
        ephemeral.last_node = last_node

    return StatePatch(ephemeral=ephemeral)


def build_a2a_message_patch(
    *,
    sender: str,
    message_type: str,
    payload: Dict[str, Any],
    recipient: str = "ALL",
    timestamp: str | None = None,
) -> StatePatch:
    """Construct a patch that appends a new A2A message."""

    message_kwargs = dict(
        sender=sender,
        recipient=recipient,
        message_type=message_type,
        payload=payload,
    )
    if timestamp is not None:
        message_kwargs["timestamp"] = timestamp

    message = A2AMessage(**message_kwargs)
    return StatePatch(**{"a2a": {"messages": [message.model_dump()]}})
