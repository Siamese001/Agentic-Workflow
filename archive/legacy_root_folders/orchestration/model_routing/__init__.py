from __future__ import annotations

"""Facade for model routing functions used by orchestration layers.

This package re-exports the existing infra.model_routing primitives so
callers can depend on a stable ``orchestration.model_routing``
namespace without changing the underlying implementation.
"""

from infra.model_routing.models import RoutingContext, ModelChoice  # noqa: F401
from infra.model_routing.policies import (  # noqa: F401
    choose_provider_and_model,
    enforce_budget,
)
from infra.model_routing.selector import select_model  # noqa: F401

__all__ = [
    "RoutingContext",
    "ModelChoice",
    "choose_provider_and_model",
    "enforce_budget",
    "select_model",
]




