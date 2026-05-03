"""W2.P2.2 + AG-RG-013 — Static headline preservation contract.

Plan: apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4
Phase: W2.P2.2 (resolved AG-RG-013 option C)

AG-RG-013 (resolved 2026-05-03, option C — Hybrid): owner.headline is the
static brand line. narrative_pass MUST NOT overwrite resume_data["headline"]
with HOP-4A output. HOP-4A output is preserved as a side artifact for
AG-RG-014 reconciliation against HOP-4B.

These tests are STRUCTURAL — they grep narrative_pass.py source. Live
verification of the static-preservation invariant is in W4.P1.
"""

from __future__ import annotations

from pathlib import Path


_NARRATIVE_PASS = (
    Path(__file__).resolve().parents[2]
    / "apps_rg" / "scripts" / "narrative_pass.py"
)


class TestAgRg013StaticPreservation:
    """narrative_pass preserves static owner.headline per AG-RG-013/C."""

    def test_narrative_pass_does_not_overwrite_headline(self):
        """resume_data['headline'] must not be assigned head_res output."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        # The forbidden assignment was the bug we just fixed
        forbidden = 'resume_data["headline"] = head_res.winner.text'
        assert forbidden not in source, (
            f"AG-RG-013/C violated: narrative_pass overwrites owner.headline. "
            f"Forbidden line: {forbidden!r}"
        )

    def test_narrative_pass_persists_headline_candidate(self):
        """HOP-4A output is saved as a side artifact."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert "headline_candidate.json" in source, (
            "AG-RG-013/C requires persisting HOP-4A output as side artifact"
        )

    def test_ag_rg_013_decision_documented(self):
        """The AG-RG-013 decision must be referenced in the source."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert "AG-RG-013" in source, "AG-RG-013 must be cited at the call site"

    def test_hop_4a_still_invoked(self):
        """HOP-4A still runs (only its destination changed)."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert "generate_headline(" in source

    def test_hop_4b_still_writes_executive_summary(self):
        """HOP-4B still owns executive_summary until AG-RG-014 reconciles."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert 'resume_data["executive_summary"] = exec_res.winner.text' in source, (
            "HOP-4B authority over executive_summary preserved pending AG-RG-014"
        )
