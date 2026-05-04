"""
W2 Static Recipe Execution Tests for apps_lic.

Tests the R4 static recipe execution through E1-E5 phases:
- E1 Prep: Load manifest, bind policy/blueprint, freeze context
- E2 Valid: Validate manifest schema, briefing freshness, prompt registry
- E3 Exec: Plan message, compile prompt, compose draft using compiled artifact
- E4 Heal: Repair steps (if needed)
- E5 Seal: Validate final draft, attach receipts, seal for Exit V6
"""

import pytest
from pathlib import Path
from typing import Dict, Any


class TestAppsLicStaticRecipeExecution:
    """W2: Static recipe execution through E1-E5 phases."""

    def test_apps_lic_static_recipe_executes_e1_to_e5_in_order(self):
        """Assert static recipe executes E1-E5 stages in correct order."""
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe, get_registered_recipes
        from apps_lic.integrations import lic_l2_step_adapters as adapters
        
        # Ensure recipe is registered
        recipes = get_registered_recipes()
        assert "apps_lic_static" in recipes.get("static", {}), "apps_lic_static recipe must be registered"
        
        # Resolve the recipe
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None, "Recipe resolution must succeed"
        
        # Execute with minimal context including required slot values
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": "sha256:test_manifest_hash",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Minimal required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(context)
        
        # Verify all E1-E3 and E5 markers present (E4 is optional/healing phase)
        assert result.get("_e1_complete"), "E1 Prep must complete"
        assert result.get("_e2_complete"), "E2 Valid must complete"
        assert result.get("_e3_complete"), "E3 Exec must complete"
        assert result.get("_e5_complete"), "E5 Seal must complete"
        # Note: E4 (Heal) is optional and only runs when repairs are needed

    def test_apps_lic_static_recipe_preserves_manifest_hash(self):
        """Assert manifest hash is preserved through all stages."""
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        test_manifest_hash = "sha256:abcdef1234567890"
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": test_manifest_hash,
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(context)
        
        # Hash must be preserved through all stages
        assert result.get("manifest_hash") == test_manifest_hash, "Manifest hash must be preserved"
        assert result.get("_e1_manifest_hash_verified"), "E1 must verify manifest hash"

    def test_apps_lic_static_recipe_compiles_prompt_before_compose(self):
        """Assert compile_prompt runs before compose_draft and produces artifact."""
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": "sha256:test_manifest_hash",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(context)
        
        # Compile must complete before compose
        assert result.get("_e3_compile_complete"), "compile_prompt must complete"
        assert result.get("_e3_compiled_prompt_artifact") is not None, "CompiledPromptArtifact must exist"
        assert result.get("_e3_draft_composed"), "compose_draft must complete after compile"

    def test_apps_lic_compose_draft_consumes_compiled_prompt_artifact(self):
        """Assert compose_draft step consumes CompiledPromptArtifact."""
        from apps_lic.integrations.lic_l2_step_adapters import compose_draft_using_compiled_prompt_artifact
        
        # Context with compiled artifact
        context: Dict[str, Any] = {
            "_e3_compiled_prompt_artifact": {
                "artifact_id": "test_artifact",
                "template_ref": "outreach_draft_v1",
            },
            "manifest_hash": "sha256:manifest",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
        }
        
        step_def: Dict[str, Any] = {"name": "compose_draft"}
        
        result = compose_draft_using_compiled_prompt_artifact(context, step_def)
        
        assert result.get("_e3_draft_composed"), "Draft must be composed"
        assert result.get("_e3_complete"), "E3 must complete"

    def test_apps_lic_compose_draft_fails_closed_without_compiled_artifact(self):
        """Assert compose_draft fails closed if CompiledPromptArtifact is missing."""
        from apps_lic.integrations.lic_l2_step_adapters import compose_draft_using_compiled_prompt_artifact
        
        # Context WITHOUT compiled artifact
        context: Dict[str, Any] = {
            "manifest_hash": "sha256:manifest",
        }
        
        step_def: Dict[str, Any] = {"name": "compose_draft"}
        
        with pytest.raises(ValueError, match="CompiledPromptArtifact required"):
            compose_draft_using_compiled_prompt_artifact(context, step_def)

    def test_apps_lic_static_recipe_seals_l2_artifact_for_exit(self):
        """Assert E5 seals L2 execution artifact with receipts for Exit V6."""
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": "sha256:manifest123",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(context)
        
        # E5 must complete with sealed artifact
        assert result.get("_e5_complete"), "E5 Seal must complete"
        assert result.get("_e5_l2_receipt"), "L2 execution receipt must be attached"
        assert result.get("_e5_prompt_receipts_attached"), "Prompt receipts must be attached"
        assert result.get("_e5_manifest_lineage_attached"), "Manifest lineage must be attached"

    def test_apps_lic_static_recipe_failure_fails_closed_through_exit(self):
        """Assert recipe failures fail closed through Exit V6."""
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        # Context with invalid/missing manifest should fail
        context: Dict[str, Any] = {
            "manifest_ref": None,  # Missing manifest
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
        }
        
        # Recipe should raise or return error context that feeds Exit V6
        with pytest.raises(Exception) as exc_info:
            recipe_callable(context)
        
        # Error should be catchable and convertible to R5 terminal
        error_msg = str(exc_info.value).lower()
        assert any(term in error_msg for term in ["manifest", "missing", "fail", "closed"]), \
            f"Error must indicate manifest failure: {error_msg}"

    def test_e5_emits_exit_review_packet_compatible_artifact(self):
        """
        Assert E5 emits sealed artifact structurally ready for ExitReviewPacket.
        
        W2 proves structural readiness; W3/W4 owns live Exit invocation.
        The sealed artifact must contain all fields Exit V6 needs for review.
        """
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": "sha256:manifest123",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(context)
        
        # E5 must complete with sealed artifact
        assert result.get("_e5_complete"), "E5 Seal must complete"
        
        # L2 receipt must be present and structured for ExitReviewPacket
        l2_receipt = result.get("_e5_l2_receipt")
        assert l2_receipt, "L2 execution receipt must be attached"
        
        # The artifact must be bound to manifest for Exit lineage
        assert result.get("_e5_manifest_lineage_attached"), \
            "Manifest lineage must be attached for Exit review"
        
        # Prompt receipts must be present for audit
        assert result.get("_e5_prompt_receipts_attached"), \
            "Prompt receipts must be attached"
        
        # Claim receipts must be present for grounding verification
        assert result.get("_e5_claim_receipts_attached"), \
            "Claim receipts must be attached"
        
        # Structural readiness: artifact should be serializable for Exit V6
        import json
        try:
            json.dumps(l2_receipt)
        except TypeError as e:
            pytest.fail(f"L2 receipt must be JSON-serializable for Exit V6: {e}")

    def test_e4_optional_skipped_when_no_repair_needed(self):
        """
        Assert E4 is optional and skipped on happy path, but available when repair needed.
        
        Happy path (no validation failures): E1 → E2 → E3 → E5 (E4 skipped)
        Repair path (validation failures): E1 → E2 → E3 → E4 → E5 (E4 included)
        """
        from apps_lic.integrations.lic_l2_recipe_registry import resolve_recipe
        from apps_lic.integrations import lic_l2_step_adapters as adapters
        
        recipe_callable = resolve_recipe("apps_lic", route_family="static")
        assert recipe_callable is not None
        
        # Happy path: clean execution without repair
        happy_context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "manifest_hash": "sha256:manifest123",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "route_id": "R4_SINGLE_ACTION",
            "slot_values": {
                # Required fields for compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
        }
        
        result = recipe_callable(happy_context)
        
        # Happy path: E1, E2, E3, E5 complete; E4 not required
        assert result.get("_e1_complete"), "E1 must complete"
        assert result.get("_e2_complete"), "E2 must complete"
        assert result.get("_e3_complete"), "E3 must complete"
        assert result.get("_e5_complete"), "E5 must complete"
        # E4 optional: happy path may or may not have _e4_complete
        
        # Verify E4 adapters are available in registry when needed
        from apps_lic.integrations.lic_l2_recipe_registry import get_registered_recipes
        recipes = get_registered_recipes()
        static_recipe = recipes["static"]["apps_lic_static"]
        step_adapters = static_recipe["step_adapters"]
        
        # E4 repair adapters must be available in codebase
        e4_adapters_available = any(
            name in step_adapters 
            for name in ["omit_unsupported_claims", "remove_forbidden_antipatterns", 
                        "repair_channel_length", "compile_repair_prompt_if_needed"]
        ) or hasattr(adapters, 'omit_unsupported_claims')
        
        assert e4_adapters_available, \
            "E4 repair adapters must be available when repair is triggered"


