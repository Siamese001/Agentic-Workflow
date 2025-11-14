from types import SimpleNamespace
from typing import Any, Dict

from typing import Any, Dict

import pytest
import stacks_v10_7.drafting as drafting_module
from agent_tools_v10_7 import EvidenceBriefAssemblerTool, EvidenceClarificationTool
from stacks_v10_7.drafting import DraftingGuildCoordinator


@pytest.fixture
def strategy_payload() -> Dict[str, Any]:
    return {
        "strategy_name": "AI Trailblazer",
        "focus_areas": ["automation", "scalability"],
        "key_achievements_to_highlight": ["Scaled platform adoption"],
        "tone": "executive",
    }


@pytest.fixture
def guild_coordinator(workflow_context, monkeypatch):
    original_dumps = drafting_module.json.dumps

    def safe_dumps(obj, *args, **kwargs):
        def default_serializer(value):
            if hasattr(value, "model_dump"):
                return value.model_dump()
            if hasattr(value, "__dict__"):
                return {k: v for k, v in value.__dict__.items() if not k.startswith("__")}
            return str(value)

        kwargs.setdefault("default", default_serializer)
        return original_dumps(obj, *args, **kwargs)

    monkeypatch.setattr(drafting_module.json, "dumps", safe_dumps)

    async def fake_clarification(self, tool_input, workflow_id):
        return {
            "request_id": "clar-1",
            "recipient": tool_input.get("recipient", "rag_team"),
            "questions": tool_input.get("questions", []),
            "priority": tool_input.get("priority", "normal"),
            "context_summary": tool_input.get("context_summary", ""),
        }

    async def fake_brief(self, tool_input, workflow_id):
        return {
            "section": tool_input.get("section", "summary"),
            "brief": tool_input.get("draft_content", ""),
            "key_points": tool_input.get("evidence_points", []),
            "outstanding_questions": tool_input.get("open_questions", []),
            "citations": [],
        }

    monkeypatch.setattr(EvidenceClarificationTool, "run_async", fake_clarification)
    monkeypatch.setattr(EvidenceBriefAssemblerTool, "run_async", fake_brief)

    clar_validator = staticmethod(lambda data: SimpleNamespace(model_dump=lambda: data))
    brief_validator = staticmethod(lambda data: SimpleNamespace(model_dump=lambda: data))
    monkeypatch.setattr(
        EvidenceClarificationTool.ClarificationRequestOutput,
        "model_validate",
        clar_validator,
    )
    monkeypatch.setattr(
        EvidenceBriefAssemblerTool.EvidenceBriefOutput,
        "model_validate",
        brief_validator,
    )

    def simple_merge(self, *layers):
        merged: Dict[str, Any] = {}
        for layer in layers:
            for key, value in layer.items():
                merged[key] = value
        return merged

    monkeypatch.setattr(DraftingGuildCoordinator, "_merge_sections", simple_merge)
    return DraftingGuildCoordinator(workflow_context)


@pytest.mark.asyncio
async def test_drafting_guild_produces_sections(guild_coordinator, strategy_payload):
    coordinator = guild_coordinator
    task_context = {
        "bullets": [
            {"text": "Led AI migration", "experience": {"company": "ACME", "title": "VP"}},
            {"text": "Improved margins 12%", "experience": {"company": "ACME", "title": "VP", "years": 3}},
        ],
        "strategy": strategy_payload,
        "resume": {"summary": "Seasoned operator"},
    }

    result = await coordinator.run_async(task_context, workflow_id="wf-draft")

    assert "summary" in result["final_output"]
    assert "experience" in result["final_output"]
    assert result["overall_status"] in {"pass", "review", "revise"}


@pytest.mark.asyncio
async def test_drafting_guild_respects_style_overrides(guild_coordinator, strategy_payload):
    coordinator = guild_coordinator
    task_context = {
        "bullets": [
            {"text": "Launch new GTM", "experience": {"company": "Globex", "title": "Director"}},
        ],
        "strategy": strategy_payload,
        "resume": {"summary": "Builder"},
    }

    result, _ = await coordinator._execute_guild(
        task_context,
        workflow_id="wf-override",
        overrides={"boost_metrics": True, "expand_summary": True},
    )

    entries = result["final_output"]["experience"]["entries"]
    assert entries
    assert "+ quantified impact" in entries[0]["bullet"]
    summary_points = result["final_output"]["summary"].get("evidence_points", [])
    assert summary_points and any("Launch" in p for p in summary_points)


@pytest.mark.asyncio
async def test_drafting_guild_handles_empty_bullets_gracefully(guild_coordinator, strategy_payload):
    coordinator = guild_coordinator
    task_context = {"bullets": [], "strategy": strategy_payload, "resume": {}}

    result = await coordinator.run_async(task_context, workflow_id="wf-empty")

    assert "final_output" in result
    assert "summary" in result["final_output"]
    assert result["final_output"]["experience"]["entries"] == []
