"""Smoke repairs against canonical full_resume proof display texts (read-only artifacts)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PROOF = REPO / "artifacts/apps_rg/runtime_proofs/full_resume_0e41a1c13cfe/lanes"


@pytest.mark.skipif(not PROOF.is_dir(), reason="canonical proof bundle not present")
def test_exec_summary_proof_text_repair_passes_credential_gate() -> None:
    from apps_rg.runtime.sections.section_authority_repairs import (
        strip_exec_summary_credential_dump_sentences,
    )
    from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_no_credential_dump

    raw = (PROOF / "executive_summary/resume_display_text.txt").read_text(encoding="utf-8")
    repaired, removed = strip_exec_summary_credential_dump_sentences(raw)
    assert removed, "expected credential sentence in stale proof"
    ok, _ = check_exec_summary_no_credential_dump(repaired)
    assert ok is True


@pytest.mark.skipif(not PROOF.is_dir(), reason="canonical proof bundle not present")
def test_ibm_narrative_proof_text_repair_strips_meta_disclaimer() -> None:
    from apps_rg.runtime.sections.section_authority_repairs import sanitize_ibm_narrative_display_text
    from apps_rg.runtime.validators.resume_narrative_display_x2 import (
        check_ibm_narrative_no_meta_disclaimer_in_display,
    )

    raw = (PROOF / "ibm_narrative/ibm_narrative_output.txt").read_text(encoding="utf-8").strip()
    cleaned, changed = sanitize_ibm_narrative_display_text(raw)
    assert changed is True
    ok, hits = check_ibm_narrative_no_meta_disclaimer_in_display(cleaned)
    assert ok is True
    assert not hits
