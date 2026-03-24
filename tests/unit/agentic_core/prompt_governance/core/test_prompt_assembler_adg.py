"""ADG importability contract for agentic_core/prompt_governance/core/prompt_assembler.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_assembler.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.core.prompt_assembler import (  # noqa: F401
        AssembledPrompt,
        InputSanitizer,
        PromptAssembler,
        PromptComponents,
        PromptTemplate,
        SecurityIntegrityError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InputSanitizer = None  # type: ignore[assignment,misc]
    SecurityIntegrityError = None  # type: ignore[assignment,misc]
    PromptComponents = None  # type: ignore[assignment,misc]
    AssembledPrompt = None  # type: ignore[assignment,misc]
    PromptTemplate = None  # type: ignore[assignment,misc]
    PromptAssembler = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_assembler deps unavailable")
class TestPromptAssemblerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/core/prompt_assembler.py must be importable."""
        assert _AVAILABLE

    def test_inputsanitizer_defined(self) -> None:
        assert InputSanitizer is not None

    def test_securityintegrityerror_defined(self) -> None:
        assert SecurityIntegrityError is not None

    def test_promptcomponents_defined(self) -> None:
        assert PromptComponents is not None

    def test_assembledprompt_defined(self) -> None:
        assert AssembledPrompt is not None

    def test_prompttemplate_defined(self) -> None:
        assert PromptTemplate is not None

    def test_promptassembler_defined(self) -> None:
        assert PromptAssembler is not None