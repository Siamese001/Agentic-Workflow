"""
L3 generic workflow stage handler registry.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W2
Purpose: Unblock ManagedWorkflowEngine construction without hardcoding any
app-domain-specific stage names or section names in core.

Design rules (non-negotiable, enforced by tests):
  - STAGE_HANDLERS is an empty dict — no default handlers pre-registered.
  - WorkflowStageHandlerRegistry is the canonical registration surface;
    STAGE_HANDLERS is the empty sentinel consumed by ManagedWorkflowEngine
    at construction so the import no longer raises ImportError.
  - resolve() fails closed: MissingWorkflowStageHandlerError on unknown stage.
  - register() fails closed: DuplicateWorkflowStageHandlerError on re-register.
  - Handlers sourced from quarantined modules are rejected at register() time
    via a quarantine-source check.
  - Handlers MUST NOT make provider/model/tool calls.
  - Handlers MUST NOT write to L4 state.
  - Handlers MUST NOT emit X3 dispositions.
  - There is NO fallback to single-step on missing handler.

W2 invariant: ManagedWorkflowEngine constructs (STAGE_HANDLERS import succeeds)
but workflow execution remains BLOCKED until explicit domain handlers are
registered via WorkflowStageHandlerRegistry.register().  That wiring happens
in W4 (apps_rg_l3_binding.py).
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Quarantine source prefixes — any handler whose __module__ starts with one
# of these strings is rejected at registration time.
# ---------------------------------------------------------------------------
_QUARANTINE_MODULE_PREFIXES: Tuple[str, ...] = (
    "apps_rg.integrations.hops",
    "apps_rg.integrations.gates",
    "apps_rg.prompt_assembly.rg_pa_compiler",
    "apps_rg.prompt_assembly.contracts",
    "apps_rg._quarantine",
)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class WorkflowStageHandlerResolutionError(Exception):
    """Base for all handler-registry resolution failures."""


class MissingWorkflowStageHandlerError(WorkflowStageHandlerResolutionError):
    """Raised when resolve() is called for a stage with no registered handler.

    Fail-closed invariant: there is no fallback to single-step execution.
    """

    def __init__(self, stage_type: str) -> None:
        self.stage_type = stage_type
        super().__init__(
            f"No workflow stage handler registered for stage_type={stage_type!r}. "
            "Register a domain handler via WorkflowStageHandlerRegistry.register() "
            "before dispatching this stage. "
            "INVARIANT: missing handler does NOT fall back to single-step execution."
        )


class DuplicateWorkflowStageHandlerError(WorkflowStageHandlerResolutionError):
    """Raised when register() is called for an already-registered stage_type."""

    def __init__(self, stage_type: str) -> None:
        self.stage_type = stage_type
        super().__init__(
            f"Duplicate workflow stage handler registration for stage_type={stage_type!r}. "
            "Each stage_type may only be registered once per registry instance."
        )


class QuarantinedWorkflowHandlerError(WorkflowStageHandlerResolutionError):
    """Raised when register() is called with a handler sourced from a quarantined module.

    Quarantined prefixes: apps_rg.integrations.hops, apps_rg.integrations.gates,
    apps_rg.prompt_assembly.rg_pa_compiler, apps_rg.prompt_assembly.contracts,
    apps_rg._quarantine.
    """

    def __init__(self, stage_type: str, handler_module: str) -> None:
        self.stage_type = stage_type
        self.handler_module = handler_module
        super().__init__(
            f"Handler for stage_type={stage_type!r} is sourced from quarantined module "
            f"{handler_module!r}. "
            "DO_NOT_IMPORT_FROM_CORE_RUNTIME — quarantined legacy apps_rg runtime modules "
            "must not be registered as active core workflow handlers."
        )


# ---------------------------------------------------------------------------
# Handler type alias
# ---------------------------------------------------------------------------

# A WorkflowStageHandler accepts a step_packet (any Mapping — intentionally
# generic so core does not depend on domain-specific contract types in W2)
# and returns a step_result Mapping.
#
# W2 constraints on all registered handlers:
#   - Must NOT call provider/model/tool APIs.
#   - Must NOT write to L4 state.
#   - Must NOT emit X3 dispositions.
# These are enforced by tests, not by this type alias.
WorkflowStageHandler = Callable[[Mapping[str, Any]], Mapping[str, Any]]


# ---------------------------------------------------------------------------
# WorkflowStageHandlerRef — lightweight reference (for logging / receipts)
# ---------------------------------------------------------------------------

class WorkflowStageHandlerRef:
    """Lightweight descriptor for a registered handler — used in receipts."""

    __slots__ = ("stage_type", "handler_name", "handler_module")

    def __init__(self, stage_type: str, handler: WorkflowStageHandler) -> None:
        self.stage_type = stage_type
        self.handler_name: str = getattr(handler, "__name__", repr(handler))
        self.handler_module: str = getattr(handler, "__module__", "")

    def as_dict(self) -> Dict[str, str]:
        return {
            "stage_type": self.stage_type,
            "handler_name": self.handler_name,
            "handler_module": self.handler_module,
        }


# ---------------------------------------------------------------------------
# WorkflowStageHandlerRegistry
# ---------------------------------------------------------------------------

class WorkflowStageHandlerRegistry:
    """Generic, fail-closed registry for L3 workflow stage handlers.

    Usage::

        registry = WorkflowStageHandlerRegistry()
        registry.register("content_generation", my_handler)
        handler = registry.resolve("content_generation")
        result = handler(step_packet)

    Invariants:
      - resolve() raises MissingWorkflowStageHandlerError if stage_type is
        not registered.  There is NO fallback.
      - register() raises DuplicateWorkflowStageHandlerError if stage_type
        is already registered.
      - register() raises QuarantinedWorkflowHandlerError if the handler's
        __module__ starts with a quarantined prefix.
      - stage_type is treated as a plain string — no dependency on the
        WorkflowStage enum so this registry is reusable by any domain.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, WorkflowStageHandler] = {}
        self._refs: Dict[str, WorkflowStageHandlerRef] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, stage_type: str, handler: WorkflowStageHandler) -> None:
        """Register *handler* for *stage_type*.

        Raises:
            DuplicateWorkflowStageHandlerError: stage_type already registered.
            QuarantinedWorkflowHandlerError: handler originates from a
                quarantined module.
            TypeError: handler is not callable.
        """
        if not callable(handler):
            raise TypeError(
                f"Handler for stage_type={stage_type!r} must be callable; "
                f"got {type(handler).__name__}."
            )
        handler_module: str = getattr(handler, "__module__", "") or ""
        for prefix in _QUARANTINE_MODULE_PREFIXES:
            if handler_module.startswith(prefix):
                raise QuarantinedWorkflowHandlerError(stage_type, handler_module)

        if stage_type in self._handlers:
            raise DuplicateWorkflowStageHandlerError(stage_type)

        self._handlers[stage_type] = handler
        self._refs[stage_type] = WorkflowStageHandlerRef(stage_type, handler)
        _logger.debug(
            "WorkflowStageHandlerRegistry.register stage_type=%r handler=%r",
            stage_type,
            handler_module + "." + getattr(handler, "__name__", "?"),
        )

    def resolve(self, stage_type: str) -> WorkflowStageHandler:
        """Return the handler for *stage_type*.

        Raises:
            MissingWorkflowStageHandlerError: no handler registered for this
                stage_type.  Does NOT fall back to single-step.
        """
        handler = self._handlers.get(stage_type)
        if handler is None:
            raise MissingWorkflowStageHandlerError(stage_type)
        return handler

    def registered_stage_types(self) -> Tuple[str, ...]:
        """Return the tuple of currently-registered stage_type strings."""
        return tuple(self._handlers.keys())

    def refs(self) -> Tuple[WorkflowStageHandlerRef, ...]:
        """Return WorkflowStageHandlerRef descriptors for all registered handlers."""
        return tuple(self._refs.values())

    def __len__(self) -> int:
        return len(self._handlers)

    def __contains__(self, stage_type: object) -> bool:
        return stage_type in self._handlers


# ---------------------------------------------------------------------------
# Module-level STAGE_HANDLERS sentinel
#
# ManagedWorkflowEngine does:
#   from .workflow_stage_handlers import STAGE_HANDLERS
#   self._stage_handlers.update(STAGE_HANDLERS)
#
# STAGE_HANDLERS is intentionally empty so that:
#   (a) the import no longer raises ImportError (W2 blocker fixed), and
#   (b) no domain handlers are silently pre-wired (domain wiring is W4).
#
# ManagedWorkflowEngine._stage_handlers will therefore start empty; any
# attempt to dispatch a stage without prior domain-handler registration
# must raise MissingWorkflowStageHandlerError via WorkflowStageHandlerRegistry.
# ---------------------------------------------------------------------------

STAGE_HANDLERS: Dict[Any, Any] = {}


__all__ = [
    "STAGE_HANDLERS",
    "WorkflowStageHandler",
    "WorkflowStageHandlerRef",
    "WorkflowStageHandlerRegistry",
    "WorkflowStageHandlerResolutionError",
    "MissingWorkflowStageHandlerError",
    "DuplicateWorkflowStageHandlerError",
    "QuarantinedWorkflowHandlerError",
]
