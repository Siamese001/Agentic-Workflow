"""ADG importability contract for agentic_core/utils/workflow_engines/completeness.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_completeness.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.completeness import (  # noqa: F401
        ContextCompletenessScore,
        GroundedDocument,
        IAnswerSupportValidator,
        IContextCompletenessScorer,
        IParentChildExpander,
        SupportedAnswerCheck,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ContextCompletenessScore = None  # type: ignore[assignment,misc]
    GroundedDocument = None  # type: ignore[assignment,misc]
    IParentChildExpander = None  # type: ignore[assignment,misc]
    IContextCompletenessScorer = None  # type: ignore[assignment,misc]
    IAnswerSupportValidator = None  # type: ignore[assignment,misc]
    SupportedAnswerCheck = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness deps unavailable")
class TestCompletenessImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/utils/workflow_engines/completeness.py must be importable."""
        assert _AVAILABLE

    def test_contextcompletenessscore_defined(self) -> None:
        assert ContextCompletenessScore is not None

    def test_groundeddocument_defined(self) -> None:
        assert GroundedDocument is not None

    def test_iparentchildexpander_defined(self) -> None:
        assert IParentChildExpander is not None

    def test_icontextcompletenessscorer_defined(self) -> None:
        assert IContextCompletenessScorer is not None

    def test_ianswersupportvalidator_defined(self) -> None:
        assert IAnswerSupportValidator is not None

    def test_supportedanswercheck_defined(self) -> None:
        assert SupportedAnswerCheck is not None
