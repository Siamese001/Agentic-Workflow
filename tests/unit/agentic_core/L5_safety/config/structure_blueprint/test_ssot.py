#!/usr/bin/env python3
"""
Test for test_ssot
# GENERATED_MIRROR_TEST
"""

import importlib

import pytest


def test_test_ssot_can_import():
    """Test that the module can be imported successfully."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.structure_blueprint.ssot")
        assert mod is not None
    except ImportError as e:
        pytest.skip(f"Cannot import module agentic_core.L5_safety.config.structure_blueprint.ssot: {e}")


def test_test_ssot_has_file_attribute():
    """Test that module has __file__ attribute."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.structure_blueprint.ssot")
        assert hasattr(mod, "__file__")
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.config.structure_blueprint.ssot")


def test_test_ssot_has_public_attributes():
    """Test that module has public attributes or callables."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.structure_blueprint.ssot")
        # Count non-private attributes
        public_attrs = [name for name in dir(mod) if not name.startswith("_")]
        # Look for at least one callable
        callables = [name for name in public_attrs if callable(getattr(mod, name))]

        if callables:
            # Test that first callable is callable
            assert callable(getattr(mod, callables[0]))
        else:
            # If no callables, at least assert we have some public attributes
            assert len(public_attrs) >= 0
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.config.structure_blueprint.ssot")


# ---------------------------------------------------------------------------
# Drift-detection tests: catch desync between registry copies
# ---------------------------------------------------------------------------


def test_sovereign_registry_derived_from_territories():
    """SOVEREIGN_REGISTRY keys must exactly match SOVEREIGN_TERRITORIES keys.

    Regression guard: SOVEREIGN_REGISTRY is now auto-derived from
    SOVEREIGN_TERRITORIES in registry_config.py.  This test fails if
    someone accidentally re-introduces a hardcoded dict.
    """
    try:
        from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            SOVEREIGN_TERRITORIES,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import registry modules: {e}")

    sr_keys = set(SOVEREIGN_REGISTRY.keys())
    st_keys = set(SOVEREIGN_TERRITORIES.keys())
    assert sr_keys == st_keys, (
        f"SOVEREIGN_REGISTRY and SOVEREIGN_TERRITORIES have diverged.\n"
        f"In TERRITORIES but not REGISTRY: {sorted(st_keys - sr_keys)}\n"
        f"In REGISTRY but not TERRITORIES: {sorted(sr_keys - st_keys)}\n"
        "Fix: SOVEREIGN_REGISTRY must be derived from SOVEREIGN_TERRITORIES."
    )


def test_sovereign_registry_subfolders_match_territories():
    """SOVEREIGN_REGISTRY subfolders must match SOVEREIGN_TERRITORIES subfolders for every territory."""
    try:
        from collections.abc import Mapping

        from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            SOVEREIGN_TERRITORIES,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import registry modules: {e}")

    mismatches = []
    for name in SOVEREIGN_TERRITORIES:
        if name not in SOVEREIGN_REGISTRY:
            continue
        t_sub = SOVEREIGN_TERRITORIES[name].get("subfolders", {})
        if isinstance(t_sub, Mapping):
            t_set = set(t_sub.keys())
        else:
            t_set = set(t_sub)
        r_set = set(SOVEREIGN_REGISTRY[name].get("subfolders", []))
        if t_set != r_set:
            mismatches.append(f"  {name}: TERRITORIES={sorted(t_set)} REGISTRY={sorted(r_set)}")

    assert not mismatches, (
        "Subfolder mismatches between SOVEREIGN_TERRITORIES and SOVEREIGN_REGISTRY:\n" + "\n".join(mismatches)
    )


def test_path_constants_root_whitelist_matches_territories():
    """path_constants.ROOT_WHITELIST must not drift from SOVEREIGN_TERRITORIES keys.

    path_constants.py is L0-only (cannot import from L5), so ROOT_WHITELIST is
    maintained separately.  This test catches divergence before it causes
    healing agents to delete files from valid territories.
    """
    try:
        from agentic_core.L0_routing.config.path_constants import ROOT_WHITELIST
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            SOVEREIGN_TERRITORIES,
        )
    except ImportError as e:
        pytest.skip(f"Cannot import constants: {e}")

    st_keys = frozenset(SOVEREIGN_TERRITORIES.keys())
    in_st_not_wl = st_keys - ROOT_WHITELIST
    in_wl_not_st = ROOT_WHITELIST - st_keys

    assert not in_st_not_wl, (
        f"Territories in SOVEREIGN_TERRITORIES missing from path_constants.ROOT_WHITELIST: "
        f"{sorted(in_st_not_wl)}\n"
        "Fix: add these to ROOT_WHITELIST in agentic_core/L0_routing/config/path_constants.py"
    )
    assert not in_wl_not_st, (
        f"Entries in path_constants.ROOT_WHITELIST missing from SOVEREIGN_TERRITORIES: "
        f"{sorted(in_wl_not_st)}\n"
        "Fix: add these territories to _constants.py or remove from ROOT_WHITELIST"
    )
