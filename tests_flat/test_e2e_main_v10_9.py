import asyncio
import importlib
import sys
import types

import pytest


def _ensure_stub(module_name: str, **attrs):
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        mod = types.ModuleType(module_name)
        sys.modules[module_name] = mod
    for name, value in attrs.items():
        if not hasattr(mod, name):
            setattr(mod, name, value)
    sys.modules[module_name] = mod


class _DummyAgent:
    def __init__(self, *_args, **_kwargs):
        self.called = True

    async def __call__(self, state):
        return state


class _DummyAdapter:
    def apply_patch(self, state, patch):
        merged = dict(state)
        merged.update(patch)
        return merged


# Provide stubs for optional dependencies.
_ensure_stub("l1_strategy_reasoner", StrategyReasoner=_DummyAgent)
_ensure_stub("l2_bullet_execution", BulletExecutionAgent=_DummyAgent)
_ensure_stub("l2_drafting_execution", DraftExecutionAgent=_DummyAgent)
_ensure_stub("l2_qa_validation", QAValidationAgent=_DummyAgent)
_ensure_stub("l2_rag_execution", RAGExecutionAgent=_DummyAgent)
_ensure_stub("l4_state", StateAdapter=_DummyAdapter)
_ensure_stub("l5_constitutional_engine", ConstitutionalEngine=_DummyAgent)
_ensure_stub("l5_safety_gateway", SafetyGateway=_DummyAgent)
_ensure_stub("prompt_builder_stack", PromptBuilderStack=_DummyAgent)
_ensure_stub("prompt_renderer_stack", PromptRendererStack=_DummyAgent)

# Provide a minimal langgraph stub for test environments without the dependency.
if "langgraph.graph" not in sys.modules:
    langgraph = types.ModuleType("langgraph")
    graph_mod = types.ModuleType("langgraph.graph")

    class DummyApp:
        def __init__(self, nodes):
            self.nodes = nodes

        async def astream_events(self, initial_state, version: str = "v1"):
            yield {"event": "on_graph_start"}
            current_state = initial_state
            for func in self.nodes.values():
                if asyncio.iscoroutinefunction(func):
                    current_state = await func(current_state)
                else:
                    current_state = func(current_state)
            yield {"event": "on_graph_end", "data": {"payload": current_state}}

    class StateGraph:
        def __init__(self, *_args, **_kwargs):
            self.nodes = {}

        def add_node(self, name, func):
            self.nodes[name] = func

        def add_edge(self, *_args, **_kwargs):
            return None

        def add_conditional_edges(self, *_args, **_kwargs):
            return None

        def compile(self, checkpointer=None):
            return DummyApp(self.nodes)

    graph_mod.StateGraph = StateGraph
    graph_mod.START = "start"
    graph_mod.END = "end"
    sys.modules["langgraph"] = langgraph
    sys.modules["langgraph.graph"] = graph_mod

from agent_orchestration_v10_7 import OrchestrationContext, get_graph_app, unwrap_node_result
from agent_stacks_v10_8.state_adapter_stack import MainGraphState


def test_e2e_workflow_runs_with_stubbed_nodes(monkeypatch, sample_job_input, sample_master_resume, config_v10_7):
    async def _run():
        context = OrchestrationContext(config_v10_7)

        def _stub_node(state, *_args, **_kwargs):
            data = state.to_dict() if hasattr(state, "to_dict") else dict(state)
            data.setdefault("draft", {"sections": ["summary"]})
            data.setdefault("qa", {"qa_passed": True, "issues": []})
            artifacts = data.get("artifacts") or {}
            artifacts.setdefault(
                "final_resume",
                {"name": data.get("resume", {}).get("name", ""), "sections": data["draft"]["sections"]},
            )
            data["artifacts"] = artifacts
            return MainGraphState.from_dict(data)

        for node_name in [
            "run_sanitize_pii",
            "run_detect_prompt_injection",
            "run_bias_check",
            "run_classify_complexity",
            "run_strategy_plan",
            "run_ambiguity_check",
            "hil_pause_node",
            "run_feedback_routing",
            "run_reconciliation",
            "run_hil_edit_injection",
            "run_prepare_parallel",
            "run_prompt_builder",
            "run_prompt_renderer",
            "run_rag_plan",
            "run_rag_exec",
            "run_join_prompt_and_rag",
            "run_bullet_plan",
            "run_bullet_exec",
            "run_draft_plan",
            "run_draft_exec",
            "run_qa_validation",
            "run_constitutional_review",
            "run_finalize",
        ]:
            monkeypatch.setattr("agent_orchestration_v10_7." + node_name, _stub_node)

        initial_state = MainGraphState.from_dict(
            {"job": sample_job_input, "resume": sample_master_resume, "hil": {"enabled": False}}
        ).to_dict()
        app = get_graph_app(checkpointer=None, config=config_v10_7, context=context)

        final_state = None
        async for event in app.astream_events(initial_state, version="v1"):
            if event.get("event") == "on_graph_end":
                payload = event.get("data") or {}
                final_state = unwrap_node_result(payload)

        assert final_state is not None
        assert final_state.get("draft", {}).get("sections")
        assert "qa_passed" in final_state.get("qa", {})
        assert isinstance(final_state.get("qa", {}).get("issues"), list)
        assert isinstance(final_state.get("artifacts", {}).get("final_resume"), dict)

    asyncio.get_event_loop().run_until_complete(_run())
