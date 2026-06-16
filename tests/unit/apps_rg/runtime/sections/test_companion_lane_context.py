from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections import companion_lane_context as ctx


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_companion_context_formats_supported_lane_payloads(
    tmp_path: Path,
    monkeypatch,
) -> None:
    paths = {
        "executive_summary": _write_json(
            tmp_path / "executive_summary.json",
            {"resume_display_text": "Executive summary text."},
        ),
        "unify_bullets": _write_json(
            tmp_path / "unify_bullets.json",
            {"bullets": [{"bullet_id": "ub1", "bullet_text": "Built platform."}]},
        ),
        "ibm_narrative": _write_json(
            tmp_path / "ibm_narrative.json",
            {"narrative_sentence": "IBM narrative sentence."},
        ),
        "ibm_bullets": _write_json(tmp_path / "invalid.json", {"bullets": "bad"}),
    }

    monkeypatch.setattr(ctx, "_companion_lane_l2_path", lambda lane: paths.get(lane))

    blob = ctx.load_companion_context()

    assert "### executive_summary\nExecutive summary text." in blob
    assert "### unify_bullets\n- ub1: Built platform." in blob
    assert "### ibm_narrative\nIBM narrative sentence." in blob
    assert "### ibm_bullets" not in blob


def test_resume_support_blob_includes_companion_context_and_normalizes_case() -> None:
    rows = [
        {"claim_text": "Led Azure migration", "technologies": ["Python", "Kubernetes"]},
        {"claim_text": "Scaled governance", "technologies": ["AWS"]},
    ]

    blob = ctx.build_resume_support_blob(rows, "Companion Narrative")

    assert "led azure migration" in blob
    assert "python" in blob
    assert "kubernetes" in blob
    assert "companion narrative" in blob


def test_c0_proof_support_blob_excludes_companion_context() -> None:
    rows = [{"claim_text": "Grounded evidence only", "technologies": ["GraphRAG"]}]

    blob = ctx.build_c0_proof_support_blob(rows)

    assert "grounded evidence only" in blob
    assert "graphrag" in blob
    assert "companion" not in blob

