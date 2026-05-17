"""W6 integration tests: G21/G22 Exit evidence — combined receipt validation.

Plan 02 W6 acceptance criteria:
- G21 gates ACTIVE via apps-owned receipts: headline SVP Engineering | X | Y | Z (fixed prefix + X/Y/Z
  segments), bullet counts, all P0 sections
- G22 gates ACTIVE via apps-owned receipts: metrics preserved from source, verbatim sections hash-match
- NO canonical G21/G22 changes: all evidence is app-specific, consumed by generic Exit eval
- UNKNOWN is never PASS
"""
from __future__ import annotations

import unittest

from apps_rg.runtime.bindings.exit_evidence_receipts import (
    AppsRgClaimSupportMap,
    AppsRgMetricPreservationEnvelope,
    AppsRgSectionValidationReceipt,
    AppsRgVerbatimIntegrityReceipt,
)


def _make_section_receipt(
    *,
    headline_valid: bool = True,
    sections_valid: bool = True,
    bullet_count_valid: bool = True,
) -> AppsRgSectionValidationReceipt:
    return AppsRgSectionValidationReceipt(
        headline_format_valid=headline_valid,
        headline_x="Agentic AI Platforms",
        headline_y="Distributed AI Systems",
        headline_z="Enterprise Governance Architecture",
        section_count_expected=7,
        section_count_actual=7 if sections_valid else 5,
        sections_valid=sections_valid,
        bullet_counts={
            "headline": 0,
            "executive_summary": 3,
            "unify_consulting": 6,
            "ibm": 5,
            "insurtech": 3,
            "ey": 3,
            "early_career": 1,
        },
        bullet_count_valid=bullet_count_valid,
        source_digest="sha256:source_master_abc",
    )


def _make_metric_envelope(*, invented: bool = False) -> AppsRgMetricPreservationEnvelope:
    invented_metrics = ["revenue_growth_pct"] if invented else []
    output_metrics: dict = {
        "years_experience": 20,
        "team_size_led": 50,
        "budget_managed_usd": 10_000_000,
    }
    if invented:
        output_metrics["revenue_growth_pct"] = 200  # hallucinated
    return AppsRgMetricPreservationEnvelope(
        source_metrics={
            "years_experience": 20,
            "team_size_led": 50,
            "budget_managed_usd": 10_000_000,
        },
        output_metrics=output_metrics,
        preserved_metrics=["years_experience", "team_size_led", "budget_managed_usd"],
        invented_metrics=invented_metrics,
        omitted_metrics=[],
        source_resume_hash="sha256:source_master_abc",
    )


def _make_verbatim_receipt(*, all_match: bool = True) -> AppsRgVerbatimIntegrityReceipt:
    edu_out = "sha256:edu_abc" if all_match else "sha256:edu_CHANGED"
    return AppsRgVerbatimIntegrityReceipt(
        education_source_hash="sha256:edu_abc",
        certifications_source_hash="sha256:cert_abc",
        early_career_source_hash="sha256:early_abc",
        education_output_hash=edu_out,
        certifications_output_hash="sha256:cert_abc",
        early_career_output_hash="sha256:early_abc",
        education_verbatim=all_match,
        certifications_verbatim=True,
        early_career_verbatim=True,
        source_resume_hash="sha256:source_master_abc",
    )


def _make_claim_support_map(*, has_unsupported: bool = False) -> AppsRgClaimSupportMap:
    claims = [
        {"claim_id": "c1", "text": "Led 50-person engineering team"},
        {"claim_id": "c2", "text": "Managed $10M budget"},
    ]
    blocked: list[str] = []
    status = {"c1": "PASS", "c2": "PASS"}
    if has_unsupported:
        claims.append({"claim_id": "c3", "text": "Grew revenue by 200%"})
        status["c3"] = "UNSUPPORTED"
        blocked.append("c3")
    return AppsRgClaimSupportMap(
        claims=claims,
        claim_evidence_refs={"c1": ["span_1a"], "c2": ["span_2a"]},
        claim_support_status=status,
        blocked_claims=blocked,
        source_resume_hash="sha256:source_master_abc",
        jd_hash="sha256:jd_abc",
        briefing_hash="sha256:brief_abc",
    )


