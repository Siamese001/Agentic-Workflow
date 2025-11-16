import copy

from prompt_renderer import PromptRenderer
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection
from prompt_views import (
    get_instructional_injection_types,
    get_prompt_taxonomy,
    get_section_names,
    get_section_types,
)


def test_get_section_names_reports_all_sections():
    renderer = PromptRenderer()
    renderer.render()

    section_names = get_section_names(renderer)

    assert section_names == renderer.SECTION_ORDER
    assert set(section_names) == {section.value for section in PromptSection}


def test_get_section_types_returns_taxonomy_mapping():
    renderer = PromptRenderer()
    renderer.render()

    section_types = get_section_types(renderer)

    assert set(section_types.keys()) == set(renderer.SECTION_ORDER)
    for name, section_type in section_types.items():
        assert name == section_type


def test_get_instructional_injection_types_returns_all_entries():
    renderer = PromptRenderer()
    renderer.render()

    injection_types = get_instructional_injection_types(renderer)

    assert len(injection_types) == len(INSTRUCTIONAL_INJECTION_ALL)
    assert set(injection_types) == set(INSTRUCTIONAL_INJECTION_ALL)


def test_get_prompt_taxonomy_returns_full_metadata():
    renderer = PromptRenderer()
    renderer.render()

    expected_metadata = renderer.get_last_render_metadata()
    taxonomy = get_prompt_taxonomy(renderer)

    assert taxonomy == expected_metadata


def test_prompt_views_are_read_only():
    renderer = PromptRenderer()
    renderer.render()

    original_metadata = copy.deepcopy(renderer.get_last_render_metadata())

    _ = get_section_names(renderer)
    _ = get_section_types(renderer)
    _ = get_instructional_injection_types(renderer)
    _ = get_prompt_taxonomy(renderer)

    assert renderer.get_last_render_metadata() == original_metadata
