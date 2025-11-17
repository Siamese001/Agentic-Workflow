"""State adapter stack for v10_8 enforcing typed patches and budget controls."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from context_budget_v10_8 import ContextBudgetConfigV10_8, ContextBudgetManagerV10_8
from core_v10_7 import WorkflowPhase

logger = logging.getLogger(__name__)


class SemanticMemoryRef(BaseModel):
    """Reference to semantic memory artifacts."""

    vector_store_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class EpisodicMemory(BaseModel):
    """Conversation-level episodic memory."""

    conversation: List[Any] = Field(default_factory=list)
    agent_notes: List[str] = Field(default_factory=list)


class MemoryState(BaseModel):
    """Unified memory container."""

    episodic: EpisodicMemory = Field(default_factory=EpisodicMemory)
    semantic: SemanticMemoryRef = Field(default_factory=SemanticMemoryRef)


class EphemeralState(BaseModel):
    """Ephemeral runtime state that should not persist across runs."""

    events: List[Dict[str, Any]] = Field(default_factory=list)
    debug_traces: List[str] = Field(default_factory=list)
    last_node: Optional[str] = None


class A2AMessage(BaseModel):
    """Agent-to-agent message payload."""

    sender: str
    message_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    recipient: Optional[str] = None
    timestamp: Optional[str] = None


class A2AContext(BaseModel):
    """Collection of agent-to-agent messages."""

    messages: List[A2AMessage] = Field(default_factory=list)


class MainGraphState(BaseModel):
    """Canonical orchestration state for the workflow graph."""

    resume: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    strategy: Optional[Dict[str, Any]] = None
    prompts: Dict[str, Any] = Field(default_factory=dict)
    bullets: List[Any] = Field(default_factory=list)
    draft: Optional[Dict[str, Any]] = None
    qa: Optional[Dict[str, Any]] = None
    safety_report: Optional[Dict[str, Any]] = None
    policy_decision: Optional[Dict[str, Any]] = None
    constitutional_review: Optional[Dict[str, Any]] = None
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    safety: Dict[str, Any] = Field(default_factory=dict)
    feedback: Dict[str, Any] = Field(default_factory=dict)
    hil: Dict[str, Any] = Field(default_factory=dict)
    a2a: A2AContext = Field(default_factory=A2AContext)
    memory: Optional[MemoryState] = None
    ephemeral: Optional[EphemeralState] = None
    phase: WorkflowPhase = WorkflowPhase.EXECUTION
    rag: Optional[Dict[str, Any]] = None
    drafting: Optional[Dict[str, Any]] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "MainGraphState":
        """Construct state from an arbitrary mapping with defaults."""

        data = data or {}
        a2a_ctx = data.get("a2a") or {}
        messages = a2a_ctx.get("messages") if isinstance(a2a_ctx, dict) else None
        if isinstance(messages, list):
            a2a_ctx = A2AContext(messages=[A2AMessage(**msg) if isinstance(msg, dict) else msg for msg in messages])
        elif isinstance(a2a_ctx, A2AContext):
            a2a_ctx = a2a_ctx
        else:
            a2a_ctx = A2AContext()

        memory = data.get("memory")
        if isinstance(memory, dict):
            memory = MemoryState(**memory)
        elif not isinstance(memory, MemoryState):
            memory = None

        ephemeral = data.get("ephemeral")
        if isinstance(ephemeral, dict):
            ephemeral = EphemeralState(**ephemeral)
        elif not isinstance(ephemeral, EphemeralState):
            ephemeral = None

        return cls(
            resume=data.get("resume"),
            job=data.get("job"),
            strategy=data.get("strategy"),
            prompts=data.get("prompts") or {},
            bullets=data.get("bullets") or [],
            draft=data.get("draft"),
            qa=data.get("qa"),
            safety_report=data.get("safety_report"),
            policy_decision=data.get("policy_decision"),
            constitutional_review=data.get("constitutional_review"),
            artifacts=data.get("artifacts") or {},
            metadata=data.get("metadata") or {},
            safety=data.get("safety") or {},
            feedback=data.get("feedback") or {},
            hil=data.get("hil") or {},
            a2a=a2a_ctx,
            memory=memory,
            ephemeral=ephemeral,
            phase=data.get("phase") or WorkflowPhase.EXECUTION,
            rag=data.get("rag"),
            drafting=data.get("drafting"),
            extra=data.get("extra") or {},
            **{k: v for k, v in data.items() if k not in {
                "resume",
                "job",
                "strategy",
                "prompts",
                "bullets",
                "draft",
                "qa",
                "safety_report",
                "policy_decision",
                "constitutional_review",
                "artifacts",
                "metadata",
                "safety",
                "feedback",
                "hil",
                "a2a",
                "memory",
                "ephemeral",
                "phase",
                "rag",
                "drafting",
                "extra",
            }},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Render the state into a serializable mapping."""

        return self.model_dump()


