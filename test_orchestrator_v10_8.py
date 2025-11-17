"""
Test Suite — Orchestrators v10.8

Responsibilities:
    • Cover orchestration logic across graph, RAG, draft, bullet, and QA orchestrators.
    • Validate intent routing between L1 reasoners and L2 execution agents.
    • Ensure state and safety integration points are respected throughout control flow.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from l3_bullet_orchestrator import BulletOrchestrator
from l3_draft_orchestrator import DraftOrchestrator
from l3_qa_orchestrator import QAOrchestrator
from l3_rag_orchestrator import RAGOrchestrator


def test_bullet_orchestrator_sequences_calls():
    orchestrator = BulletOrchestrator()
    result = orchestrator.orchestrate({"objective": "share highlights", "deliverables": ["alpha"]})

    assert result.plan["mode"] == "strategy"
    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.state["messages"]
    assert "safety_gateway" in result.state


def test_rag_orchestrator_runs_end_to_end():
    orchestrator = RAGOrchestrator()
    result = orchestrator.orchestrate({"objective": "collect"})

    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.execution_patch["last_retrieval"]["status"] == "completed"
    assert result.safety_patch["safety_gateway"]["status"] == "allowed"


def test_draft_orchestrator_integrates_safety():
    orchestrator = DraftOrchestrator()
    result = orchestrator.orchestrate({"objective": "compose", "tone": "warm"})

    assert result.plan["mode"] == "drafting"
    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.state.get("draft", {}).get("tone") == "warm"
    assert "safety_gateway" in result.state


def test_qa_orchestrator_validates_state():
    orchestrator = QAOrchestrator()
    result = orchestrator.orchestrate({"messages": [{"role": "assistant", "content": "draft"}]})

    assert result.plan["routing"]["complexity"] == "medium"
    assert result.plan["routing"]["latency_target"] == 2.0
    assert result.plan["routing"]["cost_ceiling"] == 0.02
    assert result.plan["routing"]["risk_level"] == "normal"
    assert result.execution_patch["qa_report"]["checks"]
    assert result.state["safety_gateway"]["status"] == "allowed"
