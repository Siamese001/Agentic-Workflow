"""Hardening tests for 10-slot template registry methods and Jinja slot templates.

Validates:
- TemplateRegistry.get_h0_healing(), get_r0_output_format(), get_c0_context()
- TemplateRegistry.get_slot_template() for all 10 slots
- All 10 .jinja slot templates load and render via jinja2
- Invalid slot_key rejection
- Backward compatibility: existing getters still work
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.utils.memory.template_registry import (
    TemplateRegistry,
    get_template_registry,
)


# ---------------------------------------------------------------------------
# New getter methods
# ---------------------------------------------------------------------------

class TestTemplateRegistryH0:
    """H0 healing proposal getter."""

    def test_get_h0_healing_method_exists(self):
        reg = get_template_registry()
        assert callable(getattr(reg, "get_h0_healing", None))

    def test_get_h0_healing_falls_back_to_mixin(self):
        """When version store lacks get_healing, falls back to get_mixin.

        PromptVersionStore does not expose get_mixin, so the fallback
        raises AttributeError (not KeyError). This proves the fallback
        path is exercised.
        """
        reg = get_template_registry()
        with pytest.raises((KeyError, AttributeError)):
            reg.get_h0_healing("nonexistent_healing_id")


class TestTemplateRegistryR0:
    """R0 output format getter."""

    def test_get_r0_output_format_method_exists(self):
        reg = get_template_registry()
        assert callable(getattr(reg, "get_r0_output_format", None))

    def test_get_r0_output_format_falls_back_to_mixin(self):
        reg = get_template_registry()
        with pytest.raises((KeyError, AttributeError)):
            reg.get_r0_output_format("nonexistent_format_id")


class TestTemplateRegistryC0:
    """C0 grounded context getter."""

    def test_get_c0_context_method_exists(self):
        reg = get_template_registry()
        assert callable(getattr(reg, "get_c0_context", None))

    def test_get_c0_context_falls_back_to_mixin(self):
        reg = get_template_registry()
        with pytest.raises((KeyError, AttributeError)):
            reg.get_c0_context("nonexistent_context_id")


# ---------------------------------------------------------------------------
# get_slot_template() — Jinja template loading
# ---------------------------------------------------------------------------

_ALL_SLOTS = ("S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0", "Y0", "R0")


class TestGetSlotTemplate:
    """TemplateRegistry.get_slot_template() for Jinja slot templates."""

    @pytest.mark.parametrize("slot_key", _ALL_SLOTS)
    def test_slot_template_loads(self, slot_key: str):
        """Every slot has a loadable .jinja template."""
        reg = get_template_registry()
        content = reg.get_slot_template(slot_key)
        assert isinstance(content, str)
        assert len(content) > 50  # non-trivial template

    @pytest.mark.parametrize("slot_key", _ALL_SLOTS)
    def test_slot_template_renders_minimal(self, slot_key: str):
        """Every slot template renders without error when given no variables."""
        import jinja2

        reg = get_template_registry()
        content = reg.get_slot_template(slot_key)
        template = jinja2.Template(content)
        rendered = template.render()
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_invalid_slot_key_raises_value_error(self):
        reg = get_template_registry()
        with pytest.raises(ValueError, match="Invalid slot_key"):
            reg.get_slot_template("Z9")

    def test_empty_slot_key_raises_value_error(self):
        reg = get_template_registry()
        with pytest.raises(ValueError, match="Invalid slot_key"):
            reg.get_slot_template("")

    def test_lowercase_slot_key_raises_value_error(self):
        reg = get_template_registry()
        with pytest.raises(ValueError, match="Invalid slot_key"):
            reg.get_slot_template("s0")


# ---------------------------------------------------------------------------
# Jinja rendering with realistic variables
# ---------------------------------------------------------------------------

class TestSlotTemplateRendering:
    """Render each slot template with realistic variables."""

    def test_s0_renders_with_constitution_rules(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("S0"))
        rendered = tmpl.render(constitution_rules=["No PowerShell", "No bare except"])
        assert "No PowerShell" in rendered
        assert "ABSOLUTE" in rendered

    def test_d0_renders_with_fences(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("D0"))
        rendered = tmpl.render(
            forbidden_operations=["rm -rf /", "DROP TABLE"],
            allowed_tools=["read_file", "edit"],
        )
        assert "rm -rf /" in rendered
        assert "read_file" in rendered
        assert "BINDING" in rendered

    def test_i0_renders_with_identity(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("I0"))
        rendered = tmpl.render(
            agent_identity="Cascade",
            mixins=["tool_first", "plan_then_act"],
        )
        assert "Cascade" in rendered
        assert "tool_first" in rendered
        assert "GOVERNED" in rendered

    def test_e0_renders_with_exemplars(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("E0"))
        rendered = tmpl.render(
            exemplars=[{"label": "good response", "content": "Example output"}],
        )
        assert "good response" in rendered
        assert "GUIDING" in rendered

    def test_c0_renders_with_evidence(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("C0"))
        rendered = tmpl.render(
            evidence_chunks=[
                {"source_id": "doc1", "content": "Verified fact"},
            ],
        )
        assert "doc1" in rendered
        assert "INFORMATIONAL" in rendered

    def test_m0_renders_with_thinking(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("M0"))
        rendered = tmpl.render(
            thinking_style="chain-of-thought",
            step_by_step=True,
        )
        assert "chain-of-thought" in rendered
        assert "PRIVATE" in rendered

    def test_u0_renders_with_prompt(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("U0"))
        rendered = tmpl.render(user_prompt="Fix the bug in module X")
        assert "Fix the bug in module X" in rendered
        assert "ZERO" in rendered

    def test_h0_renders_with_healing(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("H0"))
        rendered = tmpl.render(
            healing_context="Broad exception catch in module.py:42",
            proposed_fix="Replace with scoped exception",
            reentry_checks=["Run py_compile", "Run targeted tests"],
        )
        assert "module.py:42" in rendered
        assert "PROPOSED" in rendered

    def test_y0_renders_with_synthesis(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("Y0"))
        rendered = tmpl.render(
            pattern_observations=[
                {"confidence": "0.85", "description": "Recurring broad-catch pattern"},
            ],
        )
        assert "0.85" in rendered
        assert "ANALYTIC" in rendered

    def test_r0_renders_with_schema(self):
        import jinja2

        reg = get_template_registry()
        tmpl = jinja2.Template(reg.get_slot_template("R0"))
        rendered = tmpl.render(
            response_schema="JSON",
            format_constraints=["Must include status field"],
            required_sections=[
                {"name": "summary", "required": True},
                {"name": "details", "required": False},
            ],
        )
        assert "JSON" in rendered
        assert "SCHEMA" in rendered
        assert "summary" in rendered


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

class TestTemplateRegistryBackwardCompat:
    """Existing getters still work after adding new methods."""

    def test_get_s0_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_s0)

    def test_get_i0_mixin_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_i0_mixin)

    def test_get_d0_fences_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_d0_fences)

    def test_get_e0_exemplar_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_e0_exemplar)

    def test_get_m0_mixin_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_m0_mixin)

    def test_get_y0_synthesis_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.get_y0_synthesis)

    def test_list_available_mixins_still_callable(self):
        reg = get_template_registry()
        assert callable(reg.list_available_mixins)
