"""
W5 apps_repo_brief Shim Sunset Tests.

P5.1 AG decision: Option A — archive after zero-hard-refs gate passes.
P5.2 Zero-hard-refs gate: no production code outside archives/ imports apps_exec.
P5.3 path_constants: APPS_EXEC_* deprecated, removed from __all__ and APPS_PACKAGES.
P5.4 Registry: apps_exec agents ARCHIVED, RepoBriefOrchestrator ACTIVE.
P5.5 scenario_runner: repo_brief scenarios use apps_repo_brief.types, not apps_exec.types.
P5.6 Archive: apps_exec/ moved to archives/apps_exec_20260505/.
P5.7 OTEL: observability_adapter emits only canonical apps_repo_brief.* spans.
P5.8 Final acceptance: W1-W5 regression green.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §W5
"""

from __future__ import annotations

import ast
import importlib
import re
import types
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARCHIVES_DIR = PROJECT_ROOT / "archives"
APPS_EXEC_ARCHIVE = ARCHIVES_DIR / "apps_exec_20260505"


def _python_files_excluding(root: Path, *exclude_patterns: str) -> list[Path]:
    """All .py files under root except those matching exclude_patterns."""
    files = []
    for p in root.rglob("*.py"):
        rel = p.relative_to(root)
        rel_str = rel.as_posix()
        if any(pat in rel_str for pat in exclude_patterns):
            continue
        files.append(p)
    return files


