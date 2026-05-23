"""Shared fixtures for product-shape edge-case contract tests."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.l2_recipe.modular_rg_output_builder import build_rg_output_from_modular_sections
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


@dataclass
class _Pkg:
    target_role: str = "SVP Engineering"
    target_company: str = "Example Corp"


def real_status() -> str:
    return "REAL_LLM"


def minimal_lane_bundle() -> dict[str, dict]:
    st = real_status()
    bullet = (
        "Delivered measurable platform outcomes including reliability, cost reductions, "
        "and revenue-facing modernization aligned to enterprise controls."
    )
    return {
        "headline": {
            "runtime_generation_status": st,
            "headline_line": "SVP Engineering | Agentic AI platforms and governed enterprise delivery",
        },
        "executive_summary": {
            "runtime_generation_status": st,
            "resume_display_text": (
                "Executive leader delivering agentic AI platforms, retrieval systems, and "
                "governed runtime controls for regulated enterprises with measurable outcomes."
            ),
        },
        "unify_narrative": {
            "runtime_generation_status": st,
            "narrative_sentence": (
                "At Unify, scaled governed agentic platforms with deterministic routing and "
                "enterprise retrieval upgrades across regulated workflows."
            ),
        },
        "ibm_narrative": {
            "runtime_generation_status": st,
            "narrative_sentence": (
                "At IBM, delivered cloud-native AI and analytics platforms with strong uptime "
                "and modernization outcomes across financial services clients."
            ),
        },
        "unify_bullets": {
            "runtime_generation_status": st,
            "bullets": [
                {"text": bullet, "source_fact_id": f"bul_u{i}", "has_metric": True} for i in range(1, 4)
            ],
        },
        "ibm_bullets": {
            "runtime_generation_status": st,
            "bullets": [
                {"text": bullet, "source_fact_id": f"bul_i{i}", "has_metric": True} for i in range(1, 4)
            ],
        },
        "competencies": {
            "runtime_generation_status": st,
            "competencies": [
                {
                    "category_label": "Platforms",
                    "terms": [
                        {"text": "Agentic orchestration"},
                        {"text": "Retrieval and GraphRAG"},
                        {"text": "Policy gating"},
                    ],
                }
            ],
        },
    }


def six_sentence_exec_text(*, word_repeat: int = 3) -> str:
    clause = " ".join(["platform"] * word_repeat)
    return (
        f"Engineering executive delivers governed agentic AI platforms with {clause}. "
        f"The leader scales deterministic routing and policy-gated execution with {clause}. "
        f"Platform lifecycle work ties architecture to commercial adoption with {clause}. "
        f"Delivery outcomes include measurable margin improvements with {clause}. "
        f"Prior roles show quantitative depth across regulated programs with {clause}. "
        f"Governed runtime delivery stays audit-ready without weakening velocity with {clause}."
    )


def build_export(
    tmp_path: Path,
    lanes: dict[str, dict],
    *,
    run_suffix: str = "edge",
) -> Any:
    repo = find_repo_root()
    art = tmp_path / run_suffix
    art.mkdir(parents=True, exist_ok=True)
    modular_root = art / "modular_r4"
    modular_root.mkdir(parents=True, exist_ok=True)
    base = json.loads(
        (repo / "tests" / "_fixtures" / "modular_rg_merge" / "base_resume_min_for_merge.json").read_text(
            encoding="utf-8",
        ),
    )
    return build_rg_output_from_modular_sections(
        lane_l2_by_id=lanes,
        base_resume=base,
        input_package=_Pkg(),
        modular_root=modular_root,
        artifact_dir=art,
        run_id=f"pytest_{run_suffix}_{uuid.uuid4().hex[:8]}",
        reject_mocked_lanes=True,
    )


def gate_map(gates: list[Any]) -> dict[str, bool]:
    return {g.gate_id: g.pass_ for g in gates}


def minimal_unify_bullets_payload(
    *,
    heavy: int,
    moderate: int,
    light_protected: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

    bullets: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    pattern = (["HEAVY"] * heavy + ["MODERATE"] * moderate + ["LIGHT_PROTECTED"] * light_protected)
    while len(pattern) < 6:
        pattern.append("MODERATE")
    pattern = pattern[:6]
    for bid, intensity in zip(UNIFY_BULLET_IDS, pattern, strict=True):
        text = (
            f"Delivered measurable platform outcome for {bid} with traceable enterprise controls "
            f"and audit-ready delivery."
        )
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    dist = {
        "HEAVY": heavy,
        "MODERATE": moderate,
        "LIGHT_PROTECTED": light_protected,
        "total": 6,
    }
    parsed = {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": dist}
    return bullets, ledger, parsed


def fake_x1d_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
    ]
