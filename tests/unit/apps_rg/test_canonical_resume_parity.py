"""R4 ``build_raw_request_for_r4`` and ``resolve_resume_for_lanes`` share resume digest."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4
from apps_rg.runtime.resume_resolution import (
    canonical_resume_digest,
    resolve_resume_for_lanes,
)


def test_default_resume_digest_parity() -> None:
    """Same default JSON material yields identical digest on modular resolver and R4 raw request."""
    repo = Path(__file__).resolve().parents[3]
    rr = resolve_resume_for_lanes(repo_root=repo)
    raw = build_raw_request_for_r4(
        target_company="Co",
        target_role="Role",
        resume_path="",
        source_resume_text="",
    )
    assert raw["resume_hash"] == rr.resume_digest
    assert raw["resume_hash"] == canonical_resume_digest(rr.resume_payload)


def test_explicit_file_resume_parity(tmp_path: Path) -> None:
    p = tmp_path / "base.json"
    doc = {"id": "test-resume", "facts": {"employment": []}}
    p.write_text(json.dumps(doc), encoding="utf-8")
    rr = resolve_resume_for_lanes(
        source_resume_ref=str(p),
        require_run_specific=True,
        repo_root=tmp_path,
    )
    raw = build_raw_request_for_r4(
        target_company="Co",
        target_role="Role",
        resume_path=str(p),
        source_resume_text="",
    )
    assert raw["resume_hash"] == rr.resume_digest
