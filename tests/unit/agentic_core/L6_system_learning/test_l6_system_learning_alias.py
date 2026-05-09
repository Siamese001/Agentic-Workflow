"""Smoke test for plan l6-doctrinal-alignment-noninvasive-b9d3f5 W2.

Verifies the forward-import alias `agentic_core.L6_system_learning` works
as a first-class doctrinally-prefixed path to the canonical
`system_learning` package without forcing the rename.

Invariants:

1. `agentic_core.L6_system_learning` is importable.
2. The alias inherits `__layer__`/`__l6_surface__` markers from the
   canonical package (so introspection works through either path).
3. `from agentic_core.L6_system_learning import <sub>` works for the
   27 subpackages that have an `__init__.py` (matches W1 coverage).
4. Both paths resolve to the *same* module object (state-shared, no
   double-load).
5. Deep imports work: `from agentic_core.L6_system_learning.<sub> import <name>`.
6. No DeprecationWarning is emitted (non-invasive — both paths
   first-class).
"""
from __future__ import annotations

import importlib
import warnings

import pytest

# Mirrors the 27-subpackage list from W1 (subpackages with __init__.py).
SUBPACKAGES_WITH_INIT = (
    "adapters",
    "arbitration",
    "buses",
    "confidence",
    "constraints",
    "correlation",
    "embedding",
    "enforcement",
    "engines",
    "fingerprinting",
    "golden",
    "invariants",
    "logs",
    "memory",
    "meta_learning",
    "output",
    "pipelines",
    "ports",
    "provenance",
    "raw",
    "rubrics",
    "runtime_adg",
    "scripts",
    "snapshots",
    "stores",
    "types",
    "validators",
)


def test_alias_package_importable() -> None:
    alias = importlib.import_module("agentic_core.L6_system_learning")
    assert alias is not None


def test_alias_inherits_layer_markers() -> None:
    alias = importlib.import_module("agentic_core.L6_system_learning")
    assert getattr(alias, "__layer__", None) == "L6"
    assert getattr(alias, "__l6_surface__", None) == "active"


@pytest.mark.parametrize("subname", SUBPACKAGES_WITH_INIT)
def test_subpackage_importable_via_alias(subname: str) -> None:
    canonical = importlib.import_module(f"system_learning.{subname}")
    via_alias = importlib.import_module(f"agentic_core.L6_system_learning.{subname}")
    assert via_alias is canonical, (
        f"agentic_core.L6_system_learning.{subname} must be the SAME module object "
        f"as system_learning.{subname} (state-shared)"
    )


def test_alias_emits_no_deprecation_warning() -> None:
    """Non-invasive plan: both paths are first-class. No DeprecationWarning."""
    import sys

    # Force reimport so any module-level warning would re-fire.
    for mod_name in list(sys.modules):
        if mod_name == "agentic_core.L6_system_learning" or mod_name.startswith(
            "agentic_core.L6_system_learning."
        ):
            del sys.modules[mod_name]

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.import_module("agentic_core.L6_system_learning")

    deprecation_messages = [
        str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)
    ]
    # The alias itself must not warn. Upstream `system_learning` import may emit
    # unrelated DeprecationWarnings; filter to alias-related ones only.
    alias_warnings = [
        msg for msg in deprecation_messages if "L6_system_learning" in msg
    ]
    assert alias_warnings == [], (
        "agentic_core.L6_system_learning must NOT emit DeprecationWarning — both "
        f"paths are first-class. Got: {alias_warnings}"
    )


def test_deep_import_via_alias_resolves_to_canonical() -> None:
    """Verify `from agentic_core.L6_system_learning.types import ...` works
    and yields the same names as the canonical path."""
    canonical = importlib.import_module("system_learning.types")
    via_alias = importlib.import_module("agentic_core.L6_system_learning.types")

    canonical_attrs = {n for n in dir(canonical) if not n.startswith("_")}
    alias_attrs = {n for n in dir(via_alias) if not n.startswith("_")}
    assert canonical_attrs == alias_attrs, (
        "Public attribute surfaces of canonical and alias paths must match"
    )
