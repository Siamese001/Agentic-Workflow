"""Acceptance test: bullets with >20% 4-gram overlap against E0 examples must fail gate.

W5 acceptance test (Bullet Proof Bundle Redesign):
- Verifies x2_e0_example_ngram_overlap gate catches E0 leakage.
- Bullets with verbatim E0 prose fail (warn_only=False).
- Organic bullets with different phrasing pass.
- Confirms gate is wired in WARN mode in X2 runners (does not hard-block production).
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    E0_EXAMPLE_NGRAM_THRESHOLD,
    check_bullet_e0_example_ngram_overlap,
    compute_max_ngram_overlap,
    run_bullet_ngram_overlap_gates,
)


# Fabricated E0 example texts (representative of what might appear in an E0 examples block).
_SAMPLE_E0_EXAMPLES = [
    "Designed and deployed a multi-tenant agentic AI platform serving Fortune 500 financial institutions at enterprise scale.",
    "Architected data governance frameworks enabling near-real-time lineage tracking with 99.9% SLA compliance.",
    "Built reusable cloud-native microservices reducing infrastructure overhead by 30% across regulated environments.",
]


class TestE0NgramOverlapMath:
    def test_verbatim_e0_has_full_overlap(self) -> None:
        verbatim = _SAMPLE_E0_EXAMPLES[0]
        overlap = compute_max_ngram_overlap(verbatim, verbatim, n=4)
        assert overlap == 1.0

    def test_rephrased_e0_has_lower_overlap(self) -> None:
        """Rephrased version of E0 example should have substantially lower overlap."""
        rephrased = (
            "Deployed a multi-tenant AI platform for Fortune 500 financial services clients "
            "achieving enterprise-scale adoption."
        )
        overlap = compute_max_ngram_overlap(rephrased, _SAMPLE_E0_EXAMPLES[0], n=4)
        assert overlap < 0.8, f"Expected lower overlap for rephrased text, got {overlap}"

    def test_organic_bullet_has_low_e0_overlap(self) -> None:
        organic = (
            "Engineered cloud infrastructure modernization yielding 30% cost reduction "
            "across legacy IBM data center environments."
        )
        overlap = compute_max_ngram_overlap(organic, " ".join(_SAMPLE_E0_EXAMPLES), n=4)
        assert overlap < E0_EXAMPLE_NGRAM_THRESHOLD, (
            f"Expected overlap < {E0_EXAMPLE_NGRAM_THRESHOLD}, got {overlap}"
        )


class TestE0LeakageGate:
    def test_verbatim_e0_copy_fails_gate(self) -> None:
        result = check_bullet_e0_example_ngram_overlap(
            "bul_ibm_001",
            _SAMPLE_E0_EXAMPLES[0],
            _SAMPLE_E0_EXAMPLES,
            warn_only=False,
        )
        assert not result.passed, "Verbatim E0 copy should fail the gate"
        assert result.overlap_fraction > E0_EXAMPLE_NGRAM_THRESHOLD
        assert result.failure_reason is not None

    def test_organic_bullet_passes_e0_gate(self) -> None:
        organic = (
            "Engineered cloud infrastructure modernization reducing overhead by 30% "
            "for regulated financial environments at enterprise scale."
        )
        result = check_bullet_e0_example_ngram_overlap(
            "bul_ibm_001",
            organic,
            _SAMPLE_E0_EXAMPLES,
            warn_only=False,
        )
        assert result.overlap_fraction <= E0_EXAMPLE_NGRAM_THRESHOLD, (
            f"Organic bullet should have low E0 overlap, got {result.overlap_fraction}"
        )
        assert result.passed

    def test_warn_only_mode_always_passes_gate_result(self) -> None:
        """In WARN mode (default), gate result.passed is always True."""
        result = check_bullet_e0_example_ngram_overlap(
            "bul_ibm_001",
            _SAMPLE_E0_EXAMPLES[0],  # verbatim copy
            _SAMPLE_E0_EXAMPLES,
            warn_only=True,
        )
        assert result.passed, "In WARN mode, gate result.passed must always be True"
        assert result.failure_reason is not None, "WARN mode still records violation reason"

    def test_empty_e0_texts_produces_zero_overlap(self) -> None:
        result = check_bullet_e0_example_ngram_overlap(
            "bul_ibm_001",
            "Architected cloud-native AI platforms for enterprise clients.",
            [],
            warn_only=False,
        )
        assert result.overlap_fraction == 0.0
        assert result.passed


class TestE0GateWiredInRunners:
    """Verify E0 gate is wired into IBM and Unify X2 runners in WARN mode."""

    def _make_ibm_bullets(self) -> list[dict]:
        return [
            {"bullet_id": f"bul_ibm_00{i}",
             "bullet_text": f"Architected cloud-native AI platform {i} achieving 99.9% uptime for regulated clients."}
            for i in range(1, 6)
        ]

    def test_e0_gate_wired_in_ibm_runner(self) -> None:
        from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates

        bullets = self._make_ibm_bullets()
        parsed = {
            "bullets": bullets,
            "selected_fact_plan": {
                "selection_method": "augmented_skills_graph_ibm_bullets_phase2_track_ranked",
                "facts": [
                    {"fact_id": b["bullet_id"], "claim_text": b["bullet_text"],
                     "career_track": "track_data_tech_cloud_ml",
                     "graph_hop_path": ["hop1"], "graph_phase2_track_proof": True}
                    for b in bullets
                ],
            },
            "claim_ledger": [
                {"claim_text": b["bullet_text"], "source_fact_ids": [b["bullet_id"]]}
                for b in bullets
            ],
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        }
        results = run_ibm_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            claim_ledger=list(parsed["claim_ledger"]),
            allowed_fact_ids={b["bullet_id"] for b in bullets},
            jd_text="",
            runtime_generation_status="REAL_LLM",
        )
        gate_ids = {r.gate_id for r in results}
        assert "x2_e0_example_ngram_overlap_ibm" in gate_ids, (
            f"E0 ngram gate must be wired into IBM X2 runner. Found gates: {sorted(gate_ids)}"
        )

    def test_e0_gate_wired_in_unify_runner(self) -> None:
        from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates

        bullets = [
            {"bullet_id": f"bul_unify_00{i}",
             "bullet_text": f"Engineered agentic AI platform capability {i} for enterprise deployments.",
             "has_metric": False, "metric_raw": None,
             "source_fact_ids": [f"bul_unify_00{i}"]}
            for i in range(1, 7)
        ]
        parsed = {
            "bullets": bullets,
            "selected_fact_plan": {
                "selection_method": "augmented_skills_graph_unify_bullets_track_ranked",
                "facts": [
                    {"fact_id": b["bullet_id"], "claim_text": b["bullet_text"],
                     "ledger_candidate_fact_id": f"fact_engineering_platform_00{i}"}
                    for i, b in enumerate(bullets, 1)
                ],
            },
            "claim_ledger": [
                {"claim_text": b["bullet_text"], "source_fact_ids": [b["bullet_id"]]}
                for b in bullets
            ],
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        }
        results = run_unify_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            claim_ledger=list(parsed["claim_ledger"]),
            allowed_fact_ids={b["bullet_id"] for b in bullets},
            jd_text="",
            runtime_generation_status="REAL_LLM",
        )
        gate_ids = {r.gate_id for r in results}
        assert "x2_e0_example_ngram_overlap_unify" in gate_ids, (
            f"E0 ngram gate must be wired into Unify X2 runner. Found gates: {sorted(gate_ids)}"
        )

    def test_e0_gate_in_warn_mode_passes_all_in_runner(self) -> None:
        """E0 gate in WARN mode must not block production runs."""
        from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates

        bullets = self._make_ibm_bullets()
        parsed = {
            "bullets": bullets,
            "selected_fact_plan": {
                "selection_method": "augmented_skills_graph_ibm_bullets_phase2_track_ranked",
                "facts": [
                    {"fact_id": b["bullet_id"], "claim_text": b["bullet_text"],
                     "career_track": "track_data_tech_cloud_ml",
                     "graph_hop_path": ["hop1"], "graph_phase2_track_proof": True}
                    for b in bullets
                ],
            },
            "claim_ledger": [
                {"claim_text": b["bullet_text"], "source_fact_ids": [b["bullet_id"]]}
                for b in bullets
            ],
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        }
        results = run_ibm_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            claim_ledger=list(parsed["claim_ledger"]),
            allowed_fact_ids={b["bullet_id"] for b in bullets},
            jd_text="",
            runtime_generation_status="REAL_LLM",
        )
        e0_results = [r for r in results if "e0_example" in r.gate_id]
        assert e0_results, "Must have at least one E0 gate result"
        for r in e0_results:
            assert r.pass_, f"E0 gate in WARN mode must pass: {r.gate_id} => {r.failure_reason}"
