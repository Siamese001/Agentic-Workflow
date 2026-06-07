"""Contract: apps_rg section directories do not shadow core L7 proof."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.section_l7_binding_manifest import (
    CLASS_CORE_L7_UNTRUSTED,
    build_section_l7_binding_manifest,
)


def test_fake_runtime_proof_bundle_is_drift(tmp_path: Path) -> None:
    (tmp_path / "runtime_proof_bundle.json").write_text(
        json.dumps({"producer_component": "apps_rg.runtime.section_lane"}),
        encoding="utf-8",
    )
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=tmp_path,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["runtime_proof_bundle.json"] == CLASS_CORE_L7_UNTRUSTED
    assert doc["runtime_proof_bundle_99_emitted"] is False
