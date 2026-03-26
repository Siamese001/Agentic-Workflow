"""ADG contract tests for apps_shared/types/vector_similarity_result_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module vector_similarity_result_types must be importable."""
    import apps_shared.types.vector_similarity_result_types  # noqa: F401

    assert apps_shared.types.vector_similarity_result_types is not None