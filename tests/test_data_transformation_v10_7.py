import pytest
from workflow.runner import run_workflow


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def _len_or_zero(x):
    if x is None:
        return 0
    if isinstance(x, (list, dict, str)):
        return len(x)
    return 1


# --------------------------------------------------------------------
# 1. Summary must be meaningfully shorter than resume input
# --------------------------------------------------------------------
@pytest.mark.data
@pytest.mark.parametrize("resume_text", [
    "Amit Ayer is a senior leader in AI strategy and professional services delivery.",
    "Jane Doe is an experienced machine learning architect focused on cloud-scale LLM systems.",
])
def test_summary_shorter_than_input(resume_text):
    """
    Ensures the DraftingStack and Summarization agents are not identity functions.
    A summary must be significantly shorter than the resume text.
    """
    out = run_workflow({"resume": resume_text, "jd": "AI Exec"})
    summary = out.get("summary") or out.get("resume", {}).get("summary")

    assert summary, "Summary is missing from workflow output"
    assert len(summary) < len(resume_text), (
        f"Summary must be shorter than input resume.\n"
        f"Summary len={len(summary)} vs input len={len(resume_text)}"
    )


# --------------------------------------------------------------------
# 2. Strategy Stack must enrich fields (context should exist)
# --------------------------------------------------------------------
@pytest.mark.data
def test_strategy_includes_context_field():
    """
    v10.7 extends Strategy fields from ["steps","goal"] to ["steps","goal","context"].
    This verifies StrategyStack actually populates context.
    """
    out = run_workflow({"resume": "AI Exec", "jd": "Anthropic"})
    strat = out.get("strategy") or out["resume"]["strategy"]

    assert isinstance(strat, dict), "Strategy block missing"
    assert "context" in strat, "Strategy must include 'context' in v10.7"
    assert _len_or_zero(strat["context"]) > 0, "Context field must be non-empty"


# --------------------------------------------------------------------
# 3. QA stack must enrich with structured issues (not identity)
# --------------------------------------------------------------------
@pytest.mark.data
def test_qa_issues_present_and_list_like():
    """
    v10.7 QA block adds structured 'issues'.
    Ensures QAStack is not simply returning legacy fields.
    """
    out = run_workflow({"resume": "AI Exec", "jd": "Databricks"})
    qa = out.get("qa") or out["resume"]["qa"]

    assert "issues" in qa, "QA block missing required 'issues' field"
    issues = qa["issues"]

    # issues can be [], but must exist and be list-like
    assert isinstance(issues, (list, tuple)), (
        f"'issues' must be a list; got {type(issues)}"
    )


# --------------------------------------------------------------------
# 4. Event history should accumulate across agents
# --------------------------------------------------------------------
@pytest.mark.data
@pytest.mark.parametrize("case", ["Default", "QA-heavy", "RAG-heavy"])
def test_event_history_accumulates(case):
    """
    Ensures the workflow generates more than 0 events and
    that events represent multiple stages firing.

    e.g., ["safety_pass","strategy_done","rag_query","draft_complete","qa_pass"]
    """
    out = run_workflow({"resume": "Case_"+case, "jd": "AI Director"})
    events = out.get("events") or out.get("resume", {}).get("events")

    assert isinstance(events, list), "Events must be list-like"
    assert len(events) >= 2, (
        f"Events should show multiple agent actions; got only: {events}"
    )


# --------------------------------------------------------------------
# 5. RAG results must differ from input prompt (semantic transform)
# --------------------------------------------------------------------
@pytest.mark.data
@pytest.mark.parametrize("query", ["cloud leadership", "enterprise generative AI", "risk modeling"])
def test_rag_results_semantically_distinct(query):
    """
    Ensures that retrieval results differ from the prompt,
    proving RAGStack isn't identity logic.
    """
    out = run_workflow({"resume": "RAG Test", "jd": query})
    rag_block = out.get("rag") or out.get("resume", {}).get("rag")

    assert rag_block, "RAG block is missing from output"
    doc = rag_block.get("top_document") or rag_block.get("document")

    assert doc, "RAG output missing 'document' or 'top_document'"
    assert query not in doc, (
        "RAG result should not simply echo the query; ensure semantic retrieval occurs"
    )


# --------------------------------------------------------------------
# 6. Final resume object must have more fields than the original input
# --------------------------------------------------------------------
@pytest.mark.data
def test_output_enriched_vs_input():
    """
    High-level check that the system as a whole adds value.
    The resume output should have more structure and fields
    than the raw input string.
    """
    raw_input = "I led ML teams in regulated financial services."
    out = run_workflow({"resume": raw_input, "jd": "CoreWeave"})

    resume_out = out.get("resume") or out
    assert isinstance(resume_out, dict), "Output resume must be structured"

    # At least Strategy + QA + Summary or Bullets should be present
    assert len(resume_out.keys()) >= 3, (
        f"Resume output not enriched; keys={list(resume_out.keys())}"
    )
