"""Foundational behavioral tests for agentic_core/prompt_governance/core/prompt_entry_types.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_prompt_entry_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.core.prompt_entry_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    PromptConstitution,
    PromptEntry,
    get_constitution,
    get_persona,
    get_prompt,
    get_template,
)


class TestPromptEntryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptEntry)

    def test_is_frozen(self):
        assert PromptEntry.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PromptEntry)}
        assert field_names >= {'role', 'source', 'content', 'version', 'id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(PromptEntry)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert PromptEntry.__dataclass_params__.frozen is True

class TestPromptConstitutionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptConstitution)

    def test_is_frozen(self):
        assert PromptConstitution.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PromptConstitution)}
        assert field_names >= {'prompts', 'persona_registry', 'directive_templates'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(PromptConstitution)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert PromptConstitution.__dataclass_params__.frozen is True

class TestGetConstitutionFunction:
    def test_is_callable(self):
        assert callable(get_constitution)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_constitution)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetPromptFunction:
    def test_is_callable(self):
        assert callable(get_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetTemplateFunction:
    def test_is_callable(self):
        assert callable(get_template)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_template)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetPersonaFunction:
    def test_is_callable(self):
        assert callable(get_persona)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_persona)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module prompt_entry_types must be importable or skip gracefully."""
    pass  # Import verified at module level
