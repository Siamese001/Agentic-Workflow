"""
W3 acceptance tests: apps_rg workflow manifest and registry binding.

Verifies:
  - Workflow manifest has valid node topology (depends_on refs all resolve)
  - Manifest cross-profile refs all point to existing files or known profile ids
  - route_registry.yaml contains the managed workflow route entry
  - Managed workflow route is registered_not_active (not live yet)
  - Workflow manifest has no Python executable code
  - Gate cross-refs are internally consistent between manifest and runtime_gate_profile
  - Section prompt BOM slot refs are valid against prompt_bom.yaml
"""
import json
from pathlib import Path

import pytest
import yaml

_APPS_RG = Path(__file__).resolve().parents[2] / "apps_rg"
_CONFIG = _APPS_RG / "config"
_DOMAIN = _CONFIG / "domain_contract"
_MANIFEST = _CONFIG / "workflow_manifest.resume_generation.v1.yaml"
_ROUTE_REGISTRY = _CONFIG / "route_registry.yaml"
_RUNTIME_GATE_PROFILE = _DOMAIN / "runtime_gate_profile.resume_generation.v1.json"
_PROMPT_BOM = _APPS_RG / "prompt_assembly" / "prompt_bom.yaml"


def _load_manifest():
    with open(_MANIFEST, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_route_registry():
    with open(_ROUTE_REGISTRY, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_runtime_gate_profile():
    with open(_RUNTIME_GATE_PROFILE, encoding="utf-8") as f:
        return json.load(f)


def _load_prompt_bom():
    with open(_PROMPT_BOM, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Node topology ─────────────────────────────────────────────────────────

class TestWorkflowManifestNodeTopology:
    def test_all_depends_on_refs_resolve(self):
        """Every node's depends_on list references a node_id that exists in the manifest."""
        data = _load_manifest()
        node_ids = {n["node_id"] for n in data["nodes"]}
        for node in data["nodes"]:
            for dep in node.get("depends_on", []):
                assert dep in node_ids, (
                    f"Node '{node['node_id']}' depends_on '{dep}' which is not a declared node"
                )

    def test_no_circular_self_dependency(self):
        """A node must not depend on itself."""
        data = _load_manifest()
        for node in data["nodes"]:
            assert node["node_id"] not in node.get("depends_on", []), (
                f"Node '{node['node_id']}' depends on itself"
            )

    def test_exit_nodes_have_final_render_dependency(self):
        """ats_validate and guardrail nodes must depend on final_render."""
        data = _load_manifest()
        exit_nodes = [n for n in data["nodes"]
                      if n["node_type"] in ("validation", "guardrail")]
        for node in exit_nodes:
            assert "final_render" in node.get("depends_on", []), (
                f"Node '{node['node_id']}' (type={node['node_type']}) should depend on final_render"
            )

    def test_generation_nodes_have_non_empty_required_runtime_gates(self):
        """Every generation or guardrail node must have at least one required_runtime_gate."""
        data = _load_manifest()
        for node in data["nodes"]:
            if node["node_type"] in ("generation", "guardrail"):
                gates = node.get("required_runtime_gates", [])
                assert len(gates) >= 1, (
                    f"Node '{node['node_id']}' (type={node['node_type']}) has no required_runtime_gates"
                )

    def test_node_types_are_valid(self):
        valid_types = {"ingestion", "analysis", "generation", "validation", "guardrail", "render"}
        data = _load_manifest()
        for node in data["nodes"]:
            assert node["node_type"] in valid_types, (
                f"Node '{node['node_id']}' has invalid node_type '{node['node_type']}'"
            )

    def test_tiers_are_valid(self):
        valid_tiers = {"L0", "L1", "L2", "L3", "C0", "PA", "Exit", "L6"}
        data = _load_manifest()
        for node in data["nodes"]:
            assert node["tier"] in valid_tiers, (
                f"Node '{node['node_id']}' has invalid tier '{node['tier']}'"
            )

    def test_selection_policies_are_valid(self):
        valid_policies = {
            "best_factual_score", "best_role_alignment", "rule_based", "passthrough"
        }
        data = _load_manifest()
        for node in data["nodes"]:
            assert node["selection_policy"] in valid_policies, (
                f"Node '{node['node_id']}' has invalid selection_policy '{node['selection_policy']}'"
            )

    def test_archive_policies_are_valid(self):
        valid_policies = {"all_candidates", "winner_only", "none"}
        data = _load_manifest()
        for node in data["nodes"]:
            assert node["archive_policy"] in valid_policies, (
                f"Node '{node['node_id']}' has invalid archive_policy '{node['archive_policy']}'"
            )


# ── Cross-profile refs ────────────────────────────────────────────────────

class TestWorkflowManifestCrossProfileRefs:
    def test_orchestration_profile_ref_correct(self):
        data = _load_manifest()
        assert data["orchestration_profile_ref"] == "aop::apps_rg::resume_generation::v1"

    def test_runtime_gate_profile_ref_correct(self):
        data = _load_manifest()
        assert data["runtime_gate_profile_ref"] == "rgp::apps_rg::resume_generation::v1"

    def test_exit_profile_ref_correct(self):
        data = _load_manifest()
        assert data["exit_profile_ref"] == "xp::apps_rg::resume_generation::v1"

    def test_judge_profile_ref_correct(self):
        data = _load_manifest()
        assert data["judge_profile_ref"] == "jp::apps_rg::resume_generation::v1"

    def test_provider_profile_ref_correct(self):
        data = _load_manifest()
        assert data["provider_profile_ref"] == "pvp::apps_rg::resume_generation::v1"

    def test_candidate_gate_profile_ref_correct(self):
        data = _load_manifest()
        assert data["candidate_gate_profile_ref"] == "cgp::apps_rg::resume_generation::v1"

    def test_meta_feedback_profile_ref_correct(self):
        data = _load_manifest()
        assert data["meta_feedback_profile_ref"] == "lp::apps_rg::resume_generation::v1"

    def test_threshold_profile_ref_correct(self):
        data = _load_manifest()
        assert data["threshold_profile_ref"] == "atp::apps_rg::resume_generation::v1"

    def test_retrieval_profile_ref_correct(self):
        data = _load_manifest()
        assert data["retrieval_profile_ref"] == "arp::apps_rg::resume_generation::v1"

    def test_workflow_manifest_path_exists_on_disk(self):
        data = _load_manifest()
        ref_path = data.get("schema_ref", "")
        p = Path(__file__).resolve().parents[2] / ref_path
        assert p.exists(), f"schema_ref path not on disk: {ref_path}"


# ── Route registry binding ────────────────────────────────────────────────

class TestRouteRegistryBinding:
    def test_route_registry_parses(self):
        data = _load_route_registry()
        assert isinstance(data, dict)

    def test_deterministic_pipeline_route_present(self):
        data = _load_route_registry()
        route_ids = {r["route_id"] for r in data["routes"]}
        assert "apps_rg.resume_generation_v1" in route_ids

    def test_managed_workflow_route_registered(self):
        data = _load_route_registry()
        route_ids = {r["route_id"] for r in data["routes"]}
        assert "apps_rg.resume_generation_managed_v1" in route_ids, (
            "Managed workflow route 'apps_rg.resume_generation_managed_v1' not in route_registry.yaml"
        )

    def test_managed_route_status_is_not_active(self):
        data = _load_route_registry()
        managed_route = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        )
        assert managed_route.get("status") == "registered_not_active", (
            "Managed workflow route must be 'registered_not_active' in W3 — not yet live"
        )

    def test_managed_route_l3_required_true(self):
        data = _load_route_registry()
        managed_route = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        )
        assert managed_route["l3_required"] is True

    def test_managed_route_has_workflow_manifest_ref(self):
        data = _load_route_registry()
        managed_route = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        )
        assert managed_route.get("workflow_manifest_ref") == "wfm::apps_rg::resume_generation::v1"

    def test_managed_route_manifest_path_exists(self):
        data = _load_route_registry()
        managed_route = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_rg.resume_generation_managed_v1"
        )
        manifest_path = managed_route.get("workflow_manifest_path")
        assert manifest_path is not None
        p = Path(__file__).resolve().parents[2] / manifest_path
        assert p.exists(), f"workflow_manifest_path not on disk: {manifest_path}"

    def test_deterministic_route_unchanged(self):
        """The existing deterministic pipeline route must not have changed execution_form or l3_required."""
        data = _load_route_registry()
        det_route = next(r for r in data["routes"] if r["route_id"] == "apps_rg.resume_generation_v1")
        assert det_route["execution_form"] == "DETERMINISTIC_PIPELINE"
        assert det_route["l3_required"] is False


