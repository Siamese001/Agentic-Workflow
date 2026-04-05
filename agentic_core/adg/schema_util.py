"""Shim: redirects agentic_core.adg.schema_util -> agentic_core.adg.contracts.schema_util."""
import sys as _sys
import types as _types

# Pre-register this module as a placeholder so any re-entrant import of
# agentic_core.adg.schema_util during the canonical load resolves immediately.
_placeholder = _types.ModuleType(__name__)
_sys.modules[__name__] = _placeholder

import importlib as _importlib  # noqa: E402
_canonical = _importlib.import_module("agentic_core.adg.contracts.schema_util")
_sys.modules[__name__] = _canonical
# Patch the placeholder's attributes so already-bound references still work
_placeholder.__dict__.update(_canonical.__dict__)