class TestG21GatesActiveViaReceipts(unittest.TestCase):
    """G21: Schema/Completeness, headline SVP Engineering | X | Y | Z style, section counts, bullet counts."""

    def test_g21_headline_xyz_format_valid(self) -> None:
        """G21 PASS: Headline has fixed SVP Engineering prefix plus X/Y/Z populated."""
        receipt = _make_section_receipt()
        self.assertTrue(receipt.headline_format_valid)
        self.assertNotEqual(receipt.headline_x, "")
        self.assertNotEqual(receipt.headline_y, "")
        self.assertNotEqual(receipt.headline_z, "")

    def test_g21_headline_xyz_format_invalid_blocks(self) -> None:
        """G21 FAIL: Missing headline parts means invalid and cannot be treated as PASS."""
        receipt = _make_section_receipt(headline_valid=False)
        self.assertFalse(receipt.headline_format_valid)
        self.assertFalse(receipt.all_valid)

    def test_g21_all_p0_sections_present(self) -> None:
        """G21 PASS: All 7 P0 sections accounted for in bullet_counts."""
        receipt = _make_section_receipt()
        self.assertTrue(receipt.sections_valid)
        self.assertEqual(receipt.section_count_actual, 7)
        p0_sections = {
            "headline", "executive_summary", "unify_consulting",
            "ibm", "insurtech", "ey", "early_career",
        }
        self.assertEqual(set(receipt.bullet_counts.keys()), p0_sections)

    def test_g21_section_count_mismatch_fails(self) -> None:
        """G21 FAIL: Fewer sections than expected is a schema violation."""
        receipt = _make_section_receipt(sections_valid=False)
        self.assertFalse(receipt.sections_valid)
        self.assertNotEqual(receipt.section_count_expected, receipt.section_count_actual)
        self.assertFalse(receipt.all_valid)

    def test_g21_bullet_count_violation_blocks(self) -> None:
        """G21 FAIL: Invalid bullet counts — all_valid must be False."""
        receipt = _make_section_receipt(bullet_count_valid=False)
        self.assertFalse(receipt.bullet_count_valid)
        self.assertFalse(receipt.all_valid)

    def test_g21_all_valid_only_when_all_pass(self) -> None:
        """G21 requires headline + section count + bullet count all valid."""
        self.assertTrue(_make_section_receipt().all_valid)
        self.assertFalse(_make_section_receipt(headline_valid=False).all_valid)
        self.assertFalse(_make_section_receipt(sections_valid=False).all_valid)
        self.assertFalse(_make_section_receipt(bullet_count_valid=False).all_valid)


class TestG22GatesActiveViaReceipts(unittest.TestCase):
    """G22: Quality/Safety — metric preservation, verbatim hash integrity."""

    def test_g22_metric_preservation_no_invention(self) -> None:
        """G22 PASS: All metrics from source preserved, zero invented."""
        envelope = _make_metric_envelope()
        self.assertFalse(envelope.has_invention)
        self.assertEqual(envelope.preservation_rate, 1.0)

    def test_g22_invented_metric_detected(self) -> None:
        """G22 FAIL: Any metric not in source resume must be flagged as invention."""
        envelope = _make_metric_envelope(invented=True)
        self.assertTrue(envelope.has_invention)
        self.assertIn("revenue_growth_pct", envelope.invented_metrics)

    def test_g22_verbatim_sections_hash_match(self) -> None:
        """G22 PASS: Education, certifications, early career match source exactly."""
        receipt = _make_verbatim_receipt()
        self.assertTrue(receipt.all_verbatim)
        self.assertTrue(receipt.education_verbatim)
        self.assertTrue(receipt.certifications_verbatim)
        self.assertTrue(receipt.early_career_verbatim)

    def test_g22_verbatim_mutation_detected(self) -> None:
        """G22 FAIL: Education section mutation detected via hash mismatch."""
        receipt = _make_verbatim_receipt(all_match=False)
        self.assertFalse(receipt.all_verbatim)
        self.assertFalse(receipt.education_verbatim)

    def test_g22_claim_support_all_backed(self) -> None:
        """G22 PASS: All claims backed by source evidence."""
        claim_map = _make_claim_support_map()
        self.assertEqual(claim_map.blocked_claim_count, 0)
        self.assertEqual(claim_map.unsupported_rate, 0.0)

    def test_g22_unsupported_claim_blocked(self) -> None:
        """G22 FAIL: Claim without source support is blocked — not silently passed."""
        claim_map = _make_claim_support_map(has_unsupported=True)
        self.assertGreater(claim_map.blocked_claim_count, 0)
        self.assertIn("c3", claim_map.blocked_claims)
        self.assertGreater(claim_map.unsupported_rate, 0.0)


