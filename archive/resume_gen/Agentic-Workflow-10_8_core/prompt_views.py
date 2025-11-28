"""Read-only helper functions for inspecting prompt render metadata."""

from __future__ import annotations


def get_section_names(renderer):
    """Return the ordered list of section names from the last render."""

    meta = renderer.get_last_render_metadata()
    return list(meta.keys())


def get_section_types(renderer):
    """Return a mapping of section name to section type."""

    meta = renderer.get_last_render_metadata()
    return {k: v.get("section_type", "") for k, v in meta.items()}


def get_instructional_injection_types(renderer):
    """Return the instructional injection types for the first section."""

    meta = renderer.get_last_render_metadata()
    if not meta:
        return []
    first_key = next(iter(meta))
    return meta[first_key].get("instructional_injection_types", [])


def get_prompt_taxonomy(renderer):
    """Return the full render metadata map."""

    return renderer.get_last_render_metadata()
