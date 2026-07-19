from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.config.active_config_snapshot import build_active_config_snapshot
from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest
from agentic_core.L2_execution.enforcement.manifest_hash_validator import ManifestHashError


def _snapshot():
    snapshot, _ = build_active_config_snapshot(
        {name: f"{name}-bytes".encode("ascii") for name in ("budget", "model", "policy", "routing")},
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return snapshot


def _manifest(hashes: dict[str, str]) -> SurgicalManifest:
    source = "pass"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id="cid-active-config",
        node_id="node-active-config",
        target_layer="L2",
        ast_snippet=source,
        serialization_canon="canon-v1",
        fix_constraint=FixConstraint.STRICT,
        manifest_hash=hashlib.sha256(source.encode("utf-8")).hexdigest(),
        change_history=(),
        provenance_chain=(),
        **hashes,
    )


def test_gateway_uses_the_snapshot_bound_at_construction() -> None:
    snapshot = _snapshot()
    gateway = V15ExecutionGateway(active_config_snapshot=snapshot)
    manifest = _manifest(dict(snapshot.hashes()))
    assert gateway._validate_manifest(manifest, "trace-active") is manifest


def test_gateway_fails_closed_without_bound_snapshot() -> None:
    snapshot = _snapshot()
    with pytest.raises(ManifestHashError, match="ACTIVE_CONFIG_MISSING"):
        V15ExecutionGateway()._validate_manifest(_manifest(dict(snapshot.hashes())), "trace-active")
