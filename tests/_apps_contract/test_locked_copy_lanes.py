from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.locked_copy.locked_copy_manifest import LOCKED_SECTION_IDS, load_base_resume

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "locked_copy"
MANIFEST_PATH = ARTIFACT_DIR / "locked_copy_manifest.json"
X2_PATH = ARTIFACT_DIR / "locked_copy_x2_gate_outputs.json"
RECEIPT_PATH = ARTIFACT_DIR / "locked_copy_receipt.json"
BUILDER_CMD = [sys.executable, "-m", "apps_rg.runtime.locked_copy.locked_copy_builder"]


@pytest.fixture(scope="module")
def build_once() -> subprocess.CompletedProcess[str]:
    return subprocess.run(BUILDER_CMD, cwd=REPO_ROOT, text=True, capture_output=True, timeout=60)


@pytest.fixture(scope="module")
def manifest(build_once: subprocess.CompletedProcess[str]) -> dict:
    assert build_once.returncode == 0, build_once.stderr
    assert MANIFEST_PATH.is_file(), "locked_copy_manifest.json missing — run locked_copy_builder"
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sections(manifest: dict) -> dict[str, dict]:
    return {s["section_id"]: s for s in manifest["sections"]}


def test_locked_copy_manifest_exists(manifest: dict):
    assert manifest.get("manifest_id") == "locked_copy_manifest_v1"
    assert MANIFEST_PATH.is_file()


def test_every_locked_section_exists(sections: dict):
    assert set(sections.keys()) == set(LOCKED_SECTION_IDS)


def test_every_section_llm_generated_false(sections: dict):
    for sid, row in sections.items():
        assert row.get("llm_generated") is False, sid


def test_every_section_rewrite_allowed_false(sections: dict):
    for sid, row in sections.items():
        assert row.get("rewrite_allowed") is False, sid


def test_every_section_has_hashes(sections: dict):
    for sid, row in sections.items():
        assert row.get("source_hash"), sid
        assert row.get("copied_hash"), sid


def test_every_section_hash_matches(sections: dict):
    for sid, row in sections.items():
        assert row["source_hash"] == row["copied_hash"], sid
        assert row.get("byte_for_byte_match") is True, sid


def test_company_names_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    employment = (base.get("facts") or base).get("employment") or []
    expected = json.dumps([e["employer"] for e in employment], ensure_ascii=False, separators=(",", ":"))
    assert sections["company_names"]["copied_text"] == expected


def test_titles_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    employment = (base.get("facts") or base).get("employment") or []
    expected = json.dumps([e["title"] for e in employment], ensure_ascii=False, separators=(",", ":"))
    assert sections["titles"]["copied_text"] == expected


def test_locations_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    employment = (base.get("facts") or base).get("employment") or []
    expected = json.dumps([e["location"] for e in employment], ensure_ascii=False, separators=(",", ":"))
    assert sections["locations"]["copied_text"] == expected


def test_dates_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    employment = (base.get("facts") or base).get("employment") or []
    payload = [
        {
            "fact_id": e.get("fact_id"),
            "start_date": e.get("start_date"),
            "end_date": e.get("end_date"),
            "is_current": e.get("is_current"),
        }
        for e in employment
    ]
    expected = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["dates"]["copied_text"] == expected


def test_education_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    education = list((base.get("facts") or base).get("education") or [])
    expected = json.dumps(education, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["education"]["copied_text"] == expected


def test_certifications_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    certs = list((base.get("facts") or base).get("certifications") or [])
    expected = json.dumps(certs, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["certifications"]["copied_text"] == expected


def test_insurtech_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    emp = next(e for e in (base.get("facts") or base).get("employment", []) if "insurtech" in str(e.get("employer", "")).lower())
    expected = json.dumps(emp, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["insurtech"]["copied_text"] == expected


def test_ey_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    emp = next(
        e
        for e in (base.get("facts") or base).get("employment", [])
        if "ernst" in str(e.get("employer", "")).lower()
    )
    expected = json.dumps(emp, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["ey"]["copied_text"] == expected


def test_early_career_preserved(sections: dict):
    base, _, _ = load_base_resume(REPO_ROOT)
    emp = next(
        e
        for e in (base.get("facts") or base).get("employment", [])
        if "early career" in str(e.get("employer", "")).lower()
    )
    expected = json.dumps(emp, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert sections["early_career"]["copied_text"] == expected


def test_no_provider_request_artifact(build_once: subprocess.CompletedProcess[str]):
    assert not (ARTIFACT_DIR / "provider_request.json").is_file()
    assert not (ARTIFACT_DIR / "provider_response.json").is_file()
    assert not (ARTIFACT_DIR / "x1d_llm_judge_outputs.json").is_file()


def test_no_qwen_call_in_receipt(manifest: dict, build_once: subprocess.CompletedProcess[str]):
    assert manifest.get("qwen_calls_made") is False
    assert manifest.get("provider_calls_made") is False
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt.get("qwen_calls_made") is False


def test_x2_gate_outputs_all_pass(build_once: subprocess.CompletedProcess[str]):
    assert X2_PATH.is_file()
    x2 = json.loads(X2_PATH.read_text(encoding="utf-8"))
    assert x2["x2_failed"] == 0
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    required = {
        "x2_locked_copy_source_present",
        "x2_locked_copy_byte_for_byte_match",
        "x2_locked_copy_hash_match",
        "x2_locked_copy_no_llm_provider",
        "x2_locked_copy_rewrite_allowed_false",
        "x2_company_names_preserved",
        "x2_titles_preserved",
        "x2_locations_preserved",
        "x2_dates_preserved",
        "x2_education_preserved",
        "x2_certifications_preserved",
        "x2_insurtech_preserved",
        "x2_ey_preserved",
        "x2_early_career_preserved",
    }
    assert required <= gate_ids


def test_no_agentic_core_in_locked_copy_modules():
    for rel in (
        "apps_rg/runtime/locked_copy/locked_copy_builder.py",
        "apps_rg/runtime/locked_copy/locked_copy_manifest.py",
        "apps_rg/runtime/locked_copy/locked_copy_x2.py",
    ):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "from agentic_core" not in text
        assert "import agentic_core" not in text


def test_no_registry_in_locked_copy_modules():
    for rel in (
        "apps_rg/runtime/locked_copy/locked_copy_builder.py",
        "apps_rg/runtime/locked_copy/locked_copy_manifest.py",
        "apps_rg/runtime/locked_copy/locked_copy_x2.py",
    ):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
        assert "registry" not in text
