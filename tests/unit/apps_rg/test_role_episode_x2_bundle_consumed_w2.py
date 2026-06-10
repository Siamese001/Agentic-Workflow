from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any, Callable

import pytest

from apps_rg.runtime.sections import role_episode_lane


def _minimal_l2(section_id: str) -> dict[str, Any]:
    source_id = f"fact_{section_id}"
    if section_id.endswith("_bullets"):
        prefix = "bul_insurtech" if section_id.startswith("insurtech") else "bul_ey"
        bullets = [
            {
                "bullet_id": f"{prefix}_{idx:03d}",
                "bullet_text": f"Led governed agentic AI delivery with measurable platform control {idx}.",
                "source_fact_ids": [source_id],
            }
            for idx in range(1, 4)
        ]
        return {
            "section_id": section_id,
            "bullets": bullets,
            "claim_ledger": [
                {"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]}
                for b in bullets
            ],
        }
    return {
        "section_id": section_id,
        "narrative_sentence": "Led governed agentic AI delivery with measurable platform control.",
        "claim_ledger": [
            {
                "claim_text": "Led governed agentic AI delivery.",
                "source_fact_ids": [source_id],
            }
        ],
    }


@pytest.mark.parametrize(
    ("section_id", "runner"),
    [
        ("insurtech_bullets", role_episode_lane.run_insurtech_bullets_x2_gates),
        ("ey_bullets", role_episode_lane.run_ey_bullets_x2_gates),
        ("insurtech_narrative", role_episode_lane.run_insurtech_narrative_x2_gates),
        ("ey_narrative", role_episode_lane.run_ey_narrative_x2_gates),
    ],
)
def test_role_episode_x2_entrypoints_do_not_forward_bundle_consumed(
    section_id: str,
    runner: Callable[..., list[dict[str, Any]]],
) -> None:
    l2 = _minimal_l2(section_id)

    gates = runner(
        l2=l2,
        allowed=[f"fact_{section_id}"],
        runtime_generation_status="REAL_LLM",
    )

    assert gates
    assert any(g["gate_id"] == f"x2_{section_id}_runtime_real_llm" for g in gates)


def test_role_episode_x2_signatures_have_no_vestigial_bundle_consumed_forward() -> None:
    assert "bundle_consumed" not in inspect.signature(role_episode_lane._x2_gates).parameters
    assert "bundle_consumed" not in inspect.signature(role_episode_lane.run_role_episode_x2_gates).parameters

    source = Path(role_episode_lane.__file__).read_text(encoding="utf-8")
    assert "bundle_consumed=" not in source


def test_role_episode_lane_has_no_local_unknown_keyword_forwards() -> None:
    source_path = Path(role_episode_lane.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    local_defs: dict[str, ast.FunctionDef] = {
        node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    accepted: dict[str, set[str] | None] = {}
    for name, node in local_defs.items():
        if node.args.kwarg is not None:
            accepted[name] = None
        else:
            accepted[name] = {arg.arg for arg in [*node.args.args, *node.args.kwonlyargs]}

    mismatches: list[str] = []
    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
        if not isinstance(call.func, ast.Name):
            continue
        callee = call.func.id
        if callee not in accepted or accepted[callee] is None:
            continue
        for keyword in call.keywords:
            if keyword.arg is not None and keyword.arg not in accepted[callee]:
                mismatches.append(f"{source_path.name}:{call.lineno} {callee}({keyword.arg}=)")

    assert mismatches == []
