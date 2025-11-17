# views.py
"""
L4 — View Extractors (v10_9)

Provides selective projections of L4 state for use by L1/L2/L3.
"""

from __future__ import annotations

from typing import Dict, Any
import copy


def get_conversation_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": state.get("summary", ""),
    }


def get_retrieval_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }


def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "messages": copy.deepcopy(state.get("messages") or []),
        "summary": state.get("summary", ""),
        "rag_history": copy.deepcopy(state.get("rag_history") or []),
        "world": copy.deepcopy(state.get("world") or []),
    }
