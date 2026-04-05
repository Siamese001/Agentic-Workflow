"""Lightweight re-export of event_emission_mixin and SovereignEvent.

This module provides a dependency-light import path for event_emission_mixin
that avoids triggering the heavy runtime.types.__init__ (numpy cascade).
It loads sovereign_events_types.py directly via importlib.util.

SSOT: agentic_core/runtime/types/sovereign_events_types.py
"""

import importlib.util
from pathlib import Path

_SOURCE = Path(__file__).resolve().parent.parent / "runtime" / "types" / "sovereign_events_types.py"
_spec = importlib.util.spec_from_file_location("agentic_core.runtime.types.sovereign_events_types", _SOURCE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
event_emission_mixin = _mod.event_emission_mixin
SovereignEvent = _mod.SovereignEvent
__all__ = ["event_emission_mixin", "SovereignEvent"]
