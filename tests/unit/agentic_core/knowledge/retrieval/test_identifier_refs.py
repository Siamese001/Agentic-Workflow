"""Unit tests for IdentifierRefs (W5.1 — G4 JIT identifier pattern)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.identifier_refs import (
    Dereferencer,
    DereferenceResult,
    IdentifierRef,
    IdentifierRefKind,
    IdentifierRefRegistry,
)


# ---------------------------------------------------------------------------
# IdentifierRef
# ---------------------------------------------------------------------------


class TestIdentifierRef:
    def test_frozen_dataclass(self) -> None:
        ref = IdentifierRef(
            ref_id="ref-001",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_abc",
            summary="Test chunk",
            token_estimate=50,
        )
        with pytest.raises(AttributeError):
            ref.ref_id = "changed"  # type: ignore[misc]

    def test_to_prompt_text_basic(self) -> None:
        ref = IdentifierRef(
            ref_id="ref-001",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_abc",
            summary="Test chunk",
        )
        text = ref.to_prompt_text()
        assert "[ref:ref-001" in text
        assert "chunk" in text
        assert "Test chunk" in text
        assert "ACL" not in text

    def test_to_prompt_text_with_acl(self) -> None:
        ref = IdentifierRef(
            ref_id="ref-002",
            kind=IdentifierRefKind.TOOL_RESULT,
            source_key="tool_subprocess",
            summary="Subprocess output",
            acl_required=["internal"],
        )
        text = ref.to_prompt_text()
        assert "[ACL]" in text

    def test_all_kinds(self) -> None:
        for kind in IdentifierRefKind:
            ref = IdentifierRef(ref_id=f"ref-{kind.value}", kind=kind, source_key="x")
            assert ref.kind == kind


# ---------------------------------------------------------------------------
# Dereferencer
# ---------------------------------------------------------------------------


class TestDereferencer:
    @staticmethod
    def _chunk_resolver(ref: IdentifierRef) -> str | None:
        """Fake resolver that returns content based on source_key."""
        return f"Content of {ref.source_key}"

    def test_successful_dereference(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-001",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_abc",
            summary="Test",
            token_estimate=10,
            tenant="acme",
        )
        result = deref.dereference(ref)
        assert result.success
        assert "chunk_abc" in result.content
        assert result.tokens_used > 0

    def test_tenant_mismatch_blocked(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-002",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_xyz",
            tenant="other_tenant",
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "Tenant mismatch" in result.error

    def test_acl_denied(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000, acl_tags=["public"])
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-003",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_secret",
            acl_required=["internal"],
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "ACL denied" in result.error

    def test_acl_allowed_with_correct_tags(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000, acl_tags=["internal", "public"])
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-004",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_secret",
            acl_required=["internal"],
        )
        result = deref.dereference(ref)
        assert result.success

    def test_budget_exceeded(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=10)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-005",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_big",
            token_estimate=100,
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "Budget exceeded" in result.error

    def test_no_resolver_registered(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)

        ref = IdentifierRef(
            ref_id="ref-006",
            kind=IdentifierRefKind.GRAPH_NODE,
            source_key="node_123",
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "No resolver" in result.error

    def test_resolver_returns_none(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, lambda _: None)

        ref = IdentifierRef(
            ref_id="ref-007",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_missing",
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "unavailable" in result.error

    def test_resolver_raises_exception(self) -> None:
        def bad_resolver(ref: IdentifierRef) -> str | None:
            raise ValueError("broken")

        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, bad_resolver)

        ref = IdentifierRef(
            ref_id="ref-008",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_bad",
        )
        result = deref.dereference(ref)
        assert not result.success
        assert "Resolver error" in result.error

    def test_batch_dereference(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        refs = [
            IdentifierRef(
                ref_id=f"ref-{i}", kind=IdentifierRefKind.CHUNK, source_key=f"chunk_{i}", token_estimate=10
            )
            for i in range(5)
        ]
        results = deref.dereference_batch(refs)
        assert len(results) == 5
        assert all(r.success for r in results)

    def test_batch_stops_on_budget(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=25)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        refs = [
            IdentifierRef(
                ref_id=f"ref-{i}", kind=IdentifierRefKind.CHUNK, source_key=f"chunk_{i}", token_estimate=10
            )
            for i in range(5)
        ]
        results = deref.dereference_batch(refs)
        # Should stop after 2 successful (20 tokens) + 1 budget-exceeded
        assert len(results) <= 3
        assert any("Budget exceeded" in r.error for r in results if not r.success)

    def test_tokens_consumed_tracking(self) -> None:
        deref = Dereferencer(tenant="acme", token_budget=1000)
        deref.register_resolver(IdentifierRefKind.CHUNK, self._chunk_resolver)

        ref = IdentifierRef(
            ref_id="ref-001",
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_abc",
            token_estimate=50,
        )
        deref.dereference(ref)
        assert deref.tokens_consumed == 50
        assert deref.tokens_remaining == 950


# ---------------------------------------------------------------------------
# IdentifierRefRegistry
# ---------------------------------------------------------------------------


class TestIdentifierRefRegistry:
    def test_issue_ref(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        ref = registry.issue(
            kind=IdentifierRefKind.CHUNK,
            source_key="chunk_abc",
            summary="Test chunk",
            token_estimate=50,
        )
        assert ref.ref_id.startswith("ref-")
        assert ref.kind == IdentifierRefKind.CHUNK
        assert ref.source_key == "chunk_abc"

    def test_get_ref(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        ref = registry.issue(kind=IdentifierRefKind.DOCUMENT, source_key="doc_1")
        found = registry.get_ref(ref.ref_id)
        assert found is not None
        assert found.source_key == "doc_1"

    def test_get_ref_not_found(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        assert registry.get_ref("nonexistent") is None

    def test_record_dereference(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        ref = registry.issue(kind=IdentifierRefKind.CHUNK, source_key="chunk_1")
        result = DereferenceResult(ref=ref, content="hello", tokens_used=5, success=True)
        registry.record_dereference(result)
        assert len(registry.dereferenced_refs) == 1

    def test_issued_refs_list(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        registry.issue(kind=IdentifierRefKind.CHUNK, source_key="c1")
        registry.issue(kind=IdentifierRefKind.DOCUMENT, source_key="d1")
        assert len(registry.issued_refs) == 2

    def test_audit_summary(self) -> None:
        registry = IdentifierRefRegistry(query_id="q-001")
        registry.issue(kind=IdentifierRefKind.CHUNK, source_key="c1")
        registry.issue(kind=IdentifierRefKind.DOCUMENT, source_key="d1")
        summary = registry.audit_summary()
        assert summary["query_id"] == "q-001"
        assert summary["refs_issued"] == 2
        assert summary["refs_dereferenced"] == 0
