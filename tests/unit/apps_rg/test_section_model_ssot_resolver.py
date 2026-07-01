"""SSOT: apps_rg per-section generator models resolve from explicit YAML pins."""
from __future__ import annotations

import pytest

from apps_rg.runtime.section_model_limits import SectionModelSSOTError
from apps_rg.runtime.section_model_limits import resolve_section_generation_model as resolve

_SONNET = "claude-sonnet-5"


def test_sonnet_bullet_lanes() -> None:
    for section in ("competencies", "unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets"):
        assert resolve(section, environ={}) == _SONNET, section


def test_high_signal_lanes_are_sonnet_5() -> None:
    for section in ("executive_summary", "headline"):
        assert resolve(section, environ={}) == _SONNET, section


def test_missing_or_unknown_section_fails_closed() -> None:
    with pytest.raises(SectionModelSSOTError):
        resolve(None, environ={})
    with pytest.raises(SectionModelSSOTError):
        resolve("some_unmapped_section", environ={})


def test_operator_env_pin_is_ignored() -> None:
    pin = {"APPS_RG_EXTERNAL_CLAUDE_MODEL": "ignored-operator-override"}
    assert resolve("unify_bullets", environ=pin) == _SONNET
    assert resolve("headline", environ=pin) == _SONNET
