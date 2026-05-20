"""Contract tests for deterministic DOCX render (offline; uses python-docx)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

try:
    from docx import Document  # type: ignore[import-untyped]
except ImportError:
    Document = None

from apps_rg.runtime.assembly.final_resume_x2 import CANONICAL_ASSEMBLED_SECTION_ORDER
from apps_rg.runtime.internal.docx_renderer import build_docx_from_final_resume, resolve_docx_renderer_paths


_EXPECTED_ARTIFACTS = frozenset(
    {
        "amit_ayer_resume_v1.docx",
        "docx_render_manifest.json",
        "docx_render_x2_gate_outputs.json",
        "docx_render_receipt.json",
    },
)


@pytest.fixture(scope="module")
def rpaths():
    p = resolve_docx_renderer_paths()
    if Document is None:
        pytest.skip("python-docx is not installed")
    if not p.final_resume_json.is_file() or not p.docx_manifest_json.is_file():
        pytest.skip("final_resume assembly or DOCX manifest missing")
    return p


@pytest.fixture(scope="module")
def rendered(rpaths):
    return build_docx_from_final_resume(rpaths)


def test_docx_emit_dir_has_only_contract_artifacts(rpaths):
    names = sorted(f.name for f in rpaths.output_dir.iterdir() if f.is_file())
    assert names == sorted(_EXPECTED_ARTIFACTS)


def test_amit_docx_file_created(rendered: dict[str, object], rpaths):
    assert rpaths.output_docx.is_file()
    assert rendered["gates_all_pass"]


def test_docx_render_manifest_records_hashes(rendered: dict[str, object], rpaths):
    blob = json.loads((rpaths.output_dir / "docx_render_manifest.json").read_text(encoding="utf-8"))
    fr = json.loads(rpaths.final_resume_json.read_text(encoding="utf-8"))
    expected_fr_hash = hashlib.sha256(rpaths.final_resume_json.read_bytes()).hexdigest()
    assert blob["sources"]["final_resume_hash_logical"] == fr["final_resume_hash"]
    assert blob["sources"]["final_resume_sha256_bytes"] == expected_fr_hash


def test_x2_bundle_all_pass(rendered: dict[str, object], rpaths):
    x = json.loads((rpaths.output_dir / "docx_render_x2_gate_outputs.json").read_text(encoding="utf-8"))
    assert rendered["gates_all_pass"] is True
    assert x["all_pass"] is True
    assert x["failed_gate_ids"] == []


def test_receipt_contains_paths(rendered: dict[str, object], rpaths):
    rc = json.loads((rpaths.output_dir / "docx_render_receipt.json").read_text(encoding="utf-8"))
    assert rc["receipt_id"] == "docx_render_receipt_v1"
    assert rc["gates_all_pass"] == rendered["gates_all_pass"]


def test_section_heading_order_and_content_present(rpaths):
    if Document is None:
        pytest.skip("python-docx not installed")
    """Smoke: every canonical section heading exists in-document (manifest-driven titles)."""
    mb = json.loads(rpaths.docx_manifest_json.read_text(encoding="utf-8"))
    prof = {str(p["section_id"]): p for p in mb["section_profiles"]}
    doc_text = "\n".join(p.text for p in Document(str(rpaths.output_docx)).paragraphs)
    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:
        hint = prof[sid]["human_section_title_hint"]
        assert hint in doc_text


def test_render_package_under_apps_rg():
    from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root  # noqa: PLC0415
    import apps_rg.runtime.internal.docx_renderer as dr  # noqa: PLC0415

    repo = find_repo_root().resolve()
    rf = Path(dr.__file__).resolve()
    rp = rf.relative_to(repo)
    assert rp.parts[:2] == ("apps_rg", "runtime")
