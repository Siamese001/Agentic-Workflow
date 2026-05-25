"""W3: graph v2 orphan audit + controlled migration."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.graph_v2_quality_migration import (
    audit_active_skill_orphans,
    apply_w3_controlled_remediation,
    compute_graph_v2_digest,
    derive_graph_hop_path,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import load_master_skills_arsenal_ledger

REPO = Path(__file__).resolve().parents[4]


def test_derive_graph_hop_path_has_four_hops() -> None:
    row = {
        "skill_id": "skill_agentic_platform_productization",
        "career_track_id": "TRACK_GENAI_AGENTIC",
        "pillar": "pillar_agentic_ai_platforms",
        "fact_id_links": ["fact_engineering_platform_001"],
    }
    hop = derive_graph_hop_path(row)
    assert len(hop) >= 4
    assert hop[-1] == "fact_engineering_platform_001"


def test_apply_w3_strips_early_career_from_active_confirmed() -> None:
    ledger = {
        "graph_nodes": [{"node_id": "skill_test_orphan", "node_type": "skill"}],
        "skill_rows": [
            {
                "skill_id": "skill_test_orphan",
                "activation_status": "ACTIVE_CONFIRMED",
                "allowed_sections": ["executive_summary", "early_career"],
                "fact_id_links": ["fact_test_001"],
                "career_track_id": "TRACK_ACTUARIAL",
                "pillar": "pillar_test",
            }
        ],
        "graph_metadata": {},
    }
    patched, migrations = apply_w3_controlled_remediation(copy.deepcopy(ledger))
    assert len(migrations) == 1
    row = patched["skill_rows"][0]
    assert "early_career" not in row["allowed_sections"]
    assert row.get("graph_hop_path")
    assert audit_active_skill_orphans(patched) == []


def test_graph_v2_digest_stable_for_same_ledger() -> None:
    ledger = load_master_skills_arsenal_ledger(repo_root=REPO)
    d1 = compute_graph_v2_digest(ledger)
    d2 = compute_graph_v2_digest(ledger)
    assert d1 == d2


def test_live_ledger_zero_active_orphans_after_w3() -> None:
    ledger = load_master_skills_arsenal_ledger(repo_root=REPO)
    orphans = audit_active_skill_orphans(ledger)
    assert orphans == [], f"orphans remain: {orphans[:5]}"
