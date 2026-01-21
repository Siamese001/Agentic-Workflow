"""E2E check that value claims include evidence anchors."""

from __future__ import annotations

from types import SimpleNamespace

from src.lic_agentic.agents.k3_message_architect import MessageArchitect
from src.lic_agentic.reasoning.toggles import ReasoningToggles


def extract_artifact_markers(draft: str) -> list[str]:
    return [line for line in draft.splitlines() if line.startswith("[artifact_id:")]


def test_value_claims_are_anchored():
    toggles = ReasoningToggles()
    architect = MessageArchitect(toggles)
    sanitized = SimpleNamespace(
        prompt="Update on strategic wins", company_id="ACME", contact_id="C1"
    )

    plan = architect._build_plan(
        ["ACME latest milestones", "ACME recent news", "C1 profile highlights"], sanitized
    )
    plan.dedupe()
    plan.budget(max_calls=6)
    outcomes = plan.execute(architect.tool_registry, architect.content_store)
    expected_markers = len(outcomes)

    package = architect.compose(sanitized, route_decision=None)
    markers = extract_artifact_markers(package.draft)

    assert markers, "Expected at least one artifact marker in the draft"
    assert len(markers) == expected_markers
