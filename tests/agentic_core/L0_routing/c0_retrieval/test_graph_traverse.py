"""Tests for C0.3 graph_traverse."""

from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval import (
    GraphBounds,
    GraphRelation,
    SourceClass,
    expand_graph,
    normalize_pool,
)
from agentic_core.L0_routing.c0_retrieval.graph_traverse import GraphHop
from tests.agentic_core.L0_routing.c0_retrieval._factories import make_chunk, make_pool


def _empty_adjacency(node_id, relations):
    return ()


def _hydrate(chunks):
    return normalize_pool(make_pool(chunks), tenant="tenantA")


class TestGraphHopValidation:
    def test_hop_depth_must_be_positive(self):
        import pytest
        with pytest.raises(ValueError):
            GraphHop(
                relation=GraphRelation.DEFINES, src_chunk_id="a",
                dst_chunk_id="b", hop_depth=0, accepted_reason="x",
            )

    def test_reason_required(self):
        import pytest
        with pytest.raises(ValueError):
            GraphHop(
                relation=GraphRelation.DEFINES, src_chunk_id="a",
                dst_chunk_id="b", hop_depth=1, accepted_reason="   ",
            )


class TestExpandGraphBounds:
    def test_zero_hops_returns_empty(self):
        c = make_chunk()
        h = _hydrate((c,))
        out = expand_graph(h, bounds=GraphBounds(max_hops=0), adjacency=_empty_adjacency)
        assert out.neighbors == ()
        assert out.traverse.hops == ()

    def test_empty_pool_no_traversal(self):
        empty = normalize_pool(make_pool(()), tenant="tenantA")
        out = expand_graph(empty, bounds=GraphBounds(max_hops=2), adjacency=_empty_adjacency)
        assert out.neighbors == ()


class TestExpandGraphAcceptance:
    def _build_adjacency(self, neighbor_chunk, relation: GraphRelation):
        h = _hydrate((neighbor_chunk,))
        neighbor = h.hydrated[0]

        def adj(node_id, rels):
            if relation in rels:
                return ((relation, neighbor.candidate.chunk_id, neighbor),)
            return ()

        return adj

    def test_defines_accepted(self):
        src = make_chunk(chunk_id="src")
        dst = make_chunk(chunk_id="dst", file_path="docs/dst.md")
        h = _hydrate((src,))
        adj = self._build_adjacency(dst, GraphRelation.DEFINES)
        out = expand_graph(h, bounds=GraphBounds(max_hops=1), adjacency=adj)
        assert len(out.neighbors) == 1
        assert out.traverse.hops[0].relation == GraphRelation.DEFINES

    def test_duplicates_rejected(self):
        src = make_chunk(chunk_id="src")
        dst = make_chunk(chunk_id="dst", file_path="docs/dst.md")
        h = _hydrate((src,))
        adj = self._build_adjacency(dst, GraphRelation.DUPLICATES)
        out = expand_graph(h, bounds=GraphBounds(max_hops=1), adjacency=adj)
        # DUPLICATES never accepted (rejection rule)
        assert out.neighbors == ()
        assert len(out.traverse.rejections) == 1

    def test_imports_intra_source_class_accepted(self):
        src = make_chunk(chunk_id="src", source_class=SourceClass.CODE,
                         file_path="src/a.py")
        dst = make_chunk(chunk_id="dst", source_class=SourceClass.CODE,
                         file_path="src/b.py")
        h = _hydrate((src,))
        adj = self._build_adjacency(dst, GraphRelation.IMPORTS)
        out = expand_graph(h, bounds=GraphBounds(max_hops=1), adjacency=adj)
        assert len(out.neighbors) == 1

    def test_imports_cross_source_class_rejected(self):
        src = make_chunk(chunk_id="src", source_class=SourceClass.CODE,
                         file_path="src/a.py")
        dst = make_chunk(chunk_id="dst", source_class=SourceClass.DOCS,
                         file_path="docs/b.md")
        h = _hydrate((src,))
        adj = self._build_adjacency(dst, GraphRelation.IMPORTS)
        out = expand_graph(h, bounds=GraphBounds(max_hops=1), adjacency=adj)
        assert out.neighbors == ()


class TestExpandGraphHardNos:
    """Spec lines 444-448 — hard NOs."""

    def test_no_unbounded_walk(self):
        # Build a chain where every neighbor returns another neighbor.
        chunks = [make_chunk(chunk_id=f"c{i}", file_path=f"x{i}.md") for i in range(5)]
        h = _hydrate((chunks[0],))
        hydrated_dsts = []
        for c in chunks[1:]:
            hh = _hydrate((c,))
            hydrated_dsts.append(hh.hydrated[0])
        ix = {"i": 0}

        def adj(node_id, rels):
            i = ix["i"]
            ix["i"] += 1
            if i >= len(hydrated_dsts):
                return ()
            n = hydrated_dsts[i]
            return ((GraphRelation.DEFINES, n.candidate.chunk_id, n),)

        out = expand_graph(h, bounds=GraphBounds(max_hops=2), adjacency=adj)
        for hop in out.traverse.hops:
            assert hop.hop_depth <= 2

    def test_dedupe_seen_neighbors(self):
        src = make_chunk(chunk_id="src")
        # adjacency returns the SAME neighbor twice
        dst = make_chunk(chunk_id="dst", file_path="docs/dst.md")
        hh = _hydrate((dst,))
        n = hh.hydrated[0]
        h = _hydrate((src,))

        def adj(node_id, rels):
            return (
                (GraphRelation.DEFINES, n.candidate.chunk_id, n),
                (GraphRelation.DEFINES, n.candidate.chunk_id, n),
            )

        out = expand_graph(h, bounds=GraphBounds(max_hops=1), adjacency=adj)
        assert len(out.neighbors) == 1  # second occurrence deduped
        assert any(r.rejected_reason.startswith("duplicate") for r in out.traverse.rejections)
