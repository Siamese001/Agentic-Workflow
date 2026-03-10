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
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    require_manifest_hash_ok,
)
from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SurgicalManifest,
)


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
