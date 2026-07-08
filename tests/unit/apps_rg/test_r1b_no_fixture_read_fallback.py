"""apps-test-model: APP CONTRACT.

R1B production reads fail closed when the derived read projection is missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.cache.r1b_derived_index import lookup_r1b_via_derived_index
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_whole_run_preflight import execute_whole_run_r1b_preflight
from tests.unit.apps_rg.r1b_fixture_builders import (
    r1b_match_request,
    seed_admissible_r1b_store,
)


def test_missing_derived_index_does_not_read_fixture_store(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    seed_admissible_r1b_store(store)

    hit, report = lookup_r1b_via_derived_index(
        r1b_match_request(),
        projection_root=tmp_path,
        similarity_threshold=0.5,
        query_prompt_hash="prompt_profile_w7_v1",
        query_gate_hash="gate_profile_w7_v1",
    )

    assert hit is None
    assert report[0]["lookup_surface"] == "derived_index"
    assert report[0]["admissible"] is False
    assert report[0]["generation_required"] is True
    assert report[0]["fixture_store_consulted"] is False
    assert "fixture_fallback_forbidden" in report[0]["reason_codes"]


def test_fixture_record_cannot_skip_generation_without_derived_index(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    seed_admissible_r1b_store(store)

    result = execute_whole_run_r1b_preflight(
        raw_request=r1b_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )

    assert result.r1b_hit is False
    assert result.generation_required is True
    assert result.outcome == "r1b_read_projection_unavailable"
    assert result.compatibility_report[0]["fixture_store_consulted"] is False


def test_test_only_fixture_fallback_requires_explicit_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    seed_admissible_r1b_store(store)
    monkeypatch.setenv("APPS_RG_R1B_ALLOW_FIXTURE_FALLBACK_FOR_TESTS", "1")

    denied_hit, denied_report = lookup_r1b_via_derived_index(
        r1b_match_request(),
        projection_root=tmp_path,
        similarity_threshold=0.5,
    )
    assert denied_hit is None
    assert denied_report[0]["fixture_store_consulted"] is False

    hit, report = lookup_r1b_via_derived_index(
        r1b_match_request(),
        projection_root=tmp_path,
        similarity_threshold=0.5,
        query_prompt_hash="prompt_profile_w7_v1",
        query_gate_hash="gate_profile_w7_v1",
        _allow_fixture_fallback_for_tests=True,
    )

    assert hit is not None
    assert report[0]["lookup_surface"] == "fixture_mirror_test_only"
    assert report[0]["fixture_store_consulted"] is True
    assert report[0]["requires_explicit_test_flag"] is True


def test_whole_run_preflight_reports_generation_required_on_projection_missing(tmp_path: Path) -> None:
    result = execute_whole_run_r1b_preflight(
        raw_request=r1b_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
    )

    assert result.r1b_hit is False
    assert result.generation_required is True
    assert result.outcome == "r1b_read_projection_unavailable"
    assert result.compatibility_report[0]["reason_codes"] == [
        "derived_index_unavailable",
        "fixture_fallback_forbidden",
    ]
