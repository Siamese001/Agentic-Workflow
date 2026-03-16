"""
Wave 1.3 Negative Test: SurgicalManifest.verify_hash enforcement at construction sites.

Proves:
1. A valid SurgicalManifest passes ``require_manifest_hash_ok``.
2. Mutating ``ast_snippet`` after construction causes ``verify_hash()`` → False.
3. ``require_manifest_hash_ok`` raises ``ValueError`` on the mutated manifest.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.types.determinism_contracts_types import (
    require_manifest_hash_ok,
)
from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SurgicalManifest,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_manifest_verify_hash_enforced")
_emit_applies_guardrail("p0", "test_manifest_verify_hash_enforced", "p0_governance")
_emit_reads_policy_state("p0", "test_manifest_verify_hash_enforced", "policy_binding")
_emit_snapshots_state("p0", "test_manifest_verify_hash_enforced", "state_snapshot")
emit_replay_key("p0", "test_manifest_verify_hash_enforced")
emit_determinism_digest("p0", "test_manifest_verify_hash_enforced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _build_valid_manifest(snippet: str = "TestNode.op()") -> SurgicalManifest:
    """Construct a SurgicalManifest with correct hash."""
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id="TEST-0001",
        node_id="TestNode",
        target_layer="L3",
        ast_snippet=snippet,
        serialization_canon="test_canon",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(snippet.encode("utf-8")).hexdigest(),
        change_history=(),
        provenance_chain=("TEST-0001",),
    )


class TestRequireManifestHashOk:
    """require_manifest_hash_ok must raise on hash mismatch."""

    def test_valid_manifest_passes(self):
        manifest = _build_valid_manifest()
        assert manifest.verify_hash() is True
        require_manifest_hash_ok(manifest)

    def test_mutated_snippet_fails_verify(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "ast_snippet", "TAMPERED.op()")
        assert manifest.verify_hash() is False

    def test_mutated_snippet_raises_value_error(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "ast_snippet", "TAMPERED.op()")
        with pytest.raises(ValueError, match="integrity hash mismatch"):
            require_manifest_hash_ok(manifest)

    def test_mutated_hash_fails_verify(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "manifest_hash", "0" * 64)
        assert manifest.verify_hash() is False

    def test_mutated_hash_raises_value_error(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "manifest_hash", "0" * 64)
        with pytest.raises(ValueError, match="integrity hash mismatch"):
            require_manifest_hash_ok(manifest)
