"""Tests for deterministic ADG artifact digest.

Tier: unit
Plan: .windsurf/plans/three-bucket-otel-view-5db409.md (W7.3)

Per ADR-074 and the three-bucket authority model, ADG_CERTIFIED requires
that two snapshot generations of the same source produce byte-identical
artifact_digest values. This test exercises that guarantee at the
in-memory ``ADGArtifact.compute_digest()`` boundary so CI catches digest
non-determinism BEFORE a regenerated snapshot is ever written to disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

__adg_consumer_mode__ = "inventory"

from agentic_core.adg.artifact.builder import (
    ADGArtifact,
    BlindSpotReport,
    EntityRecord,
    RelationRecord,
    StructuralMetrics,
)


def _entity(adg_name: str, *, layer: str = "L2") -> EntityRecord:
    return EntityRecord(
        adg_name=adg_name,
        entity_type="module",
        layer=layer,
        identity_kind="absolute",
        confidence="high",
        resolved_path=f"{adg_name.replace('.', '/')}.py",
    )


def _relation(src: str, dst: str) -> RelationRecord:
    return RelationRecord(
        from_name=src,
        relation_type="imports",
        to_name=dst,
        edge_kind="STATIC_IMPORT",
        source_file=f"{src.replace('.', '/')}.py",
        line_no=1,
    )


def _make_artifact(*, n_entities: int = 5) -> ADGArtifact:
    return ADGArtifact(
        commit_sha="sha_irrelevant",  # excluded from digest
        scanner_digest="scanner_v1",
        entities=[_entity(f"mod_{i}") for i in range(n_entities)],
        relations=[
            _relation(f"mod_{i}", f"mod_{(i + 1) % n_entities}")
            for i in range(n_entities)
        ],
        identity_health={"resolved": n_entities, "unresolved": 0},
        structural_metrics=StructuralMetrics(),
        blind_spots=BlindSpotReport(),
    )


class TestDigestDeterminism:
    """Same inputs MUST produce the same digest, byte-for-byte."""

    def test_two_artifacts_same_input_same_digest(self) -> None:
        a1 = _make_artifact()
        a2 = _make_artifact()
        d1 = a1.compute_digest()
        d2 = a2.compute_digest()
        assert d1 == d2
        assert len(d1) == 64

    def test_idempotent_recompute(self) -> None:
        a = _make_artifact()
        assert a.compute_digest() == a.compute_digest()

    def test_commit_sha_excluded_from_digest(self) -> None:
        a1 = _make_artifact()
        a1.commit_sha = "sha_one"
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.commit_sha = "sha_two_different"
        d2 = a2.compute_digest()
        assert d1 == d2

    def test_relation_construction_order_does_not_affect_digest(self) -> None:
        a1 = ADGArtifact(
            entities=[_entity("a"), _entity("b"), _entity("c")],
            relations=[_relation("a", "b"), _relation("b", "c"), _relation("c", "a")],
        )
        a2 = ADGArtifact(
            entities=[_entity("c"), _entity("a"), _entity("b")],
            relations=[_relation("c", "a"), _relation("a", "b"), _relation("b", "c")],
        )
        assert a1.compute_digest() == a2.compute_digest()

    def test_serialized_form_is_sorted_json(self) -> None:
        from agentic_core.adg.artifact.serializer import serialize_artifact

        a1 = _make_artifact()
        a1.compute_digest()
        s1 = serialize_artifact(a1)
        s2 = serialize_artifact(a1)
        assert s1 == s2
        parsed = json.loads(s1)
        assert parsed["artifact_digest"] == a1.artifact_digest


class TestDigestSensitivity:
    """The digest MUST react to changes in canonical fields."""

    def test_changing_entity_set_changes_digest(self) -> None:
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.entities.append(_entity("extra_module"))
        assert d1 != a2.compute_digest()

    def test_changing_relation_set_changes_digest(self) -> None:
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.relations.append(_relation("mod_0", "mod_4"))
        assert d1 != a2.compute_digest()

    def test_changing_layer_changes_digest(self) -> None:
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.entities[0] = _entity(a2.entities[0].adg_name, layer="L3")
        assert d1 != a2.compute_digest()

    def test_changing_relation_endpoints_changes_digest(self) -> None:
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.relations[0] = _relation("mod_0", "mod_3")
        assert d1 != a2.compute_digest()

    def test_scanner_digest_not_in_payload(self) -> None:
        # scanner_digest is recorded in to_dict but NOT in compute_digest payload.
        # Pin the contract so refactors can't silently broaden it.
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.scanner_digest = "different_scanner"
        assert d1 == a2.compute_digest(), (
            "scanner_digest MUST NOT affect digest per ADGArtifact.compute_digest contract"
        )

    def test_schema_version_in_payload(self) -> None:
        a1 = _make_artifact()
        d1 = a1.compute_digest()
        a2 = _make_artifact()
        a2.schema_version = "v999"
        assert d1 != a2.compute_digest()
