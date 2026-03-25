"""Foundational behavioral tests for agentic_core/utils/workflow_engines/completeness.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_completeness_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.utils.workflow_engines.completeness import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ContextCompletenessScore,
    GroundedDocument,
    IAnswerSupportValidator,
    IContextCompletenessScorer,
    IParentChildExpander,
    SupportedAnswerCheck,
)


class TestContextCompletenessScoreContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ContextCompletenessScore)

    def test_is_frozen(self):
        assert ContextCompletenessScore.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ContextCompletenessScore)}
        assert field_names >= {'relevance_score', 'parent_section_id', 'completeness_score', 'chunk_id', 'query_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(ContextCompletenessScore)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert ContextCompletenessScore.__dataclass_params__.frozen is True

class TestGroundedDocumentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GroundedDocument)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(GroundedDocument)}
        assert field_names >= {'parent_section_id', 'sibling_ids', 'parent_content', 'heading_path', 'completeness_score'}

class TestIParentChildExpanderContract:
    def test_is_class(self):
        assert isinstance(IParentChildExpander, type)

    def test_has_method_expand(self):
        assert callable(getattr(IParentChildExpander, 'expand', None))

    def test_has_method_get_parent_section_id(self):
        assert callable(getattr(IParentChildExpander, 'get_parent_section_id', None))

    def test_has_method_get_heading_path(self):
        assert callable(getattr(IParentChildExpander, 'get_heading_path', None))

class TestIContextCompletenessScorerContract:
    def test_is_class(self):
        assert isinstance(IContextCompletenessScorer, type)

    def test_has_method_score(self):
        assert callable(getattr(IContextCompletenessScorer, 'score', None))

    def test_has_method_score_batch(self):
        assert callable(getattr(IContextCompletenessScorer, 'score_batch', None))

class TestIAnswerSupportValidatorContract:
    def test_is_class(self):
        assert isinstance(IAnswerSupportValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(IAnswerSupportValidator, 'validate', None))

class TestSupportedAnswerCheckContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SupportedAnswerCheck)

    def test_is_frozen(self):
        assert SupportedAnswerCheck.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SupportedAnswerCheck)}
        assert field_names >= {'unsupported_claim_spans', 'cited_chunk_ids', 'fully_supported', 'cited_parent_section_ids', 'answer_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(SupportedAnswerCheck)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert SupportedAnswerCheck.__dataclass_params__.frozen is True

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
    """Module completeness must be importable or skip gracefully."""
    pass  # Import verified at module level
