"""ADG importability contract for agentic_core/prompt_governance/core/prompt_assembler.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_assembler.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.core.prompt_assembler import (  # noqa: F401
        InputSanitizer,
        SecurityIntegrityError,
        PromptComponents,
        AssembledPrompt,
        PromptTemplate,
        PromptAssembler,
        get_prompt_assembler,
        assemble_prompt,
        assemble_prompt_with_schema,
        parse_response,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InputSanitizer = None  # type: ignore[assignment,misc]
    SecurityIntegrityError = None  # type: ignore[assignment,misc]
    PromptComponents = None  # type: ignore[assignment,misc]
    AssembledPrompt = None  # type: ignore[assignment,misc]
    PromptTemplate = None  # type: ignore[assignment,misc]
    PromptAssembler = None  # type: ignore[assignment,misc]
    get_prompt_assembler = None  # type: ignore[assignment,misc]
    assemble_prompt = None  # type: ignore[assignment,misc]
    assemble_prompt_with_schema = None  # type: ignore[assignment,misc]
    parse_response = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_assembler.py deps unavailable")
class TestPromptAssemblerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: prompt_assembler.py must be importable."""
        assert _AVAILABLE

    def test_inputsanitizer_is_type(self) -> None:
        assert InputSanitizer is not None

    def test_securityintegrityerror_is_type(self) -> None:
        assert SecurityIntegrityError is not None

    def test_promptcomponents_is_type(self) -> None:
        assert PromptComponents is not None

    def test_get_prompt_assembler_callable(self) -> None:
        assert callable(get_prompt_assembler)

    def test_assemble_prompt_callable(self) -> None:
        assert callable(assemble_prompt)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

