from core_v10_7.services import PromptTemplateManager
from prompt_builder import _format_prompt_with_defaults


def test_format_prompt_injects_governance_fields():
    prompt = _format_prompt_with_defaults("body text", goal_state="deliver", top_failures="none")
    assert "Goal State: deliver" in prompt
    assert "Top Failures: none" in prompt
    assert "body text" in prompt


def test_prompt_template_manager_returns_injection_wrapped_template():
    manager = PromptTemplateManager()
    template = manager.get_template("default")
    assert "{goal_state}" in template
    assert "{top_failures}" in template
    rendered = manager.render("default", goal_state="ship", top_failures="late", body="content")
    assert "ship" in rendered and "late" in rendered and "content" in rendered
