from l1_drafting_reasoner import DraftingReasoner
from l1_rag_reasoner import RAGReasoner
from l1_strategy_reasoner import StrategyReasoner
from prompt_envelope import PromptEnvelope
from l4_memory_manager import MemoryManager


def test_l1_plans_include_injection_framing():
    state = {"objective": "demo"}
    reasoners = [StrategyReasoner(), RAGReasoner(), DraftingReasoner()]

    for reasoner in reasoners:
        plan = reasoner.plan(state)
        injection = plan.get("injection_framing")

        assert injection is not None
        assert injection["global_goal"]
        assert injection["success_criteria"]
        assert injection["task_mode"]
        assert injection["scope_boundaries"]
        assert injection["cost_latency"]


def test_prompt_envelope_includes_injection_metadata():
    envelope = PromptEnvelope(framing="Test", context="Ctx")

    data = envelope.to_dict()
    injection = data["metadata"].get("injection", {})

    assert injection.get("framing", {}).get("global_goal")
    assert injection.get("framing", {}).get("success_criteria")
    assert injection.get("framing", {}).get("task_mode")
    assert injection.get("context", {}).get("untrusted_block_wrapping") is True
    assert injection.get("context", {}).get("canonicalize_inputs") is True
    assert injection.get("context", {}).get("apply_pruning_rules") is True
    assert injection.get("context", {}).get("enforce_structured_ordering") is True


def test_memory_manager_canonicalizes_without_semantic_change():
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "world"},
    ]
    state = {"messages": messages, "summary": "", "rag_history": [], "world": []}

    manager = MemoryManager()
    normalized = manager.reconcile_state(state)

    assert normalized["messages"][0]["content"] == "hello"
    assert normalized["messages"][1]["role"] == "assistant"
    assert normalized["metadata"]["context_consistency"] == "unchecked"
    assert len(normalized["messages"]) == len(messages)
