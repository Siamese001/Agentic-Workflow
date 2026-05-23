"""Upsert C0.2-eligible atoms from a section proof pool into fact_vectors (operator tool)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c02_fact_vector_ingest import maybe_upsert_c02_fact_vectors
from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
from apps_rg.runtime.sections.competencies_lane_defaults import (
    BRIEFING_DEFAULT,
    JD_TEXT_DEFAULT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
)
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--section", default="competencies")
    parser.add_argument("--artifact-dir", type=Path, default=None)
    args = parser.parse_args()
    import argparse as ap

    ns = ap.Namespace(
        target_company=TARGET_COMPANY_DEFAULT,
        target_title=TARGET_TITLE_DEFAULT,
        target_role=TARGET_TITLE_DEFAULT,
        jd_text=JD_TEXT_DEFAULT,
        briefing=BRIEFING_DEFAULT,
        selected_role_fact_set="",
        broad_skills_ledger_path="",
        base_resume_ref="",
        provider="qwen_vllm",
    )
    pool, _, _, _, front = load_section_proof_for_lane(
        section_id=args.section,
        args=ns,
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    del front
    c02 = fetch_c02_evidence_atoms(section_id=args.section, pool=pool, repo_root=REPO)
    receipt = maybe_upsert_c02_fact_vectors(
        list(c02.get("atoms") or []),
        section_id=args.section,
        artifact_dir=args.artifact_dir,
        repo_root=REPO,
    )
    print(receipt)
    return 0 if receipt.get("status") in ("PASS", "NOT_APPLICABLE", "EMPTY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
