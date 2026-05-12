"""C0.3 Adapter Registry — config-driven resolver for graph adapter refs.

Resolves a ``graph_adapter_ref`` (dotted-module path string carried in an app
route profile's ``graph_traverse`` block) to a live ``GraphTraversalAdapter``
instance, without any app_id branching in core.

W3 invariants (chroma-graphrag-core-wiring-gaps-b3f7a1):
  - No hardcoded app-id branches (``if app_id == "apps_*"`` forbidden).
  - No hardcoded registry dict mapping app names to adapter paths.
  - Resolution is purely dotted-path driven: the ``graph_adapter_ref`` value
    IS the dotted module path — ``apps_lic.integrations.c0_graph_adapter``.
  - Import is lazy (deferred until ``resolve_graph_adapter`` is called).
  - Import failures, missing refs, malformed refs, and invalid adapter shapes
    all fail closed with a structured ``AdapterResolutionResult``.
  - ``run_graph_traverse()`` is NEVER called here.
  - No C0.3 graph traversal is wired or executed in this module.
"""

from __future__ import annotations

import importlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


class AdapterResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    MISSING_REF = "MISSING_REF"
    INVALID_REF = "INVALID_REF"
    IMPORT_ERROR = "IMPORT_ERROR"
    INVALID_ADAPTER = "INVALID_ADAPTER"


@dataclass(frozen=True, slots=True)
class AdapterResolutionResult:
    """Structured result from ``resolve_graph_adapter()``.

    On success:  status=RESOLVED, adapter is a ``GraphTraversalAdapter``.
    On failure:  status is one of the error variants, adapter is None,
                 reason and error_type describe the failure.
    """

    status: AdapterResolutionStatus
    graph_adapter_ref: str
    adapter: Optional[Any] = None
    reason: str = ""
    error_type: str = ""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# A valid dotted path: non-empty segments of [a-zA-Z_][a-zA-Z0-9_]*, at least
# two segments (module.something), no leading/trailing dots.
_VALID_DOTTED_PATH_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$"
)

# Minimum interface that every resolved adapter must satisfy.
# Checked by attribute presence — no import of the abstract class here to
# avoid any circular dependency risk.
_REQUIRED_ADAPTER_METHODS = frozenset(
    {
        "resolve_anchor",
        "get_neighbors",
        "get_relation_path",
        "get_projection_manifest",
        "health_check",
    }
)


def _is_valid_ref(ref: str) -> bool:
    """Return True if ``ref`` is a well-formed dotted Python module path."""
    return bool(_VALID_DOTTED_PATH_RE.match(ref))


def _has_adapter_shape(obj: Any) -> bool:
    """Return True if ``obj`` exposes all required GraphTraversalAdapter methods."""
    return all(callable(getattr(obj, m, None)) for m in _REQUIRED_ADAPTER_METHODS)


# ---------------------------------------------------------------------------
# Core resolver
# ---------------------------------------------------------------------------


