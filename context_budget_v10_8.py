"""Soft context budget enforcement for v10_8 with delegate support."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContextBudgetConfig:
    """Configuration for soft context budgeting."""

    max_episodic_messages: Optional[int] = 50
    max_rag_documents: Optional[int] = 20
    max_summary_chars: Optional[int] = 12000


class ContextBudgetManager:
    """Soft-mode budget manager that wraps a delegate if provided."""

    def __init__(self, config: Optional[ContextBudgetConfig] = None, delegate: Any = None):
        self.config = config or ContextBudgetConfig()
        self.delegate = delegate

    def enforce_all(self, state: Any) -> Any:
        """Apply delegate enforcement then soft trimming for memory, RAG, and summaries."""

        if not isinstance(state, Mapping):
            return state

        updated_state: Any = state
        if self.delegate is not None:
            delegate_enforce = getattr(self.delegate, "enforce_all", None)
            if callable(delegate_enforce):
                updated_state = delegate_enforce(updated_state)

        updated_state = self._trim_episodic_memory(updated_state)
        updated_state = self._trim_rag_history(updated_state)
        updated_state = self._trim_summary(updated_state)
        return updated_state

    def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        """Delegate pruning if available, otherwise return document unchanged."""

        delegate_prune = getattr(self.delegate, "prune", None)
        if callable(delegate_prune):
            return delegate_prune(document, max_tokens)
        return document

    def _trim_episodic_memory(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_messages = self.config.max_episodic_messages
        if not max_messages:
            return state
        try:
            memory = state.get("memory") or {}
            episodic = memory.get("episodic") or {}
            conversation = episodic.get("conversation")
            if isinstance(conversation, list) and len(conversation) > max_messages:
                trimmed = conversation[-max_messages:]
                logger.info(
                    "Trimming episodic memory from %s to %s entries", len(conversation), len(trimmed)
                )
                episodic = dict(episodic, conversation=trimmed)
                memory = dict(memory, episodic=episodic)
                new_state = dict(state)
                new_state["memory"] = memory
                return new_state
        except Exception as exc:  # pragma: no cover - soft mode resiliency
            logger.warning("Soft budget enforcement failed for episodic memory: %s", exc)
        return state

    def _trim_rag_history(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_docs = self.config.max_rag_documents
        if not max_docs:
            return state
        try:
            rag = state.get("rag") or {}
            documents = rag.get("documents")
            if isinstance(documents, list) and len(documents) > max_docs:
                trimmed_docs = documents[:max_docs]
                logger.info("Trimming RAG documents from %s to %s", len(documents), len(trimmed_docs))
                rag = dict(rag, documents=trimmed_docs)
                new_state = dict(state)
                new_state["rag"] = rag
                return new_state
        except Exception as exc:  # pragma: no cover
            logger.warning("Soft budget enforcement failed for RAG history: %s", exc)
        return state

    def _trim_summary(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        max_chars = self.config.max_summary_chars
        if not max_chars:
            return state
        try:
            summary = state.get("summary")
            if isinstance(summary, str) and len(summary) > max_chars:
                logger.info("Trimming summary from %s to %s characters", len(summary), max_chars)
                new_state = dict(state)
                new_state["summary"] = summary[:max_chars]
                return new_state
            prompts = state.get("prompts") or {}
            prompt_summary = prompts.get("summary")
            if isinstance(prompt_summary, str) and len(prompt_summary) > max_chars:
                logger.info(
                    "Trimming prompt summary from %s to %s characters", len(prompt_summary), max_chars
                )
                prompts = dict(prompts, summary=prompt_summary[:max_chars])
                new_state = dict(state)
                new_state["prompts"] = prompts
                return new_state
        except Exception as exc:  # pragma: no cover
            logger.warning("Soft budget enforcement failed for summary: %s", exc)
        return state


ContextBudgetManagerV10_8 = ContextBudgetManager
ContextBudgetConfigV10_8 = ContextBudgetConfig
