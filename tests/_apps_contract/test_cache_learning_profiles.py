"""Tests for apps_* cache and learning profile contracts.

Plan: apps-core-contract-rectification-a8f3c2 Phase 3.5
Verifies: schema compliance, all 8 apps covered, field presence and format.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

ALL_APPS = [
    "apps_qna",
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_exec",
    "apps_eval",
    "apps_underwriting_ai",
]

APPS_WITH_CACHE_ENABLED = sorted(["apps_qna", "apps_research", "apps_exec"])


def _apps_with_llm_judges() -> list[str]:
    out: list[str] = []
    for app_id in ALL_APPS:
        rubric_path = REPO_ROOT / app_id / "config" / "domain_contract" / "eval_rubrics.yaml"
        if not rubric_path.is_file():
            continue
        docs = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        if not isinstance(docs, list):
            continue
        for doc in docs:
            dims = doc.get("score_dimensions", []) if isinstance(doc, dict) else []
            if any(dim.get("grader_type") == "llm_as_judge" for dim in dims if isinstance(dim, dict)):
                out.append(app_id)
                break
    return sorted(out)


APPS_WITH_HOLDOUT_REQUIRED = _apps_with_llm_judges()


# ── helpers ──────────────────────────────────────────────────────────────────


def _load_yaml(app_id: str, filename: str) -> dict[str, Any]:
    path = REPO_ROOT / app_id / "config" / "domain_contract" / filename
    assert path.is_file(), f"{filename} missing for {app_id}: {path}"
    with path.open() as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), f"{app_id}/{filename} must be a YAML dict"
    return data


# ── cache profile tests ───────────────────────────────────────────────────────


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_file_exists(app_id: str) -> None:
    path = REPO_ROOT / app_id / "config" / "domain_contract" / "cache_profiles.yaml"
    assert path.is_file(), f"cache_profiles.yaml missing for {app_id}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_required_fields(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    for field in ("cache_profile_id", "app_id", "version", "status",
                  "semantic_cache_enabled", "ttl_seconds"):
        assert field in data, f"{app_id}/cache_profiles.yaml: missing {field!r}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_id_format(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    pattern = re.compile(r"^cp::.+::.+::v\d+$")
    assert pattern.match(data["cache_profile_id"]), (
        f"{app_id}: cache_profile_id {data['cache_profile_id']!r} invalid format"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_app_id_matches(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    assert data["app_id"] == app_id


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_status_valid(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    assert data["status"] in {"draft", "active", "deprecated"}


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_cache_profile_ttl_consistent_with_enabled(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    enabled = data["semantic_cache_enabled"]
    ttl = data["ttl_seconds"]
    if not enabled:
        assert ttl == 0, (
            f"{app_id}: semantic_cache_enabled=false but ttl_seconds={ttl} (expected 0)"
        )
    else:
        assert ttl > 0, (
            f"{app_id}: semantic_cache_enabled=true but ttl_seconds=0"
        )


@pytest.mark.parametrize("app_id", APPS_WITH_CACHE_ENABLED)
def test_cache_enabled_apps_have_similarity_threshold(app_id: str) -> None:
    data = _load_yaml(app_id, "cache_profiles.yaml")
    assert "similarity_threshold" in data, (
        f"{app_id}: cache-enabled app missing similarity_threshold"
    )
    thresh = data["similarity_threshold"]
    assert 0.0 <= thresh <= 1.0


# ── learning profile tests ────────────────────────────────────────────────────


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_file_exists(app_id: str) -> None:
    path = REPO_ROOT / app_id / "config" / "domain_contract" / "learning_profiles.yaml"
    assert path.is_file(), f"learning_profiles.yaml missing for {app_id}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_required_fields(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    for field in ("learning_profile_id", "app_id", "version", "status",
                  "promotion_threshold", "min_n_each_arm", "holdout_required"):
        assert field in data, f"{app_id}/learning_profiles.yaml: missing {field!r}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_id_format(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    pattern = re.compile(r"^lp::.+::.+::v\d+$")
    assert pattern.match(data["learning_profile_id"]), (
        f"{app_id}: learning_profile_id {data['learning_profile_id']!r} invalid format"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_app_id_matches(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    assert data["app_id"] == app_id


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_promotion_threshold_range(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    thresh = data["promotion_threshold"]
    assert 0.50 <= thresh <= 1.0, (
        f"{app_id}: promotion_threshold {thresh} out of range [0.50, 1.0]"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_learning_profile_min_n_positive(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    assert data["min_n_each_arm"] >= 10, (
        f"{app_id}: min_n_each_arm must be >= 10"
    )


@pytest.mark.parametrize("app_id", APPS_WITH_HOLDOUT_REQUIRED)
def test_llm_judge_apps_require_holdout(app_id: str) -> None:
    data = _load_yaml(app_id, "learning_profiles.yaml")
    assert data["holdout_required"] is True, (
        f"{app_id}: has LLM judges but holdout_required=false"
    )


# ── L4 record tests ───────────────────────────────────────────────────────────


def test_l4_record_has_cache_profile_refs_field() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(AppDomainContractRecord)}
    assert "cache_profile_refs" in field_names, (
        "AppDomainContractRecord missing cache_profile_refs (Phase 3.4)"
    )


def test_l4_record_has_learning_profile_refs_field() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(AppDomainContractRecord)}
    assert "learning_profile_refs" in field_names, (
        "AppDomainContractRecord missing learning_profile_refs (Phase 3.4)"
    )


def test_l4_record_new_refs_default_empty() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord

    rec = AppDomainContractRecord(
        app_domain_contract_id="adc::apps_qna::test",
        app_id="apps_qna",
        app_version="1.0.0",
        domain="test_domain",
        owner_surface="apps_qna",
        status="draft",
    )
    assert rec.cache_profile_refs == ()
    assert rec.learning_profile_refs == ()


def test_l4_record_accepts_all_three_new_refs() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord

    rec = AppDomainContractRecord(
        app_domain_contract_id="adc::apps_qna::test",
        app_id="apps_qna",
        app_version="1.0.0",
        domain="test_domain",
        owner_surface="apps_qna",
        status="draft",
        repair_profile_refs=("rp::apps_qna::qna_pack_build::v1",),
        cache_profile_refs=("cp::apps_qna::qna_pack_build::v1",),
        learning_profile_refs=("lp::apps_qna::qna_pack_build::v1",),
    )
    assert len(rec.repair_profile_refs) == 1
    assert len(rec.cache_profile_refs) == 1
    assert len(rec.learning_profile_refs) == 1
