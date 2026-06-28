"""Contract tests for final resume assembly artifacts (deterministic stitching; no runtime providers)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.runtime.internal.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths, resolve_default_paths
from apps_rg.runtime.assembly.final_resume_x2 import CANONICAL_ASSEMBLED_SECTION_ORDER
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


_REQUIRED_ARTIFACT_FILENAMES = frozenset(
    {
        "final_resume.json",
        "final_resume_manifest.json",
        "final_resume_x2_gate_outputs.json",
        "final_resume_receipt.json",
        "orchestration_fingerprint.json",
        "cross_section_x2_gate_outputs.json",
        "kept_removed_claims.json",
        "overlap_decisions.json",
        "aggregation_preflight.json",
        "coherent_rollup_policy.json",
        "review_lane_policy.json",
        "cross_section_warn_resolution.json",
    },
)

_PRODUCT_RELEASE_ARTIFACT_FILENAMES = frozenset(
    {
        "full_resume_llm_coherence_review.json",
        "x1d_full_resume_judge_outputs.json",
    },
)

_FORBIDDEN_ASSEMBLY_INLINE_PATTERNS = (
    "provider_",
    "retired_provider",
    "real_l2_generation_result",
)


@pytest.fixture(scope="module")
def paths(tmp_path_factory: pytest.TempPathFactory) -> FinalResumePaths:
    base = resolve_default_paths(find_repo_root())
    if not base.rollup_json.is_file() or not base.locked_manifest.is_file():
        pytest.skip("final resume assembly prerequisites missing (rollup and/or locked manifest)")
    out = tmp_path_factory.mktemp("final_resume_asm_contract")
    return FinalResumePaths(
        repo_root=base.repo_root,
        rollup_json=base.rollup_json,
        locked_manifest=base.locked_manifest,
        locked_x2=base.locked_x2,
        base_resume=base.base_resume,
        output_dir=out,
    )


@pytest.fixture(scope="module")
def rollup_blob(paths: FinalResumePaths) -> dict[str, object]:
    return json.loads(paths.rollup_json.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def locked_manifest_blob(paths: FinalResumePaths) -> dict[str, object]:
    return json.loads(paths.locked_manifest.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def assembled(paths: FinalResumePaths) -> dict[str, object]:
    prev_struct = os.environ.get("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY")
    prev_coherence = os.environ.get("APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW")
    os.environ["APPS_RG_ASSEMBLY_STRUCTURAL_ONLY"] = "1"
    os.environ["APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW"] = "0"
    try:
        return assemble_final_resume(paths, skip_preflight=True)
    finally:
        if prev_struct is None:
            os.environ.pop("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", None)
        else:
            os.environ["APPS_RG_ASSEMBLY_STRUCTURAL_ONLY"] = prev_struct
        if prev_coherence is None:
            os.environ.pop("APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW", None)
        else:
            os.environ["APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW"] = prev_coherence


def _norm_posix(rel: str) -> str:
    return rel.replace("\\", "/")


def test_final_resume_artifacts_exist(assembled: dict[str, object], paths: FinalResumePaths) -> None:
    out_dir = paths.output_dir
    for name in sorted(_REQUIRED_ARTIFACT_FILENAMES):
        assert (out_dir / name).is_file(), f"missing artifact {name}"


def test_required_core_artifacts_written(paths: FinalResumePaths, assembled: dict[str, object]) -> None:
    names = {p.name for p in paths.output_dir.iterdir() if p.is_file()}
    missing = _REQUIRED_ARTIFACT_FILENAMES - names
    assert not missing, f"missing required artifacts: {sorted(missing)}"


def test_gates_pass(assembled: dict[str, object]) -> None:
    assert assembled["gates_all_pass"], f"FAILED_GATES:{','.join(assembled['failed_gate_ids'])}"


def test_required_sections_and_order(paths: FinalResumePaths, assembled: dict[str, object]) -> None:
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    ids_in_order = [str(s["section_id"]) for s in blob["sections"]]
    assert set(ids_in_order) == set(CANONICAL_ASSEMBLED_SECTION_ORDER)
    assert ids_in_order == list(CANONICAL_ASSEMBLED_SECTION_ORDER)


def test_generated_sections_point_at_latest_successful_real(
    rollup_blob: dict[str, object],
    paths: FinalResumePaths,
    assembled: dict[str, object],
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
    assembled: dict[str, object],
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
    assembled: dict[str, object],
) -> None:
    by_id = {str(s["section_id"]): s for s in locked_manifest_blob.get("sections", []) if isinstance(s, dict)}
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    inv = blob["locked_copy_invariants"]
    for ik in ("company_names", "titles", "locations", "dates"):
        assert inv[ik]["copied_text_exact"] == by_id[ik]["copied_text"]


def test_hashes_and_aggregate_hash(paths: FinalResumePaths, assembled: dict[str, object]) -> None:
    blob = json.loads((paths.output_dir / "final_resume.json").read_text(encoding="utf-8"))
    assert str(blob["final_resume_hash"])
    assert all(str(s.get("section_hash")) for s in blob["sections"])
    inv = blob["locked_copy_invariants"]
    for ik in ("company_names", "titles", "locations", "dates"):
        assert str(inv[ik]["section_hash"])


def test_structural_assembly_no_inline_lane_provider_files(paths: FinalResumePaths, assembled: dict[str, object]) -> None:
    """Structural assembly must not re-invoke lane providers; aggregate judge files allowed in product mode only."""
    for f in paths.output_dir.iterdir():
        if not f.is_file():
            continue
        n = f.name.lower()
        if n in {x.lower() for x in _PRODUCT_RELEASE_ARTIFACT_FILENAMES}:
            continue
        for pat in _FORBIDDEN_ASSEMBLY_INLINE_PATTERNS:
            assert pat not in n, f"unexpected inline generation artifact: {f.name}"
        assert not n.endswith(".docx")


def test_product_release_mode_emits_aggregate_judge_artifacts(tmp_path: Path) -> None:
    base = resolve_default_paths(find_repo_root())
    if not base.rollup_json.is_file():
        pytest.skip("rollup missing")
    out = tmp_path / "product_asm"
    paths = FinalResumePaths(
        repo_root=base.repo_root,
        rollup_json=base.rollup_json,
        locked_manifest=base.locked_manifest,
        locked_x2=base.locked_x2,
        base_resume=base.base_resume,
        output_dir=out,
    )
    prev_struct = os.environ.pop("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", None)
    os.environ["APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW"] = "1"
    os.environ["APPS_RG_FULL_RESUME_COHERENCE_JUDGE_MODE"] = "mocked"
    try:
        result = assemble_final_resume(paths, skip_preflight=True)
    finally:
        if prev_struct is not None:
            os.environ["APPS_RG_ASSEMBLY_STRUCTURAL_ONLY"] = prev_struct
    blob = json.loads((out / "final_resume.json").read_text(encoding="utf-8"))
    assert blob["calls"]["judge_calls_made"] is True
    assert (out / "full_resume_llm_coherence_review.json").is_file()
    assert (out / "x1d_full_resume_judge_outputs.json").is_file()
    x2 = json.loads((out / "final_resume_x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2.get("gates") or []}
    assert "x2_final_resume_aggregate_judge_executed" in gate_ids
    assert "x2_no_judge_calls" not in gate_ids
    sem = blob.get("assembly_proof_semantics") or {}
    assert sem.get("aggregate_judge_executed") is True


def test_assembler_lives_under_apps_rg_overlay_only() -> None:
    from apps_rg.runtime import assembly as modpkg  # noqa: PLC0415

    root_pkg = Path(modpkg.__file__).resolve().parent
    repo = find_repo_root()
    rp = root_pkg.relative_to(repo)
    assert rp.parts[:2] == ("apps_rg", "runtime")
    assert "agentic_core" not in rp.parts
