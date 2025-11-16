import pytest

from prompt_renderer import PromptRenderer
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection, SECTION_ORDER


@pytest.fixture
def renderer():
    return PromptRenderer()


def test_render_metadata_sections(renderer):
    renderer.render()
    metadata = renderer.get_last_render_metadata()

    assert set(metadata.keys()) == set(renderer.SECTION_ORDER)
    for section in renderer.SECTION_ORDER:
        assert metadata[section]["section_type"] == section
        assert metadata[section]["instructional_injection_types"] == INSTRUCTIONAL_INJECTION_ALL


def test_render_metadata_contains_all_instructional_injections(renderer):
    renderer.render()
    metadata = renderer.get_last_render_metadata()

    for section in renderer.SECTION_ORDER:
        assert len(metadata[section]["instructional_injection_types"]) == len(INSTRUCTIONAL_INJECTION_ALL)
        assert set(metadata[section]["instructional_injection_types"]) == set(INSTRUCTIONAL_INJECTION_ALL)


def test_render_output_unchanged(renderer):
    rendered = renderer.render()
    expected = (
        "[Framing]\nYou are an orchestrator coordinating deterministic agents.\n\n"
        "[Context]\nUse the provided state to ground your response.\n\n"
        "[Reasoning]\nKeep reasoning minimal; downstream layers handle cognition.\n\n"
        "[Instructions]\nFollow the requested format and stay within scope.\n\n"
        "[Safety Signals]\nRespect safety directives from the gateway.\n\n"
        "[Output Schema]\nReturn plain text content respecting the schema."
    )
    assert rendered == expected


def test_renderer_section_order_matches_taxonomy(renderer):
    expected_order = [section.value for section in SECTION_ORDER]
    assert renderer.SECTION_ORDER == expected_order
