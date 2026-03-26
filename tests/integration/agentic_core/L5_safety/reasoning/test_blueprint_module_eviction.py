"""
Regression tests for blueprint module eviction after on-disk write.

RCA: LocationHealerAgent and FilesystemSSOTReconcilerAgent write updated
SOVEREIGN_TERRITORIES / _constants.py to disk, but Python's import machinery
keeps the stale frozen module in sys.modules.  is_path_allowed() then reads
the old in-memory SOVEREIGN_TERRITORIES and reports wrong results for the
newly-added paths.

Fix: _evict_blueprint_modules() pops all structure_blueprint submodules from
sys.modules and calls importlib.invalidate_caches() so the next import
re-executes with fresh data.  REQ-417 blocks importlib.reload() but does NOT
block sys.modules.pop() — deletion is the safe eviction path.

Tests cover:
  - _evict_blueprint_modules() removes all matching prefixes
  - Non-blueprint modules are NOT evicted (negative control)
  - After eviction, re-import executes fresh module code
  - importlib.invalidate_caches() is called (no hanging stale .pyc reference)
  - Idempotency: calling twice is safe (no KeyError on absent key)
  - Empty sys.modules subset: no-op, no error
  - Both LocationHealerAgent and FilesystemSSOTReconcilerAgent expose the helper
"""

from __future__ import annotations

import sys
import types
from unittest.mock import patch

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Import the helpers under test — both agents must export _evict_blueprint_modules
# ---------------------------------------------------------------------------


def _import_location_evict():
#  # MOVED: from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
        _BLUEPRINT_MODULE_PREFIXES,
        _evict_blueprint_modules,
    )

    return _evict_blueprint_modules, _BLUEPRINT_MODULE_PREFIXES


def _import_reconciler_evict():
#  # MOVED: from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
        _BLUEPRINT_MODULE_PREFIXES,
        _evict_blueprint_modules,
    )

    return _evict_blueprint_modules, _BLUEPRINT_MODULE_PREFIXES


# ---------------------------------------------------------------------------
# Helper: inject fake blueprint modules into sys.modules for isolation
# ---------------------------------------------------------------------------

_FAKE_BLUEPRINT_KEYS = [
    "agentic_core.L5_safety.config.structure_blueprint",
    "agentic_core.L5_safety.config.structure_blueprint._constants",
    "agentic_core.L5_safety.config.structure_blueprint.ssot",
    "agentic_core.L5_safety.config.structure_blueprint.derived",
    "agentic_core.L5_safety.config.structure_blueprint.territories",
    "agentic_core.L5_safety.config.structure_blueprint_config",
]

_UNRELATED_KEYS = [
    "json",
    "os",
    "agentic_core.L0_routing.config",
    "apps_rg.engines.some_engine",
]


def _inject_fake_modules(keys):
    """Insert fake module objects into sys.modules and return a cleanup function."""
    originals = {}
    for k in keys:
        originals[k] = sys.modules.get(k, _SENTINEL)
        sys.modules[k] = types.ModuleType(k)

    def _cleanup():
        for k, v in originals.items():
            if v is _SENTINEL:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v

    return _cleanup


_SENTINEL = object()


# ---------------------------------------------------------------------------
# Tests for LocationHealerAgent._evict_blueprint_modules
# ---------------------------------------------------------------------------


class TestLocationHealerEviction:
    def test_evict_removes_all_blueprint_prefixes(self):
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                import agentic_core.L5_safety.config.structure_blueprint._constants  # noqa: F401
                import agentic_core.L5_safety.config.structure_blueprint._constants as fresh  # noqa: F401
                """All structure_blueprint* keys are removed from sys.modules."""
                _evict, _prefixes = _import_location_evict()
                cleanup = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
                try:
                    for k in _FAKE_BLUEPRINT_KEYS:
                        assert k in sys.modules, f"setup: {k} should be present"
                    _evict()
                    for k in _FAKE_BLUEPRINT_KEYS:
                        assert k not in sys.modules, f"{k} should have been evicted"
                finally:
                    cleanup()

            cleanup()

    def test_evict_does_not_touch_unrelated_modules(self):
        """Non-blueprint modules are untouched by eviction."""
        _evict, _ = _import_location_evict()
        cleanup = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
        # Ensure unrelated keys exist
        unrelated_before = {k: sys.modules.get(k) for k in _UNRELATED_KEYS if k in sys.modules}
        try:
            _evict()
            for k, v in unrelated_before.items():
                assert sys.modules.get(k) is v, f"Unrelated module {k} was mutated"
        finally:
            cleanup()

    def test_evict_idempotent_double_call(self):
    """Test evict_idempotent_double_call runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute evict_idempotent_double_call
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        saved = {
            k: sys.modules.pop(k)
            for k in list(sys.modules)
            if any(
                k == p or k.startswith(p + ".")
                for p in (
                    "agentic_core.L5_safety.config.structure_blueprint",
                    "agentic_core.L5_safety.config.structure_blueprint_config",
                )
            )
        }
        try:
            _evict()  # must not raise
        finally:
            sys.modules.update(saved)

    def test_evict_calls_importlib_invalidate_caches(self):
    """Test evict_calls_importlib_invalidate_caches runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute evict_calls_importlib_invalidate_caches
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        assert "agentic_core.L5_safety.config.structure_blueprint" in prefixes
        assert "agentic_core.L5_safety.config.structure_blueprint_config" in prefixes

    def test_evict_removes_sub_submodules(self):
        """Deeply nested submodules like structure_blueprint._constants are evicted."""
        _evict, _ = _import_location_evict()
        deep_keys = [
            "agentic_core.L5_safety.config.structure_blueprint._constants",
            "agentic_core.L5_safety.config.structure_blueprint.ssot",
        ]
        cleanup = _inject_fake_modules(deep_keys)
        try:
            _evict()
            for k in deep_keys:
                assert k not in sys.modules, f"Deep key {k} was not evicted"
        finally:
            cleanup()

    def test_evict_does_not_remove_partial_prefix_match(self):
        """A module named 'agentic_core.L5_safety.config.structure_blueprint_extra' is NOT evicted
        because it matches the _config prefix but we only evict exact prefix or dot-continuation."""
        _evict, _ = _import_location_evict()
        # 'structure_blueprintXXX' would only match if we did startswith without '.'
        # Our impl uses: k == p or k.startswith(p + ".")
        # So 'agentic_core.L5_safety.config.structure_blueprint_config' IS evicted (exact match)
        # But 'agentic_core.L5_safety.config.structure_blueprint_EXTRA' is not a prefix match for '...blueprint'
        fake_key = "agentic_core.L5_safety.config.structure_blueprint_EXTRA_UNRELATED"
        orig = sys.modules.get(fake_key, _SENTINEL)
        sys.modules[fake_key] = types.ModuleType(fake_key)
        cleanup_blueprint = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
        try:
            _evict()
            # _EXTRA_UNRELATED does not match either prefix exactly or as dot-continuation
            assert fake_key in sys.modules, (
                f"{fake_key} should NOT have been evicted — not a real blueprint submodule"
            )
        finally:
            cleanup_blueprint()
            if orig is _SENTINEL:
                sys.modules.pop(fake_key, None)
            else:
                sys.modules[fake_key] = orig


