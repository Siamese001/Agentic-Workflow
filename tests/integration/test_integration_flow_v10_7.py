import pytest
from workflow.runner import run_workflow


# ---------------------------------------------------------------------
# Helper: ensure predictable event progression
# ---------------------------------------------------------------------
EXPECTED_EVENT_ORDER = [
    "safety",      # SafetyGuardStack
    "strategy",    # StrategyStack
    "rag",         # RAGStack
    "bullet",      # BulletStack
    "draft",       # DraftingStack
    "qa",          # QAStack
    "hil",         # HILInteractionStack (only sometimes)
]


def _normalize_events(events):
    """
    Extracts canonical event prefixes from the workflow's event list.
    Supports string or dict-based event objects.
    """
    norm = []
    for e in events:
        if isinstance(e, str):
            norm.append(e.lower())
        elif isinstance(e, dict):
            # e.g., {"qa_pass": "..."}
            for k in e.keys():
                norm.append(k.lower())
        else:
            norm.append(str(e).lower())
    return norm


# ---------------------------------------------------------------------
# 1. Multi-Agent data handoff: strategy → rag → bullet → drafting → qa
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_agent_handoff_sequence_and_state_accumulation():
    out = run_workflow({"resume": "IntegrationTestUser", "jd": "AI Exec"})
    resume = out["resume"]

    # Ensure key blocks exist:
    for blk in ["strategy", "qa"]:
        assert blk in resume, f"Missing required block '{blk}'"

    # Strategy should feed downstream (non-empty):
    assert resume["strategy"].get("steps"), "Strategy steps empty (handoff broken)"
    assert resume["strategy"].get("goal"), "Strategy goal empty"

    # QA should incorporate upstream context:
    assert "issues" in resume["qa"], "QA issues missing"
    assert isinstance(resume["qa"]["issues"], list)


# ---------------------------------------------------------------------
# 2. Event progression must follow DAG order
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_event_progression_respects_dag_order():
    out = run_workflow({"resume": "OrderTest", "jd": "AWS"})
    events = _normalize_events(out["events"])

    # For each expected prefix, ensure it appears *after* earlier ones
    positions = {}
    for prefix in EXPECTED_EVENT_ORDER:
        for idx, evt in enumerate(events):
            if prefix in evt:
                positions[prefix] = idx
                break

    # Safety must be first if present
    if "safety" in positions:
        assert positions["safety"] == min(positions.values())

    # Enforce order: strategy before rag, rag before bullet, etc.
    for earlier, later in zip(EXPECTED_EVENT_ORDER, EXPECTED_EVENT_ORDER[1:]):
        if earlier in positions and later in positions:
            assert positions[earlier] < positions[later], (
                f"Event '{earlier}' must occur before '{later}' — DAG violation."
            )


# ---------------------------------------------------------------------
# 3. Parallel/branch merge correctness
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_parallel_merge_behavior():
    out = run_workflow({"resume": "parallel-merge", "jd": "scenario"})
    events = _normalize_events(out["events"])

    # At least rag + bullet should appear when parallel paths probe RAG differently
    assert any("rag" in e for e in events), "Missing RAG event in parallel-merge"
    assert any("bullet" in e for e in events), "Missing Bullet event"

    # Order must still respect DAG
    rag_idx = min(idx for idx, e in enumerate(events) if "rag" in e)
    bullet_idx = min(idx for idx, e in enumerate(events) if "bullet" in e)
    assert rag_idx < bullet_idx, "RAG must precede Bullet in parallel merge scenarios"


# ---------------------------------------------------------------------
# 4. Retry/low-confidence loop regenerates downstream agents
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_retry_regenerates_downstream_agents():
    out = run_workflow({"resume": "RetryFlow", "jd": "AI Exec", "low_confidence": True})
    events = _normalize_events(out["events"])

    # Must produce explicit retry event
    assert any("retry" in e for e in events), "Retry event missing"

    # After retry, downstream agents (draft/qa) should appear again or show regenerated state
    draft_count = sum("draft" in e for e in events)
    qa_count = sum("qa" in e for e in events)
    assert draft_count >= 1, "Drafting agent did not run after retry"
    assert qa_count >= 1, "QA agent did not run after retry"


# ---------------------------------------------------------------------
# 5. HIL (human-in-loop) triggers correctly and does not break DAG
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_hil_trigger_sequence():
    out = run_workflow({"resume": "hil-trigger", "jd": "scenario"})
    events = _normalize_events(out["events"])

    # Must contain a hil-related event
    assert any("hil" in e for e in events), "HIL event missing in hil-trigger scenario"

    # HIL must appear AFTER QA
    if any("hil" in e for e in events):
        hil_idx = min(idx for idx, e in enumerate(events) if "hil" in e)
        qa_idx = min(idx for idx, e in enumerate(events) if "qa" in e)
        assert qa_idx < hil_idx, "HIL must occur after QA"


# ---------------------------------------------------------------------
# 6. End-to-End full completion without data loss
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_end_to_end_state_not_lost():
    """
    Ensures that data inserted by early stacks remains intact after all downstream stacks run.
    """
    out = run_workflow({"resume": "E2EUser", "jd": "AI Director"})
    resume = out["resume"]

    # Strategy seeds context; QA must not erase it
    assert resume["strategy"].get("context"), "Strategy context lost during flow"

    # Summary or bullets must exist after Drafting
    assert any(
        k in resume and resume[k] for k in ("summary", "bullets")
    ), "Drafting output missing summary/bullets — state loss detected"

    # Issues must be preserved in QA
    assert "issues" in resume["qa"], "QA issues lost or overwritten"


# ---------------------------------------------------------------------
# 7. Handoff content must differ from original input (no passthrough)
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_multistack_passthrough_prevention():
    """
    Ensures no agent acts as a full passthrough identity function.
    """
    raw = "This is a long resume string that should trigger drafting and summary mechanisms."
    out = run_workflow({"resume": raw, "jd": "AI Exec"})
    resume = out["resume"]

    # Summary must differ significantly from input
    summary = resume.get("summary")
    assert summary, "Summary missing"
    assert summary != raw, "Summary identical to input — passthrough detected"

    # RAG must not echo resume text
    rag = resume.get("rag", {})
    if "document" in rag:
        assert raw not in rag["document"], (
            "RAG document contains raw resume text — RAG passthrough detected"
        )


# ---------------------------------------------------------------------
# 8. Event count grows with agent count (state accumulation)
# ---------------------------------------------------------------------
@pytest.mark.integration
def test_events_accumulate_across_agents():
    out = run_workflow({"resume": "EventAccum", "jd": "CoreWeave"})
    events = out["events"]

    assert len(events) >= 4, (
        f"Not enough events to reflect multi-agent execution: {events}"
    )
