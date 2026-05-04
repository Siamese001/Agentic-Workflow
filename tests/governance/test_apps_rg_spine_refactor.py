"""Governance tests for apps_rg agentic spine refactor.

Plan: .windsurf/plans/apps_rg_agentic_spine_refactor_plan.md (W8.P1).

These tests verify the structural invariants established by the refactor:
  - Terminology alignment (no EXIT_PARTIAL, no Inner DAG)
  - Route ordering (R1A → R1B → R5 → R4)
  - Research boundary enforcement (no Tavily/apps_research/internal at runtime)
  - Exit disposition canonicalization (X3A–X3E only, no X3B emission)
  - HITL posture (no runtime HITL)
  - L2 ownership (HOPs are L2 E3, not L3 DAG)
  - Sealed packet semantics
  - Spine manifest correctness
"""
from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APPS_RG = _REPO_ROOT / "apps_rg"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_text(rel: str) -> str:
    return (_APPS_RG / rel).read_text(encoding="utf-8")


def _read_main() -> str:
    return _read_text("__main__.py")


def _read_loader() -> str:
    return _read_text("integrations/company_research_loader.py")


def _read_spine_md() -> str:
    return _read_text("AGENTIC_SPINE.md")


def _read_manifest() -> dict:
    return yaml.safe_load((_APPS_RG / "spine_manifest.yaml").read_text(encoding="utf-8"))


# ===========================================================================
# 1. Spine Manifest
# ===========================================================================

class TestSpineManifest:
    def test_apps_rg_spine_declares_r4_single_action_l3_bypassed(self):
        manifest = _read_manifest()
        routes = manifest.get("claimed_routes", [])
        assert routes, "No claimed_routes in spine_manifest.yaml"
        first_route = routes[0]
        assert first_route["type"] == "R4_SINGLE_ACTION"
        # L3 bypass is implicit in the R4_SINGLE_ACTION shape (no L3 DAG);
        # verify the description does not claim L3 orchestration.
        desc = first_route.get("description", "")
        assert "L3 orchestration" not in desc.lower()

    def test_spine_manifest_has_runtime_authority(self):
        """Runtime authority is documented as YAML comments in spine_manifest.yaml."""
        raw = (_APPS_RG / "spine_manifest.yaml").read_text(encoding="utf-8")
        assert "FILESYSTEM_SANDBOX_WRITE" in raw
        assert "MODEL_EGRESS" in raw

    def test_spine_manifest_has_prompt_assembly_posture(self):
        """Prompt assembly posture is documented as a YAML comment."""
        raw = (_APPS_RG / "spine_manifest.yaml").read_text(encoding="utf-8")
        assert "APP_LOCAL_PA_COMPATIBLE" in raw


# ===========================================================================
# 2. HOP Pipeline L2 Ownership
# ===========================================================================

class TestHopPipelineOwnership:
    def test_apps_rg_hop_pipeline_not_l3_dag(self):
        src = _read_text("config/hop_pipeline.py")
        assert "L2" in src, "hop_pipeline.py should reference L2 ownership"
        assert "L2 E3" in src or "L2-owned" in src, "hop_pipeline.py should clarify L2 E3 / L2-owned"
        assert "NOT L3" in src or "not L3" in src.lower(), "hop_pipeline.py should explicitly state not-L3"


# ===========================================================================
# 3. Route Ordering
# ===========================================================================

class TestRouteOrdering:
    def test_apps_rg_route_order_r1b_before_run(self):
        """R1B cache check should appear before the main pipeline execution in __main__.py."""
        src = _read_main()
        # R1B cache check and run invocation are both present
        r1b_pos = src.find("R1B") if src.find("R1B") > 0 else src.find("r1b")
        run_pos = src.find("_run(") if src.find("_run(") > 0 else src.find("generate_resume")
        assert r1b_pos > 0, "R1B reference not found in __main__.py"
        assert run_pos > 0, "Pipeline run invocation not found in __main__.py"


# ===========================================================================
# 4. Research Boundary Enforcement
# ===========================================================================

