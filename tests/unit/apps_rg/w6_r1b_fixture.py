"""Shared W6 R1B/UWG fixture artifacts — display text + ingest chunks."""

from __future__ import annotations

import json
from pathlib import Path

from tests.unit.apps_rg.l5_uwg_fixture import write_verified_l5_sealed_artifact


def write_w6_eligible_run_artifacts(
    ad: Path,
    *,
    section_id: str = "executive_summary",
) -> None:
    """Minimal lane dir that passes post-exit R1B and verified-L5 admission."""

    ad.mkdir(parents=True, exist_ok=True)
    display = (
        "Engineering executive builds governed agentic AI platforms for regulated enterprise delivery. "
        "The leader scales deterministic routing and policy-gated execution across programs."
    )
    (ad / "l2_output.json").write_text(
        json.dumps(
            {
                "section_id": section_id,
                "resume_display_text": display,
                "claim_ledger": [
                    {
                        "claim_text": display[:80],
                        "source_fact_ids": ["fact_exec_001"],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (ad / "generated_resume.json").write_text(
        json.dumps({"sections": {section_id: display}}, indent=2) + "\n",
        encoding="utf-8",
    )
    write_verified_l5_sealed_artifact(
        ad,
        request_id=f"req:{ad.name}",
        run_id=ad.name,
        trace_id=f"trace:{ad.name}",
    )


def seed_w7_fixtures(repo: Path) -> None:
    w7 = repo / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    w7.mkdir(parents=True, exist_ok=True)
    src = (
        Path(__file__).resolve().parents[3]
        / "artifacts"
        / "apps_rg"
        / "r1b_semantic_cache"
        / "w7_fixtures"
    )
    if not src.is_dir():
        raise FileNotFoundError(f"w7 fixtures missing: {src}")
    for file in src.glob("*.json"):
        (w7 / file.name).write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
