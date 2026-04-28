from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

# Configuration constants

"""MCP Provider mappings and defaults.

Phase 1 - Pillar 3: Typed Contracts (Strict Schemas)
"""

from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.L0_routing.config.pipeline_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)


class ProviderType(Enum):
    """Supported MCP Provider types."""

    STUB = "stub"
    REDIS = "redis"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HTTP = "http"
    CUSTOM = "custom"


DEFAULT_PROVIDER_MODULES: dict[str, str] = {
    "stub": None,
    "redis": "redis",
    "chromadb": "chromadb",
    "qdrant": "qdrant_client",
    "openai": "openai",
    "anthropic": "anthropic",
    "google": "google.genai",
    "http": "httpx",
}


DEFAULT_PROVIDER_CLASSES: dict[str, str] = {
    "stub": "MCPClientStub",
    "redis": "Redis",
    "chromadb": "Client",
    "qdrant": "QdrantClient",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "GenerativeModel",
    "http": "Client",
}


def get_default_module(Provider: str) -> str | None:
    """Get default module name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Module name or None if stub
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_default_module", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_default_module", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_default_module")
    return DEFAULT_PROVIDER_MODULES.get(Provider.lower())


def get_default_class(Provider: str) -> str | None:
    """Get default class name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Class name or None
    """
    return DEFAULT_PROVIDER_CLASSES.get(Provider.lower())


def register_provider(
    Provider: str,
    module: str,
    class_name: str,
) -> None:
    """Register a custom Provider mapping.

    Args:
        Provider: Provider identifier
        module: Python module path
        class_name: Class name within module
    """
    DEFAULT_PROVIDER_MODULES[Provider.lower()] = module
    DEFAULT_PROVIDER_CLASSES[Provider.lower()] = class_name
