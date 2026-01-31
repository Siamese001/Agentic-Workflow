"""Minimal MCP compatibility layer for local testing."""

from __future__ import annotations

import importlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict  # noqa: F401

logger = logging.getLogger("mcp")

_ROOT = Path(__file__).resolve().parent.parent
_TOOL_CACHE: dict[str, Any] = {}
_SCHEMA_CACHE: dict[str, Any] = {}
_AGENT_CACHE: dict[str, Any] = {}
_CONTEXT_STATE: dict[str, Any] = {}

_AGENT_SPECS: dict[str, tuple[str, str]] = {
    "SafetyGuardStack": ("stacks_v10_7", "PromptInjectionDetectorAgent"),
    "StrategyStack": ("stacks_v10_7", "ToTStrategistAgent"),
    "RAGStack": ("stacks_v10_7", "RAG_SearchAgent"),
    "DraftingStack": ("stacks_v10_7", "DraftingGuildCoordinator"),
    "QAStack": ("agent_orchestration_v10_7", "QAConductorAgent"),
    "HILStack": ("stacks_v10_7", "HILFeedbackRouterAgent"),
    "MetaLearningLoop": ("agent_orchestration_v10_7", "MetaLearningLoop"),
}


def _load_module(module_name: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:  # pragma: no cover - defensive fallback
        logger.warning("MCP tool module '%s' unavailable: %s", module_name, exc)
        return SimpleNamespace()


def get_tool(tool_id: str) -> Any:
    """Resolve a tool by id using lazy imports."""

    if tool_id not in _TOOL_CACHE:
        module_name = tool_id
        if tool_id == "chromadb":
            module_name = "chromadb"
        elif tool_id == "redis":
            module_name = "redis"
        elif tool_id == "openai":
            module_name = "openai"
        _TOOL_CACHE[tool_id] = _load_module(module_name)
    return _TOOL_CACHE[tool_id]


def get_agent(agent_id: str) -> Any:
    """Return an agent class registered for the manifest."""

    if agent_id in _AGENT_CACHE:
        return _AGENT_CACHE[agent_id]

    spec = _AGENT_SPECS.get(agent_id)
    if not spec:
        raise KeyError(f"Agent '{agent_id}' is not registered in MCP manifest")

    module_name, attr = spec
    module = _load_module(module_name)
    try:
        agent_cls = getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - misconfiguration guard
        raise KeyError(
            f"Module '{module_name}' does not expose '{attr}' for agent '{agent_id}'"
        ) from exc

    _AGENT_CACHE[agent_id] = agent_cls
    return agent_cls


def get_schema(schema_name: str) -> dict[str, Any]:
    """Load and cache schemas declared in the manifest."""

    if schema_name not in _SCHEMA_CACHE:
        schema_path = Path(schema_name)
        if not schema_path.is_absolute():
            schema_path = _ROOT / schema_path
        try:
            with open(schema_path, encoding="utf-8") as handle:
                _SCHEMA_CACHE[schema_name] = json.load(handle)
        except FileNotFoundError as exc:  # pragma: no cover - defensive fallback
            raise FileNotFoundError(f"Schema '{schema_name}' not found at {schema_path}") from exc
    return json.loads(json.dumps(_SCHEMA_CACHE[schema_name]))


def sync_context(context: Any, *, scope: str = "default") -> None:
    """Persist the latest workflow context for other MCP participants."""

    try:
        _CONTEXT_STATE[scope] = context
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.debug("Failed to sync context for scope '%s': %s", scope, exc)


def emit_event(payload: dict[str, Any]) -> None:
    """Broadcast telemetry events to the MCP runtime."""

    logger.info("[MCP] %s", json.dumps(payload, default=str))


def register_tool(tool_id: str, factory: Callable[[], Any]) -> None:
    """Allow tests to inject custom tools."""

    _TOOL_CACHE.pop(tool_id, None)
    _TOOL_CACHE[tool_id] = factory()


def reset_state() -> None:
    """Helper for tests to clear cached registries."""

    _TOOL_CACHE.clear()
    _SCHEMA_CACHE.clear()
    _AGENT_CACHE.clear()
    _CONTEXT_STATE.clear()
