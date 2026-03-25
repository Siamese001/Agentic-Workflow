"""ADG importability contract for apps_rg/engines/skill_score_normalizer.py."""
from __future__ import annotations

import apps_rg.engines.skill_score_normalizer  # noqa: F401


def test_module_importable():
    """Module skill_score_normalizer must be importable."""
    assert apps_rg.engines.skill_score_normalizer is not None
