"""
apps_rg.config - Configuration for Resume Generation app.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from apps_rg.config.agent_spec_config import RGAgentSpecs

_logger = logging.getLogger(__name__)
_SPEC_FILE = Path(__file__).parent / "rg_agent_specs.json"
_cached_specs: RGAgentSpecs | None = None


def load_rg_specs() -> RGAgentSpecs:
    """Load RG agent specs from rg_agent_specs.json (cached).

    Falls back to ``RGAgentSpecs()`` with field defaults if the file is missing
    or malformed. Imported by ``apps_rg.engines.base_rg_engine`` at engine
    instantiation; absent prior to 2026-04-28 (engines silently ran with
    ``self.rg_specs = None``).
    """
    global _cached_specs
    if _cached_specs is not None:
        return _cached_specs
    if _SPEC_FILE.is_file():
        try:
            data = json.loads(_SPEC_FILE.read_text(encoding="utf-8"))
            _cached_specs = RGAgentSpecs(**data)
            return _cached_specs
        except (json.JSONDecodeError, ValueError, TypeError) as exc:  # guardian: allow-log-and-fallback -- spec file malformed; defaults are safe
            _logger.warning("rg_agent_specs.json invalid (%s); using defaults", exc)
    _cached_specs = RGAgentSpecs()
    return _cached_specs


__all__ = ["RGAgentSpecs", "load_rg_specs"]
