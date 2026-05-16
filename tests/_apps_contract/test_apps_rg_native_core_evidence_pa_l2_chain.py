"""W3: Evidence discipline, PA hashes, generic artifact refs (no new L2 generation)."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest
import yaml

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import REQUIRED_BINDING_SECTIONS, validate_app_binding_package
from agentic_core.runtime.bindings.evidence_policy_validator import validate_evidence_discipline_document
from agentic_core.runtime.bindings.profile_validators import run_profile_validators

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"
_POLICY = REPO_ROOT / "agentic_core/runtime/bindings/generic_binding_validation_policy.binding_v1.yaml"


def test_evidence_discipline_passes_fixture_policy() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    policy = yaml.safe_load(_POLICY.read_text(encoding="utf-8"))
    doc = yaml.safe_load(pkg.section_paths["evidence_discipline"].read_text(encoding="utf-8"))
    detail = validate_evidence_discipline_document(doc, repo_root=REPO_ROOT, policy_doc=policy)
    assert detail.status == "PASS"


def test_targeting_paths_cannot_overlap_canonical_primary_paths() -> None:
    policy = yaml.safe_load(_POLICY.read_text(encoding="utf-8"))
    doc = yaml.safe_load((FIXTURE_PKG / "evidence_discipline.yaml").read_text(encoding="utf-8"))
    canon = doc.setdefault("canonical_proof_evidence", {})
    tgt = doc.setdefault("targeting_context_only", {})
    overlap = "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
    canon["primary_paths"] = [overlap]
    tgt["examples_non_proof_paths"] = [overlap]
    detail = validate_evidence_discipline_document(doc, repo_root=REPO_ROOT, policy_doc=policy)
    assert detail.status == "FAIL"


def test_pa_lane_hashes_validate_fixture() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    sections = {k: pkg.section_paths[k] for k in REQUIRED_BINDING_SECTIONS}
    details = run_profile_validators(sections, REPO_ROOT)
    pa = next(d for d in details if d.section_name == "pa_lane_refs")
    assert pa.status == "PASS"


def test_pa_malformed_hash_fails_in_copy(tmp_path: Path) -> None:
    pkg_root = tmp_path / "pkg"
    shutil.copytree(FIXTURE_PKG, pkg_root)
    pkg = load_app_binding_package(pkg_root)
    sections = {k: pkg.section_paths[k] for k in REQUIRED_BINDING_SECTIONS}
    pa_path = sections["pa_lane_refs"]
    doc = yaml.safe_load(pa_path.read_text(encoding="utf-8"))
    first_key = next(iter(doc["file_hashes"].keys()))
    doc["file_hashes"][first_key] = "0" * 64
    pa_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    details = run_profile_validators(sections, REPO_ROOT)
    pa = next(d for d in details if d.section_name == "pa_lane_refs")
    assert pa.status == "FAIL"


def test_missing_pa_artifact_file_fails_binding_consumer(tmp_path: Path) -> None:
    pkg_root = tmp_path / "pkg"
    shutil.copytree(FIXTURE_PKG, pkg_root)
    pkg = load_app_binding_package(pkg_root)
    pa_path = pkg.section_paths["pa_lane_refs"]
    doc = yaml.safe_load(pa_path.read_text(encoding="utf-8"))
    bogus = "apps_rg/prompt_assembly/section_prompt_contracts/__missing_native_core__.yaml"
    doc["file_hashes"][bogus] = hashlib.sha256(b"").hexdigest()
    pa_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    vr = validate_app_binding_package(pkg)
    assert vr.status == "FAIL"


def test_binding_fixture_remains_pass_on_canonical_tree() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    assert validate_app_binding_package(pkg).status == "PASS"
