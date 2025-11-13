"""Unit tests covering MessageArchitect planning and composition."""
from types import SimpleNamespace
from unittest.mock import patch

from src.lic_agentic.agents.k3_message_architect import DraftPackage, MessageArchitect
from src.lic_agentic.rag.content_store import ContentStore
from src.lic_agentic.rag.retrieval_planner import RetrievalJob
from src.lic_agentic.rag.tool_registry import BaseTool, ToolRegistry, ToolResult
from src.lic_agentic.reasoning.toggles import ReasoningToggles


def _make_architect(lic_context, toggles: ReasoningToggles | None = None) -> MessageArchitect:
    return MessageArchitect(lic_context, toggles or ReasoningToggles())


def _build_plan(lic_context, architect: MessageArchitect, wants, sanitized):
    planner = lic_context.resolve("retrieval_planner")
    architect._configure_plan(planner, wants, sanitized)
    return planner.plan


class StaticTool(BaseTool):
    name = "static"

    def run(self, query: str, context):
        return ToolResult(f"static evidence for {query}", ["http://static"], 10, 0.99)


def test_derive_wants_falls_back_to_prompt(lic_context):
    architect = _make_architect(lic_context, ReasoningToggles())
    wants = architect._derive_wants(
        "Investigate opportunity", SimpleNamespace(company_id=None, contact_id=None)
    )
    assert wants == ["Context for: Investigate opportunity"]


def test_record_evidence_supports_cached_strings(lic_context):
    toggles = ReasoningToggles()
    registry = ToolRegistry()
    registry.register(StaticTool())
    store = ContentStore()
    architect = _make_architect(lic_context, toggles)
    architect.registry = registry
    architect.content_store = store
    sanitized = SimpleNamespace(company_id="ACME", contact_id="C1")
    plan = _build_plan(lic_context, architect, ["ACME latest milestones"], sanitized)
    job = plan.jobs[0]
    cache_key = registry.make_key(
        {"tool": job.tool, "query": job.query, "scope": job.scope}, plan.context
    )
    store.put(cache_key, "cached summary", {"tool": job.tool})
    retrievals = [("cache", job, "cached summary")]
    evidence = architect._record_evidence(retrievals, sanitized)
    assert evidence and evidence[0][1] == "cached summary"


def test_record_evidence_with_tool_result_uses_stable_ids(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    sanitized = SimpleNamespace(company_id="ACME", contact_id="C1")
    job = RetrievalJob(
        tool="web_search", query="ACME latest milestones", scope="outreach", section="value_wedge"
    )
    payload = ToolResult("Latest milestone summary", ["http://example.com"], 140, 0.75)
    evidence = architect._record_evidence([("live", job, payload)], sanitized)
    artifact_id, summary, metadata = evidence[0]
    assert artifact_id == architect._stable_artifact_id(job, sanitized.company_id)
    assert summary == "Latest milestone summary"
    assert metadata["latency_ms"] == 140


def test_compose_appends_reflexion_and_artifacts(lic_context):
    toggles = ReasoningToggles(reflexion=True)
    architect = _make_architect(lic_context, toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id="C1")
    package = architect.compose(sanitized, route_decision=None)
    assert isinstance(package, DraftPackage)
    assert "Reflexion:" in package.draft
    assert "[artifact_id:" in package.draft


def test_compose_without_company_uses_baseline_marker(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    sanitized = SimpleNamespace(prompt="", company_id=None, contact_id=None)
    package = architect.compose(sanitized, route_decision=None)
    assert package.artifacts
    assert "[artifact_id:" in package.draft


def test_build_plan_includes_profile_lookup_jobs(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id="C1")
    wants = architect._derive_wants("Hello", sanitized)
    plan = _build_plan(lic_context, architect, wants, sanitized)
    assert any(job.tool == "profile_lookup" for job in plan.jobs)
    assert plan.context["contact_id"] == "C1"
    assert plan.context["company_id"] == "ACME"


def test_stable_artifact_id_depends_on_query(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    job_a = RetrievalJob(tool="web_search", query="A", scope="outreach", section="value_wedge")
    job_b = RetrievalJob(tool="web_search", query="B", scope="outreach", section="value_wedge")
    assert architect._stable_artifact_id(job_a, "ACME") != architect._stable_artifact_id(job_b, "ACME")


def test_draft_package_with_draft_clones_artifacts():
    package = DraftPackage("Subject", {"aid": "Summary"}, 120)
    updated = package.with_draft("Subject 2")
    assert updated.draft == "Subject 2"
    assert updated.artifacts == package.artifacts
    assert updated.total_latency_ms == package.total_latency_ms


def test_score_quality_counts_reflexion_bonus():
    from src.lic_agentic.agents.k3_message_architect import score_quality

    assert score_quality("Value for you", reflexion=True) > score_quality("Value for you", reflexion=False)


def test_select_tool_for_news_queries(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    assert architect._select_tool_for_want("ACME news update") == "news"
    assert architect._select_tool_for_want("Profile insights") == "profile_lookup"
    assert architect._select_tool_for_want("Generic want") == "web_search"


def test_compose_falls_back_to_baseline_artifacts(lic_context):
    toggles = ReasoningToggles()
    architect = _make_architect(lic_context, toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id=None)

    with patch.object(MessageArchitect, "_record_evidence", return_value=[]):
        package = architect.compose(sanitized, route_decision=None)

    assert package.artifacts == {"baseline": "Value proposition here."}
