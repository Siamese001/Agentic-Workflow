"""
W2 verification tests for apps_repo_brief Route Consolidation + Config Canonicalization.

Covers:
  P2.2 — Route registry migration (canonical route + deprecated aliases)
  P2.3 — C0 contradiction resolved in cert_route_registry
  P2.4 — Deprecation notice in apps_exec/spine_manifest.yaml
  P2.7 — Sibling doc comment updates
  P2.8 — cache_compat.yaml schema
  P2.9 — PromptBOM S0-R0 slots
  P2.10 — Prompt registry template references
  P2.11 — Real template bodies (no placeholders)
  P2.12 — PA compiler scaffold
  P2.6 — OTEL dual-span adapter

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P2.*
"""

from __future__ import annotations

import importlib
from pathlib import Path
import yaml
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARB_DIR = _REPO_ROOT / "apps_repo_brief"
_EXEC_DIR = _REPO_ROOT / "apps_exec"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), f"Expected mapping at {path}"
    return data


# ---------------------------------------------------------------------------
# P2.2 — Route registry: canonical route + deprecated aliases present
# ---------------------------------------------------------------------------

class TestP22RouteRegistry:
    _reg = _REPO_ROOT / "apps_repo_brief" / "config" / "route_registry.yaml"

    def test_route_registry_exists(self):
        assert self._reg.exists(), "apps_repo_brief/config/route_registry.yaml missing"

    def test_canonical_route_present(self):
        data = _load_yaml(self._reg)
        ids = [r["route_id"] for r in data.get("routes", [])]
        assert "apps_repo_brief.executive_brief_v1" in ids

    def test_canonical_route_is_r3_grounded_read(self):
        data = _load_yaml(self._reg)
        canon = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_repo_brief.executive_brief_v1"
        )
        assert canon["route_family"] == "R3_SIMPLE_GROUNDED_READ"

    def test_canonical_route_requires_c0(self):
        data = _load_yaml(self._reg)
        canon = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_repo_brief.executive_brief_v1"
        )
        assert canon["c0_required"] is True

    def test_deprecated_alias_execution_v1_present(self):
        data = _load_yaml(self._reg)
        ids = [r["route_id"] for r in data.get("routes", [])]
        assert "apps_exec.execution_v1" in ids

    def test_deprecated_alias_single_step_v1_present(self):
        data = _load_yaml(self._reg)
        ids = [r["route_id"] for r in data.get("routes", [])]
        assert "apps_exec.single_step_v1" in ids

    def test_deprecated_aliases_marked_deprecated(self):
        data = _load_yaml(self._reg)
        for r in data["routes"]:
            if r["route_id"].startswith("apps_exec."):
                assert r.get("deprecated") is True, (
                    f"apps_exec route {r['route_id']} must be marked deprecated"
                )

    def test_deprecated_aliases_point_to_canonical(self):
        data = _load_yaml(self._reg)
        for r in data["routes"]:
            if r["route_id"].startswith("apps_exec."):
                assert r.get("deprecation_replacement") == "apps_repo_brief.executive_brief_v1"


# ---------------------------------------------------------------------------
# P2.3 — cert_route_registry: C0 contradiction resolved
# ---------------------------------------------------------------------------

class TestP23CertRouteRegistry:
    _reg = _REPO_ROOT / "apps_repo_brief" / "config" / "cert_route_registry.yaml"

    def test_cert_route_registry_exists(self):
        assert self._reg.exists()

    def test_canonical_cert_route_present(self):
        data = _load_yaml(self._reg)
        ids = [r["route_id"] for r in data.get("routes", [])]
        assert "apps_repo_brief.executive_brief_v1" in ids

    def test_cert_route_requires_c0(self):
        data = _load_yaml(self._reg)
        r = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_repo_brief.executive_brief_v1"
        )
        assert r.get("c0_required") is True

    def test_no_template_only_language(self):
        content = (self._reg).read_text(encoding="utf-8")
        assert "template-driven (no C0" not in content, (
            "apps_repo_brief cert_route_registry must not contain 'template-driven (no C0' — contradiction resolved in W1/W2"
        )

    def test_invoke_exit_eval_true(self):
        data = _load_yaml(self._reg)
        r = next(
            r for r in data["routes"]
            if r["route_id"] == "apps_repo_brief.executive_brief_v1"
        )
        assert r.get("invoke_exit_eval") is True


