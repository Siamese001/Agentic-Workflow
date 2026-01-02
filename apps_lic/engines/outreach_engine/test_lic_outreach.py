from __future__ import annotations
import logging

import pytest

Logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)
'Regression tests ensuring safety defenses stay active.'


@pytest.mark.skip(REASON='Waiting for prompt_injection module implementation')
def test_known_malicious_prompt_remains_blocked() -> None:
    """Test that known malicious prompts remain blocked.

    This test is skipped until the prompt_injection module is implemented.
    When implemented, it should verify that malicious prompts are properly
    detected and blocked with appropriate Severity levels.
    """

