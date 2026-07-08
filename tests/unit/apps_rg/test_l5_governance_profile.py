"""apps-test-model: LAW."""

from pathlib import Path

import pytest

from apps_rg.runtime.l5.governance_profile import (
    REQUIRED_PROFILE_SECTIONS,
    load_l5_governance_profile,
    profile_digest_from_mapping,
)


def test_l5_governance_profile_loads_required_sections() -> None:
    profile = load_l5_governance_profile()

    assert profile.profile_ref == "apps_rg/profiles/rg_l5_governance_profile.yaml"
    assert len(profile.profile_digest) == 64
    assert not profile.missing_sections
    for section in REQUIRED_PROFILE_SECTIONS:
        assert profile.section(section)


def test_l5_governance_profile_digest_is_deterministic() -> None:
    first = load_l5_governance_profile()
    second = load_l5_governance_profile()

    assert first.profile_digest == second.profile_digest
    assert first.profile_digest == profile_digest_from_mapping(first.data)


def test_l5_governance_profile_missing_section_strict_raises(tmp_path: Path) -> None:
    path = tmp_path / "profile.yaml"
    path.write_text("safety_enforcement:\n  policy_ref: p\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required section"):
        load_l5_governance_profile(path, strict=True)


def test_l5_governance_profile_missing_section_non_strict_records(tmp_path: Path) -> None:
    path = tmp_path / "profile.yaml"
    path.write_text("safety_enforcement:\n  policy_ref: p\n", encoding="utf-8")

    profile = load_l5_governance_profile(path, strict=False)

    assert "authority_context" in profile.missing_sections
    assert profile.section("authority_context") == {}
