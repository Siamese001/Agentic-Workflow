"""Runtime-hardened LEAF_DOMAIN blueprint contract tests."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps


@pytest.fixture(scope="module")
def territories_mod():
    return pytest.importorskip("agentic_core.L5_safety.config.structure_blueprint.territories")


@pytest.fixture(scope="module")
def path_constants():
    return pytest.importorskip("agentic_core.L0_routing.config.path_constants")


def test_leaf_domain_blueprint_is_accessible(territories_mod, path_constants):
    getter = getattr(territories_mod, "get_all_territories", None)
    assert callable(getter), "get_all_territories must be callable"
    territories = getter()
    assert isinstance(territories, dict)
    agentic_core_dir = getattr(path_constants, "AGENTIC_CORE_DIR", None)
    assert isinstance(agentic_core_dir, str) and agentic_core_dir
    root_entry = territories.get(agentic_core_dir, {})
    assert isinstance(root_entry, dict)


def test_leaf_domains_are_declared_as_a_list(territories_mod, path_constants):
    territories = territories_mod.get_all_territories()
    root_entry = territories.get(path_constants.AGENTIC_CORE_DIR, {})
    leaf_domains = root_entry.get("leaf_domains", [])
    assert isinstance(leaf_domains, list)
    assert all(isinstance(item, str) and item for item in leaf_domains)