# ---------------------------------------------------------------------------
# P2.4 — apps_exec/spine_manifest.yaml has deprecation notice
# ---------------------------------------------------------------------------

class TestP24ArtifactRename:
    _manifest = _EXEC_DIR / "spine_manifest.yaml"

    def test_exec_spine_manifest_has_deprecation_notice(self):
        content = self._manifest.read_text(encoding="utf-8")
        assert "DEPRECATION NOTICE" in content, (
            "apps_exec/spine_manifest.yaml should contain a W2 DEPRECATION NOTICE"
        )

    def test_exec_spine_manifest_references_apps_repo_brief(self):
        content = self._manifest.read_text(encoding="utf-8")
        assert "apps_repo_brief" in content


# ---------------------------------------------------------------------------
# P2.7 — Sibling spine manifests updated
# ---------------------------------------------------------------------------

class TestP27SiblingDocUpdates:
    def test_apps_rg_spine_manifest_notes_rename(self):
        path = _REPO_ROOT / "apps_rg" / "spine_manifest.yaml"
        if not path.exists():
            pytest.skip("apps_rg/spine_manifest.yaml not present")
        content = path.read_text(encoding="utf-8")
        assert "apps_repo_brief" in content

    def test_apps_rfp_spine_manifest_notes_rename(self):
        path = _REPO_ROOT / "apps_rfp" / "spine_manifest.yaml"
        if not path.exists():
            pytest.skip("apps_rfp/spine_manifest.yaml not present")
        content = path.read_text(encoding="utf-8")
        assert "apps_repo_brief" in content


# ---------------------------------------------------------------------------
# P2.8 — cache_compat.yaml schema
# ---------------------------------------------------------------------------

class TestP28CacheCompatSchema:
    _schema = _ARB_DIR / "config" / "cache_compat.yaml"

    def test_cache_compat_exists(self):
        assert self._schema.exists()

    def test_r1a_section_present(self):
        data = _load_yaml(self._schema)
        assert "r1a_exact_cache" in data

    def test_r1a_required_fields_complete(self):
        data = _load_yaml(self._schema)
        required = data["r1a_exact_cache"]["required_fields"]
        expected = {
            "normalized_request_hash", "audience", "emphasis_areas_hash",
            "repo_snapshot_id", "retrieval_surface_id", "policy_hash",
            "blueprint_hash", "persona_schema_version", "rubric_version",
            "source_freshness_window",
        }
        assert expected.issubset(set(required))

    def test_r1b_section_present(self):
        data = _load_yaml(self._schema)
        assert "r1b_semantic_cache" in data

    def test_board_forbidden_from_semantic_terminal_return(self):
        data = _load_yaml(self._schema)
        forbidden_audiences = data["r1b_semantic_cache"]["terminal_return_forbidden_audiences"]
        assert "board" in forbidden_audiences

    def test_forbidden_patterns_present(self):
        data = _load_yaml(self._schema)
        assert "forbidden" in data
        assert "semantic_terminal_return_for_board_without_exact_match" in data["forbidden"]


# ---------------------------------------------------------------------------
# P2.9 — PromptBOM S0-R0 slots
# ---------------------------------------------------------------------------

