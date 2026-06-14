"""Wave 4.2 — unit tests for apps_rg.integrations.c0_graph_types.

Covers the apps_rg-owned graph adapter value objects: enum string-value
contracts, frozen dataclass construction, and the __post_init__ ValueError
invariants for AnchorCandidate / ResolvedGraphAnchor / GraphNeighbor.
"""

from __future__ import annotations

import dataclasses

import pytest

from apps_rg.integrations.c0_graph_types import (
    AclStatus,
    AnchorCandidate,
    AnchorType,
    FreshnessStatus,
    GraphAdapterHealth,
    GraphNeighbor,
    GraphRelationPath,
    GraphTraversalAdapter,
    ProjectionManifest,
    ResolvedGraphAnchor,
)


class TestEnums:
    @pytest.mark.parametrize(
        "member,value",
        [
            (AclStatus.ALLOWED, "allowed"),
            (AclStatus.CLEARED, "cleared"),
            (AclStatus.DENIED, "denied"),
            (AclStatus.UNKNOWN, "unknown"),
        ],
    )
    def test_acl_status_values(self, member: AclStatus, value: str) -> None:
        assert member.value == value
        assert isinstance(member, str)  # str-Enum mixin

    def test_acl_status_member_set(self) -> None:
        assert {m.value for m in AclStatus} == {
            "allowed",
            "cleared",
            "denied",
            "unknown",
        }

    def test_freshness_status_member_set(self) -> None:
        assert {m.value for m in FreshnessStatus} == {
            "fresh",
            "current",
            "stale",
            "historical",
            "unknown",
        }

    def test_anchor_type_member_count_and_unknown(self) -> None:
        assert AnchorType.UNKNOWN.value == "unknown"
        # 18 named anchor categories declared in the module.
        assert len(list(AnchorType)) == 18

    @pytest.mark.parametrize(
        "member,value",
        [
            (AnchorType.DOCUMENT, "document"),
            (AnchorType.CODE_SYMBOL, "code_symbol"),
            (AnchorType.EVALUATION_BUNDLE, "evaluation_bundle"),
            (AnchorType.SEALED_RUN, "sealed_run"),
        ],
    )
    def test_anchor_type_values(self, member: AnchorType, value: str) -> None:
        assert member.value == value


class TestAnchorCandidate:
    def test_minimal_construction_defaults(self) -> None:
        ac = AnchorCandidate(
            anchor_value="v",
            anchor_type=AnchorType.DOCUMENT,
            original_evidence_id="ev1",
        )
        assert ac.confidence == 0.5
        assert ac.hint_source_id is None
        assert ac.hint_file_path is None

    def test_frozen(self) -> None:
        ac = AnchorCandidate(
            anchor_value="v",
            anchor_type=AnchorType.DOCUMENT,
            original_evidence_id="ev1",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            ac.anchor_value = "other"  # type: ignore[misc]

    def test_empty_anchor_value_raises(self) -> None:
        with pytest.raises(ValueError, match="anchor_value is required"):
            AnchorCandidate(
                anchor_value="",
                anchor_type=AnchorType.DOCUMENT,
                original_evidence_id="ev1",
            )

    def test_empty_evidence_id_raises(self) -> None:
        with pytest.raises(ValueError, match="original_evidence_id is required"):
            AnchorCandidate(
                anchor_value="v",
                anchor_type=AnchorType.DOCUMENT,
                original_evidence_id="",
            )


class TestResolvedGraphAnchor:
    def _valid_kwargs(self) -> dict:
        return dict(
            anchor_id="a1",
            original_evidence_id="ev1",
            anchor_type=AnchorType.MODULE,
            anchor_value="mod",
            resolved_node_id="n1",
            graph_source="adg",
            source_id="src1",
            source_version="v1",
            confidence=0.9,
            resolution_reason="exact",
            acl_status=AclStatus.ALLOWED,
        )

    def test_valid_construction(self) -> None:
        rga = ResolvedGraphAnchor(**self._valid_kwargs())
        assert rga.tenant is None
        assert rga.acl_status is AclStatus.ALLOWED

    @pytest.mark.parametrize(
        "field,msg",
        [
            ("anchor_id", "anchor_id is required"),
            ("resolved_node_id", "resolved_node_id is required"),
            ("graph_source", "graph_source is required"),
            ("source_id", "source_id is required"),
        ],
    )
    def test_required_fields_raise_when_empty(self, field: str, msg: str) -> None:
        kwargs = self._valid_kwargs()
        kwargs[field] = ""
        with pytest.raises(ValueError, match=msg):
            ResolvedGraphAnchor(**kwargs)

    def test_acl_status_accepts_raw_str(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["acl_status"] = "allowed"
        rga = ResolvedGraphAnchor(**kwargs)
        assert rga.acl_status == "allowed"


class TestGraphNeighbor:
    def _valid_kwargs(self) -> dict:
        return dict(
            node_id="n1",
            node_type="module",
            source_id="src",
            source_type="adg",
            source_version="v1",
            relation_type="imports",
            relation_path=("a", "b"),
            hop_distance=1,
        )

    def test_defaults(self) -> None:
        gn = GraphNeighbor(**self._valid_kwargs())
        assert gn.acl_status is AclStatus.UNKNOWN
        assert gn.freshness_status is FreshnessStatus.UNKNOWN
        assert gn.candidate_text_or_payload == ""

    def test_empty_node_id_raises(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["node_id"] = ""
        with pytest.raises(ValueError, match="node_id is required"):
            GraphNeighbor(**kwargs)

    def test_empty_relation_type_raises(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["relation_type"] = ""
        with pytest.raises(ValueError, match="relation_type is required"):
            GraphNeighbor(**kwargs)

    def test_negative_hop_distance_raises(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["hop_distance"] = -1
        with pytest.raises(ValueError, match="hop_distance must be >= 0"):
            GraphNeighbor(**kwargs)

    def test_zero_hop_distance_allowed(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["hop_distance"] = 0
        assert GraphNeighbor(**kwargs).hop_distance == 0


class TestPlainValueObjects:
    def test_graph_relation_path(self) -> None:
        p = GraphRelationPath(
            start_node_id="s",
            end_node_id="e",
            relations=("r1",),
            nodes=("s", "e"),
        )
        assert p.nodes == ("s", "e")

    def test_projection_manifest_defaults(self) -> None:
        pm = ProjectionManifest(
            graph_source="adg",
            projection_version="v1",
            snapshot_pointer="ptr",
            snapshot_built_at="2026-01-01",
            canonical_source_hash="hash",
        )
        assert pm.is_stale is False
        assert pm.stale_reason == ""

    def test_graph_adapter_health_defaults(self) -> None:
        h = GraphAdapterHealth(
            healthy=True,
            backend="sqlite",
            latency_p50_ms=1.0,
            latency_p95_ms=2.0,
        )
        assert h.last_error == ""


class TestProtocol:
    def test_runtime_checkable_negative(self) -> None:
        assert not isinstance(object(), GraphTraversalAdapter)
