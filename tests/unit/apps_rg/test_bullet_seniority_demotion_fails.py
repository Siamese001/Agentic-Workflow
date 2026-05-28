"""Acceptance test: seniority demotion against base baseline must fail X2.

W5 acceptance test (Bullet Proof Bundle Redesign):
- Verifies x2_bullet_seniority_floor gate rejects weak-verb bullets.
- Verifies strong-verb + scale-signal bullets pass the floor.
- Verifies the gate correctly scores seniority proxies.
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.bullet_quality_floor_x2 import (
    SCALE_SIGNALS,
    SENIORITY_FLOOR_SCORE,
    STRONG_ACTION_VERBS,
    WEAK_ACTION_VERBS,
    check_bullet_seniority_floor,
    run_bullet_quality_floor_gates,
)


class TestSeniorityScore:
    def test_strong_verb_at_start_gives_positive_score(self) -> None:
        for verb in list(STRONG_ACTION_VERBS)[:10]:
            text = f"{verb.capitalize()} cloud-native AI platforms for regulated financial institutions."
            result = check_bullet_seniority_floor("bul_ibm_001", text)
            assert result.score >= 1, f"Expected score >= 1 for strong verb {verb!r}, got {result.score}"

    def test_weak_verb_at_start_decrements_score(self) -> None:
        weak_bullets = [
            "Supported cloud migration projects at enterprise scale.",
            "Helped the team deliver analytics solutions for financial clients.",
            "Assisted stakeholders in deploying AI platforms.",
        ]
        for text in weak_bullets:
            result = check_bullet_seniority_floor("bul_ibm_001", text)
            assert result.score < SENIORITY_FLOOR_SCORE, (
                f"Expected score < {SENIORITY_FLOOR_SCORE} for weak-verb bullet: {text[:60]}. "
                f"Got score={result.score}"
            )
            assert not result.passed, f"Weak verb bullet should fail gate: {text[:60]}"

    def test_scale_signal_increases_score(self) -> None:
        for signal in list(SCALE_SIGNALS)[:5]:
            text = f"Deployed AI platforms across {signal} deployments."
            result = check_bullet_seniority_floor("bul_ibm_001", text)
            signal_found = any(s.startswith("scale_signal") for s in result.signals)
            assert signal_found, f"Expected scale_signal in signals for {signal!r}, got {result.signals}"

    def test_numeric_metric_increases_score(self) -> None:
        bullets_with_metrics = [
            ("bul_ibm_001", "Achieved 99.9% uptime across distributed AI platforms."),
            ("bul_ibm_002", "Delivered 30% infrastructure overhead reduction."),
            ("bul_ibm_005", "Generated $15M in incremental co-sell revenue."),
        ]
        for bid, text in bullets_with_metrics:
            result = check_bullet_seniority_floor(bid, text)
            assert "numeric_metric" in result.signals, (
                f"Expected numeric_metric signal for: {text[:60]}, got {result.signals}"
            )

    def test_svp_level_bullet_passes_floor(self) -> None:
        svp_bullets = [
            "Architected cloud-native AI platform serving regulated financial institutions at 99.9% uptime.",
            "Engineered near-real-time data lineage frameworks reducing regulatory response latency by 50%.",
            "Led enterprise-scale cloud modernization reducing infrastructure overhead by 30%.",
            "Structured multi-year hyperscaler alliances generating $15M in incremental revenue.",
            "Designed reusable SaaS platform architecture improving renewal rates by 25%.",
        ]
        for i, text in enumerate(svp_bullets, 1):
            result = check_bullet_seniority_floor(f"bul_ibm_00{i}", text)
            assert result.passed, (
                f"SVP-level bullet should pass seniority floor: {text[:60]}. "
                f"Score={result.score}, signals={result.signals}"
            )

    def test_junior_sounding_bullet_fails_floor(self) -> None:
        """Pure participation/support verbs without scale signals should fail."""
        junior_bullets = [
            "Helped stakeholders understand cloud technology benefits.",
            "Supported the team in implementing analytics features.",
            "Participated in cloud migration planning sessions.",
        ]
        for i, text in enumerate(junior_bullets, 1):
            result = check_bullet_seniority_floor(f"bul_ibm_00{i}", text)
            assert not result.passed, (
                f"Junior-sounding bullet should fail seniority floor: {text[:60]}. "
                f"Got score={result.score}"
            )


class TestSeniorityGateInX2Runner:
    def test_demoted_bullets_fail_quality_gate_runner(self) -> None:
        weak_bullets = [
            {"bullet_id": "bul_ibm_001",
             "bullet_text": "Helped stakeholders adopt cloud AI platform technologies."},
            {"bullet_id": "bul_ibm_002",
             "bullet_text": "Supported cloud migration activities at the client site."},
            {"bullet_id": "bul_ibm_003",
             "bullet_text": "Assisted with regulatory workflow process improvements."},
            {"bullet_id": "bul_ibm_004",
             "bullet_text": "Participated in data lineage implementation planning."},
            {"bullet_id": "bul_ibm_005",
             "bullet_text": "Contributed to partnership discussions with hyperscalers."},
        ]
        sen_pass, sen_results, _, _, _, _ = run_bullet_quality_floor_gates(
            weak_bullets, section_id="ibm_bullets"
        )
        assert not sen_pass, "Weak-verb bullets should fail seniority floor in gate runner"
        failures = [r for r in sen_results if not r.passed]
        assert len(failures) >= 3, f"Expected >= 3 failures, got {len(failures)}"

    def test_strong_bullets_pass_quality_gate_runner(self) -> None:
        strong_bullets = [
            {"bullet_id": "bul_ibm_001",
             "bullet_text": "Architected cloud-native AI platforms achieving 99.9% uptime for regulated financial institutions."},
            {"bullet_id": "bul_ibm_002",
             "bullet_text": "Led cloud infrastructure modernization reducing overhead by 30% enterprise-wide."},
            {"bullet_id": "bul_ibm_003",
             "bullet_text": "Converted regulatory analytics workflows into SaaS platforms improving renewal rates by 25%."},
            {"bullet_id": "bul_ibm_004",
             "bullet_text": "Engineered data lineage and observability frameworks reducing regulatory latency by 50%."},
            {"bullet_id": "bul_ibm_005",
             "bullet_text": "Forged multi-year hyperscaler alliances generating $15M in incremental revenue."},
        ]
        sen_pass, sen_results, _, _, _, _ = run_bullet_quality_floor_gates(
            strong_bullets, section_id="ibm_bullets"
        )
        failures = [r for r in sen_results if not r.passed]
        assert sen_pass, f"Strong bullets should pass seniority floor. Failures: {[r.failure_reason for r in failures]}"

    def test_seniority_floor_constant_is_one(self) -> None:
        """The floor must be >= 1 to catch empty/junior bullets."""
        assert SENIORITY_FLOOR_SCORE >= 1, "SENIORITY_FLOOR_SCORE must be >= 1"

    def test_strong_verb_coverage_includes_key_svp_verbs(self) -> None:
        """Key SVP Engineering verbs must be in the strong verb set."""
        required_verbs = {
            "architected", "engineered", "operationalized", "designed",
            "deployed", "led", "built", "established",
        }
        missing = required_verbs - STRONG_ACTION_VERBS
        assert not missing, f"Missing SVP verbs from STRONG_ACTION_VERBS: {missing}"

    def test_weak_verb_set_includes_participation_verbs(self) -> None:
        required_weak = {"supported", "helped", "assisted", "participated"}
        missing = required_weak - WEAK_ACTION_VERBS
        assert not missing, f"Missing participation verbs from WEAK_ACTION_VERBS: {missing}"
