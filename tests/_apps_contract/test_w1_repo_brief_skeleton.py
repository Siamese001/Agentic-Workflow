"""W1 verification — apps_repo_brief skeleton smoke tests.

Covers:
  - P1.1  apps_repo_brief.__init__ importable, APP_NAME correct
  - P1.2  reasoning shim re-exports ExecOrchestrator
  - P1.3  spine_manifest.yaml exists + declares R3_grounded_read + c0_required
  - P1.4  route_registry.yaml + cert_route_registry.yaml exist + route IDs
  - P1.5  path_constants.py exports APPS_REPO_BRIEF_DIR + APPS_REPO_BRIEF_SUBFOLDER_MAP
  - P1.6  ssot.py exports APPS_REPO_BRIEF_DIR + PROJECT_ROOT_WHITELIST includes it
  - P1.7  cross_app_import_allowlist.yaml has apps_eval->apps_repo_brief entry
  - P1.8  app_inventory.yaml has APP-REPO-BRIEF row
  - P1.9  scenario_runner registry has repo_brief_* keys
  - P1.10 __main__.py is a pure shim (no heavy imports, has main())
  - P1.11 cert/fec_producer.py produce_fec returns canonical shape

Plan: docs/archive/windsurf/legacy-tree/plans/apps-repo-brief-plan3-zero-loss-overwrite.md W1
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# P1.1 — package importable, APP_NAME
# ---------------------------------------------------------------------------

class TestP1PackageInit:
    def test_importable(self):
        import apps_repo_brief
        assert apps_repo_brief.APP_NAME == "apps_repo_brief"

    def test_app_version_present(self):
        import apps_repo_brief
        assert isinstance(apps_repo_brief.APP_VERSION, str)
        assert apps_repo_brief.APP_VERSION


# ---------------------------------------------------------------------------
# P1.2 — reasoning shim
# ---------------------------------------------------------------------------

class TestP1ReasoningShim:
    def test_shim_exports_exec_orchestrator(self):
        try:
            from apps_repo_brief.reasoning import ExecOrchestrator
            assert ExecOrchestrator is not None
        except ImportError as exc:
            pytest.skip(f"apps_exec not available (expected in CI): {exc}")

    def test_reasoning_init_importable(self):
        import apps_repo_brief.reasoning
        assert apps_repo_brief.reasoning is not None


# ---------------------------------------------------------------------------
# P1.3 — spine_manifest.yaml
# ---------------------------------------------------------------------------

class TestP1SpineManifest:
    def test_manifest_exists(self):
        p = _REPO_ROOT / "apps_repo_brief" / "spine_manifest.yaml"
        assert p.exists(), "apps_repo_brief/spine_manifest.yaml missing"

    def test_manifest_declares_r3_grounded_read(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "spine_manifest.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        routes = data.get("claimed_routes", [])
        assert any(r.get("type") == "R3_grounded_read" for r in routes)

    def test_manifest_c0_required_true(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "spine_manifest.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        routes = data.get("claimed_routes", [])
        grounded = [r for r in routes if r.get("type") == "R3_grounded_read"]
        assert grounded, "No R3_grounded_read route"
        assert grounded[0].get("c0_required") is True

    def test_manifest_app_name(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "spine_manifest.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        assert data.get("app") == "apps_repo_brief"


# ---------------------------------------------------------------------------
# P1.4 — route registries
# ---------------------------------------------------------------------------

class TestP1RouteRegistries:
    def test_route_registry_exists(self):
        p = _REPO_ROOT / "apps_repo_brief" / "config" / "route_registry.yaml"
        assert p.exists()

    def test_canonical_route_present(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "config" / "route_registry.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        ids = [r["route_id"] for r in data.get("routes", [])]
        assert "apps_repo_brief.executive_brief_v1" in ids

    def test_cert_route_registry_exists(self):
        p = _REPO_ROOT / "apps_repo_brief" / "config" / "cert_route_registry.yaml"
        assert p.exists()

    def test_cert_route_registry_invoke_exit_eval(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "config" / "cert_route_registry.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        routes = data.get("routes", [])
        assert any(r.get("invoke_exit_eval") is True for r in routes)

    def test_cert_route_registry_c0_required(self):
        import yaml
        p = _REPO_ROOT / "apps_repo_brief" / "config" / "cert_route_registry.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        routes = data.get("routes", [])
        assert any(r.get("c0_required") is True for r in routes)


# ---------------------------------------------------------------------------
# P1.5 — path_constants
# ---------------------------------------------------------------------------

class TestP1PathConstants:
    def test_apps_repo_brief_dir_exported(self):
        from agentic_core.L0_routing.config.path_constants import APPS_REPO_BRIEF_DIR
        assert APPS_REPO_BRIEF_DIR == "apps_repo_brief"

    def test_apps_repo_brief_subfolder_map_exported(self):
        from agentic_core.L0_routing.config.path_constants import APPS_REPO_BRIEF_SUBFOLDER_MAP
        assert "config" in APPS_REPO_BRIEF_SUBFOLDER_MAP

    def test_apps_packages_includes_repo_brief(self):
        from agentic_core.L0_routing.config.path_constants import APPS_PACKAGES
        assert "apps_repo_brief" in APPS_PACKAGES


# ---------------------------------------------------------------------------
# P1.6 — ssot.py
# ---------------------------------------------------------------------------

class TestP1Ssot:
    def test_ssot_apps_repo_brief_dir(self):
        from agentic_core.L5_safety.config.structure_blueprint.ssot import APPS_REPO_BRIEF_DIR
        assert APPS_REPO_BRIEF_DIR == "apps_repo_brief"

    def test_ssot_project_root_whitelist(self):
        from agentic_core.L5_safety.config.structure_blueprint.ssot import PROJECT_ROOT_WHITELIST
        assert "apps_repo_brief" in PROJECT_ROOT_WHITELIST


# ---------------------------------------------------------------------------
# P1.7 — cross_app_import_allowlist.yaml
# ---------------------------------------------------------------------------

class TestP1CrossAppAllowlist:
    def test_allowlist_has_repo_brief_entry(self):
        import yaml
        p = _REPO_ROOT / "config" / "cross_app_import_allowlist.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        entries = data.get("allowed_imports", [])
        repo_brief_entries = [e for e in entries if e.get("target") == "apps_repo_brief"]
        assert repo_brief_entries, "No apps_repo_brief entry in cross_app_import_allowlist.yaml"

    def test_allowlist_repo_brief_entry_is_lazy(self):
        import yaml
        p = _REPO_ROOT / "config" / "cross_app_import_allowlist.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        entries = data.get("allowed_imports", [])
        repo_brief_entries = [e for e in entries if e.get("target") == "apps_repo_brief"]
        assert all(e.get("lazy") is True for e in repo_brief_entries)


# ---------------------------------------------------------------------------
# P1.8 — app_inventory.yaml
# ---------------------------------------------------------------------------

class TestP1AppInventory:
    def test_inventory_has_repo_brief_row(self):
        import yaml
        p = _REPO_ROOT / "docs" / "wave_g" / "G1b_apps_inventory" / "app_inventory.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        ids = [a["id"] for a in data.get("apps", [])]
        assert "APP-REPO-BRIEF" in ids

    def test_inventory_app_count_updated(self):
        import yaml
        p = _REPO_ROOT / "docs" / "wave_g" / "G1b_apps_inventory" / "app_inventory.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        assert data.get("app_count", 0) >= 9


# ---------------------------------------------------------------------------
# P1.9 — scenario_runner
# ---------------------------------------------------------------------------

class TestP1ScenarioRunner:
    def test_scenario_registry_has_repo_brief_keys(self):
        import apps_eval.engines.scenario_runner as sr
        scenarios = getattr(sr, "_SCENARIO_DEFINITIONS", getattr(sr, "SCENARIOS", {}))
        assert "repo_brief_recruiter" in scenarios
        assert "repo_brief_cto" in scenarios
        assert "repo_brief_dry_run" in scenarios

    def test_scenario_functions_defined(self):
        import apps_eval.engines.scenario_runner as sr
        assert callable(getattr(sr, "_scenario_repo_brief_recruiter", None))
        assert callable(getattr(sr, "_scenario_repo_brief_cto", None))
        assert callable(getattr(sr, "_scenario_repo_brief_dry_run", None))

    def test_scenario_functions_return_skip_without_apps_exec(self):
        """Each scenario must return SKIP (not crash) when apps_repo_brief or apps_exec
        is unavailable. We can test this by checking the tuple shape."""
        import apps_eval.engines.scenario_runner as sr
        for fn_name in ("_scenario_repo_brief_recruiter", "_scenario_repo_brief_cto", "_scenario_repo_brief_dry_run"):
            fn = getattr(sr, fn_name)
            outcome, score, msg = fn()
            # In CI, apps_exec may not be available → SKIP is expected.
            # If available, may return PASS. FAIL would indicate a regression.
            assert outcome in ("SKIP", "PASS"), f"{fn_name}: got {outcome!r} — {msg}"


# ---------------------------------------------------------------------------
# P1.10 — __main__ is a pure shim
# ---------------------------------------------------------------------------

class TestP1MainEntrypoint:
    def test_main_importable(self):
        import apps_repo_brief.__main__ as m
        assert callable(m.main)

    def test_main_has_no_heavy_imports_at_module_level(self):
        p = _REPO_ROOT / "apps_repo_brief" / "__main__.py"
        source = p.read_text(encoding="utf-8")
        forbidden = [
            "from apps_repo_brief.engines",
            "from apps_repo_brief.reasoning.ExecOrchestrator import",
            "ExecOrchestrator(",
            "GovernedExecRun(",
        ]
        for token in forbidden:
            assert token not in source, f"__main__.py contains forbidden heavy import: {token!r}"


# ---------------------------------------------------------------------------
# P1.11 — cert/fec_producer.py
# ---------------------------------------------------------------------------

class TestP1FecProducer:
    def test_produce_fec_importable(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        assert callable(produce_fec)

    def test_produce_fec_schema_version(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        result = produce_fec({})
        assert result["schema_version"] == "1.0"

    def test_produce_fec_producer_id(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        result = produce_fec({})
        assert result["producer"] == "apps_repo_brief.cert.fec_producer"

    def test_produce_fec_canonical_route(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        result = produce_fec({})
        assert result["route_id"] == "apps_repo_brief.executive_brief_v1"

    def test_produce_fec_source_collection(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        result = produce_fec({})
        assert result["source_collection"] == "repo_brief_docs"

    def test_produce_fec_never_raises_on_malformed_input(self):
        from apps_repo_brief.cert.fec_producer import produce_fec
        for bad_ctx in [None, 42, "string", [], object()]:
            result = produce_fec(bad_ctx)
            assert isinstance(result, dict)

    def test_cert_init_registers_producer(self):
        try:
            import apps_repo_brief.cert  # triggers register_producer side-effect
            from apps_shared.cert.fec_producer import resolve_fec
            fec = resolve_fec("apps_repo_brief", {})
            assert fec["producer"] == "apps_repo_brief.cert.fec_producer"
        except ImportError as exc:
            pytest.skip(f"apps_shared.cert.fec_producer not available: {exc}")
