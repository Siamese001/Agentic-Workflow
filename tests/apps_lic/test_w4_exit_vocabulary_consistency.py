from __future__ import annotations

import json
from pathlib import Path

import yaml

from apps_lic.runtime.bindings.pa_binding import pa_compose_apps_lic
from tests.apps_lic.test_w5_apps_lic_c0_pa import _canonical_pipeline


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_EXIT_PATH = (
    REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "validation_exit.v1.yaml"
)
LEGACY_EXIT_PROFILE_PATH = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "exit_profile.outreach_message.v1.json"
)
PROMPT_SLOT_REGISTRY_PATH = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "prompt_slot_registry.v1.yaml"
)

CANONICAL_DISPOSITIONS = {"clear_draft", "review_required", "blocked", "abstain"}
LEGACY_GATES = {"G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28"}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_w4_validation_exit_owns_canonical_disposition_vocabulary() -> None:
    validation_exit = _load_yaml(VALIDATION_EXIT_PATH)

    assert set(validation_exit["exit"]["allowed_dispositions"]) == CANONICAL_DISPOSITIONS
    assert validation_exit["exit"]["default_disposition"] == "blocked"


def test_w4_legacy_exit_profile_is_fenced_and_points_to_validation_exit_ssot() -> None:
    legacy_profile = _load_json(LEGACY_EXIT_PROFILE_PATH)

    assert legacy_profile["status"] == "compatibility_fenced"
    assert legacy_profile["runtime_authority"] is False
    assert (
        legacy_profile["canonical_exit_profile_ref"]
        == "apps_lic/config/domain_contract/validation_exit.v1.yaml"
    )
    assert legacy_profile["fail_closed_on_unmapped_legacy_gate"] is True
    assert legacy_profile["fail_closed_on_unmapped_legacy_disposition"] is True


def test_w4_legacy_g21_g28_labels_map_to_x1_family_and_known_gates() -> None:
    validation_exit = _load_yaml(VALIDATION_EXIT_PATH)
    legacy_profile = _load_json(LEGACY_EXIT_PROFILE_PATH)
    known_x2_gates = set(validation_exit["x2_gates"]["universal"]) | set(
        validation_exit["x2_gates"]["conditional"]
    )

    assert set(legacy_profile["legacy_gate_map"]) == LEGACY_GATES
    for gate_id, mapping in legacy_profile["legacy_gate_map"].items():
        assert mapping["canonical_family"] == "X1", gate_id
        for canonical_gate in mapping.get("canonical_x2_gates", []):
            assert canonical_gate in known_x2_gates, (gate_id, canonical_gate)


def test_w4_legacy_disposition_map_converges_to_canonical_exit_dispositions() -> None:
    legacy_profile = _load_json(LEGACY_EXIT_PROFILE_PATH)

    assert set(legacy_profile["canonical_allowed_exit_dispositions"]) == CANONICAL_DISPOSITIONS
    assert legacy_profile["canonical_default_disposition"] == "blocked"
    assert set(legacy_profile["legacy_disposition_map"].values()) <= CANONICAL_DISPOSITIONS
    assert legacy_profile["legacy_disposition_map"] == {
        "APPROVED": "clear_draft",
        "APPROVED_WITH_NOTES": "review_required",
        "REJECTED": "blocked",
        "HITL_REQUIRED": "review_required",
        "ABSTAIN": "abstain",
    }


def test_w4_prompt_slots_aliases_and_x_terms_are_not_exit_dispositions() -> None:
    slot_registry = _load_yaml(PROMPT_SLOT_REGISTRY_PATH)
    validation_exit = _load_yaml(VALIDATION_EXIT_PATH)
    legacy_profile = _load_json(LEGACY_EXIT_PROFILE_PATH)

    prompt_terms = (
        set(slot_registry["prompt_slots"])
        | set(slot_registry["runtime_aliases"])
        | set(slot_registry["non_prompt_terms"])
    )
    active_dispositions = set(validation_exit["exit"]["allowed_dispositions"])

    assert prompt_terms.isdisjoint(active_dispositions)
    assert prompt_terms <= set(legacy_profile["forbidden_as_exit_dispositions"])


def test_w4_pa_artifact_does_not_emit_x3_or_exit_dispositions() -> None:
    vr, l1, route, fec = _canonical_pipeline()
    cpa = pa_compose_apps_lic(route, l1, fec, vr)

    serialized_lineage = json.dumps(dict(cpa.slot_lineage_map), sort_keys=True)
    serialized_hashes = json.dumps(dict(cpa.component_hash_map), sort_keys=True)

    assert "X3" not in cpa.slot_lineage_map
    assert "X3" not in serialized_lineage
    assert "X3" not in serialized_hashes
    assert CANONICAL_DISPOSITIONS.isdisjoint(cpa.slot_lineage_map)
    assert CANONICAL_DISPOSITIONS.isdisjoint(cpa.component_hash_map)
