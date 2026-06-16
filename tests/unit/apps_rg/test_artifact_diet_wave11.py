"""Wave 11 artifact diet tests."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.artifact_diet import (
    build_artifact_diet_receipt,
    classify_artifact,
    compact_artifact_links,
)
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run


def _write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_artifact_diet_classifies_heavy_diagnostics_out_of_compact_links() -> None:
    assert classify_artifact("l2_output.json").diet_class == "proof_core"
    assert classify_artifact("x3_disposition.json").compact_link is True
    assert classify_artifact("provider_response.json").diet_class == "diagnostic_heavy"
    assert classify_artifact("provider_response.json").compact_link is False
    assert classify_artifact("compiled_prompt.txt").compact_link is False
    assert classify_artifact("command_output.txt").compact_link is False


def test_compact_artifact_links_keep_proof_surfaces_only() -> None:
    links = {
        "l2_output.json": "artifacts/l2_output.json",
        "x2_gate_outputs.json": "artifacts/x2_gate_outputs.json",
        "provider_response.json": "artifacts/provider_response.json",
        "compiled_prompt.txt": "artifacts/compiled_prompt.txt",
        "command_output.txt": "artifacts/command_output.txt",
    }
    compact = compact_artifact_links(links)
    assert compact == {
        "l2_output.json": "artifacts/l2_output.json",
        "x2_gate_outputs.json": "artifacts/x2_gate_outputs.json",
    }
    receipt = build_artifact_diet_receipt(links)
    assert receipt["legacy_artifact_links_preserved"] is True
    assert receipt["compact_link_count"] == 2
    assert receipt["legacy_link_count"] == 5
    assert receipt["diagnostic_retained_on_disk_count"] == 3


def test_finalize_runtime_proof_run_emits_compact_links_without_dropping_legacy(
    tmp_path: Path,
) -> None:
    repo = tmp_path
    ad = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "headline" / "real" / "run-1"
    _write(ad / "l2_output.json", json.dumps({"runtime_generation_status": "REAL_LLM"}))
    _write(ad / "x2_gate_outputs.json")
    _write(ad / "x3_disposition.json")
    _write(ad / "provider_request.json")
    _write(ad / "provider_response.json", json.dumps({"raw": "verbose"}))
    _write(ad / "compiled_prompt.txt", "large prompt")
    _write(ad / "command_output.txt", "display text")

    finalize_runtime_proof_run(
        repo,
        "headline",
        "external_claude",
        ad,
        run_id="run-1",
        section_id="headline",
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted=True,
    )

    manifest = json.loads((ad / "run_manifest.json").read_text(encoding="utf-8"))
    legacy = manifest["artifact_links"]
    compact = manifest["artifact_links_compact"]
    diet = manifest["artifact_diet"]

    assert "provider_response.json" in legacy
    assert "compiled_prompt.txt" in legacy
    assert "command_output.txt" in legacy
    assert "provider_response.json" not in compact
    assert "compiled_prompt.txt" not in compact
    assert "command_output.txt" not in compact
    assert "l2_output.json" in compact
    assert "x3_disposition.json" in compact
    assert diet["mode"] == "manifest_compact_non_destructive"
    assert diet["legacy_artifact_links_preserved"] is True
    assert diet["diagnostic_retained_on_disk_count"] >= 3

    pointer = json.loads(
        (
            repo
            / "artifacts"
            / "apps_rg"
            / "runtime_proofs"
            / "headline"
            / "latest_successful_real_run.json"
        ).read_text(encoding="utf-8")
    )
    assert "artifact_links_compact" in pointer
    assert "provider_response.json" not in pointer["artifact_links_compact"]