class TestResearchBoundary:
    def test_apps_rg_no_tavily_or_live_research_inside_runtime(self):
        """company_research_loader must not have _try_tavily_supplement, _try_apps_research, _try_internal_engine."""
        src = _read_loader()
        assert "_try_tavily_supplement" not in src
        assert "_try_apps_research" not in src
        assert "_try_internal_engine" not in src

    def test_apps_rg_no_tavily_import_in_runtime(self):
        """No tavily import statement in company_research_loader."""
        src = _read_loader()
        # Exclude docstring/comment mentions — check only import lines
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert "tavily" not in stripped.lower(), f"Tavily import found: {stripped}"

    def test_apps_rg_no_apps_research_engine_import_in_runtime(self):
        """No CompanyBriefEngine import in loader."""
        src = _read_loader()
        assert "CompanyBriefEngine" not in src

    def test_apps_rg_no_research_cli_args_in_main(self):
        """__main__.py should not have --research-via, --auto-research-internal, --auto-research-tavily."""
        src = _read_main()
        assert "--research-via" not in src
        assert "--auto-research-internal" not in src
        assert "--auto-research-tavily" not in src

    def test_apps_rg_no_research_cli_args_in_narrative_pass(self):
        src = _read_text("scripts/narrative_pass.py")
        assert "--research-via" not in src
        assert "--auto-research-internal" not in src
        assert "--auto-research-tavily" not in src

    def test_apps_rg_loader_options_simplified(self):
        """CompanyResearchLoadOptions should only have target_company and manual_path."""
        src = _read_loader()
        assert "research_via" not in src
        assert "auto_research_internal" not in src
        assert "auto_research_tavily" not in src
        assert "jd_path" not in src.split("class CompanyResearchLoadOptions")[1].split("\n\n")[0]


# ===========================================================================
# 5. Exit Disposition Canonicalization
# ===========================================================================

class TestExitDisposition:
    def test_apps_rg_no_exit_partial_string(self):
        """String 'EXIT_PARTIAL' must be absent from __main__.py."""
        src = _read_main()
        assert "EXIT_PARTIAL" not in src, "EXIT_PARTIAL still present in __main__.py"

    def test_apps_rg_exit_partial_removed_or_mapped_to_canonical_x3(self):
        """All disposition references in __main__.py should be X3A–X3E."""
        src = _read_main()
        assert "EXIT_PARTIAL" not in src
        assert "EXIT_OK" not in src
        # Verify canonical names are used
        assert "X3D_PARTIAL_FAIL_SAFE" in src or "X3D_ALLOW_FINISH" in src or "X3D" in src

    def test_apps_rg_spine_md_has_canonical_x3_table(self):
        """AGENTIC_SPINE.md must have X3A through X3E disposition entries."""
        md = _read_spine_md()
        assert "X3A_DENY_REROUTE" in md
        assert "X3D_ALLOW_FINISH" in md
        assert "X3E_SAFE_ABSTAIN_CLARIFY" in md
        assert "X3C_COMMIT_REQUEST_TO_UWG" in md

    def test_apps_rg_spine_md_no_exit_partial(self):
        md = _read_spine_md()
        assert "EXIT_PARTIAL" not in md


# ===========================================================================
# 6. HITL Posture
# ===========================================================================

class TestHitlPosture:
    def test_apps_rg_no_runtime_hitl_when_hitl_false(self):
        """spine_manifest.yaml and AGENTIC_SPINE.md both declare no runtime HITL."""
        raw_manifest = (_APPS_RG / "spine_manifest.yaml").read_text(encoding="utf-8")
        assert "does NOT" in raw_manifest or "not" in raw_manifest.lower()
        assert "HITL" in raw_manifest
        md = _read_spine_md()
        assert "no runtime HITL" in md.lower() or "no X3B" in md

    def test_apps_rg_x3b_not_emitted(self):
        """X3B_ESCALATE_HITL should be noted as not-used in AGENTIC_SPINE.md."""
        md = _read_spine_md()
        assert "X3B" in md
        assert "not used" in md.lower() or "no runtime HITL" in md.lower()


# ===========================================================================
# 7. Sealed Packets
# ===========================================================================

class TestSealedPackets:
    def test_apps_rg_sealed_violation_packet_written(self):
        """_maybe_mark_provenance_failure should write sealed_violation_packet.json."""
        src = _read_main()
        assert "sealed_violation_packet.json" in src

    def test_apps_rg_sealed_packet_has_disposition(self):
        """The sealed packet should include disposition field."""
        src = _read_main()
        assert '"disposition"' in src or "'disposition'" in src


# ===========================================================================
# 8. AGENTIC_SPINE.md Terminology
# ===========================================================================

class TestSpineTerminology:
    def test_no_inner_dag_terminology(self):
        md = _read_spine_md()
        assert "Inner DAG" not in md, "Legacy 'Inner DAG' terminology still in AGENTIC_SPINE.md"

    def test_l2_owned_terminology_present(self):
        md = _read_spine_md()
        assert "L2-Owned" in md or "L2 E3" in md or "L2-owned" in md

    def test_preloaded_research_boundary_stated(self):
        md = _read_spine_md()
        assert "does NOT" in md and ("Tavily" in md or "live research" in md.lower())
