"""
Phase 6 — Wave 3 Tests: End-to-end read-only retrieval + static audit.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
    RetrievalMutationViolation,
    assert_not_read_only,
    is_read_only_retrieval_active,
    read_only_retrieval_scope,
)
from agentic_core.L4_state.engines.readonly_retrieval_orchestrator import (
    retrieve_with_readonly_guarantee,
)
from agentic_core.L4_state.types.retrieval_anchor import AnchoredResult, RetrievalAnchor
from agentic_core.L4_state.types.retrieval_boundary_snapshot import (
    RetrievalBoundarySnapshot,
)

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_CONFIG_HASHES = {
    "policy_hash": "aaa111",
    "routing_hash": "bbb222",
    "model_hash": "ccc333",
    "budget_hash": "ddd444",
}

_ORCHESTRATOR_MODULE = (
    Path(__file__).parent.parent.parent
    / "agentic_core"
    / "L4_state"
    / "engines"
    / "readonly_retrieval_orchestrator.py"
)

_SCOPE_MODULE = (
    Path(__file__).parent.parent.parent
    / "agentic_core"
    / "L4_state"
    / "enforcement"
    / "readonly_retrieval_scope.py"
)


def _make_anchored_result(chunk_id: str) -> AnchoredResult:
    anchor = RetrievalAnchor(
        source_doc_id=f"doc-{chunk_id}",
        chunk_id=chunk_id,
        char_start=0,
        char_end=10,
        retrieved_at_utc=_TS,
        version_hash=f"vh-{chunk_id}",
    )
    return AnchoredResult(content=f"content of {chunk_id}", anchor=anchor)


def _fake_query_fn(query: str, top_k: int, domain: str) -> list[AnchoredResult]:
    """Simulated L4 query — returns deterministic results, no side effects."""
    return [_make_anchored_result(f"chunk-{i}") for i in range(min(top_k, 2))]


def _mutating_query_fn(query: str, top_k: int, domain: str) -> list[AnchoredResult]:
    """Simulated bad query that attempts a mutation inside the retrieval scope."""
    assert_not_read_only("redis.setex")  # must raise inside scope
    return []


class TestRetrievalRemainingFunctional:
    def test_retrieval_returns_anchored_results(self):
        """
        Core Wave 3 guarantee: real retrieval entrypoint returns AnchoredResult list.
        """
        results, snapshot = retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="test query",
            top_k=2,
            domain="agentic_core",
            active_config_hashes=_CONFIG_HASHES,
            created_at_utc=_TS,
            _query_fn=_fake_query_fn,
        )
        assert len(results) == 2
        assert all(isinstance(r, AnchoredResult) for r in results)

    def test_retrieval_returns_boundary_snapshot(self):
        """Retrieval must produce a RetrievalBoundarySnapshot."""
        _, snapshot = retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="test query",
            top_k=2,
            domain="agentic_core",
            active_config_hashes=_CONFIG_HASHES,
            created_at_utc=_TS,
            _query_fn=_fake_query_fn,
        )
        assert isinstance(snapshot, RetrievalBoundarySnapshot)
        assert len(snapshot.snapshot_hash) == 64

    def test_snapshot_anchors_match_results(self):
        """Snapshot anchors must correspond to the returned result anchors."""
        results, snapshot = retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="test query",
            top_k=2,
            domain="agentic_core",
            active_config_hashes=_CONFIG_HASHES,
            created_at_utc=_TS,
            _query_fn=_fake_query_fn,
        )
        result_chunk_ids = {r.anchor.chunk_id for r in results}
        snapshot_chunk_ids = {a.chunk_id for a in snapshot.anchors}
        assert result_chunk_ids == snapshot_chunk_ids

    def test_snapshot_contains_config_hashes(self):
        _, snapshot = retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="test query",
            top_k=1,
            domain="agentic_core",
            active_config_hashes=_CONFIG_HASHES,
            created_at_utc=_TS,
            _query_fn=_fake_query_fn,
        )
        assert snapshot.active_config_hashes == _CONFIG_HASHES

    def test_retrieval_with_no_query_fn_returns_empty(self):
        """Default (no _query_fn) returns empty results + valid snapshot."""
        results, snapshot = retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="test query",
            top_k=5,
            domain="agentic_core",
            active_config_hashes=_CONFIG_HASHES,
            created_at_utc=_TS,
        )
        assert results == []
        assert isinstance(snapshot, RetrievalBoundarySnapshot)

    def test_scope_is_inactive_after_retrieval(self):
        """Scope must be released after retrieve_with_readonly_guarantee returns."""
        retrieve_with_readonly_guarantee(
            mission_id="m1",
            query="q",
            top_k=1,
            domain="dom",
            active_config_hashes={},
            created_at_utc=_TS,
            _query_fn=_fake_query_fn,
        )
        assert is_read_only_retrieval_active() is False

    def test_snapshot_is_non_mutating(self):
        """
        Snapshot creation must not raise RetrievalMutationViolation
        (it is itself non-mutating).
        """
        with read_only_retrieval_scope():
            from agentic_core.L4_state.types.retrieval_boundary_snapshot import (
                create_retrieval_boundary_snapshot,
            )

            snap = create_retrieval_boundary_snapshot(
                mission_id="m1",
                query="q",
                top_k=1,
                domain="dom",
                active_config_hashes={},
                anchors=[],
                created_at_utc=_TS,
            )
        assert isinstance(snap, RetrievalBoundarySnapshot)


class TestMutationBlockedDuringRetrieval:
    def test_mutation_blocked_inside_retrieval_scope(self):
        """
        Any attempted persistent mutation inside the retrieval path raises
        RetrievalMutationViolation.
        """
        with pytest.raises(RetrievalMutationViolation) as exc_info:
            retrieve_with_readonly_guarantee(
                mission_id="m1",
                query="test query",
                top_k=2,
                domain="agentic_core",
                active_config_hashes=_CONFIG_HASHES,
                created_at_utc=_TS,
                _query_fn=_mutating_query_fn,
            )
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc_info.value)

    def test_mutation_blocked_includes_operation_name(self):
        with pytest.raises(RetrievalMutationViolation) as exc_info:
            retrieve_with_readonly_guarantee(
                mission_id="m1",
                query="q",
                top_k=1,
                domain="dom",
                active_config_hashes={},
                created_at_utc=_TS,
                _query_fn=_mutating_query_fn,
            )
        assert "redis.setex" in str(exc_info.value)

    def test_scope_released_even_after_mutation_violation(self):
        """Scope must be cleaned up even when a mutation violation is raised."""
        with pytest.raises(RetrievalMutationViolation):
            retrieve_with_readonly_guarantee(
                mission_id="m1",
                query="q",
                top_k=1,
                domain="dom",
                active_config_hashes={},
                created_at_utc=_TS,
                _query_fn=_mutating_query_fn,
            )
        assert is_read_only_retrieval_active() is False


class TestStaticAuditNoDirectUpsertInRetrieval:
    def test_orchestrator_module_exists(self):
        assert _ORCHESTRATOR_MODULE.exists(), f"Orchestrator module not found: {_ORCHESTRATOR_MODULE}"

    def test_scope_module_exists(self):
        assert _SCOPE_MODULE.exists(), f"Scope module not found: {_SCOPE_MODULE}"

    def test_no_direct_upsert_call_in_orchestrator(self):
        """
        Static AST audit: readonly_retrieval_orchestrator.py must not contain
        any direct call to 'upsert' or 'setex' (must go through scope guard seam).
        """
        source = _ORCHESTRATOR_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden_calls: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # Check attribute calls: obj.upsert(), obj.setex()
                if isinstance(func, ast.Attribute):
                    if func.attr in ("upsert", "setex", "set"):
                        forbidden_calls.append(func.attr)
                # Check bare name calls: upsert(), setex()
                elif isinstance(func, ast.Name):
                    if func.id in ("upsert", "setex"):
                        forbidden_calls.append(func.id)

        assert forbidden_calls == [], (
            f"readonly_retrieval_orchestrator.py contains direct mutation calls "
            f"that bypass the scope guard: {forbidden_calls}"
        )

    def test_orchestrator_imports_read_only_scope(self):
        """Orchestrator must import and use read_only_retrieval_scope."""
        source = _ORCHESTRATOR_MODULE.read_text(encoding="utf-8")
        assert "read_only_retrieval_scope" in source

    def test_orchestrator_imports_retrieval_boundary_snapshot(self):
        """Orchestrator must produce a RetrievalBoundarySnapshot."""
        source = _ORCHESTRATOR_MODULE.read_text(encoding="utf-8")
        assert "RetrievalBoundarySnapshot" in source or "create_retrieval_boundary_snapshot" in source

    def test_scope_module_uses_global_flag(self):
        """Scope module must use a module-level boolean flag (not thread-local)."""
        source = _SCOPE_MODULE.read_text(encoding="utf-8")
        assert "_READ_ONLY_RETRIEVAL_ACTIVE" in source