class StatePatch(BaseModel):
    """Typed patch definition for state mutations."""

    resume: Optional[Dict[str, Any]] = None
    strategy: Optional[Dict[str, Any]] = None
    rag: Optional[Dict[str, Any]] = None
    bullets: Optional[List[Any]] = None
    drafting: Optional[Dict[str, Any]] = None
    qa: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    safety_report: Optional[Dict[str, Any]] = None
    policy_decision: Optional[Dict[str, Any]] = None
    constitutional_review: Optional[Dict[str, Any]] = None
    memory: Optional[MemoryState] = None
    ephemeral: Optional[EphemeralState] = None
    a2a: Optional[A2AContext] = None
    extra: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class StateAdapterStack:
    """Purely schema-driven state adapter with budget enforcement."""

    def __init__(self, context: Any, debug_mode: bool = False):
        self.context = context
        self.debug_mode = debug_mode

    def apply_patch(self, state_dict: Dict[str, Any], patch: Dict[str, Any] | StatePatch) -> Dict[str, Any]:
        """Apply a typed patch to a state dict with budget enforcement."""

        base_state = MainGraphState.from_dict(state_dict)
        normalized_patch = self._normalize_patch(patch)
        merged_state = self._merge_state(base_state, normalized_patch)
        final_state = self._enforce_budget(merged_state.to_dict())
        return final_state

    def _merge_state(self, base_state: MainGraphState, patch: StatePatch) -> MainGraphState:
        base_dict = base_state.to_dict()
        patch_dict = patch.model_dump(exclude_none=True)

        # Special handling for a2a messages to append rather than replace
        if "a2a" in patch_dict:
            a2a_patch = patch_dict.pop("a2a") or {}
            messages = a2a_patch.get("messages") if isinstance(a2a_patch, dict) else None
            base_messages = []
            if isinstance(base_dict.get("a2a"), dict):
                base_messages = list(base_dict.get("a2a", {}).get("messages") or [])
            if isinstance(messages, list):
                base_messages.extend(messages)
            if base_messages:
                patch_dict["a2a"] = {"messages": base_messages}

        merged = self._deep_merge(base_dict, patch_dict)
        validated = MainGraphState.from_dict(merged)
        return validated

    def _deep_merge(self, base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(base)
        for key, value in patch.items():
            if value is None:
                continue
            if key in {"memory", "ephemeral"}:
                result[key] = value.model_dump() if hasattr(value, "model_dump") else value
                continue
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                result[key] = self._deep_merge(base.get(key, {}), value)
            elif isinstance(value, list):
                result[key] = value
            else:
                result[key] = value
        return result

    def _normalize_patch(self, value: Any) -> StatePatch:
        if isinstance(value, StatePatch):
            return value
        if isinstance(value, dict):
            normalized = {}
            if "memory" in value and isinstance(value["memory"], dict):
                normalized["memory"] = MemoryState(**value["memory"])
            if "ephemeral" in value and isinstance(value["ephemeral"], dict):
                normalized["ephemeral"] = EphemeralState(**value["ephemeral"])
            if "a2a" in value and isinstance(value["a2a"], dict):
                messages = value["a2a"].get("messages") if isinstance(value["a2a"], dict) else None
                if isinstance(messages, list):
                    normalized["a2a"] = A2AContext(
                        messages=[A2AMessage(**msg) if isinstance(msg, dict) else msg for msg in messages]
                    )
            normalized.update({k: v for k, v in value.items() if k not in {"memory", "ephemeral", "a2a"}})
            return StatePatch(**normalized)
        raise TypeError("Patch must be a mapping or StatePatch instance")

    def _enforce_budget(self, state: Dict[str, Any]) -> Dict[str, Any]:
        manager = getattr(self.context, "context_budget_manager", None)
        try:
            if manager is None:
                return state
            enforced = manager.enforce_all(state)
            if isinstance(enforced, dict):
                return enforced
            return state
        except Exception as exc:  # pragma: no cover - soft mode
            logger.warning("Context budget enforcement failed: %s", exc)
            return state


def patch_memory(
    conversation: Optional[List[Any]] = None,
    agent_notes: Optional[List[str]] = None,
    vector_store_ids: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> StatePatch:
    """Build a patch targeting the memory bucket."""

    episodic = EpisodicMemory(
        conversation=conversation or [],
        agent_notes=agent_notes or [],
    )
    semantic = SemanticMemoryRef(
        vector_store_ids=vector_store_ids or [],
        tags=tags or [],
    )
    memory_state = MemoryState(episodic=episodic, semantic=semantic)
    return StatePatch(memory=memory_state)


def patch_ephemeral_events(
    events: Optional[List[Dict[str, Any]]] = None,
    debug_traces: Optional[List[str]] = None,
    last_node: Optional[str] = None,
) -> StatePatch:
    """Build a patch for ephemeral runtime data."""

    ephemeral_state = EphemeralState(
        events=events or [],
        debug_traces=debug_traces or [],
        last_node=last_node,
    )
    return StatePatch(ephemeral=ephemeral_state)


def build_a2a_message_patch(
    sender: str,
    message_type: str,
    payload: Dict[str, Any],
    recipient: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> StatePatch:
    """Construct a patch that appends an agent-to-agent message."""

    final_timestamp = timestamp or datetime.utcnow().isoformat()
    message = A2AMessage(
        sender=sender,
        message_type=message_type,
        payload=payload,
        recipient=recipient,
        timestamp=final_timestamp,
    )
    return StatePatch(a2a=A2AContext(messages=[message]))


__all__ = [
    "StatePatch",
    "StateAdapterStack",
    "patch_memory",
    "patch_ephemeral_events",
    "build_a2a_message_patch",
    "MainGraphState",
    "MemoryState",
    "EpisodicMemory",
    "SemanticMemoryRef",
    "EphemeralState",
    "A2AMessage",
    "A2AContext",
    "WorkflowPhase",
    "ContextBudgetConfigV10_8",
    "ContextBudgetManagerV10_8",
]
