# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/integration/test_cache_rag_matrix_v10_7.py
#   - tests/rag/test_rag_invariants_v10_7.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/integration/test_cache_rag_matrix_v10_7.py -----
import asyncio

import pytest

from core_v10_7 import CacheManager

@pytest.mark.parametrize(
    "provider,model,temps",
    [
        ("openai", "gpt-test", [0.0, 0.1, 0.2]),
        ("anthropic", "claude-3", [0.0, 0.3]),
        ("gemini", "1.5-pro", [0.2, 0.5]),
    ],
)
def test_cache_roundtrip_variants(
    cache_manager: CacheManager, provider, model, temps
):
    for temp in temps:
        key = f"{provider}-{model}-{temp}"
        asyncio.run(
            cache_manager.set_llm_cache(
                provider, model, key, temp, {"content": key}
            )
        )
        got = asyncio.run(cache_manager.get_llm_cache(provider, model, key, temp))
        assert got and got["content"] == key

@pytest.mark.parametrize("tool", ["search", "rerank", "hybrid", "bm25", "embed"])
def test_tool_cache_variants(cache_manager: CacheManager, tool):
    payload = {"k": tool}
    cache_manager.set_tool_cache(tool, payload, {"ok": True, "tool": tool})
    assert cache_manager.get_tool_cache(tool, payload)["ok"]
# ----- END: tests/integration/test_cache_rag_matrix_v10_7.py -----
# ----- BEGIN: tests/rag/test_rag_invariants_v10_7.py -----
import pytest
from workflow.runner import run_workflow


# ---------------------------------------------------------------
# Helper: detect fields for RAG correctness
# ---------------------------------------------------------------
def _extract_rag_block(out):
    # RAG block may be top-level or inside resume
    return (
        out.get("rag")
        or out.get("resume", {}).get("rag")
        or {}
    )


# ---------------------------------------------------------------
# 1. RAG output must differ from the raw query
# ---------------------------------------------------------------
@pytest.mark.rag
@pytest.mark.parametrize("query", [
    "cloud infrastructure",
    "generative AI leadership",
    "risk modeling optimization",
])
def test_rag_not_query_echo(query):
    out = run_workflow({"resume": "RAG Test User", "jd": query})
    rag = _extract_rag_block(out)

    assert rag, "Missing RAG block"
    doc = rag.get("document") or rag.get("top_document")

    assert doc, "RAG output must contain a document"
    assert query not in doc, "RAG document must not simply echo the JD query"


# ---------------------------------------------------------------
# 2. Metadata-aware retrieval must fire in FakeChroma stub
# ---------------------------------------------------------------
@pytest.mark.rag
def test_metadata_filtering_occurs():
    """
    The FakeCollection stub resolves documents only when metadata matches.
    So the workflow must pass meaningful metadata queries.
    """
    out = run_workflow({"resume": "meta-sensitive", "jd": "AI Exec"})
    rag = _extract_rag_block(out)

    assert rag, "RAG block missing"
    assert rag.get("document"), (
        "RAG did not retrieve document — metadata filtering may have failed"
    )


# ---------------------------------------------------------------
# 3. RAG output structure invariants
# ---------------------------------------------------------------
@pytest.mark.rag
def test_rag_block_structure():
    out = run_workflow({"resume": "structure-test", "jd": "Anthropic"})
    rag = _extract_rag_block(out)

    required = ["document", "score", "source_uri"]
    for field in required:
        assert field in rag, f"RAG missing required field '{field}'"


# ---------------------------------------------------------------
# 4. Basic rerank invariant (FakeChroma only returns 1 doc, but 
#    we confirm scoring shape)
# ---------------------------------------------------------------
@pytest.mark.rag
def test_rerank_score_is_numeric():
    out = run_workflow({"resume": "rerank-test", "jd": "AWS"})
    rag = _extract_rag_block(out)
    score = rag.get("score")

    assert isinstance(score, (int, float)), (
        f"RAG score must be numeric; got {type(score)}"
    )


# ---------------------------------------------------------------
# 5. HyDE must activate only under specific triggers
# ---------------------------------------------------------------
@pytest.mark.rag
@pytest.mark.parametrize("should_trigger, query", [
    (True,  "simulate-hyde"),
    (False, "regular query for resume"),
])
def test_hyde_activation_semantics(should_trigger, query):
    """
    v10.7 HyDE logic should fire conditionally.
    We infer activation from events containing 'hyde' or
    RAG metadata indicating hypothetical doc generation.
    """
    out = run_workflow({"resume": "HyDEUser", "jd": query})
    events = [str(e).lower() for e in out.get("events", [])]

    hyde_fired = any("hyde" in e for e in events)

    if should_trigger:
        assert hyde_fired, "HyDE should have activated but did not"
    else:
        assert not hyde_fired, "HyDE activated unexpectedly"


# ---------------------------------------------------------------
# 6. Refinement loop: sequences with low confidence require re-entry
# ---------------------------------------------------------------
@pytest.mark.rag
@pytest.mark.parametrize("trigger", ["low_conf", "refinement-needed"])
def test_refinement_loop_reenters_rag(trigger):
    """
    If confidence / coverage is low, v10.7 re-enters retrieval with refinement.
    We detect refinement via multiple 'rag' events in the event list.
    """
    out = run_workflow({"resume": "User", "jd": trigger})
    events = [str(e).lower() for e in out.get("events", [])]

    rag_count = sum("rag" in e for e in events)
    assert rag_count >= 1, "RAG must run at least once"

    if trigger in {"low_conf", "refinement-needed"}:
        assert rag_count >= 2, (
            "Refinement path expected but RAG did not re-enter"
        )


# ---------------------------------------------------------------
# 7. RAG must never emit raw embedding arrays or debug info
# ---------------------------------------------------------------
@pytest.mark.rag
def test_rag_no_embedding_leakage():
    out = run_workflow({"resume": "LeakTest", "jd": "AI Exec"})
    rag = _extract_rag_block(out)

    serialized = str(rag)
    forbidden = ["[0.", "[1.", "[2.", "embedding", "embedding_fn"]

    assert not any(f in serialized for f in forbidden), (
        f"RAG leaked embedding/debug info: {serialized}"
    )


# ---------------------------------------------------------------
# 8. RAG output must retain stable type shapes (e.g., doc is str)
# ---------------------------------------------------------------
@pytest.mark.rag
def test_rag_output_types_stable():
    out = run_workflow({"resume": "TypeTest", "jd": "Cloud"})
    rag = _extract_rag_block(out)

    assert isinstance(rag.get("document"), str), "RAG document must be string"
    assert isinstance(rag.get("score"), (int, float)), "RAG score must be numeric"
    assert isinstance(rag.get("source_uri"), str), "RAG source_uri must be string"


# ---------------------------------------------------------------
# 9. No cross-contamination: RAG should not destroy upstream fields
# ---------------------------------------------------------------
@pytest.mark.rag
def test_rag_preserves_strategy_context():
    out = run_workflow({"resume": "ContextKeepUser", "jd": "Exec"})
    resume = out["resume"]

    # Strategy context must remain intact after RAG
    strat_ctx = resume["strategy"].get("context")
    assert strat_ctx, "Strategy context was lost or cleared during RAG execution"
# ----- END: tests/rag/test_rag_invariants_v10_7.py -----
