"""
Test Suite — End-to-End v10.8

Responsibilities:
    • Provide high-level coverage across all layers in the v10.8 architecture.
    • Validate coordinated flows from reasoning through execution, state, and safety layers.
    • Ensure prompt system integration aligns with orchestration expectations.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_rag_orchestrator import RAGOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l4_state_adapter import StateAdapter


def test_end_to_end_control_flow():
    adapter = StateAdapter()

    rag = RAGOrchestrator(state_adapter=adapter)
    rag_result = rag.orchestrate({"objective": "collect research"})

    draft = DraftOrchestrator(state_adapter=adapter)
    draft_result = draft.orchestrate({"objective": "summarize research", "tone": "neutral"})

    bullets = BulletOrchestrator(state_adapter=adapter)
    bullet_result = bullets.orchestrate({"deliverables": ["summary", "actions"]})

    qa = QAOrchestrator(state_adapter=adapter)
    qa_result = qa.orchestrate(adapter.state)

    assert rag_result.state["last_retrieval"]["status"] == "completed"
    assert "draft" in draft_result.state
    assert bullet_result.state["messages"]
    assert qa_result.state["safety_gateway"]["status"] == "allowed"
