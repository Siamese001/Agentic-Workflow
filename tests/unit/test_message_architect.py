from types import SimpleNamespace

from src.lic_agentic.agents.k3_message_architect import MessageArchitect
from src.lic_agentic.rag.content_store import ContentStore
from src.lic_agentic.rag.tool_registry import ToolRegistry, BaseTool, ToolResult
from src.lic_agentic.reasoning.toggles import ReasoningToggles


class StaticTool(BaseTool):
    name = "static"

    def run(self, query: str, context):
        return ToolResult(f"static evidence for {query}", ["http://static"], 10, 0.99)


def test_derive_wants_falls_back_to_prompt():
    architect = MessageArchitect(ReasoningToggles())
    wants = architect._derive_wants("Investigate opportunity", SimpleNamespace(company_id=None, contact_id=None))
    assert wants == ["Context for: Investigate opportunity"]


def test_record_evidence_supports_cached_strings():
    toggles = ReasoningToggles()
    registry = ToolRegistry()
    registry.register(StaticTool())
    store = ContentStore()
    architect = MessageArchitect(toggles, tool_registry=registry, content_store=store)
    sanitized = SimpleNamespace(company_id="ACME", contact_id="C1")
    plan = architect._build_plan(["ACME latest milestones"], sanitized)
    job = plan.jobs[0]
    cache_key = registry.make_key({"tool": job.tool, "query": job.query, "scope": job.scope}, plan.context)
    store.put(cache_key, "cached summary", {"tool": job.tool})
    retrievals = [("cache", job, "cached summary")]
    evidence, latency = architect._record_evidence(retrievals, sanitized)
    assert evidence and evidence[0][1] == "cached summary"
    assert latency == 0


def test_compose_appends_reflexion_and_artifacts():
    toggles = ReasoningToggles(reflexion=True)
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id="C1")
    package = architect.compose(sanitized, route_decision=None)
    assert "Reflexion:" in package.draft
    assert "[artifact_id:" in package.draft
    assert package.artifacts


def test_compose_without_company_uses_baseline_marker():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="", company_id=None, contact_id=None)
    package = architect.compose(sanitized, route_decision=None)
    assert "[artifact_id:baseline]" in package.draft
    assert package.artifacts == {"baseline": "Value proposition here."}
