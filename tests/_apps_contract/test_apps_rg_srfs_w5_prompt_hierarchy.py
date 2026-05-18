"""W5: apps_rg section prompt templates encode proof vs targeting hierarchy (YAML contract, no LLM)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates"

# (section_id, template_filename, flags)
SECTION_PROMPTS: list[tuple[str, str, dict[str, bool]]] = [
    ("headline", "headline_tailor_v1.yaml", {"slot_bodies": True}),
    ("executive_summary", "executive_summary.generate_scratch_v1.yaml", {"slot_bodies": True}),
    ("unify_bullets", "unify_bullet_tailor_v1.yaml", {}),
    ("unify_narrative", "unify_position_narrative_v1.yaml", {"narrative_companion": True}),
    ("ibm_bullets", "ibm_bullet_tailor_v1.yaml", {}),
    ("ibm_narrative", "ibm_position_narrative_v1.yaml", {"narrative_companion": True}),
    ("competencies", "competency_selector_v2.yaml", {"competencies_inventory": True}),
]


def _load_yaml(name: str) -> dict:
    path = TEMPLATES_DIR / name
    assert path.is_file(), f"Missing template {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _flatten_slot_bodies(doc: dict, *slot_keys: str) -> str:
    bodies = doc.get("slot_bodies") or {}
    return "\n".join(str(bodies.get(k) or "") for k in slot_keys)


def _audit_text(section_id: str, fname: str, flags: dict[str, bool]) -> str:
    doc = _load_yaml(fname)
    chunks: list[str] = []
    w5 = doc.get("w5_proof_targeting_harmonization")
    assert isinstance(w5, str) and w5.strip(), f"{fname}: w5_proof_targeting_harmonization required"
    chunks.append(w5)
    if flags.get("slot_bodies"):
        if section_id == "headline":
            chunks.append(_flatten_slot_bodies(doc, "S0"))
        elif section_id == "executive_summary":
            chunks.append(_flatten_slot_bodies(doc, "S0", "I0"))
    for key in ("purpose", "sovereign_oath", "source_authority_hierarchy", "north_star_semantic_contract"):
        val = doc.get(key)
        if isinstance(val, str):
            chunks.append(val)
        elif isinstance(val, dict):
            chunks.append(yaml.safe_dump(val, sort_keys=True))
    return "\n".join(chunks).lower()


@pytest.mark.parametrize("section_id,fname,flags", SECTION_PROMPTS)
def test_w5_each_section_prompt_has_hierarchy_contract(section_id: str, fname: str, flags: dict[str, bool]) -> None:
    text = _audit_text(section_id, fname, flags)

    assert "selectedrolefactset" in text, f"{fname}: SRFS / SelectedRoleFactSet proof substrate"
    assert "jd" in text and ("briefing" in text), f"{fname}: JD and briefing mentioned"
    assert "targeting" in text, f"{fname}: targeting-only framing"
    assert "never proof" in text or "not proof" in text, f"{fname}: must forbid proof misuse"

    assert "source_fact" in text, f"{fname}: source_fact_ids / proof tokens"

    allow = ("allowlist" in text) or ("slice" in text) or ("allow" in text and "fact" in text)
    assert allow, f"{fname}: allowlist/slice / allowed facts for SRFS alignment"

    fail_gate = ("x2" in text) or ("out-of-slice" in text) or ("fail" in text and "gate" in text)
    assert fail_gate, f"{fname}: deterministic failure / slice enforcement signal"

    if flags.get("narrative_companion"):
        assert ("companion" in text) or ("read-only" in text), f"{fname}: companion bullets context"
    if flags.get("competencies_inventory"):
        assert "verified_skill" in text, f"{fname}: verified_skill_inventory rule"


def test_w5_unify_narrative_finalized_bullets_companion_not_proof() -> None:
    doc = _load_yaml("unify_position_narrative_v1.yaml")
    oath = str(doc.get("sovereign_oath") or "").lower()
    assert "companion" in oath or "read-only" in oath
    assert "unify_narrative" in oath and "slice" in oath


def test_w5_ibm_narrative_finalized_bullets_companion_not_proof() -> None:
    doc = _load_yaml("ibm_position_narrative_v1.yaml")
    oath = str(doc.get("sovereign_oath") or "").lower()
    assert "companion" in oath or "read-only" in oath
    assert "ibm_narrative" in oath and "slice" in oath


def test_w5_competencies_pa_slots_inventory_not_proof_without_slice() -> None:
    path = TEMPLATES_DIR / "competency_selector_v2.pa_slots.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    s0 = str((doc.get("slot_bodies") or {}).get("S0") or "").lower()
    assert "verified_skill_inventory" in s0
    assert ("srfs" in s0 or "allowlist" in s0) and ("not proof" in s0 or "proof if" in s0 or "outside" in s0)


def test_w5_omission_and_invention_banned_in_w5_blocks() -> None:
    """Each w5 excerpt forbids invention and names targeting vs selected-fact proof."""
    for _sid, fname, _flags in SECTION_PROMPTS:
        doc = _load_yaml(fname)
        w5 = str(doc.get("w5_proof_targeting_harmonization") or "").lower()
        assert "targeting" in w5, fname
        assert "selectedrolefactset" in w5, fname
        assert ("omit" in w5) or ("drop" in w5) or ("unsupported" in w5), fname
