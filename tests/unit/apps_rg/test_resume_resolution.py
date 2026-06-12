"""apps_rg resume_resolution — SSOT, digests, and fail-closed behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.resume_resolution import (
    ResumeResolutionError,
    ResumeSource,
    build_canonical_resume_payload,
    canonical_resume_digest,
    load_candidate_static_profile_json,
    resolve_resume_for_lanes,
    u0_inline_text_from_payload,
)


def test_default_ssot_loads_json() -> None:
    repo = Path(__file__).resolve().parents[3]
    rr = resolve_resume_for_lanes(repo_root=repo, require_run_specific=False)
    assert rr.resume_source == ResumeSource.DEFAULT_SSOT
    assert rr.resume_dict is not None
    assert rr.resume_digest == canonical_resume_digest(rr.resume_payload)
    assert "DEFAULT_SSOT" in rr.resume_ref_used


def test_inline_json_digest_stable() -> None:
    raw = json.dumps({"a": 1, "b": {"c": 2}}, sort_keys=False)
    p1 = build_canonical_resume_payload(raw)
    p2 = build_canonical_resume_payload(raw + "  \n")
    assert p1 == p2
    assert canonical_resume_digest(p1) == canonical_resume_digest(p2)
    assert u0_inline_text_from_payload(p1) == json.dumps(
        p1, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )


def test_ref_only_json_file(tmp_path: Path) -> None:
    p = tmp_path / "r.json"
    body = {"base_resume_id": "x", "facts": {}}
    p.write_text(json.dumps(body), encoding="utf-8")
    rr = resolve_resume_for_lanes(
        source_resume_ref=str(p),
        require_run_specific=True,
        repo_root=tmp_path,
    )
    assert rr.resume_source == ResumeSource.RUN_SPECIFIC
    assert rr.resume_dict == body


def test_ref_only_plain_text_fails_when_json_required(tmp_path: Path) -> None:
    p = tmp_path / "r.txt"
    p.write_text("plain resume \n", encoding="utf-8")
    with pytest.raises(ResumeResolutionError, match="plain text"):
        resolve_resume_for_lanes(
            source_resume_ref=str(p),
            require_run_specific=True,
            require_json_document=True,
            repo_root=tmp_path,
        )


def test_ref_only_plain_text_allowed_without_json_requirement(tmp_path: Path) -> None:
    p = tmp_path / "r.txt"
    p.write_text("plain resume \n", encoding="utf-8")
    rr = resolve_resume_for_lanes(
        source_resume_ref=str(p),
        require_run_specific=True,
        require_json_document=False,
        repo_root=tmp_path,
    )
    assert rr.resume_dict is None
    assert rr.resume_payload["material_kind"] == "plain"


def test_require_run_specific_fail_closed() -> None:
    with pytest.raises(ResumeResolutionError, match="required resume material"):
        resolve_resume_for_lanes(require_run_specific=True, require_json_document=False)


def test_inline_precedes_ref(tmp_path: Path) -> None:
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"file": True}), encoding="utf-8")
    rr = resolve_resume_for_lanes(
        source_resume_text=json.dumps({"inline": True}),
        source_resume_ref=str(p),
        require_run_specific=True,
        repo_root=tmp_path,
    )
    assert rr.resume_dict == {"inline": True}


def test_candidate_static_profile_default_loads_static_identity_only() -> None:
    repo = Path(__file__).resolve().parents[3]
    profile, path, digest = load_candidate_static_profile_json(repo_root=repo)
    assert path.name == "candidate_static_profile.json"
    assert digest
    assert profile["name"] == "Amit Ayer"
    assert "employment_identity" in profile
    assert "skills" not in profile
    assert "facts" not in profile


def test_final_resume_default_paths_include_candidate_static_profile() -> None:
    from apps_rg.runtime.assembly.final_resume_manifest import resolve_default_paths

    repo = Path(__file__).resolve().parents[3]
    paths = resolve_default_paths(repo)
    assert paths.candidate_static_profile is not None
    assert paths.candidate_static_profile.name == "candidate_static_profile.json"
