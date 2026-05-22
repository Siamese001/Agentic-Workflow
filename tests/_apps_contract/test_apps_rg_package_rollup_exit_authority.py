"""Package rollup prefers exit_disposition_receipt over lane x3 mirror."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.disposition_authority import (
    EXIT_DISPOSITION_RECEIPT_ARTIFACT,
    resolve_lane_x3_from_artifact_refs,
)
def test_resolve_lane_x3_prefers_exit_disposition_receipt(tmp_path: Path) -> None:
    repo = tmp_path
    lane_dir = repo / "artifacts/apps_rg/runtime_proofs/headline/real/run1"
    lane_dir.mkdir(parents=True)
    (lane_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_REVIEW_SECTION", "disposition_authority": "lane"}),
        encoding="utf-8",
    )
    (lane_dir / EXIT_DISPOSITION_RECEIPT_ARTIFACT).write_text(
        json.dumps(
            {
                "x3_code": "X3_ALLOW",
                "disposition_authority": "lane",
                "section_x3_mirror_only": True,
                "x3_disposition": {"x3_code": "X3_ALLOW"},
            }
        ),
        encoding="utf-8",
    )
    refs = {
        "x3_disposition.json": "artifacts/apps_rg/runtime_proofs/headline/real/run1/x3_disposition.json",
        EXIT_DISPOSITION_RECEIPT_ARTIFACT: (
            f"artifacts/apps_rg/runtime_proofs/headline/real/run1/{EXIT_DISPOSITION_RECEIPT_ARTIFACT}"
        ),
    }
    resolved = resolve_lane_x3_from_artifact_refs(artifact_refs=refs, repo_root=repo)
    assert resolved["x3_code"] == "X3_ALLOW"
    assert resolved["authoritative_artifact"] == EXIT_DISPOSITION_RECEIPT_ARTIFACT


def test_lane_mirror_cannot_claim_spine_without_spine_authority(tmp_path: Path) -> None:
    repo = tmp_path
    lane_rel = "artifacts/apps_rg/runtime_proofs/headline/real/run1"
    lane_dir = repo / lane_rel
    lane_dir.mkdir(parents=True)
    (lane_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "spine_x3_claimed": True, "disposition_authority": "lane"}),
        encoding="utf-8",
    )
    refs = {"x3_disposition.json": f"{lane_rel}/x3_disposition.json"}
    resolved = resolve_lane_x3_from_artifact_refs(artifact_refs=refs, repo_root=repo)
    assert resolved["spine_x3_claimed"] is False or resolved.get("disposition_authority") != "spine"
    raw = json.loads((lane_dir / "x3_disposition.json").read_text(encoding="utf-8"))
    assert raw.get("spine_x3_claimed") is True
    assert raw.get("disposition_authority") == "lane"
