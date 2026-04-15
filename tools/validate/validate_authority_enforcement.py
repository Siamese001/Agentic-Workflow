"""End-to-end validation of the authority-enforcement implementation.

Checks every invariant required by the close-out scope:
  1. Policy domain classification (5 query probes)
  2. Collection routing for policy domain
  3. arch_docs live metadata (T4_implementation_evidence, invalid=True)
  4. curated_agent_docs live metadata (valid normative sources)
  5. fail-closed normative filter on arch_docs chunks
  6. tier-aware rerank: arch_docs gets zero bonus, curated wins
  7. CitationAnchor provenance from chunk metadata
  8. AGEN YAML seed files parse correctly and carry required fields

Exit code 0 = all pass.  Non-zero = at least one FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CHROMA_STORE = REPO_ROOT / "data" / "cache" / "chromadb"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PASS = "PASS"
_FAIL = "FAIL"
_results: list[tuple[str, str, str]] = []  # (label, status, detail)


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = _PASS if condition else _FAIL
    _results.append((label, status, detail))
    marker = "  OK" if condition else "FAIL"
    print(f"  [{marker}] {label}" + (f" — {detail}" if detail else ""))
    return condition


# ---------------------------------------------------------------------------
# 1. Domain classification
# ---------------------------------------------------------------------------


def validate_domain_classification() -> None:
    print("\n── 1. Domain classification ──")
    from agentic_core.L3_orchestration.reasoning.engines.query_intent_detector import (
        QueryIntentDetector,
    )

    det = QueryIntentDetector()

    probes = [
        ("Can I use bare except here?", "policy"),
        ("Is subprocess.run without timeout allowed?", "policy"),
        ("What should I use for dependency / blast-radius analysis?", "best_practice"),
        ("What are the constitutional hard constraints for agentic code?", "policy"),
        ("L3 layer design invariants and safety trust boundary enforcement", "architecture"),
    ]
    for query, expected in probes:
        got = det.detect_topic_domain(query)
        check(
            f"classify: {query[:55]!r}",
            got == expected,
            f"expected={expected!r} got={got!r}",
        )


# ---------------------------------------------------------------------------
# 2. Collection routing
# ---------------------------------------------------------------------------


def validate_routing() -> None:
    print("\n── 2. Collection routing ──")
    from agentic_core.L3_orchestration.reasoning.engines.query_router import QueryRouter

    cases = [
        ("policy", "curated_agent_docs"),
        ("architecture", "arch_docs"),
        ("best_practice", "curated_agent_docs"),
        ("tool_contracts", "curated_agent_docs"),
        ("general", "code_chunks"),
    ]
    for domain, expected in cases:
        got = QueryRouter._get_target_collection(domain, "code_chunks")
        check(f"route domain={domain!r}", got == expected, f"expected={expected!r} got={got!r}")

    pf = QueryRouter._get_arch_prefilter("policy")
    check("no arch prefilter for policy", pf is None, f"got={pf!r}")


# ---------------------------------------------------------------------------
# 3. Live arch_docs metadata
# ---------------------------------------------------------------------------


def validate_arch_docs_metadata() -> None:
    print("\n── 3. arch_docs live metadata ──")
    try:
        import chromadb
    except ImportError:
        check("chromadb import", False, "chromadb not installed")
        return

    client = chromadb.PersistentClient(path=str(CHROMA_STORE))
    try:
        col = client.get_collection("arch_docs")
    except (
        ValueError,
        KeyError,
    ) as exc:  # guardian: allow-broad-exception -- chromadb raises ValueError/KeyError when collection absent
        check("arch_docs collection exists", False, str(exc))
        return

    check("arch_docs collection exists", True)
    results = col.get(limit=20, include=["metadatas"])
    metas = results.get("metadatas") or []
    check("arch_docs has chunks", len(metas) > 0, f"got {len(metas)} chunks")
    if not metas:
        return

    for key, expected_val in [
        ("source_collection", "arch_docs"),
        ("authority_tier", "T4_implementation_evidence"),
        ("normative_scope", "evidence_only"),
        ("invalid_for_normative_use", True),
    ]:
        hits = [m for m in metas if m.get(key) == expected_val]
        check(
            f"arch_docs[{key}]={expected_val!r}",
            len(hits) == len(metas),
            f"{len(hits)}/{len(metas)} chunks correct",
        )


# ---------------------------------------------------------------------------
# 4. Live curated_agent_docs metadata
# ---------------------------------------------------------------------------


def validate_curated_metadata() -> None:
    print("\n── 4. curated_agent_docs live metadata ──")
    try:
        import chromadb
    except ImportError:
        return

    client = chromadb.PersistentClient(path=str(CHROMA_STORE))
    try:
        col = client.get_collection("curated_agent_docs")
    except (
        ValueError,
        KeyError,
    ) as exc:  # guardian: allow-broad-exception -- chromadb raises ValueError/KeyError when collection absent
        check("curated_agent_docs collection exists", False, str(exc))
        return

    check("curated_agent_docs collection exists", True)
    results = col.get(limit=20, include=["metadatas"])
    metas = results.get("metadatas") or []
    check("curated has chunks", len(metas) > 0)
    if not metas:
        return

    check(
        "curated source_collection=curated_agent_docs",
        all(m.get("source_collection") == "curated_agent_docs" for m in metas),
        f"sample={len(metas)}",
    )
    check(
        "curated invalid_for_normative_use=False",
        all(m.get("invalid_for_normative_use") is False for m in metas),
        f"sample={len(metas)}",
    )
    valid_tiers = {"T1_vendor", "T2_standard", "T3_guidance", "T4_repo_canonical"}
    tiers_seen = {m.get("authority_tier") for m in metas}
    check(
        "curated authority_tier in allowed set",
        tiers_seen <= valid_tiers,
        f"tiers seen={tiers_seen}",
    )


# ---------------------------------------------------------------------------
# 5. Fail-closed normative filter
# ---------------------------------------------------------------------------


def validate_normative_filter() -> None:
    print("\n── 5. Fail-closed normative filter ──")
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
        LOW_NORMATIVE_COVERAGE,
        filter_normative_sources,
    )
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
        HybridSearchResult,
    )

    def _make(cid: str, **meta: object) -> HybridSearchResult:
        return HybridSearchResult(
            chunk_id=cid,
            content="x",
            metadata=dict(meta),
            combined_score=0.9,
            source="vector",
            vector_score=0.9,
            lexical_score=0.0,
        )

    arch = _make(
        "a1",
        source_collection="arch_docs",
        authority_tier="T4_implementation_evidence",
        normative_scope="evidence_only",
        invalid_for_normative_use=True,
        authority_level=0.9,
    )
    curated = _make(
        "c1",
        source_collection="curated_agent_docs",
        authority_tier="T3_guidance",
        normative_scope="external_authority",
        invalid_for_normative_use=False,
        authority_level=0.9,
    )
    no_prov = _make("n1")  # empty metadata — must fail closed

    accepted, rejected = filter_normative_sources([arch, curated, no_prov])
    check("arch_docs rejected by normative filter", arch in rejected)
    check("curated_agent_docs accepted", curated in accepted)
    check("missing-provenance chunk rejected (fail-closed)", no_prov in rejected)
    check("LOW_NORMATIVE_COVERAGE constant exported", LOW_NORMATIVE_COVERAGE == "LOW_NORMATIVE_COVERAGE")

    accepted_empty, _ = filter_normative_sources([arch])
    check("all-arch batch yields empty accepted", accepted_empty == [])


# ---------------------------------------------------------------------------
# 6. Tier-aware rerank
# ---------------------------------------------------------------------------


def validate_tier_aware_rerank() -> None:
    print("\n── 6. Tier-aware rerank ──")
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
        apply_authority_rerank,
    )
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
        HybridSearchResult,
    )

    def _r(cid: str, score: float, tier: str) -> HybridSearchResult:
        return HybridSearchResult(
            chunk_id=cid,
            content="x",
            metadata={"authority_tier": tier, "authority_level": 1.0},
            combined_score=score,
            source="vector",
            vector_score=score,
            lexical_score=0.0,
        )

    arch_impl = _r("arch", 0.85, "T4_implementation_evidence")
    curated_t4 = _r("curated_local", 0.80, "T4_repo_canonical")
    curated_t3 = _r("curated_ext", 0.75, "T3_guidance")

    out = apply_authority_rerank([arch_impl, curated_t4, curated_t3], authority_bonus=0.15, tier_aware=True)
    arch_score = next(r.combined_score for r in out if r.chunk_id == "arch")
    check(
        "arch T4_impl gets zero bonus — score stays 0.85", arch_score == 0.85, f"arch_score={arch_score:.4f}"
    )
    check(
        "arch_docs does not rank first under tier_aware rerank",
        out[0].chunk_id != "arch",
        f"rank-1={out[0].chunk_id!r} score={out[0].combined_score:.3f}",
    )


# ---------------------------------------------------------------------------
# 7. CitationAnchor provenance from chunk metadata
# ---------------------------------------------------------------------------


def validate_citation_anchor() -> None:
    print("\n── 7. CitationAnchor provenance ──")
    from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
        make_citation_anchor_from_chunk,
    )
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
        HybridSearchResult,
    )

    r = HybridSearchResult(
        chunk_id="agen0001",
        content="no bare except",
        metadata={
            "source_collection": "curated_agent_docs",
            "authority_tier": "T4_repo_canonical",
            "authority_level": 0.97,
            "file_path": "docs/requirements/registry/policy/AGEN-0001.yaml",
            "layer": "docs",
            "canonical_digest": "abc123",
        },
        combined_score=0.97,
        source="vector",
        vector_score=0.97,
        lexical_score=0.0,
    )
    anchor = make_citation_anchor_from_chunk(r)
    check(
        "anchor.collection from metadata source_collection",
        anchor.collection == "curated_agent_docs",
        f"got={anchor.collection!r}",
    )
    check("anchor.file_path from metadata", "AGEN-0001" in anchor.file_path)
    check(
        "anchor.provenance_confidence from authority_level",
        abs(anchor.provenance_confidence - 0.97) < 0.001,
        f"got={anchor.provenance_confidence}",
    )

    # Fallback: missing source_collection → uses source field
    r2 = HybridSearchResult(
        chunk_id="fb1",
        content="x",
        metadata={"source": "curated_agent_docs"},
        combined_score=0.8,
        source="vector",
        vector_score=0.8,
        lexical_score=0.0,
    )
    anchor2 = make_citation_anchor_from_chunk(r2)
    check(
        "anchor fallback to source field when source_collection absent",
        anchor2.collection == "curated_agent_docs",
        f"got={anchor2.collection!r}",
    )


# ---------------------------------------------------------------------------
# 8. YAML seed files
# ---------------------------------------------------------------------------


def validate_yaml_seeds() -> None:
    print("\n── 8. YAML seed files ──")
    seeds = [
        (REPO_ROOT / "docs/requirements/registry/policy/AGEN-0001.yaml", "policy", "T4_repo_canonical"),
        (REPO_ROOT / "docs/requirements/registry/policy/AGEN-0002.yaml", "policy", "T4_repo_canonical"),
        (
            REPO_ROOT / "docs/requirements/registry/best_practice/AGEN-0050.yaml",
            "best_practice",
            "T4_repo_canonical",
        ),
    ]
    required_fields = [
        "id",
        "title",
        "domain",
        "status",
        "authority_tier",
        "source_collection",
        "normative_scope",
        "statement",
        "rationale",
    ]

    for path, expected_domain, expected_tier in seeds:
        check(f"{path.name} exists", path.exists())
        if not path.exists():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            check(f"{path.name} parses as YAML", False, str(exc))
            continue
        check(f"{path.name} parses as YAML", True)
        missing = [f for f in required_fields if f not in data]
        check(f"{path.name} required fields present", not missing, f"missing={missing}")
        check(
            f"{path.name} domain={expected_domain!r}",
            data.get("domain") == expected_domain,
            f"got={data.get('domain')!r}",
        )
        check(
            f"{path.name} authority_tier={expected_tier!r}",
            data.get("authority_tier") == expected_tier,
            f"got={data.get('authority_tier')!r}",
        )
        check(
            f"{path.name} source_collection=curated_agent_docs",
            data.get("source_collection") == "curated_agent_docs",
            f"got={data.get('source_collection')!r}",
        )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 72)
    print("Authority Enforcement — End-to-End Validation")
    print("=" * 72)

    validate_domain_classification()
    validate_routing()
    validate_arch_docs_metadata()
    validate_curated_metadata()
    validate_normative_filter()
    validate_tier_aware_rerank()
    validate_citation_anchor()
    validate_yaml_seeds()

    print("\n" + "=" * 72)
    failures = [r for r in _results if r[1] == _FAIL]
    passes = [r for r in _results if r[1] == _PASS]
    print(f"Result: {len(passes)} PASS  {len(failures)} FAIL  (total {len(_results)})")
    if failures:
        print("\nFailed checks:")
        for label, _, detail in failures:
            print(f"  x {label}" + (f" — {detail}" if detail else ""))
    print("=" * 72)
    sys.exit(len(failures))


if __name__ == "__main__":
    main()
