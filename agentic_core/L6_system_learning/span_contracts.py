"""Compatibility shim — canonical implementation lives in ``runtime_adg.span_contracts``."""

from __future__ import annotations

__layer__ = "L6"

from agentic_core.L6_system_learning.runtime_adg.span_contracts import *  # noqa: F403  # guardian: allow-star-import -- runtime_adg compat re-export shim