# ── Gate cross-reference consistency ─────────────────────────────────────

class TestGateCrossRefConsistency:
    def test_manifest_runtime_gate_ids_declared_in_gate_profile(self):
        """Gate IDs referenced in node required_runtime_gates must exist in gate profile stages."""
        manifest = _load_manifest()
        gate_profile = _load_runtime_gate_profile()

        # Collect all gate_ids from all stages in the gate profile
        declared_gate_ids = set()
        for stage_data in gate_profile["stages"].values():
            for gate in stage_data.get("required_gates", []):
                declared_gate_ids.add(gate["gate_id"])
        # Also add conditional gate ids
        for cond_gate_id in gate_profile.get("conditional_gate_triggers", {}).keys():
            declared_gate_ids.add(cond_gate_id)

        # Check manifest node gate references
        undeclared = []
        for node in manifest["nodes"]:
            for gate_ref in node.get("required_runtime_gates", []):
                if gate_ref not in declared_gate_ids:
                    undeclared.append(f"{node['node_id']}: {gate_ref}")

        assert not undeclared, (
            f"Manifest references gate IDs not in runtime_gate_profile: {undeclared}"
        )


# ── No executable code in manifest ───────────────────────────────────────

class TestNoExecutableCodeInManifest:
    _FORBIDDEN_PATTERNS = [
        ("\nimport apps_rg", "Python import"),
        ("\nfrom apps_rg", "Python import"),
        ("\nimport agentic_core", "Python import"),
        ("\ndef ", "Python function definition"),
        ("\nclass ", "Python class definition"),
        ("\nlambda ", "Python lambda"),
        ("\nsubprocess", "subprocess call"),
        ("\nos.system", "os.system call"),
    ]

    @pytest.mark.parametrize("pattern,label", _FORBIDDEN_PATTERNS)
    def test_manifest_has_no_executable_pattern(self, pattern, label):
        content = "\n" + _MANIFEST.read_text(encoding="utf-8")
        assert pattern not in content, (
            f"workflow_manifest contains forbidden pattern ({label}): '{pattern}'"
        )


# ── Prompt BOM slot refs ──────────────────────────────────────────────────

class TestSectionPromptSlotRefs:
    def _all_valid_slots(self):
        bom = _load_prompt_bom()
        return set(bom["required_slots"]) | set(bom.get("slot_definitions", {}).keys())

    @pytest.mark.parametrize("fname", [
        "header_block.yaml",
        "professional_summary.yaml",
        "skills_block.yaml",
        "experience_block.yaml",
        "education_block.yaml",
        "certifications_block.yaml",
        "selected_projects_block.yaml",
        "final_render.yaml",
    ])
    def test_section_prompt_slots_are_valid_bom_slots(self, fname):
        """All slot references in section prompts must be valid slots from prompt_bom.yaml."""
        valid_slots = self._all_valid_slots()
        p = _CONFIG / "section_prompts" / fname
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        required = data.get("slot_requirements", {}).get("required", [])
        optional = data.get("slot_requirements", {}).get("optional", [])
        for slot in required + optional:
            assert slot in valid_slots, (
                f"{fname}: slot '{slot}' not in prompt_bom.yaml valid slots {valid_slots}"
            )
