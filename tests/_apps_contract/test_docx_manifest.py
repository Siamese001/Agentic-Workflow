"""Contract tests for DOCX render manifest (filesystem plan only; never emits .docx here)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.assembly.final_resume_x2 import CANONICAL_ASSEMBLED_SECTION_ORDER
from apps_rg.runtime.render.docx_manifest_builder import (
    PLANNED_DOCX_POSIX,
    build_docx_manifest,
    resolve_docx_manifest_paths,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

_EXPECTED_MANIFEST_ARTIFACTS = frozenset(
    {
        "docx_manifest.json",
        "docx_manifest_x2_gate_outputs.json",
        "docx_manifest_receipt.json",
    },
)


@pytest.fixture(scope="module")
def mf_paths():
    p = resolve_docx_manifest_paths(find_repo_root())
    if not p.final_resume_json.is_file():
        pytest.skip("final_resume.json missing — run final_resume_assembler first")
    return p


@pytest.fixture(scope="module")
def built(mf_paths):
    return build_docx_manifest(mf_paths)


def test_docx_manifest_exists(mf_paths):
    assert (mf_paths.output_dir / "docx_manifest.json").is_file()


def test_only_expected_manifest_artifacts_written(mf_paths):
    names = sorted(f.name for f in mf_paths.output_dir.iterdir() if f.is_file())
    assert names == sorted(_EXPECTED_MANIFEST_ARTIFACTS)


def test_docx_manifest_references_final_resume(mf_paths, built):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    fr_rel = mf_paths.repo_root.joinpath(Path(m["sources"]["final_resume_json"])).resolve()
    expected = mf_paths.final_resume_json.resolve()
    assert fr_rel == expected
    assert built["gates_all_pass"]


def test_final_resume_hash_matches(mf_paths, built):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    fb = json.loads(mf_paths.final_resume_json.read_text(encoding="utf-8"))
    assert m["sources"]["final_resume_hash"] == fb["final_resume_hash"]
    assert m["sources"]["final_resume_hash"]


def test_section_order_matches_final_resume(mf_paths):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    fb = json.loads(mf_paths.final_resume_json.read_text(encoding="utf-8"))
    fr_ids = [str(s["section_id"]) for s in fb["sections"]]
    assert m["section_render_order"] == fr_ids
    assert m["section_render_order"] == list(CANONICAL_ASSEMBLED_SECTION_ORDER)


def test_all_sections_have_style_mappings(mf_paths):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    prof = {str(p["section_id"]): p for p in m["section_profiles"]}
    assert set(prof.keys()) == set(CANONICAL_ASSEMBLED_SECTION_ORDER)
    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:
        sm = prof[sid]["style_mapping"]
        assert str(sm["paragraph_primary_style"]).strip()
        assert isinstance(sm["section_heading_outline_level"], int)
        assert "bullet_list_style_external_id" in sm


def test_generated_and_locked_refs_present(mf_paths):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    fg = m["generated_sections_render_refs"]
    lk = m["locked_sections_render_refs"]
    fb = json.loads(mf_paths.final_resume_json.read_text(encoding="utf-8"))
    for sec in fb["sections"]:
        sid = str(sec["section_id"])
        if sec.get("section_kind") == "generated_lane":
            assert sid in fg
            assert isinstance(fg[sid], dict)
        elif sec.get("section_kind") == "locked_copy_inline":
            assert sid in lk


def test_guarantees_and_docx_created_flags(mf_paths):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    g = m["guarantees"]
    assert g["no_rewrite"] is True
    assert g["provider_calls_made"] is False
    assert g["qwen_calls_made"] is False
    assert g["judge_calls_made"] is False
    pd = m["planned_output_docx"]
    pop = pd["output_docx_planned_path"]
    assert isinstance(pop, str) and pop.strip()
    assert pd["docx_created"] is False


def test_planned_docx_path_declared_manifest_never_claims_emit(mf_paths):
    m = json.loads((mf_paths.output_dir / "docx_manifest.json").read_text(encoding="utf-8"))
    posix = str(m["planned_output_docx"]["output_docx_planned_path"]).replace("\\", "/")
    assert posix == PLANNED_DOCX_POSIX.replace("\\", "/")
    pd = m["planned_output_docx"]
    assert pd["docx_created"] is False


def test_docx_manifest_x2_all_pass(mf_paths):
    x = json.loads((mf_paths.output_dir / "docx_manifest_x2_gate_outputs.json").read_text(encoding="utf-8"))
    assert x["all_pass"] is True


def test_render_package_is_apps_rg_only() -> None:
    from apps_rg.runtime import render as rp  # noqa: PLC0415

    p = Path(rp.__file__).resolve().relative_to(find_repo_root())
    assert "agentic_core" not in p.parts
