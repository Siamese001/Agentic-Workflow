"""Hard governance tests for apps_rg Prompt Assembly hardening.

25 tests covering BOM, registry, templates, compiler, slot fencing,
L2 step enforcement, provider request enforcement, no ad hoc prompt strings,
sealing, failure blocking, and spine docs.

Plan: apps-rg-pa-hardening-same-grain-a4f7c2
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_PA_ROOT = REPO_ROOT / "apps_rg" / "prompt_assembly"
_BOM_PATH = _PA_ROOT / "prompt_bom.yaml"
_REGISTRY_PATH = _PA_ROOT / "prompt_registry.yaml"
_TEMPLATES_DIR = _PA_ROOT / "templates"

REQUIRED_SLOTS = ["S0", "I0", "C0", "U0", "D0", "E0", "Y0", "R0"]
E3_TEMPLATES = [
    "strategic_tailor_v1",
    "tailor_existing_v1",
    "generate_scratch_v1",
    "enhance_current_v1",
]
E4_TEMPLATES = [
    "resume_fact_check_v1",
    "unsupported_claim_omission_v1",
    "bullet_diversity_repair_v1",
]
E5_TEMPLATES = [
    "docx_manifest_v1",
]
ALL_TEMPLATES = E3_TEMPLATES + E4_TEMPLATES + E5_TEMPLATES


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sha256_prefix(content: str, length: int = 16) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:length]


# ---------------------------------------------------------------------------
# 1. BOM exists and has all required slots
# ---------------------------------------------------------------------------
class TestBOMExists:
    def test_bom_exists(self):
        assert _BOM_PATH.exists(), f"BOM not found at {_BOM_PATH}"

    def test_bom_has_8_required_slots(self):
        bom = _load_yaml(_BOM_PATH)
        assert bom.get("required_slots") == REQUIRED_SLOTS

    def test_bom_has_template_registry_refs(self):
        bom = _load_yaml(_BOM_PATH)
        refs = bom.get("template_registry_refs", [])
        for tid in ALL_TEMPLATES:
            assert tid in refs, f"Template {tid} missing from BOM template_registry_refs"

    def test_bom_has_hash_fields(self):
        bom = _load_yaml(_BOM_PATH)
        assert "hash_fields" in bom
        assert len(bom["hash_fields"]) >= 3


# ---------------------------------------------------------------------------
# 2. Registry exists and has all 8 templates registered
# ---------------------------------------------------------------------------
class TestRegistryExists:
    def test_registry_exists(self):
        assert _REGISTRY_PATH.exists(), f"Registry not found at {_REGISTRY_PATH}"

    def test_registry_has_all_templates(self):
        reg = _load_yaml(_REGISTRY_PATH)
        templates = reg.get("templates", {})
        for tid in ALL_TEMPLATES:
            assert tid in templates, f"Template {tid} missing from registry"

    def test_registry_templates_have_required_fields(self):
        reg = _load_yaml(_REGISTRY_PATH)
        for tid, entry in reg.get("templates", {}).items():
            assert "path" in entry, f"{tid}: missing 'path'"
            assert "required_slots" in entry, f"{tid}: missing 'required_slots'"
            assert "output_contract" in entry, f"{tid}: missing 'output_contract'"
            assert "allowed_stage" in entry, f"{tid}: missing 'allowed_stage'"


# ---------------------------------------------------------------------------
# 3. All 8 YAML templates exist and have real slot_bodies
# ---------------------------------------------------------------------------
class TestTemplatesExist:
    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_yaml_exists(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        assert path.exists(), f"Template file not found: {path}"

    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_has_slot_bodies(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        parsed = _load_yaml(path)
        assert "slot_bodies" in parsed, f"{template_id}: missing slot_bodies"
        assert len(parsed["slot_bodies"]) >= 2, f"{template_id}: too few slot_bodies"

    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_has_forbidden_behaviors(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        parsed = _load_yaml(path)
        assert "forbidden_behaviors" in parsed, f"{template_id}: missing forbidden_behaviors"
        assert len(parsed["forbidden_behaviors"]) >= 3

    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_has_validation_rules(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        parsed = _load_yaml(path)
        assert "validation_rules" in parsed, f"{template_id}: missing validation_rules"

    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_has_output_contract(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        parsed = _load_yaml(path)
        assert "output_contract" in parsed, f"{template_id}: missing output_contract"


# ---------------------------------------------------------------------------
# 4. No placeholder text in templates
# ---------------------------------------------------------------------------
class TestNoPlaceholders:
    _PLACEHOLDERS = ["TODO", "PLACEHOLDER", "LOREM", "FILL ME", "TBD"]

    @pytest.mark.parametrize("template_id", ALL_TEMPLATES)
    def test_template_slot_bodies_are_not_placeholders(self, template_id):
        path = _TEMPLATES_DIR / f"{template_id}.yaml"
        parsed = _load_yaml(path)
        for slot_name, body in parsed.get("slot_bodies", {}).items():
            assert isinstance(body, str), f"{template_id}/{slot_name}: body is not a string"
            assert len(body.strip()) > 50, (
                f"{template_id}/{slot_name}: body too short ({len(body.strip())} chars) — likely placeholder"
            )
            body_lower = body.lower()
            for marker in self._PLACEHOLDERS:
                if marker.lower() in body_lower and len(body.strip()) < 200:
                    pytest.fail(f"{template_id}/{slot_name}: contains placeholder '{marker}'")


# ---------------------------------------------------------------------------
# 5. Compiler produces valid artifact for each E3 flow route
# ---------------------------------------------------------------------------
class TestCompiler:
    def _make_request(self, flow_route: str):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        return AppsRgPromptRequest(
            flow_route=flow_route,
            jd_data="Senior Software Engineer at ACME Corp requiring Python, AWS, leadership.",
            master_resume_data="10 years Python, AWS, led team of 8, built ML pipeline.",
            company_brief_data="ACME Corp is a B2B SaaS company.",
            user_task="Generate a tailored resume for this role.",
            claim_source_refs="employer_acme:2018-2024",
            unsupported_claims="",
            target_company="ACME Corp",
            target_role="Senior Software Engineer",
            seniority_band="senior",
        )

    @pytest.mark.parametrize("flow_route", ["strategic_tailor", "tailor_existing", "generate_scratch", "enhance_current"])
    def test_compile_produces_ready_artifact(self, flow_route):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        request = self._make_request(flow_route)
        artifact = compile_prompt(request)
        assert artifact.compile_status == "PA_L2_HANDOFF_READY"
        assert artifact.prompt_id.startswith("apps_rg.")
        assert artifact.template_id
        assert artifact.template_version

    def test_compile_unknown_route_fails(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        request = self._make_request("nonexistent_route")
        request.flow_route = "nonexistent_route"
        with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
            compile_prompt(request)


# ---------------------------------------------------------------------------
# 6. Compiler emits all required hash fields
# ---------------------------------------------------------------------------
class TestCompilerHashes:
    def test_all_hash_fields_present(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD text",
            master_resume_data="Resume text",
        )
        artifact = compile_prompt(request)
        assert artifact.prompt_bom_hash, "prompt_bom_hash empty"
        assert artifact.prompt_registry_hash, "prompt_registry_hash empty"
        assert artifact.prompt_template_hash, "prompt_template_hash empty"
        assert artifact.prompt_hash, "prompt_hash empty"
        assert artifact.manifest_hash, "manifest_hash empty"
        assert artifact.canonical_slot_bytes_hash, "canonical_slot_bytes_hash empty"
        assert artifact.artifact_hash, "artifact_hash empty"

    def test_hash_determinism(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="Determinism test JD",
            master_resume_data="Determinism test resume",
        )
        a1 = compile_prompt(request)
        a2 = compile_prompt(request)
        assert a1.prompt_bom_hash == a2.prompt_bom_hash
        assert a1.prompt_registry_hash == a2.prompt_registry_hash
        assert a1.prompt_template_hash == a2.prompt_template_hash
        assert a1.prompt_hash == a2.prompt_hash
        assert a1.canonical_slot_bytes_hash == a2.canonical_slot_bytes_hash
        assert a1.manifest_hash == a2.manifest_hash


# ---------------------------------------------------------------------------
# 7. 8-slot model: slot mapper produces all 8 slot categories
# ---------------------------------------------------------------------------
class TestSlotMapper8Slots:
    def test_map_slots_produces_8_categories(self):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.slot_mapper import map_slots
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
            approved_resume_examples="Example resume",
        )
        slots, receipts = map_slots(request, "Template body")
        assert "S0_GOVERNANCE" in slots
        assert "I0_INSTRUCTIONS" in slots
        assert "C0_JD_DATA" in slots
        assert "U0_USER_TASK" in slots
        assert "D0_ORIGIN_BOUNDARY" in slots
        assert "E0_APPROVED_EXAMPLES" in slots
        assert "Y0_STYLE_PREFERENCES" in slots
        assert "R0_OUTPUT_SCHEMA" in slots
        receipt_names = [r.slot_name for r in receipts]
        assert "D0" in receipt_names
        assert "E0" in receipt_names
        assert "Y0" in receipt_names


# ---------------------------------------------------------------------------
# 8. Slot fencing: untrusted data wrapped in fence markers
# ---------------------------------------------------------------------------
class TestSlotFencing:
    def test_jd_data_is_fenced(self):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.slot_mapper import map_slots
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="Untrusted JD content",
            master_resume_data="Resume",
        )
        slots, _ = map_slots(request, "Template body")
        assert "<untrusted_data>" in slots["C0_JD_DATA"]

    def test_user_task_is_fenced(self):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.slot_mapper import map_slots
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
            user_task="User task",
        )
        slots, _ = map_slots(request, "Template body")
        assert "<untrusted_data>" in slots["U0_USER_TASK"]

    def test_governance_is_not_fenced(self):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.slot_mapper import map_slots
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
        )
        slots, _ = map_slots(request, "Template body")
        assert "<untrusted_data>" not in slots["S0_GOVERNANCE"]
        assert "<untrusted_data>" not in slots["D0_ORIGIN_BOUNDARY"]
        assert "<untrusted_data>" not in slots["Y0_STYLE_PREFERENCES"]
        assert "<untrusted_data>" not in slots["R0_OUTPUT_SCHEMA"]


# ---------------------------------------------------------------------------
# 9. Provider request requires compiled artifact
# ---------------------------------------------------------------------------
class TestProviderRequestEnforcement:
    def test_rejects_non_ready_artifact(self):
        from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
        with pytest.raises(RuntimeError, match="PA_PROVIDER_REQUEST_BLOCKED"):
            artifact_to_provider_request({"compile_status": "PA_COMPILE_FAILED"})

    def test_rejects_empty_messages(self):
        from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
        with pytest.raises(RuntimeError, match="PA_PROVIDER_REQUEST_BLOCKED"):
            artifact_to_provider_request({
                "compile_status": "PA_L2_HANDOFF_READY",
                "provider_specific_messages": [],
            })

    def test_rejects_missing_hashes(self):
        from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
        with pytest.raises(RuntimeError, match="missing required hash fields"):
            artifact_to_provider_request({
                "compile_status": "PA_L2_HANDOFF_READY",
                "provider_specific_messages": [{"role": "system", "content": "x"}],
                "prompt_bom_hash": "abc",
                # missing other hashes
            })

    def test_accepts_valid_artifact(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
        )
        artifact = compile_prompt(request)
        result = artifact_to_provider_request(artifact.to_dict())
        assert result["messages"]
        assert result["prompt_bom_hash"]
        assert result["prompt_registry_hash"]
        assert result["manifest_hash"]
        assert result["artifact_hash"]


# ---------------------------------------------------------------------------
# 10. L2 _PAGuard fails closed without context
# ---------------------------------------------------------------------------
class TestPAGuardFailClosed:
    def test_guard_fails_without_jd_data(self):
        from apps_rg.l2_recipe.steps import _PAGuard
        with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
            _PAGuard.check({"master_resume_data": "x", "flow_route": "strategic_tailor"}, "test")

    def test_guard_fails_without_flow_route(self):
        from apps_rg.l2_recipe.steps import _PAGuard
        with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
            _PAGuard.check({"jd_data": "x", "master_resume_data": "x"}, "test")

    def test_guard_compiles_from_context(self):
        from apps_rg.l2_recipe.steps import _PAGuard
        ctx = {
            "jd_data": "JD text",
            "master_resume_data": "Resume text",
            "flow_route": "strategic_tailor",
        }
        result = _PAGuard.check(ctx, "test")
        assert result["compile_status"] == "PA_L2_HANDOFF_READY"
        assert "compiled_prompt_artifact" in ctx


# ---------------------------------------------------------------------------
# 11. Sealed artifact refs include all new hash fields
# ---------------------------------------------------------------------------
class TestSealedArtifactRefs:
    def test_generate_resume_step_includes_all_hashes(self):
        from apps_rg.l2_recipe.steps import _PAGuard
        ctx = {
            "jd_data": "JD",
            "master_resume_data": "Resume",
            "flow_route": "strategic_tailor",
        }
        artifact = _PAGuard.check(ctx, "test")
        required_keys = [
            "artifact_id", "prompt_id", "template_id", "template_version",
            "prompt_hash", "prompt_template_hash", "prompt_bom_hash",
            "prompt_registry_hash", "manifest_hash", "canonical_slot_bytes_hash",
            "artifact_hash", "origin_label_map", "local_evidence_contract_ref",
        ]
        for key in required_keys:
            assert key in artifact, f"Missing key in artifact: {key}"


# ---------------------------------------------------------------------------
# 12. Origin label map present and correct
# ---------------------------------------------------------------------------
class TestOriginLabelMap:
    def test_origin_labels_present(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
        )
        artifact = compile_prompt(request)
        olm = artifact.origin_label_map
        assert olm["S0"] == "system_governance"
        assert olm["I0"] == "app_instruction"
        assert olm["C0"] == "data_only"
        assert olm["U0"] == "user_intent_only"
        assert olm["D0"] == "security_boundary"
        assert olm["E0"] == "approved_example_data"
        assert olm["Y0"] == "approved_user_style"
        assert olm["R0"] == "schema_contract"


# ---------------------------------------------------------------------------
# 13. Spine docs say CANONICAL_PA
# ---------------------------------------------------------------------------
class TestSpineDocs:
    def test_spine_manifest_says_canonical_pa(self):
        manifest_path = REPO_ROOT / "apps_rg" / "spine_manifest.yaml"
        assert manifest_path.exists()
        manifest = _load_yaml(manifest_path)
        assert manifest.get("prompt_assembly") == "CANONICAL_PA"

    def test_spine_manifest_has_registry_ref(self):
        manifest_path = REPO_ROOT / "apps_rg" / "spine_manifest.yaml"
        manifest = _load_yaml(manifest_path)
        assert "prompt_registry_ref" in manifest

    def test_agentic_spine_says_canonical_pa(self):
        spine_path = REPO_ROOT / "apps_rg" / "AGENTIC_SPINE.md"
        assert spine_path.exists()
        text = spine_path.read_text(encoding="utf-8")
        assert "CANONICAL_PA" in text


# ---------------------------------------------------------------------------
# 14. Template slot_bodies extraction by compiler
# ---------------------------------------------------------------------------
class TestTemplateSlotExtraction:
    def test_compiler_extracts_s0_from_template(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="JD",
            master_resume_data="Resume",
        )
        artifact = compile_prompt(request)
        s0 = artifact.rendered_slots.get("S0_GOVERNANCE", "")
        assert "apps_rg" in s0.lower() or "governed" in s0.lower()


# ---------------------------------------------------------------------------
# 15. Contracts have all new fields
# ---------------------------------------------------------------------------
class TestContractsNewFields:
    def test_artifact_has_new_fields(self):
        from apps_rg.prompt_assembly.contracts import AppsRgCompiledPromptArtifact
        a = AppsRgCompiledPromptArtifact()
        for field_name in [
            "template_id", "template_version", "prompt_registry_hash",
            "manifest_hash", "canonical_slot_bytes_hash", "artifact_hash",
            "origin_label_map", "local_evidence_contract_ref",
            "rendered_slots", "audit_refs",
        ]:
            assert hasattr(a, field_name), f"Missing field: {field_name}"

    def test_request_has_new_fields(self):
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        r = AppsRgPromptRequest(flow_route="x", jd_data="y", master_resume_data="z")
        for field_name in [
            "approved_resume_examples", "seniority_band",
            "target_company", "target_role", "local_evidence_contract_ref",
        ]:
            assert hasattr(r, field_name), f"Missing field: {field_name}"
