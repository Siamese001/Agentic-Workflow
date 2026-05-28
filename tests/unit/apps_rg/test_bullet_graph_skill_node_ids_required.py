"""Acceptance test: every bullet must have graph_skill_node_ids in change_log.

W5 acceptance test (Bullet Proof Bundle Redesign):
- Verifies x2_ibm_bullet_graph_skill_node_ids_required gate.
- Verifies x2_unify_bullet_graph_skill_node_ids_required gate.
- Bullets missing graph_skill_node_ids fail the gate.
- Bullets with populated skill_ids_used or graph_skill_node_ids pass.
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID,
    run_ibm_bullets_x2_gates,
)
from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates

# ---------------------------------------------------------------------------
# Minimal test fixtures
# ---------------------------------------------------------------------------

def _make_ibm_bullet(
    bullet_id: str = "bul_ibm_001",
    bullet_text: str = "Architected cloud-native AI platforms achieving 99.9% uptime.",
    metric_raw: str = "99.9% uptime",
) -> dict:
    return {
        "bullet_id": bullet_id,
        "bullet_text": bullet_text,
        "has_metric": bool(metric_raw),
        "metric_raw": metric_raw,
        "source_fact_ids": [bullet_id],
    }


def _make_five_ibm_bullets() -> list[dict]:
    return [
        _make_ibm_bullet("bul_ibm_001", "Architected cloud-native AI platforms achieving 99.9% uptime.", "99.9% uptime"),
        _make_ibm_bullet("bul_ibm_002", "Led cloud infrastructure modernization reducing overhead by 30%.", "30%"),
        _make_ibm_bullet("bul_ibm_003", "Converted regulatory workflows into SaaS platforms improving renewal rates by 25%.", "25%"),
        _make_ibm_bullet("bul_ibm_004", "Engineered real-time data lineage and observability frameworks cutting latency by 50%.", "50%"),
        _make_ibm_bullet("bul_ibm_005", "Forged hyperscaler alliances generating $15M in incremental revenue.", "$15M"),
    ]


def _make_ibm_parsed_output(
    bullets: list[dict],
    change_log: list[dict],
) -> dict:
    return {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": "augmented_skills_graph_ibm_bullets_phase2_track_ranked",
            "facts": [
                {"fact_id": b["bullet_id"], "claim_text": b["bullet_text"],
                 "metric_raw": b.get("metric_raw"), "has_metric": b.get("has_metric"),
                 "career_track": "track_data_tech_cloud_ml", "graph_hop_path": ["hop1"],
                 "graph_phase2_track_proof": True}
                for b in bullets
            ],
        },
        "claim_ledger": [
            {"claim_text": b["bullet_text"], "source_fact_ids": [b["bullet_id"]]}
            for b in bullets
        ],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": change_log,
        "self_check": {"bullets_composed_from_graph_evidence": True},
    }


def _run_ibm_gates_and_find(gate_id: str, parsed: dict) -> "tuple[bool, str | None]":
    bullets = list(parsed.get("bullets") or [])
    claim_ledger = list(parsed.get("claim_ledger") or [])
    results = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
        allowed_fact_ids={b["bullet_id"] for b in bullets},
        jd_text="",
        runtime_generation_status="REAL_LLM",
    )
    for r in results:
        if r.gate_id == gate_id:
            return r.pass_, r.failure_reason
    return True, None  # gate not found → treat as pass (gate may not exist in old path)


class TestIbmGraphSkillNodeIdsRequired:
    def test_bullets_with_graph_skill_node_ids_pass(self) -> None:
        bullets = _make_five_ibm_bullets()
        change_log = [
            {
                "bullet_id": b["bullet_id"],
                "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"],
                "fact_ids_used": [b["bullet_id"]],
            }
            for b in bullets
        ]
        parsed = _make_ibm_parsed_output(bullets, change_log)
        passed, reason = _run_ibm_gates_and_find(
            IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID, parsed
        )
        assert passed, f"Expected pass when graph_skill_node_ids present; got: {reason}"

    def test_bullets_with_skill_ids_used_pass(self) -> None:
        """Unify-compatible field name skill_ids_used should also satisfy the gate."""
        bullets = _make_five_ibm_bullets()
        change_log = [
            {
                "bullet_id": b["bullet_id"],
                "skill_ids_used": ["skill_sr_cloud_data_platform_engineering"],
            }
            for b in bullets
        ]
        parsed = _make_ibm_parsed_output(bullets, change_log)
        passed, reason = _run_ibm_gates_and_find(
            IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID, parsed
        )
        assert passed, f"Expected pass when skill_ids_used present; got: {reason}"

    def test_bullets_missing_graph_skill_node_ids_fail(self) -> None:
        bullets = _make_five_ibm_bullets()
        change_log = [
            {
                "bullet_id": b["bullet_id"],
                # intentionally missing graph_skill_node_ids
            }
            for b in bullets
        ]
        parsed = _make_ibm_parsed_output(bullets, change_log)
        passed, reason = _run_ibm_gates_and_find(
            IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID, parsed
        )
        assert not passed, "Expected fail when graph_skill_node_ids missing from change_log"
        assert reason is not None
        assert "graph_skill_node_ids" in reason.lower() or "missing" in reason.lower()

    def test_bullets_with_no_change_log_entries_fail(self) -> None:
        bullets = _make_five_ibm_bullets()
        parsed = _make_ibm_parsed_output(bullets, change_log=[])
        passed, reason = _run_ibm_gates_and_find(
            IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID, parsed
        )
        assert not passed, "Expected fail when change_log has no entries at all"

    def test_partial_change_log_failure(self) -> None:
        """Only some bullets with skill IDs — gate should fail for those missing."""
        bullets = _make_five_ibm_bullets()
        change_log = [
            {"bullet_id": "bul_ibm_001", "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"]},
            {"bullet_id": "bul_ibm_002"},  # missing skill IDs
        ]
        parsed = _make_ibm_parsed_output(bullets, change_log)
        passed, reason = _run_ibm_gates_and_find(
            IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID, parsed
        )
        assert not passed, "Expected fail when some bullets have missing skill IDs"


class TestUnifyGraphSkillNodeIdsRequired:
    GATE_ID = "x2_unify_bullet_graph_skill_node_ids_required"

    def _make_six_unify_bullets(self) -> list[dict]:
        return [
            {
                "bullet_id": f"bul_unify_00{i}",
                "bullet_text": f"Engineered agentic AI platform capability {i} achieving measurable enterprise outcomes.",
                "has_metric": False,
                "metric_raw": None,
                "source_fact_ids": [f"bul_unify_00{i}"],
            }
            for i in range(1, 7)
        ]

    def _make_unify_parsed(self, bullets: list[dict], change_log: list[dict]) -> dict:
        return {
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
            "change_log": change_log,
            "self_check": {"bullets_composed_from_graph_evidence": True},
        }

    def _run_and_find(self, parsed: dict) -> "tuple[bool, str | None]":
        bullets = list(parsed.get("bullets") or [])
        claim_ledger = list(parsed.get("claim_ledger") or [])
        results = run_unify_bullets_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            allowed_fact_ids={b["bullet_id"] for b in bullets},
            jd_text="",
            runtime_generation_status="REAL_LLM",
        )
        for r in results:
            if r.gate_id == self.GATE_ID:
                return r.pass_, r.failure_reason
        return True, None

    def test_bullets_with_skill_ids_used_pass(self) -> None:
        bullets = self._make_six_unify_bullets()
        change_log = [
            {
                "bullet_id": b["bullet_id"],
                "skill_ids_used": ["skill_agentic_control_plane_design"],
                "fact_ids_used": [b["bullet_id"]],
            }
            for b in bullets
        ]
        parsed = self._make_unify_parsed(bullets, change_log)
        passed, reason = self._run_and_find(parsed)
        assert passed, f"Expected pass when skill_ids_used present; got: {reason}"

    def test_bullets_missing_skill_ids_fail(self) -> None:
        bullets = self._make_six_unify_bullets()
        change_log = [
            {"bullet_id": b["bullet_id"]}  # no skill IDs
            for b in bullets
        ]
        parsed = self._make_unify_parsed(bullets, change_log)
        passed, reason = self._run_and_find(parsed)
        assert not passed, "Expected fail when skill_ids_used missing from change_log"
