"""W6: cross-section graph coherence aggregation."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.aggregation.cross_section_x2 import (
    VERDICT_PASS,
    VERDICT_WARN,
    build_cross_section_graph_coherence_receipt,
    check_cross_section_graph_coherence,
    run_cross_section_x2_gates,
)


def _native_meta(fid: str) -> dict:
    return {
        "native_c03_status": "EMITTED",
        "native_c03_final_evidence": {
            "contract_type": "apps_rg.native_c03_final_evidence",
            "selected_source_fact_ids": [fid],
        },
    }


def _role_meta(bundle_id: str, fid: str, skills: list[str]) -> dict:
    return {
        "role_episode_bundle_consumption": True,
        "role_episode_bundle_ids": [bundle_id],
        "role_episode_bundles": [
            {
                "role_episode_bundle_id": bundle_id,
                "linked_source_fact_ids": [fid],
                "graph_skill_node_ids": skills,
            }
        ],
    }


def _write_runtime_payload(repo: Path, lane: str, meta: dict) -> dict:
    run_dir = repo / lane
    run_dir.mkdir(parents=True)
    (run_dir / "runtime_payload.json").write_text(
        json.dumps({"proof_pool_metadata": meta}, ensure_ascii=False),
        encoding="utf-8",
    )
    return {"lane": lane, "artifact_dir": lane}


def _section(section_id: str, snapshot: dict) -> dict:
    return {
        "section_id": section_id,
        "section_kind": "generated_lane",
        "l2_output_snapshot": snapshot,
    }


def test_cross_section_graph_coherence_receipt_passes_with_breadth(tmp_path: Path) -> None:
    pointers = [
        _write_runtime_payload(tmp_path, "executive_summary", _native_meta("fact_exec")),
        _write_runtime_payload(
            tmp_path,
            "unify_bullets",
            _role_meta("reb_unify", "fact_unify", ["skill_platform", "skill_dependency"]),
        ),
        _write_runtime_payload(
            tmp_path,
            "ibm_bullets",
            _role_meta("reb_ibm", "fact_ibm", ["skill_cloud", "skill_finops"]),
        ),
        _write_runtime_payload(tmp_path, "competencies", _native_meta("fact_comp")),
    ]
    final_resume = {
        "sections": [
            _section(
                "executive_summary",
                {
                    "resume_display_text": "Executive platform summary.",
                    "claim_ledger": [{"claim_text": "platform", "source_fact_ids": ["fact_exec"]}],
                },
            ),
            _section(
                "unify_bullets",
                {
                    "bullets": [
                        {
                            "bullet_text": "Unify platform outcome.",
                            "source_fact_ids": ["fact_unify"],
                            "role_episode_bundle_id": "reb_unify",
                            "graph_skill_node_ids": ["skill_platform", "skill_dependency"],
                        }
                    ],
                    "claim_ledger": [{"claim_text": "unify", "source_fact_ids": ["fact_unify"]}],
                },
            ),
            _section(
                "ibm_bullets",
                {
                    "bullets": [
                        {
                            "bullet_text": "IBM cloud outcome.",
                            "source_fact_ids": ["fact_ibm"],
                            "role_episode_bundle_id": "reb_ibm",
                            "graph_skill_node_ids": ["skill_cloud", "skill_finops"],
                        }
                    ],
                    "claim_ledger": [{"claim_text": "ibm", "source_fact_ids": ["fact_ibm"]}],
                },
            ),
            _section(
                "competencies",
                {
                    "competencies": [
                        {
                            "term": "Platform governance",
                            "source_fact_ids": ["fact_comp"],
                            "source_skill_ids": ["skill_platform"],
                        }
                    ],
                    "claim_ledger": [{"claim_text": "competency", "source_fact_ids": ["fact_comp"]}],
                },
            ),
        ]
    }

    receipt = build_cross_section_graph_coherence_receipt(
        repo=tmp_path,
        final_resume_blob=final_resume,
        sealed_index={"pointers": pointers},
    )

    assert receipt["status"] == VERDICT_PASS
    assert receipt["active_section_count"] == 4
    assert receipt["native_c03_section_count"] == 2
    assert receipt["role_episode_section_count"] == 2
    assert receipt["unique_graph_skill_node_count"] == 4
    assert receipt["warnings"] == []


def test_cross_section_graph_coherence_warns_on_metadata_only_section(tmp_path: Path) -> None:
    pointers = [
        _write_runtime_payload(
            tmp_path,
            "unify_bullets",
            _role_meta("reb_unify", "fact_unify", ["skill_platform"]),
        )
    ]
    final_resume = {
        "sections": [
            _section(
                "unify_bullets",
                {
                    "bullets": [{"bullet_text": "Generic outcome.", "source_fact_ids": ["other_fact"]}],
                    "claim_ledger": [{"claim_text": "generic", "source_fact_ids": ["other_fact"]}],
                },
            )
        ]
    }

    gate = check_cross_section_graph_coherence(
        repo=tmp_path,
        final_resume_blob=final_resume,
        sealed_index={"pointers": pointers},
    )

    assert gate.verdict == VERDICT_WARN
    assert gate.observed["status"] == VERDICT_WARN
    warning_codes = {
        violation["reason_code"]
        for row in gate.observed["warnings"]
        for violation in row.get("violations", [])
        if isinstance(violation, dict)
    }
    assert "role_episode_metadata_without_bundle_use" in warning_codes


def test_run_cross_section_x2_gates_includes_graph_coherence_gate(tmp_path: Path) -> None:
    pointers = [_write_runtime_payload(tmp_path, "executive_summary", _native_meta("fact_exec"))]
    final_resume = {
        "sections": [
            _section(
                "executive_summary",
                {
                    "resume_display_text": "Executive platform summary.",
                    "claim_ledger": [{"claim_text": "platform", "source_fact_ids": ["fact_exec"]}],
                },
            )
        ]
    }

    gates, *_ = run_cross_section_x2_gates(
        repo=tmp_path,
        final_resume_blob=final_resume,
        fingerprint={"review_lanes": []},
        sealed_index={"pointers": pointers},
    )
    by_id = {gate.gate_id: gate for gate in gates}

    assert "x2_cross_section_graph_coherence" in by_id
    assert by_id["x2_cross_section_graph_coherence"].verdict == VERDICT_WARN
    assert by_id["x2_cross_section_graph_coherence"].observed["active_section_count"] == 1
