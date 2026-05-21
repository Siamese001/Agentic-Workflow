"""P1 — real Brown & Brown artifact dirs: display text must become embeddable chunk rows."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_semantic_chunk_builder import build_chunk_rows_from_run_dir
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

REPO_ROOT = Path(__file__).resolve().parents[2]
BROWN_RUN = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_0e41a1c13cfe"


@pytest.mark.skipif(not BROWN_RUN.is_dir(), reason="Brown & Brown run artifacts not on disk")
@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_brown_lane_display_text_chunks(lane: str) -> None:
    lane_dir = BROWN_RUN / "lanes" / lane
    if not lane_dir.is_dir():
        pytest.skip(f"lane missing: {lane}")
    manifest = json.loads((lane_dir / "run_manifest.json").read_text(encoding="utf-8"))
    rows = build_chunk_rows_from_run_dir(lane_dir, manifest=manifest)
    out_rows = [r for r in rows if str(r.get("chunk_type", "")).endswith("_output")]
    assert out_rows, f"no section output row for {lane}"
    text = str(out_rows[0].get("chunk_text") or "")
    assert len(text.strip()) >= 8, f"display text too short for {lane}: {text!r}"


@pytest.mark.skipif(not BROWN_RUN.is_dir(), reason="Brown & Brown run artifacts not on disk")
def test_brown_whole_run_root_collects_lane_children() -> None:
    manifest_path = BROWN_RUN / "run_manifest.json"
    if not manifest_path.is_file():
        manifest = {
            "run_id": BROWN_RUN.name,
            "section_id": "integrated_whole_run",
            "proof_eligible": True,
            "runtime_generation_status": "REAL_LLM",
        }
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = build_chunk_rows_from_run_dir(BROWN_RUN, manifest=manifest)
    section_types = {r.get("chunk_type") for r in rows if str(r.get("chunk_type", "")).endswith("_output")}
    present_lanes = [lane for lane in GENERATED_LANES if f"{lane}_output" in section_types]
    assert len(present_lanes) >= 5, f"expected most lanes, got {present_lanes}"
