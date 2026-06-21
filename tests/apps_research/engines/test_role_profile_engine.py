"""Tests for apps_research.engines.role_profile_engine (plan §P2.3)."""

from __future__ import annotations

import pytest

from apps_research.engines.role_profile_engine import RoleProfileEngine
from apps_research.types.role_profile import RoleProfile


def test_engine_produces_schema_valid_profile_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.delenv("APPS_RESEARCH_RETRIEVAL_V2", raising=False)
    engine = RoleProfileEngine()
    payload = engine.execute({"role": "VP Data Science", "depth": "shallow"})
    profile = RoleProfile.model_validate(payload)
    assert profile.role == "VP Data Science"
    assert len(profile.required_skills) >= 3
    assert len(profile.nice_to_have) >= 1
    assert profile.scope  # non-empty


def test_empty_role_raises():
    with pytest.raises(ValueError):
        RoleProfileEngine().execute({"role": "", "depth": "standard"})


def test_topic_alias_supported():
    payload = RoleProfileEngine().execute({"topic": "Director of ML"})
    assert payload["role"] == "Director of ML"