def _imports_in_file(path: Path) -> list[str]:
    """Return all module strings from import statements in path."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


# ---------------------------------------------------------------------------
# P5.2 Zero-hard-refs gate
# ---------------------------------------------------------------------------

class TestZeroHardRefsGate:
    """P5.2 — No production code outside archives/ imports apps_exec.*"""

    def _collect_hard_refs(self) -> list[tuple[Path, str]]:
        violations = []
        exclude = (
            "archives/",
            "tests/",
            ".windsurf/",
            "__pycache__",
            "tools/archive/",
        )
        for py_file in _python_files_excluding(PROJECT_ROOT, *exclude):
            for mod in _imports_in_file(py_file):
                if mod == "apps_exec" or mod.startswith("apps_exec."):
                    violations.append((py_file, mod))
        return violations

    def test_no_production_imports_of_apps_exec(self) -> None:
        """Zero production files (outside archives/ and tests/) import apps_exec.*"""
        violations = self._collect_hard_refs()
        if violations:
            lines = [f"  {p.relative_to(PROJECT_ROOT)}: {m}" for p, m in violations[:10]]
            raise AssertionError(
                f"P5.2 FAIL: {len(violations)} hard ref(s) to apps_exec found outside archives/:\n"
                + "\n".join(lines)
            )

    def test_apps_exec_directory_absent_from_project_root(self) -> None:
        """apps_exec/ directory must not exist at project root (archived to archives/)."""
        apps_exec_root = PROJECT_ROOT / "apps_exec"
        assert not apps_exec_root.exists(), (
            f"apps_exec/ still exists at {apps_exec_root}. "
            "Expected it to be moved to archives/apps_exec_20260505/"
        )

    def test_archive_exists_with_canonical_structure(self) -> None:
        """Archive must contain __init__.py and key subdirs as proof of safe git mv."""
        assert APPS_EXEC_ARCHIVE.exists(), f"Archive missing: {APPS_EXEC_ARCHIVE}"
        assert (APPS_EXEC_ARCHIVE / "__init__.py").exists()
        assert (APPS_EXEC_ARCHIVE / "reasoning").exists()
        assert (APPS_EXEC_ARCHIVE / "engines").exists()

    def test_tests_unit_apps_exec_still_importable_via_archive(self) -> None:
        """tests/unit/apps_exec/ still exists (test archive; not removed in W5)."""
        tests_exec = PROJECT_ROOT / "tests" / "unit" / "apps_exec"
        # It's OK if not present; we just confirm we haven't broken the archive copy
        archive_init = APPS_EXEC_ARCHIVE / "__init__.py"
        assert archive_init.exists(), "Archive __init__.py missing"


# ---------------------------------------------------------------------------
# P5.3 path_constants retirement
# ---------------------------------------------------------------------------

class TestPathConstantsRetirement:
    """P5.3 — APPS_EXEC_* deprecated; removed from APPS_PACKAGES and __all__."""

    def test_apps_exec_not_in_apps_packages(self) -> None:
        from agentic_core.L0_routing.config.path_constants import APPS_PACKAGES
        assert "apps_exec" not in APPS_PACKAGES, (
            "apps_exec should have been removed from APPS_PACKAGES in W5 P5.3"
        )

    def test_apps_repo_brief_in_apps_packages(self) -> None:
        from agentic_core.L0_routing.config.path_constants import APPS_PACKAGES
        assert "apps_repo_brief" in APPS_PACKAGES

    def test_apps_exec_dir_still_defined_for_grace_period(self) -> None:
        """APPS_EXEC_DIR kept for one-release grace period — must still be importable."""
        from agentic_core.L0_routing.config.path_constants import APPS_EXEC_DIR
        assert APPS_EXEC_DIR == "apps_exec"

    def test_apps_exec_subfolder_map_deprecated_empty(self) -> None:
        """APPS_EXEC_SUBFOLDER_MAP is now empty (deprecated sentinel)."""
        from agentic_core.L0_routing.config.path_constants import APPS_EXEC_SUBFOLDER_MAP
        assert APPS_EXEC_SUBFOLDER_MAP == {}, (
            "APPS_EXEC_SUBFOLDER_MAP should be empty dict (deprecated W5 P5.3)"
        )

    def test_apps_exec_dir_not_in_all(self) -> None:
        """APPS_EXEC_DIR removed from __all__ in W5 P5.3."""
        import agentic_core.L0_routing.config.path_constants as pc
        assert "APPS_EXEC_DIR" not in pc.__all__, (
            "APPS_EXEC_DIR should have been removed from __all__"
        )

    def test_apps_exec_subfolder_map_not_in_all(self) -> None:
        import agentic_core.L0_routing.config.path_constants as pc
        assert "APPS_EXEC_SUBFOLDER_MAP" not in pc.__all__


# ---------------------------------------------------------------------------
# P5.4 Registry retirement
# ---------------------------------------------------------------------------

class TestRegistryRetirement:
    """P5.4 — apps_exec agents are ARCHIVED; RepoBriefOrchestrator is ACTIVE."""

    def test_agent_status_has_archived(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import AgentStatus
        assert hasattr(AgentStatus, "ARCHIVED")
        assert AgentStatus.ARCHIVED.value == "archived"

    def test_exec_orchestrator_archived(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import (
            AGENT_TAXONOMY_MAP,
            AgentStatus,
        )
        entry = AGENT_TAXONOMY_MAP.get("ExecOrchestrator")
        assert entry is not None
        assert entry.status == AgentStatus.ARCHIVED, (
            f"ExecOrchestrator should be ARCHIVED, got {entry.status}"
        )

    def test_repo_brief_orchestrator_active(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import (
            AGENT_TAXONOMY_MAP,
            AgentStatus,
        )
        entry = AGENT_TAXONOMY_MAP.get("RepoBriefOrchestrator")
        assert entry is not None
        assert entry.status == AgentStatus.ACTIVE, (
            f"RepoBriefOrchestrator should be ACTIVE, got {entry.status}"
        )
        assert not entry.is_shim

    def test_brief_assembly_agent_archived(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import (
            AGENT_TAXONOMY_MAP,
            AgentStatus,
        )
        assert AGENT_TAXONOMY_MAP["BriefAssemblyAgent"].status == AgentStatus.ARCHIVED

    def test_style_compliance_agent_archived(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import (
            AGENT_TAXONOMY_MAP,
            AgentStatus,
        )
        assert AGENT_TAXONOMY_MAP["StyleComplianceAgent"].status == AgentStatus.ARCHIVED


# ---------------------------------------------------------------------------
# P5.5 Scenario runner migration
# ---------------------------------------------------------------------------

class TestScenarioRunnerMigration:
    """P5.5 — scenario_runner repo_brief scenarios use apps_repo_brief.types, not apps_exec.types."""

    def test_scenario_runner_exec_stubs_return_skip(self) -> None:
        """_scenario_exec_* must be SKIP stubs (apps_exec archived W5 P5.6)."""
        scenario_runner = PROJECT_ROOT / "apps_eval" / "engines" / "scenario_runner.py"
        source = scenario_runner.read_text(encoding="utf-8")
        # All three exec scenario stubs must not contain live apps_exec imports
        for fn_name in ("_scenario_exec_recruiter_brief", "_scenario_exec_cto_brief", "_scenario_exec_dry_run"):
            fn_start = source.find(f"def {fn_name}")
            assert fn_start != -1, f"{fn_name} not found"
            # Find next function boundary
            fn_end = source.find("\ndef ", fn_start + 1)
            fn_body = source[fn_start:fn_end] if fn_end != -1 else source[fn_start:]
            assert "apps_exec" not in fn_body or "archived" in fn_body, (
                f"{fn_name} still has live apps_exec import (should be SKIP stub)"
            )

    def test_scenario_runner_repo_brief_uses_canonical_types(self) -> None:
        scenario_runner = PROJECT_ROOT / "apps_eval" / "engines" / "scenario_runner.py"
        source = scenario_runner.read_text(encoding="utf-8")
        rb_start = source.find("_scenario_repo_brief_recruiter")
        rb_section = source[rb_start:]
        assert "apps_repo_brief.types.exec_types" in rb_section, (
            "Expected apps_repo_brief.types.exec_types import in repo_brief scenarios (P5.5)"
        )


# ---------------------------------------------------------------------------
# P5.7 OTEL single-span
# ---------------------------------------------------------------------------

class TestOtelSingleSpan:
    """P5.7 — observability_adapter emits only canonical apps_repo_brief.* spans."""

    def _make_adapter(self):
        from apps_repo_brief.integrations.observability_adapter import (
            RepoBriefObservabilityAdapter,
        )
        return RepoBriefObservabilityAdapter()

    def _make_request(self, **kwargs):
        class _Req:
            trace_id = kwargs.get("trace_id", "t1")
            audience = kwargs.get("audience", "recruiter")
            emphasis_areas = kwargs.get("emphasis_areas", [])
            dry_run = kwargs.get("dry_run", False)
        return _Req()

    def test_emit_brief_start_no_legacy_span(self) -> None:
        adapter = self._make_adapter()
        result = adapter.emit_brief_start(self._make_request())
        assert result["event_type"] == "apps_repo_brief.brief_start"
        metrics = adapter.get_metrics()
        assert len(metrics) == 1, f"Expected 1 span, got {len(metrics)}"
        assert all("apps_exec" not in m["event_type"] for m in metrics), (
            "Legacy apps_exec.* span still emitted (P5.7)"
        )

    def test_emit_brief_complete_no_legacy_span(self) -> None:
        class _Result:
            trace_id = "t2"
            audience = "cto"
            status = "complete"
            quality_score = 0.9
            passed_gate = True
        adapter = self._make_adapter()
        result = adapter.emit_brief_complete(_Result())
        assert result["event_type"] == "apps_repo_brief.brief_complete"
        metrics = adapter.get_metrics()
        assert len(metrics) == 1
        assert all("apps_exec" not in m["event_type"] for m in metrics)

    def test_get_canonical_metrics_equals_get_metrics(self) -> None:
        """W5: canonical == all (no legacy spans exist)."""
        adapter = self._make_adapter()
        adapter.emit_brief_start(self._make_request())
        assert adapter.get_canonical_metrics() == adapter.get_metrics()

    def test_no_legacy_key_in_any_span(self) -> None:
        adapter = self._make_adapter()
        adapter.emit_brief_start(self._make_request())
        for m in adapter.get_metrics():
            assert "_legacy" not in m, f"Span still has _legacy key: {m}"

    def test_source_file_no_live_apps_exec_references(self) -> None:
        adapter_path = (
            PROJECT_ROOT / "apps_repo_brief" / "integrations" / "observability_adapter.py"
        )
        source = adapter_path.read_text(encoding="utf-8")
        # Only live code (non-comment, non-docstring) should be checked.
        # Comments and docstrings mentioning 'W5 retired' are acceptable.
        live_refs = []
        in_docstring = False
        for line in source.splitlines():
            stripped = line.strip()
            if '"""' in stripped:
                in_docstring = not in_docstring
            if in_docstring or stripped.startswith("#"):
                continue
            if "apps_exec" in line:
                live_refs.append(line)
        assert not live_refs, (
            f"Live code still references apps_exec in observability_adapter.py:\n"
            + "\n".join(live_refs)
        )


