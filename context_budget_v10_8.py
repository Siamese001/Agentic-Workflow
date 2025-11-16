"""v10.8 soft-mode context budget enforcement."""

from __future__ import annotations

import copy
import logging
from typing import Any, MutableMapping, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ContextBudgetConfig(BaseModel):
    max_episodic_messages: int = 50
    max_rag_documents: int = 10
    max_summary_chars: int = 4000


class ContextBudgetManager:
    """Lightweight state-aware budget manager for L4.

    Soft mode intentionally avoids aggressive pruning to prevent regressions
    while the P4/P5 migration is in progress.
    """

    _TRIGGER_RATIO: float = 1.0

    def __init__(
        self,
        config: Optional[ContextBudgetConfig] = None,
        *,
        delegate: Any = None,
    ) -> None:
        self.config = config or ContextBudgetConfig()
        self.delegate = delegate
        self.logger = logging.getLogger(f"{__name__}.ContextBudgetManager")

    async def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        """Delegate text pruning to the legacy budget manager when available."""

        if self.delegate and hasattr(self.delegate, "prune"):
            return await self.delegate.prune(document, max_tokens)
        return document

    def enforce_all(self, state: Any) -> Any:
        """Apply conservative pruning across episodic memory, RAG history, and summary."""

        working_state = self._coerce_mapping(state)
        if working_state is None:
            return state

        self._trim_episodic_memory(working_state)
        self._trim_rag_history(working_state)
        self._trim_summary(working_state)

        return working_state

    def _trim_episodic_memory(self, state: MutableMapping[str, Any]) -> None:
        memory = self._ensure_mapping(state.get("memory"))
        episodic = self._ensure_mapping(memory.get("episodic")) if memory else None
        conversation = episodic.get("conversation") if episodic else None

        if not isinstance(conversation, list):
            return

        limit = self.config.max_episodic_messages
        if len(conversation) <= limit * self._TRIGGER_RATIO:
            return

        episodic["conversation"] = conversation[-limit:]
        memory["episodic"] = episodic
        state["memory"] = memory
        self.logger.info("Episodic memory pruned to %s messages", limit)

    def _trim_rag_history(self, state: MutableMapping[str, Any]) -> None:
        rag = self._ensure_mapping(state.get("rag"))
        history = rag.get("history") if rag else None

        if not isinstance(history, list):
            return

        limit = self.config.max_rag_documents
        if len(history) <= limit * self._TRIGGER_RATIO:
            return

        rag["history"] = history[-limit:]
        state["rag"] = rag
        self.logger.info("RAG history trimmed to %s documents", limit)

    def _trim_summary(self, state: MutableMapping[str, Any]) -> None:
        summary_parent = None
        summary_key = None
        summary_value: Optional[str] = None

        resume = self._ensure_mapping(state.get("resume"))
        if resume and isinstance(resume.get("summary"), str):
            summary_parent = resume
            summary_key = "summary"
            summary_value = resume.get("summary")
        elif isinstance(state.get("summary"), str):
            summary_parent = state
            summary_key = "summary"
            summary_value = state.get("summary")

        if not summary_parent or not summary_key or not isinstance(summary_value, str):
            return

        limit = self.config.max_summary_chars
        if len(summary_value) <= limit * self._TRIGGER_RATIO:
            return

        trimmed = f"{summary_value[:limit]}\n\n[... SUMMARY TRIMMED ...]"
        summary_parent[summary_key] = trimmed
        if resume is summary_parent:
            state["resume"] = resume
        self.logger.info("Summary truncated to %s characters", limit)

    def _coerce_mapping(self, state: Any) -> Optional[MutableMapping[str, Any]]:
        if isinstance(state, MutableMapping):
            return state
        if hasattr(state, "to_dict") and callable(state.to_dict):
            try:
                return copy.deepcopy(state.to_dict())
            except Exception:
                return None
        if hasattr(state, "model_dump") and callable(state.model_dump):
            try:
                return copy.deepcopy(state.model_dump())
            except Exception:
                return None
        return None

    def _ensure_mapping(self, value: Any) -> Optional[MutableMapping[str, Any]]:
        if isinstance(value, MutableMapping):
            return value
        if hasattr(value, "model_dump") and callable(value.model_dump):
            try:
                return value.model_dump()
            except Exception:
                return None
        return None

    def __getattr__(self, name: str) -> Any:  # pragma: no cover - defensive forwarding
        if self.delegate and hasattr(self.delegate, name):
            return getattr(self.delegate, name)
        raise AttributeError(name)


__all__ = ["ContextBudgetConfig", "ContextBudgetManager"]