class TestP29PromptBOM:
    _bom = _ARB_DIR / "prompt_assembly" / "prompt_bom.yaml"

    def test_prompt_bom_exists(self):
        assert self._bom.exists()

    def test_all_required_slots_present(self):
        data = _load_yaml(self._bom)
        slots = data.get("slots", {})
        required_slot_ids = {"S0", "I0", "C0", "U0", "A0", "D0", "R0"}
        assert required_slot_ids.issubset(set(slots.keys()))

    def test_optional_slots_present(self):
        data = _load_yaml(self._bom)
        slots = data.get("slots", {})
        assert "E0" in slots
        assert "Y0" in slots

    def test_c0_slot_has_binding_contract(self):
        data = _load_yaml(self._bom)
        c0 = data["slots"]["C0"]
        assert "binding_contract" in c0
        assert "FinalEvidenceContract" in c0["binding_contract"]

    def test_all_required_slots_marked_required(self):
        data = _load_yaml(self._bom)
        for slot_id in ["S0", "I0", "C0", "U0", "A0", "D0", "R0"]:
            slot = data["slots"][slot_id]
            assert slot.get("required") is True, f"Slot {slot_id} must be required=true"

    def test_hash_fields_present(self):
        data = _load_yaml(self._bom)
        assert "hash_fields" in data

    def test_route_id_is_canonical(self):
        data = _load_yaml(self._bom)
        assert data.get("route_id") == "apps_repo_brief.executive_brief_v1"


# ---------------------------------------------------------------------------
# P2.10 — Prompt registry template references
# ---------------------------------------------------------------------------

class TestP210PromptRegistry:
    _reg = _ARB_DIR / "config" / "prompt_registry.yaml"

    def test_prompt_registry_exists(self):
        assert self._reg.exists()

    def test_synthesis_template_registered(self):
        data = _load_yaml(self._reg)
        ids = [t["template_id"] for t in data.get("templates", [])]
        assert "repo_brief_synthesis_v1" in ids

    def test_evidence_to_context_template_registered(self):
        data = _load_yaml(self._reg)
        ids = [t["template_id"] for t in data.get("templates", [])]
        assert "repo_evidence_to_prompt_context_v1" in ids

    def test_unsupported_claim_template_registered(self):
        data = _load_yaml(self._reg)
        ids = [t["template_id"] for t in data.get("templates", [])]
        assert "unsupported_repo_claim_omission_v1" in ids

    def test_caveat_repair_template_registered(self):
        data = _load_yaml(self._reg)
        ids = [t["template_id"] for t in data.get("templates", [])]
        assert "caveat_and_confidence_repair_v1" in ids

    def test_length_repair_template_registered(self):
        data = _load_yaml(self._reg)
        ids = [t["template_id"] for t in data.get("templates", [])]
        assert "brief_length_and_structure_repair_v1" in ids

    def test_all_templates_have_path_field(self):
        data = _load_yaml(self._reg)
        for t in data.get("templates", []):
            assert "path" in t, f"Template {t.get('template_id')} missing path field"

    def test_hash_fields_present(self):
        data = _load_yaml(self._reg)
        assert "hash_fields" in data


# ---------------------------------------------------------------------------
# P2.11 — Real template bodies (no placeholders)
# ---------------------------------------------------------------------------

