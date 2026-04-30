"""Tests for apps_research.provenance — per-claim provenance skeleton.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (P3 NEXT_STEP)
"""
from __future__ import annotations

import unittest

from apps_research.provenance import (
    ClaimWithProvenance,
    ConfidenceBand,
    ProvenanceLedger,
    ProvenanceMode,
    ProvenanceValidationResult,
)


class TestConfidenceBand(unittest.TestCase):
    def test_high_threshold(self) -> None:
        self.assertEqual(ConfidenceBand.from_score(0.85), ConfidenceBand.HIGH)
        self.assertEqual(ConfidenceBand.from_score(0.99), ConfidenceBand.HIGH)
        self.assertEqual(ConfidenceBand.from_score(1.0), ConfidenceBand.HIGH)

    def test_medium_threshold(self) -> None:
        self.assertEqual(ConfidenceBand.from_score(0.60), ConfidenceBand.MEDIUM)
        self.assertEqual(ConfidenceBand.from_score(0.84), ConfidenceBand.MEDIUM)

    def test_low_threshold(self) -> None:
        self.assertEqual(ConfidenceBand.from_score(0.40), ConfidenceBand.LOW)
        self.assertEqual(ConfidenceBand.from_score(0.59), ConfidenceBand.LOW)

    def test_speculative_threshold(self) -> None:
        self.assertEqual(ConfidenceBand.from_score(0.0), ConfidenceBand.SPECULATIVE)
        self.assertEqual(ConfidenceBand.from_score(0.39), ConfidenceBand.SPECULATIVE)

    def test_out_of_range_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ConfidenceBand.from_score(1.5)
        with self.assertRaises(ValueError):
            ConfidenceBand.from_score(-0.1)


class TestClaimWithProvenance(unittest.TestCase):
    def _claim(self, **overrides) -> ClaimWithProvenance:
        defaults = dict(
            claim_id="c1",
            text="Agentic systems exhibit emergent compositional behavior.",
            supporting_source_ids=("src-001",),
            confidence_score=0.8,
            confidence_band=ConfidenceBand.MEDIUM,
        )
        defaults.update(overrides)
        return ClaimWithProvenance(**defaults)

    def test_minimal_construction(self) -> None:
        claim = self._claim()
        self.assertEqual(claim.claim_id, "c1")
        self.assertEqual(claim.supporting_source_ids, ("src-001",))

    def test_zero_sources_rejected(self) -> None:
        with self.assertRaises(Exception):
            self._claim(supporting_source_ids=())

    def test_empty_text_rejected(self) -> None:
        with self.assertRaises(Exception):
            self._claim(text="too short")

    def test_out_of_range_score_rejected(self) -> None:
        with self.assertRaises(Exception):
            self._claim(confidence_score=1.5)

    def test_round_trip(self) -> None:
        claim = self._claim(supporting_source_ids=("a", "b", "c"))
        rebuilt = ClaimWithProvenance.model_validate(claim.model_dump())
        self.assertEqual(claim.supporting_source_ids, rebuilt.supporting_source_ids)


class TestProvenanceLedger(unittest.TestCase):
    def _make_claim(self, claim_id: str, sources: tuple[str, ...]) -> ClaimWithProvenance:
        return ClaimWithProvenance(
            claim_id=claim_id,
            text=f"Test claim {claim_id} with reasonable length.",
            supporting_source_ids=sources,
            confidence_score=0.75,
            confidence_band=ConfidenceBand.MEDIUM,
        )

    def test_empty_ledger_validates(self) -> None:
        ledger = ProvenanceLedger()
        v = ledger.validate(known_source_ids={"a", "b"})
        self.assertTrue(v.passed)
        self.assertEqual(v.n_claims, 0)

    def test_all_sources_known_passes(self) -> None:
        ledger = ProvenanceLedger()
        ledger.add(self._make_claim("c1", ("src-1",)))
        ledger.add(self._make_claim("c2", ("src-1", "src-2")))
        v = ledger.validate(known_source_ids={"src-1", "src-2", "src-3"})
        self.assertTrue(v.passed)
        self.assertEqual(v.n_claims, 2)
        self.assertEqual(v.n_orphan_claims, 0)
        # src-3 is known but uncited — surfaces as soft warning.
        self.assertEqual(v.unsupported_source_ids, ("src-3",))

    def test_unknown_source_id_fails(self) -> None:
        ledger = ProvenanceLedger()
        ledger.add(self._make_claim("c1", ("src-real", "src-fabricated")))
        v = ledger.validate(known_source_ids={"src-real"})
        self.assertFalse(v.passed)
        self.assertEqual(v.n_orphan_claims, 1)
        self.assertEqual(v.orphan_claim_ids, ("c1",))
        self.assertEqual(len(v.violation_strings), 1)
        self.assertIn("src-fabricated", v.violation_strings[0])

    def test_jsonable_serialization(self) -> None:
        ledger = ProvenanceLedger()
        ledger.add(self._make_claim("c1", ("src-1",)))
        ledger.add(self._make_claim("c2", ("src-1", "src-2")))
        out = ledger.to_jsonable()
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["claim_id"], "c1")
        self.assertEqual(out[1]["supporting_source_ids"], ["src-1", "src-2"])

    def test_add_many(self) -> None:
        ledger = ProvenanceLedger()
        ledger.add_many([
            self._make_claim("c1", ("a",)),
            self._make_claim("c2", ("b",)),
        ])
        self.assertEqual(len(ledger.claims), 2)


class TestProvenanceMode(unittest.TestCase):
    def test_modes_distinct(self) -> None:
        self.assertNotEqual(ProvenanceMode.NONE, ProvenanceMode.SECTION)
        self.assertNotEqual(ProvenanceMode.SECTION, ProvenanceMode.PER_CLAIM)


if __name__ == "__main__":
    unittest.main()
