"""Contract tests for final resume assembly artifacts (deterministic stitching; no runtime providers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.assembly.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths, resolve_default_paths
from apps_rg.runtime.assembly.final_resume_x2 import CANONICAL_ASSEMBLED_SECTION_ORDER
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


_EXPECTED_ARTIFACT_FILENAMES = frozenset(
    {
        "final_resume.json",
        "final_resume_manifest.json",
        "final_resume_x2_gate_outputs.json",
        "final_resume_receipt.json",
    },
)


@pytest.fixture(scope="module")
def paths() -> FinalResumePaths:
    p = resolve_default_paths(find_repo_root())
    if not p.rollup_json.is_file() or not p.locked_manifest.is_file():
        pytest.skip("final resume assembly prerequisites missing (rollup and/or locked manifest)")
    return p


@pytest.fixture(scope="module")
def rollup_blob(paths: FinalResumePaths) -> dict[str, object]:
    return json.loads(paths.rollup_json.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def locked_manifest_blob(paths: FinalResumePaths) -> dict[str, object]:
    return json.loads(paths.locked_manifest.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def assembled(paths: FinalResumePaths) -> dict[str, object]:
    return assemble_final_resume(paths)


def _norm_posix(rel: str) -> str:
    return rel.replace("\\", "/")


def test_final_resume_artifacts_exist(assembled: dict[str, object], paths: FinalResumePaths) -> None:
    out_dir = paths.output_dir
    for name in sorted(_EXPECTED_ARTIFACT_FILENAMES):
        assert (out_dir / name).is_file(), f"missing artifact {name}"


def test_only_expected_artifacts_written(paths: FinalResumePaths) -> None:
    names = sorted(p.name for p in paths.output_dir.iterdir() if p.is_file())
    assert names == sorted(_EXPECTED_ARTIFACT_FILENAMES)


def test_gates_pass(assembled: dict[str, object]) -> None:
    assert assembled["gates_all_pass"], f"FAILED_GATES:{','.join(assembled['failed_gate_ids'])}"


def test_required_sections_and_order(paths: FinalResumePaths) -> None:
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    ids_in_order = [str(s["section_id"]) for s in blob["sections"]]
    assert set(ids_in_order) == set(CANONICAL_ASSEMBLED_SECTION_ORDER)
    assert ids_in_order == list(CANONICAL_ASSEMBLED_SECTION_ORDER)


def test_generated_sections_point_at_latest_successful_real(
    rollup_blob: dict[str, object],
    paths: FinalResumePaths,
) -> None:
    lanes = rollup_blob["lanes"]
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    for sec in blob["sections"]:
        if sec.get("section_kind") != "generated_lane":
            continue
        lane_id = str(sec["section_id"])
        lane = lanes[lane_id]  # type: ignore[index]
        expected_rel = Path(str(lane["latest_successful_real_artifact_path"]))
        disp = (sec.get("disposition_refs") or {}).get("generated_lane") or {}
        got_dir = Path(str(disp.get("latest_successful_real_artifact_dir")))
        assert _norm_posix(str(got_dir)) == _norm_posix(str(expected_rel))

        l2_on_disk = json.loads(
            (paths.repo_root / got_dir / "l2_output.json").read_text(encoding="utf-8"),
        )
        assert l2_on_disk == sec["l2_output_snapshot"]


def test_locked_sections_match_manifest(
    paths: FinalResumePaths,
    locked_manifest_blob: dict[str, object],
) -> None:
    by_id = {
        str(s["section_id"]): s for s in locked_manifest_blob.get("sections", []) if isinstance(s, dict)
    }
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    locked_ids = (
        "insurtech",
        "ey",
        "early_career",
        "education",
        "certifications",
    )
    for sid in locked_ids:
        mf = by_id[sid]
        sec = next(s for s in blob["sections"] if s["section_id"] == sid)
        assert sec["copied_text_exact"] == mf["copied_text"]


def test_invariants_preserve_manifest_exact(
    paths: FinalResumePaths,
    locked_manifest_blob: dict[str, object],
) -> None:
    by_id = {str(s["section_id"]): s for s in locked_manifest_blob.get("sections", []) if isinstance(s, dict)}
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    inv = blob["locked_copy_invariants"]
    for ik in ("company_names", "titles", "locations", "dates"):
        assert inv[ik]["copied_text_exact"] == by_id[ik]["copied_text"]


def test_hashes_and_aggregate_hash(paths: FinalResumePaths) -> None:
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    assert str(blob["final_resume_hash"])
    assert all(str(s.get("section_hash")) for s in blob["sections"])
    inv = blob["locked_copy_invariants"]
    for ik in ("company_names", "titles", "locations", "dates"):
        assert str(inv[ik]["section_hash"])


def test_output_dir_has_no_provider_qwen_judge_docx_files(paths: FinalResumePaths) -> None:
    for f in paths.output_dir.iterdir():
        if not f.is_file():
            continue
        n = f.name.lower()
        assert n in {x.lower() for x in _EXPECTED_ARTIFACT_FILENAMES}
        assert not n.startswith("provider_")
        assert "qwen" not in n
        assert "x1d" not in n
        assert "llm_judge" not in n
        assert not n.endswith(".docx")


def test_assembler_lives_under_apps_rg_overlay_only() -> None:
    from apps_rg.runtime import assembly as modpkg  # noqa: PLC0415

    root_pkg = Path(modpkg.__file__).resolve().parent
    repo = find_repo_root()
    rp = root_pkg.relative_to(repo)
    assert rp.parts[:2] == ("apps_rg", "runtime")
    assert "agentic_core" not in rp.parts
