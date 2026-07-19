"""ADG-hotspot scaffold tests for `agentic_core.L2_execution.enforcement.manifest_hash_validator` (fanin=1, band=P4).

Auto-generated speculative scaffold. Verify class/function names against actual
module before extending these scaffolds with behavioral assertions.
"""
from __future__ import annotations

import importlib

import pytest

from agentic_core.L0_routing.config.active_config_snapshot import build_active_config_snapshot
from agentic_core.L2_execution.enforcement.manifest_hash_validator import (
    ManifestHashError,
    validate_manifest_hashes,
)


MODULE_PATH = "agentic_core.L2_execution.enforcement.manifest_hash_validator"


def test_module_imports():
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )


def _active_snapshot():
    snapshot, _ = build_active_config_snapshot(
        {name: f"{name}-bytes".encode("ascii") for name in ("budget", "model", "policy", "routing")},
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return snapshot


def test_validate_manifest_hashes_accepts_bound_snapshot():
    snapshot = _active_snapshot()
    validate_manifest_hashes(dict(snapshot.hashes()), snapshot)


def test_validate_manifest_hashes_rejects_mismatch_and_missing_snapshot():
    snapshot = _active_snapshot()
    manifest = dict(snapshot.hashes())
    manifest["policy_hash"] = "0" * 64
    with pytest.raises(ManifestHashError, match="policy_hash"):
        validate_manifest_hashes(manifest, snapshot)
    with pytest.raises(ManifestHashError, match="ACTIVE_CONFIG_MISSING"):
        validate_manifest_hashes(dict(snapshot.hashes()), None)
