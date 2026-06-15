from __future__ import annotations

import pytest

from apps_rg.runtime.validators import achv_bullet_synthesizer_validator as validator


def test_achv_bullet_synthesizer_static_keyword_catalogs_are_available() -> None:
    synth = validator.AchvBulletSynthesizer

    assert {"led", "built", "delivered"} <= synth.VERB_KEYWORDS
    assert {"python", "aws", "api"} <= synth.TECH_KEYWORDS
    assert {"leadership", "stakeholder"} <= synth.SOFT_KEYWORDS


def test_factory_fails_loudly_until_runtime_dependencies_are_wired() -> None:
    with pytest.raises(NameError, match="BulletSynthesizerConfig|SELF"):
        validator.create_achv_bullet_synthesizer()


def test_direct_construction_fails_loudly_until_runtime_dependencies_are_wired() -> None:
    with pytest.raises(NameError, match="BulletSynthesizerConfig|SELF"):
        validator.AchvBulletSynthesizer()