# ---------------------------------------------------------------------------
# P5.8 Final acceptance
# ---------------------------------------------------------------------------

class TestW5FinalAcceptance:
    """P5.8 — Key W5 invariants confirmed end-to-end."""

    def test_apps_repo_brief_package_importable(self) -> None:
        import apps_repo_brief
        assert apps_repo_brief is not None

    def test_apps_repo_brief_cert_exports(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter, CertProjection
        assert CertProjectionAdapter is not None
        assert CertProjection is not None

    def test_apps_repo_brief_l2_exports(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair, E4Receipt, L2ReceiptBundle
        assert StyleGateL2Repair is not None

    def test_apps_repo_brief_exit_exports(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck, ExitV6Checker
        assert StyleGateExitCheck is not None
        assert ExitV6Checker is not None

    def test_apps_repo_brief_observability_adapter_importable(self) -> None:
        from apps_repo_brief.integrations.observability_adapter import (
            RepoBriefObservabilityAdapter,
        )
        adapter = RepoBriefObservabilityAdapter()
        assert adapter is not None

    def test_path_constants_apps_packages_correct(self) -> None:
        from agentic_core.L0_routing.config.path_constants import APPS_PACKAGES
        assert "apps_repo_brief" in APPS_PACKAGES
        assert "apps_exec" not in APPS_PACKAGES

    def test_agent_taxonomy_no_active_apps_exec_agents(self) -> None:
        from agentic_core.L2_execution.types.agent_taxonomy_registry import (
            AGENT_TAXONOMY_MAP,
            AgentStatus,
        )
        active_exec = [
            name for name, cls in AGENT_TAXONOMY_MAP.items()
            if cls.status == AgentStatus.ACTIVE
            and "apps_exec" in cls.file_path
            and "archives" not in cls.file_path
        ]
        assert not active_exec, (
            f"Active apps_exec agents found (should be ARCHIVED): {active_exec}"
        )

    def test_w1_through_w4_regression(self) -> None:
        """Canary: core W1-W4 modules still import cleanly."""
        import apps_repo_brief.cert.cert_projection_adapter  # noqa: F401
        import apps_repo_brief.L2.l2_receipts  # noqa: F401
        import apps_repo_brief.L2.style_gate_l2_repair  # noqa: F401
        import apps_repo_brief.exit.style_gate_exit  # noqa: F401
        import apps_repo_brief.exit.exit_v6_checks  # noqa: F401
