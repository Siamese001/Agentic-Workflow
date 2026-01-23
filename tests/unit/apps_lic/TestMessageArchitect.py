"""Unit tests covering MessageArchitect planning and composition."""


class StaticTool(BaseTool):
    name = "static"

    def run(self, query: str, context):
        return ToolResult(f"static evidence for {query}", ["http://static"], 10, 0.99)


def test_derive_wants_falls_back_to_prompt():
    architect = MessageArchitect(ReasoningToggles())
    wants = architect._derive_wants(
        "Investigate opportunity", SimpleNamespace(company_id=None, contact_id=None)
    )
    assert wants == ["Context for: Investigate opportunity"]


def test_record_evidence_supports_cached_strings():
    toggles = ReasoningToggles()
    registry = tool_registry()
    registry.register(StaticTool())
    store = ContentStore()
    architect = MessageArchitect(toggles, tool_registry=registry, content_store=store)
    sanitized = SimpleNamespace(company_id="ACME", contact_id="C1")
    plan = architect._build_plan(["ACME latest milestones"], sanitized)
    job = plan.jobs[0]
    cache_key = registry.make_key(
        {"tool": job.tool, "query": job.query, "scope": job.scope}, plan.context
    )
    store.put(cache_key, "cached summary", {"tool": job.tool})
    retrievals = [("cache", job, "cached summary")]
    evidence = architect._record_evidence(retrievals, sanitized)
    assert evidence and evidence[0][1] == "cached summary"


def test_record_evidence_with_tool_result_uses_stable_ids():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
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


def test_compose_appends_reflexion_and_artifacts():
    toggles = ReasoningToggles(reflexion=True)
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id="C1")
    package = architect.compose(sanitized, route_decision=None)
    assert isinstance(package, DraftPackage)
    assert "Reflexion:" in package.draft
    assert "[artifact_id:" in package.draft


def test_compose_without_company_uses_baseline_marker():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="", company_id=None, contact_id=None)
    package = architect.compose(sanitized, route_decision=None)
    assert package.artifacts
    assert "[artifact_id:" in package.draft


def test_build_plan_includes_profile_lookup_jobs():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id="C1")
    wants = architect._derive_wants("Hello", sanitized)
    plan = architect._build_plan(wants, sanitized)
    assert any(job.tool == "profile_lookup" for job in plan.jobs)
    assert plan.context["contact_id"] == "C1"
    assert plan.context["company_id"] == "ACME"


def test_stable_artifact_id_depends_on_query():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    job_a = RetrievalJob(tool="web_search", query="A", scope="outreach", section="value_wedge")
    job_b = RetrievalJob(tool="web_search", query="B", scope="outreach", section="value_wedge")
    assert architect._stable_artifact_id(job_a, "ACME") != architect._stable_artifact_id(
        job_b, "ACME"
    )


def test_draft_package_with_draft_clones_artifacts():
    package = DraftPackage("Subject", {"aid": "Summary"}, 120)
    updated = package.with_draft("Subject 2")
    assert updated.draft == "Subject 2"
    assert updated.artifacts == package.artifacts
    assert updated.total_latency_ms == package.total_latency_ms


def test_score_quality_counts_reflexion_bonus():
    assert score_quality("Value for you", reflexion=True) > score_quality(
        "Value for you", reflexion=False
    )


def test_select_tool_for_news_queries():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    assert architect._select_tool_for_want("ACME news update") == "news"
    assert architect._select_tool_for_want("Profile insights") == "profile_lookup"
    assert architect._select_tool_for_want("Generic want") == "web_search"


def test_compose_falls_back_to_baseline_artifacts():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(prompt="Hello", company_id="ACME", contact_id=None)

    class EmptyPlan:
        jobs = []

        def __init__(self):
            self.context = {}

        def dedupe(self):
            return None

        def budget(self, *_args, **_kwargs):
            return None

        def execute(self, *_args, **_kwargs):
            return []

    with patch.object(MessageArchitect, "_build_plan", return_value=EmptyPlan()):
        package = architect.compose(sanitized, route_decision=None)

    assert package.artifacts == {"baseline": "Value proposition here."}