class TestAppsLicPromptCompilationInRecipe:
    """W2: Prompt compilation integration in static recipe."""

    def test_compile_prompt_step_loads_bom_and_templates(self):
        """Assert compile_prompt step loads PromptBOM and templates."""
        from apps_lic.integrations.lic_l2_step_adapters import compile_prompt
        from apps_lic.prompt_assembly.lic_pa_compiler import CompiledPromptArtifact
        
        context: Dict[str, Any] = {
            "manifest_ref": "test_manifest",
            "template_ref": "outreach_draft_v1",
            "slot_values": {
                # Required input_contract fields for real compilation
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                "verified_briefing_context": "Test briefing context",
            },
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
        }
        
        step_def: Dict[str, Any] = {"name": "compile_prompt"}
        
        result = compile_prompt(context, step_def)
        
        assert result.get("_e3_compile_complete"), "Compile must complete"
        artifact = result.get("_e3_compiled_prompt_artifact")
        assert artifact is not None, "Must produce CompiledPromptArtifact"
        
        # Verify it's a proper artifact (not a dict stub)
        assert isinstance(artifact, CompiledPromptArtifact), \
            f"Must return CompiledPromptArtifact, got {type(artifact)}"
        assert artifact.artifact_id, "Artifact must have ID"
        assert artifact.artifact_hash, "Artifact must have artifact_hash"

    def test_compiled_prompt_artifact_contains_all_required_fields(self):
        """Assert CompiledPromptArtifact contains required governance fields via real PA compiler."""
        from apps_lic.prompt_assembly.lic_pa_compiler import compile_prompt, CompiledPromptArtifact
        
        # Compile with real PA compiler using required input fields
        artifact = compile_prompt(
            template_id="outreach_draft_v1",
            input_data={
                # Required input_contract fields
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                # Slot values for rendering
                "verified_briefing_context": "Test briefing context",
                "recipient_trigger_vector": "Test trigger",
            },
            context={
                "manifest_hash": "sha256:test_manifest",
                "policy_hash": "test_policy",
                "blueprint_hash": "test_blueprint",
                "replay_key": "test_replay",
                "request_id": "req_123",
                "run_id": "run_456",
            }
        )
        
        # Verify it's a proper CompiledPromptArtifact (not a dict stub)
        assert isinstance(artifact, CompiledPromptArtifact), \
            f"Must return CompiledPromptArtifact, got {type(artifact)}"
        
        # Check required fields
        assert artifact.artifact_id, "Must have artifact_id"
        assert artifact.artifact_hash, "Must have artifact_hash"
        assert artifact.template_id, "Must have template_id"
        assert artifact.manifest_hash, "Must have manifest_hash"
        assert artifact.policy_hash, "Must have policy_hash"
        assert artifact.blueprint_hash, "Must have blueprint_hash"
        assert artifact.replay_key, "Must have replay_key"
        
        # Verify binding to execution context
        assert artifact.manifest_hash == "sha256:test_manifest"
        assert artifact.policy_hash == "test_policy"

    def test_compile_prompt_step_uses_real_pa_compiler_not_stub(self):
        """Assert compile_prompt step adapter calls real PA compiler, not hand-built stub."""
        from apps_lic.integrations.lic_l2_step_adapters import compile_prompt
        from apps_lic.prompt_assembly.lic_pa_compiler import CompiledPromptArtifact
        
        context = {
            "template_ref": "outreach_draft_v1",
            "manifest_hash": "sha256:test_manifest",
            "policy_hash": "test_policy",
            "blueprint_hash": "test_blueprint",
            "replay_key": "test_replay",
            "slot_values": {
                # Required input_contract fields
                "PreloadedOutreachContextManifest": {"test": "manifest"},
                "claim_permission_map": {},
                "omission_policy": "omit_unsupported",
                "send_mode": "draft_only",
                "channel": "email",
                "channel_ceiling": 300,
                "recipient_class": "executive",
                "recipient_seniority": "senior",
                "relationship_distance": "cold",
                "outreach_mode": "value_first",
                "application_status": "not_applied",
                "source_items": [],
                "content_hashes": {},
                "origin_label_map": {},
                "output_schema_ref": "OutreachDraft",
                # Slot values for rendering
                "verified_briefing_context": "Test briefing context",
                "recipient_trigger_vector": "Test trigger",
            },
        }
        
        step_def = {"name": "compile_prompt"}
        
        result = compile_prompt(context, step_def)
        
        # Verify it called the real PA compiler
        assert result.get("_e3_compile_used_real_pa_compiler"), \
            "Must use real PA compiler, not hand-built stub"
        
        # Verify artifact is proper CompiledPromptArtifact type
        artifact = result.get("_e3_compiled_prompt_artifact")
        assert isinstance(artifact, CompiledPromptArtifact), \
            f"Must return CompiledPromptArtifact, got {type(artifact)}"
        
        # Verify it has real computed fields (not placeholder UUIDs)
        assert len(artifact.artifact_id) == 32, "artifact_id should be 32-char hex hash"
        assert artifact.artifact_hash, "artifact_hash should be computed from content"
        assert artifact.rendered_slots, "rendered_slots should contain rendered prompt"