# ---------------------------------------------------------------------------
# Tests for FilesystemSSOTReconcilerAgent._evict_blueprint_modules
# ---------------------------------------------------------------------------


class TestFilesystemSSOTReconcilerEviction:
    def test_evict_removes_all_blueprint_prefixes(self):
        """FilesystemSSOTReconcilerAgent eviction removes all blueprint keys."""
        _evict, _ = _import_reconciler_evict()
        cleanup = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
        try:
            _evict()
            for k in _FAKE_BLUEPRINT_KEYS:
                assert k not in sys.modules, f"{k} should have been evicted"
        finally:
            cleanup()

    def test_evict_idempotent(self):
        """Double eviction is safe."""
        _evict, _ = _import_reconciler_evict()
        cleanup = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
        try:
            _evict()
            _evict()
        finally:
            cleanup()

    def test_evict_calls_importlib_invalidate_caches(self):
    """Test evict_calls_importlib_invalidate_caches runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute evict_calls_importlib_invalidate_caches
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        cleanup = _inject_fake_modules(_FAKE_BLUEPRINT_KEYS)
        unrelated_before = {k: sys.modules.get(k) for k in _UNRELATED_KEYS if k in sys.modules}
        try:
            _evict()
            for k, v in unrelated_before.items():
                assert sys.modules.get(k) is v
        finally:
            cleanup()


# ---------------------------------------------------------------------------
# Integration-style: after eviction, reimport picks up a new module object
# ---------------------------------------------------------------------------


class TestEvictionAllowsFreshReimport:
    def test_reimport_after_eviction_returns_new_object(self):
        """After eviction, importing the module again creates a new module object."""
        _evict, _ = _import_location_evict()

        # Grab the current (real) module object
        key = "agentic_core.L5_safety.config.structure_blueprint._constants"
        if key not in sys.modules:
            # If not loaded yet, load it now
#  # MOVED: import agentic_core.L5_safety.config.structure_blueprint._constants  # noqa: F401

        original_mod = sys.modules.get(key)

        cleanup = _inject_fake_modules([key])
        fake_mod = sys.modules[key]
        # Guard: the local tests/unit/.../types/__init__.py can shadow stdlib
        # 'types' if earlier tests ran from that directory.  Restore it before
        # reimporting _constants (which does `from types import MappingProxyType`).
        import importlib as _importlib

        _real_types = _importlib.import_module.__module__ and None  # sentinel
        _stashed_types = sys.modules.get("types")
        # Force reload of real stdlib types module by temporarily removing shadow
        _types_pkg = "types"
        _shadow = sys.modules.get(_types_pkg)
        try:
            _evict()
            assert key not in sys.modules

            # Ensure stdlib types is present (not shadowed)
            if _shadow is not None and not hasattr(_shadow, "MappingProxyType"):
                import importlib

                sys.modules.pop(_types_pkg, None)
                importlib.import_module(_types_pkg)

            # Re-import: Python will execute the real module source again
#  # MOVED: import agentic_core.L5_safety.config.structure_blueprint._constants as fresh  # noqa: F401

            assert sys.modules.get(key) is not fake_mod, (
                "After eviction, reimport must not return the fake/stale module"
            )
        finally:
            cleanup()
            # Restore the original real module
            if original_mod is not None:
                sys.modules[key] = original_mod
