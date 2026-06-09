from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_REGISTRY_PATH = REPO_ROOT / "apps_lic" / "config" / "prompt_registry.yaml"
PROMPT_BOM_PATH = REPO_ROOT / "apps_lic" / "prompt_assembly" / "prompt_bom.yaml"
TEMPLATE_DIR = REPO_ROOT / "apps_lic" / "prompt_assembly" / "templates"
OUTPUT_SCHEMA_PATH = (
    REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "output_schema.yaml"
)

GENERATION_REQUIRED_FIELDS = {
    "subject",
    "message_body",
    "channel",
    "recipient_class",
    "relationship_posture",
    "intended_next_step",
    "claims_used",
    "unsupported_claims",
    "omitted_claims",
    "personalization_confidence",
    "tone_risk_flags",
    "hitl_questions",
    "signature_block",
    "metadata",
    "send_mode",
}

PROVIDER_LITERAL_FRAGMENTS = {
    "qwen_vllm",
    "Qwen/Qwen2.5-32B-Instruct-AWQ",
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _registry() -> dict:
    return _load_yaml(PROMPT_REGISTRY_PATH)


def _template(path: Path) -> dict:
    return _load_yaml(path)


def test_w2_all_yaml_templates_are_registered_and_bom_referenced() -> None:
    registry = _registry()
    bom = _load_yaml(PROMPT_BOM_PATH)

    template_files = {path.name for path in TEMPLATE_DIR.glob("*.yaml")}
    registry_files = {
        Path(entry["path"]).name for entry in registry["templates"].values()
    }
    bom_refs = set(bom["template_registry_refs"])

    assert template_files == registry_files
    assert set(registry["templates"]) == bom_refs


def test_w2_registry_entries_match_template_contracts() -> None:
    registry = _registry()

    for template_id, entry in registry["templates"].items():
        path = REPO_ROOT / entry["path"]
        template = _template(path)

        assert template["template_id"] == template_id
        assert template["allowed_stage"] == entry["allowed_stage"]
        assert template["required_slots"] == entry["required_slots"]
        assert template["output_contract"]["type"] == entry["output_contract"]


def test_w2_e3_generation_templates_share_outreach_draft_candidate_contract() -> None:
    registry = _registry()
    output_schema = _load_yaml(OUTPUT_SCHEMA_PATH)
    schema_contract = output_schema["generation_contract"]

    assert registry["default_generation_output_contract"] == "OutreachDraftCandidate"
    assert schema_contract["name"] == "OutreachDraftCandidate"
    assert set(schema_contract["required_fields"]) == GENERATION_REQUIRED_FIELDS
    assert {"provider_profile", "model"} <= set(schema_contract["forbidden_fields"])

    for entry in registry["templates"].values():
        if entry["allowed_stage"] != "E3_EXEC":
            continue
        template = _template(REPO_ROOT / entry["path"])
        r0 = template["slot_bodies"]["R0"]

        assert template["output_contract"]["type"] == "OutreachDraftCandidate"
        for field in GENERATION_REQUIRED_FIELDS:
            assert f"- {field}" in r0


def test_w2_e3_templates_expose_inmail_and_short_chat_channel_rules() -> None:
    registry = _registry()

    for entry in registry["templates"].values():
        if entry["allowed_stage"] != "E3_EXEC":
            continue
        template = _template(REPO_ROOT / entry["path"])
        r0 = template["slot_bodies"]["R0"]

        assert "linkedin_inmail" in r0
        assert "subject must be non-empty" in r0
        assert "signature_block is required" in r0
        assert "linkedin_chat" in r0
        assert "subject must be empty" in r0
        assert "under 300 characters" in r0
        assert "Do not infer channel from length" in r0


def test_w2_active_generation_templates_do_not_hardcode_provider_or_model() -> None:
    registry = _registry()

    for entry in registry["templates"].values():
        if entry["allowed_stage"] != "E3_EXEC":
            continue
        text = (REPO_ROOT / entry["path"]).read_text(encoding="utf-8")
        for fragment in PROVIDER_LITERAL_FRAGMENTS:
            assert fragment not in text
        r0 = _template(REPO_ROOT / entry["path"])["slot_bodies"]["R0"]
        assert "- provider_profile" not in r0
        assert "- model" not in r0