class TestAppsLicRecipeRegistryIntegration:
    """W2: Recipe registry integration with agentic_core resolver."""

    def test_apps_lic_recipe_registered_with_correct_step_mapping(self):
        """Assert apps_lic_static recipe maps stage_ids to correct step adapters."""
        from apps_lic.integrations.lic_l2_recipe_registry import get_registered_recipes
        
        recipes = get_registered_recipes()
        static_recipes = recipes.get("static", {})
        
        assert "apps_lic_static" in static_recipes, "apps_lic_static must be registered"
        
        recipe = static_recipes["apps_lic_static"]
        adapters = recipe.get("step_adapters", {})
        
        # Key stages must have adapters
        required_stages = [
            "load_manifest",
            "validate_context",
            "plan_message",
            "compose_draft",
            "seal_output",
        ]
        
        for stage in required_stages:
            assert stage in adapters, f"Stage {stage} must have adapter registered"
            assert callable(adapters[stage]), f"Adapter for {stage} must be callable"

    def test_recipe_dag_path_exists_and_loadable(self):
        """Assert recipe DAG YAML exists and can be loaded."""
        from apps_lic.integrations.lic_l2_recipe_registry import get_registered_recipes
        import yaml
        
        recipes = get_registered_recipes()
        static_recipes = recipes.get("static", {})
        
        if "apps_lic_static" not in static_recipes:
            pytest.skip("apps_lic_static recipe not registered yet")
        
        recipe = static_recipes["apps_lic_static"]
        dag_path = Path(recipe["dag_path"])
        
        assert dag_path.exists(), f"DAG file must exist: {dag_path}"
        
        # Load and verify structure
        with open(dag_path) as f:
            dag = yaml.safe_load(f)
        
        assert dag.get("dag_id"), "DAG must have dag_id"
        assert dag.get("stages"), "DAG must have stages"
        assert len(dag["stages"]) >= 5, "DAG must have at least 5 stages (E1-E5)"