def resolve_graph_adapter(graph_adapter_ref: str) -> AdapterResolutionResult:
    """Resolve a ``graph_adapter_ref`` dotted-path string to a live adapter.

    The ref is the dotted module path carried verbatim in the app route
    profile's ``graph_traverse.graph_adapter_ref`` field.  Core does NOT
    maintain a hardcoded mapping of app names to adapter modules — the ref
    value IS the location.

    Resolution steps:
    1. Validate ref is non-empty → MISSING_REF on empty/None.
    2. Validate ref is a well-formed dotted path → INVALID_REF on malformed.
    3. Lazily import the module → IMPORT_ERROR on ImportError/ModuleNotFoundError.
    4. Call ``module.get_graph_adapter()`` if present; else try the module
       directly as an adapter instance.
    5. Validate the resolved object has the required GraphTraversalAdapter shape
       → INVALID_ADAPTER if any method is missing.
    6. Return RESOLVED with the adapter.

    No app_id branching. No hardcoded app-specific entries. No run_graph_traverse.

    Args:
        graph_adapter_ref: Dotted module path string, e.g.
            ``"apps_lic.integrations.c0_graph_adapter"``.

    Returns:
        ``AdapterResolutionResult`` with status RESOLVED on success or an
        error status on failure.
    """
    # --- Step 1: missing ref ---
    if not graph_adapter_ref or not graph_adapter_ref.strip():
        _LOGGER.debug("resolve_graph_adapter: empty ref → MISSING_REF")
        return AdapterResolutionResult(
            status=AdapterResolutionStatus.MISSING_REF,
            graph_adapter_ref=graph_adapter_ref or "",
            reason="graph_adapter_ref is empty or None",
            error_type="MISSING_REF",
        )

    ref = graph_adapter_ref.strip()

    # --- Step 2: malformed ref ---
    if not _is_valid_ref(ref):
        _LOGGER.debug("resolve_graph_adapter: malformed ref=%r → INVALID_REF", ref)
        return AdapterResolutionResult(
            status=AdapterResolutionStatus.INVALID_REF,
            graph_adapter_ref=ref,
            reason=f"graph_adapter_ref {ref!r} is not a valid dotted Python module path",
            error_type="INVALID_REF",
        )

    # --- Step 3: lazy import ---
    try:
        module = importlib.import_module(ref)
    except (ImportError, ModuleNotFoundError) as exc:
        _LOGGER.warning(
            "resolve_graph_adapter: import failed for ref=%r: %s",
            ref,
            exc,
        )
        return AdapterResolutionResult(
            status=AdapterResolutionStatus.IMPORT_ERROR,
            graph_adapter_ref=ref,
            reason=f"Failed to import module {ref!r}: {exc}",
            error_type=type(exc).__name__,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- import_module may raise any exception from broken module init code
        _LOGGER.error(
            "resolve_graph_adapter: unexpected error importing ref=%r: %s",
            ref,
            exc,
        )
        return AdapterResolutionResult(
            status=AdapterResolutionStatus.IMPORT_ERROR,
            graph_adapter_ref=ref,
            reason=f"Unexpected error importing module {ref!r}: {exc}",
            error_type=type(exc).__name__,
        )

    # --- Step 4: resolve adapter object ---
    # Preferred: module exposes get_graph_adapter() factory
    factory = getattr(module, "get_graph_adapter", None)
    if callable(factory):
        try:
            adapter = factory()
        except Exception as exc:  # guardian: allow-broad-exception -- adapter factory may raise any exception
            _LOGGER.error(
                "resolve_graph_adapter: get_graph_adapter() raised for ref=%r: %s",
                ref,
                exc,
            )
            return AdapterResolutionResult(
                status=AdapterResolutionStatus.IMPORT_ERROR,
                graph_adapter_ref=ref,
                reason=f"get_graph_adapter() raised for {ref!r}: {exc}",
                error_type=type(exc).__name__,
            )
    else:
        # Fallback: module itself might be the adapter (unusual but allowed)
        adapter = module

    # --- Step 5: validate shape ---
    if not _has_adapter_shape(adapter):
        missing = sorted(
            m for m in _REQUIRED_ADAPTER_METHODS if not callable(getattr(adapter, m, None))
        )
        _LOGGER.warning(
            "resolve_graph_adapter: adapter from ref=%r missing methods=%s → INVALID_ADAPTER",
            ref,
            missing,
        )
        return AdapterResolutionResult(
            status=AdapterResolutionStatus.INVALID_ADAPTER,
            graph_adapter_ref=ref,
            reason=f"Adapter from {ref!r} is missing required methods: {missing}",
            error_type="INVALID_ADAPTER",
        )

    # --- Step 6: success ---
    _LOGGER.debug("resolve_graph_adapter: RESOLVED ref=%r adapter=%r", ref, adapter)
    return AdapterResolutionResult(
        status=AdapterResolutionStatus.RESOLVED,
        graph_adapter_ref=ref,
        adapter=adapter,
    )


__all__ = [
    "AdapterResolutionStatus",
    "AdapterResolutionResult",
    "resolve_graph_adapter",
]