class TestP211TemplateFiles:
    _tpl_dir = _ARB_DIR / "prompt_assembly" / "templates"

    def _required_templates(self):
        return [
            "repo_brief_synthesis_v1.yaml",
            "repo_evidence_to_prompt_context_v1.yaml",
            "unsupported_repo_claim_omission_v1.yaml",
            "caveat_and_confidence_repair_v1.yaml",
            "brief_length_and_structure_repair_v1.yaml",
            "repo_citation_alignment_repair_v1.yaml",
        ]

    def test_templates_directory_exists(self):
        assert self._tpl_dir.exists()

    def test_all_required_template_files_exist(self):
        for filename in self._required_templates():
            path = self._tpl_dir / filename
            assert path.exists(), f"Template file missing: {filename}"

    def test_no_todo_in_templates(self):
        for filename in self._required_templates():
            content = (self._tpl_dir / filename).read_text(encoding="utf-8")
            assert "TODO" not in content, f"Template {filename} contains TODO placeholder"

    def test_all_templates_have_input_contract(self):
        for filename in self._required_templates():
            data = _load_yaml(self._tpl_dir / filename)
            assert "input_contract" in data, f"Template {filename} missing input_contract"

    def test_all_templates_have_forbidden_behaviors(self):
        for filename in self._required_templates():
            data = _load_yaml(self._tpl_dir / filename)
            assert "forbidden_behaviors" in data, f"Template {filename} missing forbidden_behaviors"

    def test_all_templates_have_hash_fields(self):
        for filename in self._required_templates():
            data = _load_yaml(self._tpl_dir / filename)
            assert "hash_fields" in data, f"Template {filename} missing hash_fields"

    def test_synthesis_template_has_slot_bodies(self):
        data = _load_yaml(self._tpl_dir / "repo_brief_synthesis_v1.yaml")
        assert "slot_bodies" in data

    def test_synthesis_template_forbidden_behaviors_no_retrieve(self):
        data = _load_yaml(self._tpl_dir / "repo_brief_synthesis_v1.yaml")
        fbs = data.get("forbidden_behaviors", [])
        assert "retrieve_new_information" in fbs

    def test_repair_templates_have_authorized_actions(self):
        for filename in [
            "caveat_and_confidence_repair_v1.yaml",
            "brief_length_and_structure_repair_v1.yaml",
            "repo_citation_alignment_repair_v1.yaml",
        ]:
            data = _load_yaml(self._tpl_dir / filename)
            assert "authorized_repair_actions" in data, (
                f"Repair template {filename} missing authorized_repair_actions"
            )

    def test_repair_templates_disallow_new_evidence_retrieval(self):
        for filename in [
            "caveat_and_confidence_repair_v1.yaml",
            "brief_length_and_structure_repair_v1.yaml",
            "repo_citation_alignment_repair_v1.yaml",
        ]:
            data = _load_yaml(self._tpl_dir / filename)
            fbs = data.get("forbidden_behaviors", [])
            assert "retrieve_new_evidence" in fbs, (
                f"Repair template {filename} must forbid retrieve_new_evidence"
            )

    def test_evidence_to_context_blocks_weak_to_strong_promotion(self):
        data = _load_yaml(
            self._tpl_dir / "repo_evidence_to_prompt_context_v1.yaml"
        )
        fbs = data.get("forbidden_behaviors", [])
        assert "promote_weak_evidence_to_strong" in fbs

    def test_templates_have_output_contract(self):
        for filename in self._required_templates():
            data = _load_yaml(self._tpl_dir / filename)
            assert "output_contract" in data, f"Template {filename} missing output_contract"

    def test_templates_have_validation_rules(self):
        for filename in self._required_templates():
            data = _load_yaml(self._tpl_dir / filename)
            assert "validation_rules" in data, f"Template {filename} missing validation_rules"


# ---------------------------------------------------------------------------
# P2.12 — PA compiler scaffold importable and functional
# ---------------------------------------------------------------------------

