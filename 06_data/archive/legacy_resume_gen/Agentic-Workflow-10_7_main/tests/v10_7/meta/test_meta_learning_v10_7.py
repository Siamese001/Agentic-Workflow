import json
from types import SimpleNamespace

import json

import pytest

from core_v10_7 import ConfigV10_7
from run_learning_v10_7 import (
    AsyncToolCritiqueAgent,
    AsyncToolGeneratorAgent,
    HotReloadRuleManager,
    _read_log_tail,
    run_meta_learning,
)


class StubLLMClient:
    def __init__(self, payload: dict):
        self.payload = payload

    async def chat_completion_async(self, *_, **__):
        return {"content": json.dumps(self.payload)}


@pytest.mark.asyncio
async def test_meta_learning_exits_when_disabled(caplog):
    config = ConfigV10_7("master_config_v10_7.json")
    config.meta_loop_config.enable_meta_learning = False
    caplog.set_level("INFO")

    await run_meta_learning(config)

    assert any("Meta-learning disabled" in rec.message for rec in caplog.records)


def test_meta_learning_reads_logs_and_writes_rules(tmp_path):
    log_path = tmp_path / "feedback.log"
    log_path.write_text(json.dumps({"event": "failure"}) + "\n")
    tail, count = _read_log_tail(str(log_path))
    assert "failure" in tail
    assert count == 1

    rules_path = tmp_path / "rules.jsonl"
    manager = HotReloadRuleManager(str(rules_path))
    rule = {"type": "rule_change", "description": "Add QA guard", "config_changes": {}}
    assert manager.write_proposed_rule(rule, confidence=0.95)
    contents = rules_path.read_text().strip().splitlines()
    assert contents


@pytest.mark.asyncio
async def test_meta_learning_generates_and_critiques_tools(workflow_context):
    generator_payload = {"tool_code": "def tool():\n    pass", "tool_name": "AutoTool"}
    workflow_context.get_model_client = lambda *_, **__: StubLLMClient(generator_payload)

    generator = AsyncToolGeneratorAgent(workflow_context)
    gen_output = await generator.run_async({"id": "hyp-1"}, workflow_id="wf-meta")
    assert gen_output["generated_tool_code"]
    assert gen_output["generated_tool_name"]

    critique_payload = {"critique_passed": True, "notes": []}
    workflow_context.get_model_client = lambda *_, **__: StubLLMClient(critique_payload)

    critique_agent = AsyncToolCritiqueAgent(workflow_context)
    critique = await critique_agent.run_async(gen_output["generated_tool_code"], workflow_id="wf-meta")
    assert critique.get("critique_passed") is True
