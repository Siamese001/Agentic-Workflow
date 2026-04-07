"""E3 regression tests for ADGArtifact.compute_digest (canonical-stream hash).

Verifies:
1. Digest is a valid 64-char SHA256 hex string.
2. Digest is deterministic: identical input -> identical output on repeated calls.
3. Digest is sensitive: any change to entities or relations changes the digest.
4. Digest is schema-version-sensitive: different schema_version -> different digest.
"""
from __future__ import annotations

from agentic_core.adg.artifact.builder_types import (
    ADGArtifact,
    EntityRecord,
    RelationRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_artifact(
    schema_version: str = "v3",
    entities: list[EntityRecord] | None = None,
    relations: list[RelationRecord] | None = None,
) -> ADGArtifact:
    art = ADGArtifact(
        schema_version=schema_version,
        commit_sha="abc123",
        repo_state_hash="deadbeef",
        scanner_digest="feedcafe",
    )
    art.entities = entities or []
    art.relations = relations or []
    return art


def _entity(adg_name: str, entity_type: str = "module") -> EntityRecord:
    return EntityRecord(
        adg_name=adg_name,
        entity_type=entity_type,
        layer="L0",
        identity_kind="module",
        confidence="high",
        resolved_path=adg_name.replace(".", "/") + ".py",
    )


def _relation(
    from_name: str,
    relation_type: str,
    to_name: str,
    source_file: str = "a.py",
    line_no: int = 1,
) -> RelationRecord:
    return RelationRecord(
        from_name=from_name,
        relation_type=relation_type,
        to_name=to_name,
        edge_kind="static",
        source_file=source_file,
        line_no=line_no,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestComputeDigestE3:
    def test_digest_is_sha256_hex(self) -> None:
        art = _make_artifact(entities=[_entity("mod.a")], relations=[_relation("mod.a", "imports", "mod.b")])
        d = art.compute_digest()
        assert len(d) == 64, f"expected 64 chars, got {len(d)}"
        assert all(c in "0123456789abcdef" for c in d), f"non-hex chars in {d!r}"

    def test_digest_stored_on_artifact(self) -> None:
        art = _make_artifact(entities=[_entity("mod.a")])
        d = art.compute_digest()
        assert art.artifact_digest == d

    def test_digest_deterministic_repeated_calls(self) -> None:
        art = _make_artifact(
            entities=[_entity("mod.a"), _entity("mod.b")],
            relations=[_relation("mod.a", "imports", "mod.b")],
        )
        d1 = art.compute_digest()
        d2 = art.compute_digest()
        assert d1 == d2, f"digest changed between calls: {d1} vs {d2}"

    def test_digest_deterministic_order_independent(self) -> None:
        """Digest must be identical regardless of entity/relation insertion order."""
        e1, e2 = _entity("mod.a"), _entity("mod.b")
        r = _relation("mod.a", "imports", "mod.b")

        art1 = _make_artifact(entities=[e1, e2], relations=[r])
        art2 = _make_artifact(entities=[e2, e1], relations=[r])

        assert art1.compute_digest() == art2.compute_digest()

    def test_digest_sensitive_to_entity_change(self) -> None:
        base = _make_artifact(entities=[_entity("mod.a")], relations=[])
        changed = _make_artifact(entities=[_entity("mod.DIFFERENT")], relations=[])
        assert base.compute_digest() != changed.compute_digest()

    def test_digest_sensitive_to_relation_change(self) -> None:
        e = _entity("mod.a")
        base = _make_artifact(entities=[e], relations=[_relation("mod.a", "imports", "mod.b")])
        changed = _make_artifact(entities=[e], relations=[_relation("mod.a", "imports", "mod.DIFFERENT")])
        assert base.compute_digest() != changed.compute_digest()

    def test_digest_sensitive_to_relation_type_change(self) -> None:
        e = _entity("mod.a")
        base = _make_artifact(entities=[e], relations=[_relation("mod.a", "imports", "mod.b")])
        changed = _make_artifact(entities=[e], relations=[_relation("mod.a", "calls", "mod.b")])
        assert base.compute_digest() != changed.compute_digest()

    def test_digest_sensitive_to_schema_version(self) -> None:
        e = _entity("mod.a")
        r = _relation("mod.a", "imports", "mod.b")
        v3 = _make_artifact(schema_version="v3", entities=[e], relations=[r])
        v4 = _make_artifact(schema_version="v4", entities=[e], relations=[r])
        assert v3.compute_digest() != v4.compute_digest()

    def test_empty_artifact_digest_is_valid(self) -> None:
        art = _make_artifact()
        d = art.compute_digest()
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    def test_digest_excludes_commit_sha(self) -> None:
        """Same graph content, different commit_sha → same digest."""
        e = _entity("mod.a")
        r = _relation("mod.a", "imports", "mod.b")

        art1 = _make_artifact(entities=[e], relations=[r])
        art1.commit_sha = "commit_aaa"

        art2 = _make_artifact(entities=[e], relations=[r])
        art2.commit_sha = "commit_bbb"

        assert art1.compute_digest() == art2.compute_digest()

    def test_digest_excludes_repo_state_hash(self) -> None:
        """Same graph content, different repo_state_hash → same digest."""
        e = _entity("mod.a")
        r = _relation("mod.a", "imports", "mod.b")

        art1 = _make_artifact(entities=[e], relations=[r])
        art1.repo_state_hash = "hash_aaa"

        art2 = _make_artifact(entities=[e], relations=[r])
        art2.repo_state_hash = "hash_bbb"

        assert art1.compute_digest() == art2.compute_digest()