class TestP212PACompiler:
    def test_pa_compiler_importable(self):
        mod = importlib.import_module("apps_repo_brief.prompt_assembly.repo_brief_pa_compiler")
        assert hasattr(mod, "RepoBriefPACompiler")

    def test_pa_compiler_loads_bom_and_registry(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        compiler.load()
        assert compiler._bom
        assert compiler._registry

    def test_pa_compiler_resolves_synthesis_template(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        entry = compiler._get_template_entry("repo_brief_synthesis_v1")
        assert entry["template_id"] == "repo_brief_synthesis_v1"

    def test_pa_compiler_validates_missing_slots(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        missing = compiler.validate_slots("repo_brief_synthesis_v1", {"S0", "I0"})
        assert len(missing) > 0  # C0, U0, A0, D0, R0 are missing

    def test_pa_compiler_no_missing_slots_when_all_provided(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        all_slots = {"S0", "I0", "C0", "U0", "A0", "D0", "E0", "Y0", "R0"}
        missing = compiler.validate_slots("repo_brief_synthesis_v1", all_slots)
        assert missing == []

    def test_pa_compiler_validates_input_contract_missing(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        missing = compiler.validate_input_contract("repo_brief_synthesis_v1", {})
        assert "FinalEvidenceContract" in missing

    def test_pa_compiler_emits_compiled_artifact(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        bundle = {
            "normalized_repo_brief_task": {},
            "FinalEvidenceContract": {"contract_type": "apps_repo_brief.FinalEvidenceContract.v1", "status": {}},
            "BriefingCoverageMatrix": {"briefing_profile_id": "bp-1"},
            "SourcePortfolioSummary": {"surface_id": "sp-1"},
            "ClaimEvidenceMap": {"map_id": "cem-1"},
            "ContradictionMatrix": {"matrix_id": "cm-1"},
            "FreshnessReport": {"report_id": "fr-1"},
            "SynthesisGuidanceForPA": {},
            "repo_brief_depth_profile": "REPO_BRIEF_STANDARD",
            "audience_schema_ref": "recruiter_v1",
            "output_schema_ref": "governed_repo_brief_packet_v1",
            "policy_hash": "ph-aaa",
            "blueprint_hash": "bh-bbb",
            "replay_key": "rk-ccc",
        }
        artifact = compiler.compile(
            template_id="repo_brief_synthesis_v1",
            evidence_bundle=bundle,
            request_id="req-1",
            run_id="run-1",
            trace_id="trace-1",
            route_id="apps_repo_brief.executive_brief_v1",
            selected_capability="apps_repo_brief.generate_executive_brief_v1",
            policy_hash="ph-aaa",
            blueprint_hash="bh-bbb",
            replay_key="rk-ccc",
        )
        assert artifact["artifact_id"].startswith("cpa.")
        assert "manifest_hash" in artifact
        assert "prompt_bom_hash" in artifact
        assert "prompt_registry_hash" in artifact
        assert "template_hash" in artifact
        assert artifact["route_id"] == "apps_repo_brief.executive_brief_v1"

    def test_pa_compiler_raises_on_unknown_template(self):
        from apps_repo_brief.prompt_assembly.repo_brief_pa_compiler import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        with pytest.raises(ValueError, match="not found in prompt registry"):
            compiler._get_template_entry("nonexistent_template_id")

    def test_pa_compiler_does_not_retrieve_or_route(self):
        """Structural: PA compiler module must not import routing or retrieval."""
        import inspect
        from apps_repo_brief.prompt_assembly import repo_brief_pa_compiler as mod
        src = inspect.getsource(mod)
        assert "AgenticRouter" not in src
        assert "c0_retrieval" not in src
        assert "adg_edge_fanout" not in src


# ---------------------------------------------------------------------------
# P2.6 — OTEL dual-span adapter
# ---------------------------------------------------------------------------

class TestP26OTELDualSpan:
    def test_observability_adapter_importable(self):
        mod = importlib.import_module(
            "apps_repo_brief.integrations.observability_adapter"
        )
        assert hasattr(mod, "RepoBriefObservabilityAdapter")

    def test_emit_brief_start_emits_dual_spans(self):
        from apps_repo_brief.integrations.observability_adapter import (
            RepoBriefObservabilityAdapter,
        )

        class _FakeRequest:
            trace_id = "t1"
            audience = "recruiter"
            emphasis_areas = []
            dry_run = False

        adapter = RepoBriefObservabilityAdapter()
        adapter.emit_brief_start(_FakeRequest())
        metrics = adapter.get_metrics()
        event_types = {m["event_type"] for m in metrics}
        assert "apps_repo_brief.brief_start" in event_types
        assert "apps_exec.brief_start" in event_types

    def test_canonical_metrics_excludes_legacy(self):
        from apps_repo_brief.integrations.observability_adapter import (
            RepoBriefObservabilityAdapter,
        )

        class _FakeRequest:
            trace_id = "t1"
            audience = "cto"
            emphasis_areas = []
            dry_run = False

        adapter = RepoBriefObservabilityAdapter()
        adapter.emit_brief_start(_FakeRequest())
        canonical = adapter.get_canonical_metrics()
        for m in canonical:
            assert not m.get("_legacy")

    def test_evidence_gate_emits_canonical_only(self):
        from apps_repo_brief.integrations.observability_adapter import (
            RepoBriefObservabilityAdapter,
        )
        adapter = RepoBriefObservabilityAdapter()
        event = adapter.emit_evidence_gate(
            evidence_status="PASS",
            source_count=10,
            citation_anchor_count=20,
            section_coverage_pct=0.9,
        )
        assert event["event_type"] == "apps_repo_brief.evidence_gate"
        assert event["evidence_status"] == "PASS"
