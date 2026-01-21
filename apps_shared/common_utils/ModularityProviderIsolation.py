from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skip(reason="Provider SDK isolation will be enforced in later refactor phases.")
def test_only_providers_contain_provider_sdks() -> None:
    """Placeholder for Provider SDK isolation tests.

    In later phases this will assert that only providers/* import concrete SDKs
    like openai, anthropic, google.generativeai, redis, chromadb, etc.
    """

    assert True