class TestG21G22NoCanonicalGateChanges(unittest.TestCase):
    """Evidence is app-owned — canonical G21/G22 gate modules are NOT modified."""

    def test_receipt_types_are_app_owned(self) -> None:
        """Receipt types live in apps_rg, not agentic_core."""
        import apps_rg.runtime.bindings.exit_evidence_receipts as mod
        module_path = mod.__spec__.origin  # type: ignore[union-attr]
        self.assertIn("apps_rg", module_path)
        self.assertNotIn("agentic_core", module_path)

    def test_receipts_do_not_import_canonical_g21_g22(self) -> None:
        """Receipt module must not import from canonical G21/G22 gate modules."""
        import ast
        import importlib.util
        import pathlib

        spec = importlib.util.find_spec(
            "apps_rg.runtime.bindings.exit_evidence_receipts"
        )
        assert spec is not None and spec.origin is not None
        source = pathlib.Path(spec.origin).read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden_patterns = ("g21", "g22", "gate_mesh", "gate_verdict")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module.lower()
                elif isinstance(node, ast.Import):
                    module = " ".join(alias.name.lower() for alias in node.names)
                for pattern in forbidden_patterns:
                    self.assertNotIn(
                        pattern,
                        module,
                        msg=f"exit_evidence_receipts imports canonical gate module matching '{pattern}'",
                    )

    def test_all_receipt_types_exported(self) -> None:
        """All four receipt types are exported from exit_evidence_receipts."""
        from apps_rg.runtime.bindings import exit_evidence_receipts as m

        self.assertIn("AppsRgSectionValidationReceipt", m.__all__)
        self.assertIn("AppsRgMetricPreservationEnvelope", m.__all__)
        self.assertIn("AppsRgVerbatimIntegrityReceipt", m.__all__)
        self.assertIn("AppsRgClaimSupportMap", m.__all__)


class TestUnknownIsNeverPass(unittest.TestCase):
    """UNKNOWN is never PASS — missing receipts cannot be treated as clean."""

    def test_section_receipt_required_for_g21_pass(self) -> None:
        """G21 PASS requires explicit all_valid=True — cannot be inferred from absence."""
        receipt = _make_section_receipt(headline_valid=False)
        # A failed receipt must NOT be re-interpreted as valid
        self.assertFalse(receipt.all_valid)

    def test_metric_envelope_required_for_g22_pass(self) -> None:
        """G22 PASS requires explicit has_invention=False — cannot default to clean."""
        envelope = _make_metric_envelope(invented=True)
        self.assertTrue(envelope.has_invention)
        # Non-zero invented_metrics means G22 UNKNOWN/FAIL, not PASS
        self.assertNotEqual(len(envelope.invented_metrics), 0)

    def test_verbatim_receipt_required_for_g22_pass(self) -> None:
        """G22 PASS for verbatim sections requires all_verbatim=True — mismatch is FAIL."""
        receipt = _make_verbatim_receipt(all_match=False)
        self.assertFalse(receipt.all_verbatim)

    def test_claim_support_required_not_assumed(self) -> None:
        """Blocked claims cannot be silently passed — explicit check required."""
        claim_map = _make_claim_support_map(has_unsupported=True)
        self.assertGreater(claim_map.blocked_claim_count, 0)
        # unsupported_rate > 0 means G22 cannot be PASS
        self.assertGreater(claim_map.unsupported_rate, 0.0)


class TestG21G22IntegrationFullBundle(unittest.TestCase):
    """Integration: all four receipt types together form a complete G21/G22 evidence bundle."""

    def test_full_bundle_clean_run(self) -> None:
        """Clean run: all receipts PASS, no invention, all verbatim, no blocked claims."""
        section = _make_section_receipt()
        metrics = _make_metric_envelope()
        verbatim = _make_verbatim_receipt()
        claims = _make_claim_support_map()

        self.assertTrue(section.all_valid)
        self.assertFalse(metrics.has_invention)
        self.assertTrue(verbatim.all_verbatim)
        self.assertEqual(claims.blocked_claim_count, 0)

        # Shared provenance hash ties all receipts to same source
        hashes = {
            section.source_digest,
            metrics.source_resume_hash,
            verbatim.source_resume_hash,
            claims.source_resume_hash,
        }
        # All reference the same source resume
        self.assertEqual(len(hashes), 1)

    def test_full_bundle_any_fail_means_g21_g22_not_pass(self) -> None:
        """If any receipt fails, the combined G21/G22 evidence is not PASS."""
        section = _make_section_receipt(headline_valid=False)  # G21 fail
        metrics = _make_metric_envelope()
        verbatim = _make_verbatim_receipt()
        claims = _make_claim_support_map()

        all_pass = (
            section.all_valid
            and not metrics.has_invention
            and verbatim.all_verbatim
            and claims.blocked_claim_count == 0
        )
        self.assertFalse(all_pass)

    def test_full_bundle_invention_fails_g22(self) -> None:
        """Invented metric in one envelope makes G22 FAIL even if other receipts pass."""
        section = _make_section_receipt()
        metrics = _make_metric_envelope(invented=True)  # G22 fail
        verbatim = _make_verbatim_receipt()
        claims = _make_claim_support_map()

        all_pass = (
            section.all_valid
            and not metrics.has_invention
            and verbatim.all_verbatim
            and claims.blocked_claim_count == 0
        )
        self.assertFalse(all_pass)


if __name__ == "__main__":
    unittest.main()
