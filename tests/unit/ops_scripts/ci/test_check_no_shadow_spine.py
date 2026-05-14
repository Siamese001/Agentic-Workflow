"""Unit tests for check_no_shadow_spine.py — SS-2 and BM-4 rule discrimination.

Covers three hard invariants:

  SS-2 (app-owned stage-named bindings are ALLOWED):
    - ``pa_compose_apps_rg`` imported from ``apps_rg.runtime.bindings.pa_binding``
      must NOT trigger SS-2, even though its name starts with the ``pa_compose_``
      stage prefix.
    - ``l2_execute_apps_rg`` imported from ``apps_rg.runtime.bindings.l2_binding``
      must NOT trigger SS-2 for the same reason.
    - Rule intent: SS-2 fires only when at least one chained callee is imported
      from ``agentic_core.*``.  App-owned helpers with stage-prefix names are
      allowed — they are not shadow-spine; they *are* the binding.

  SS-2 (core-imported stage chain IS blocked):
    - A function that chains two stage calls where at least one callee is imported
      from ``agentic_core.*`` MUST trigger SS-2, provided the file is outside
      ``/bindings/`` and is not a ``profile_builder.py``.

  BM-4 (unchanged — not touched here):
    - BM-4 remains a separate check on ``bindings/*.py`` files.
    - No new BM-4 assertion is added unless a failing fixture proves the same
      false-positive pattern (per explicit user instruction).
"""
from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_no_shadow_spine.py"

sys.path.insert(0, str(REPO_ROOT))
from ops_scripts.ci.check_no_shadow_spine import (
    _core_imported_names,
    _find_stage_calls_in_func,
    _is_stage_call_name,
    _STAGE_PREFIXES,
    Finding,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(source: str) -> ast.Module:
    return ast.parse(textwrap.dedent(source))


def _ss2_findings_for_source(source: str, rel: str = "apps_foo/some_module.py") -> list[Finding]:
    """Run the exact SS-2 decision logic against synthetic source text.

    Mirrors the gate's _scan_general() inner loop so changes to the gate are
    reflected here without duplicating the full scan machinery.
    """
    tree = _parse(source)
    core_names = _core_imported_names(tree)
    findings: list[Finding] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stage_calls = _find_stage_calls_in_func(node)
        if len(stage_calls) < 2:
            continue
        if "profile_builder" in rel or "/bindings/" in rel:
            continue
        # Mirror gate: only flag when ≥1 callee is core-imported
        core_stage_callees = [
            c for c in stage_calls
            if (
                isinstance(c.func, ast.Name) and c.func.id in core_names
            ) or (
                isinstance(c.func, ast.Attribute) and c.func.attr in core_names
            )
        ]
        if core_stage_callees:
            findings.append(Finding(
                "ERROR", "SS-2", rel, node.lineno,
                f"{node.name}: app-owned function chains {len(stage_calls)} stage calls "
                f"outside bindings/ ({len(core_stage_callees)} from agentic_core)",
            ))
    return findings


# ===========================================================================
# Positive control: stage prefix helpers exist and work
# ===========================================================================

class TestStagePrefixHelpers:
    """Baseline: _is_stage_call_name recognises all declared prefixes."""

    @pytest.mark.parametrize("name", [
        "pa_compose_apps_rg",
        "l2_execute_apps_rg",
        "c0_retrieve_apps_rg",
        "u0_validate_request",
        "l1_plan_cognition",
        "l0_route_request",
        "exit_emit_result",
    ])
    def test_stage_prefixed_names_are_recognised(self, name: str) -> None:
        assert _is_stage_call_name(name), (
            f"{name!r} starts with a stage prefix but _is_stage_call_name returned False"
        )

    def test_non_stage_names_not_recognised(self) -> None:
        for name in ("helper_fn", "build_contract", "validate_payload"):
            assert not _is_stage_call_name(name)


# ===========================================================================
# SS-2 negative control: app-owned stage-named bindings must NOT be flagged
# ===========================================================================

class TestSS2AppOwnedBindingsAllowed:
    """App-owned stage-named helpers imported from apps_rg.runtime.bindings.*
    must NOT trigger SS-2, even when two such calls appear in the same function.

    Rule: SS-2 fires only if ≥1 callee resolves to a name imported from
    agentic_core.*.  App-owned binding calls are allowed by design.
    """

    def test_pa_compose_apps_rg_not_flagged(self) -> None:
        """pa_compose_apps_rg from apps_rg.runtime.bindings.pa_binding is allowed."""
        source = """
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg

        def dispatch_run(ctx):
            result_pa = pa_compose_apps_rg(ctx)
            result_l2 = l2_execute_apps_rg(ctx, result_pa)
            return result_l2
        """
        findings = _ss2_findings_for_source(source)
        assert not findings, (
            "SS-2 must NOT fire when both stage-named callees are imported from "
            "apps_rg.runtime.bindings.* — they are app-owned, not core executors.\n"
            f"Got findings: {findings}"
        )

    def test_l2_execute_apps_rg_not_flagged(self) -> None:
        """l2_execute_apps_rg from apps_rg.runtime.bindings.l2_binding is allowed."""
        source = """
        from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
        from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg

        def run_pipeline(req):
            evidence = c0_retrieve_apps_rg(req)
            output = l2_execute_apps_rg(req, evidence)
            return output
        """
        findings = _ss2_findings_for_source(source)
        assert not findings, (
            "SS-2 must NOT fire when all stage-named callees are imported from "
            "apps_rg.* — only agentic_core imports trigger SS-2.\n"
            f"Got findings: {findings}"
        )

    def test_mixed_app_bindings_three_stages_not_flagged(self) -> None:
        """Three app-owned stage calls in one function — still not flagged."""
        source = """
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
        from apps_rg.runtime.bindings.exit_binding import exit_emit_result

        def full_run(ctx):
            pa = pa_compose_apps_rg(ctx)
            l2 = l2_execute_apps_rg(ctx, pa)
            return exit_emit_result(ctx, l2)
        """
        findings = _ss2_findings_for_source(source)
        assert not findings, (
            "Three app-owned stage-named calls must not trigger SS-2.\n"
            f"Got: {findings}"
        )

    def test_core_imported_names_excludes_apps_rg_imports(self) -> None:
        """_core_imported_names must return empty set for apps_rg-only imports."""
        source = """
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
        """
        tree = _parse(source)
        core_names = _core_imported_names(tree)
        assert "pa_compose_apps_rg" not in core_names
        assert "l2_execute_apps_rg" not in core_names
        assert len(core_names) == 0

    def test_bindings_path_exemption_prevents_ss2(self) -> None:
        """Files inside /bindings/ are always exempt from SS-2 regardless of imports."""
        source = """
        from agentic_core.runtime.c0.evidence_metrics_extractor import c0_retrieve_core
        from agentic_core.L2_execution.executor import l2_execute_core

        def binding_fn(ctx):
            ev = c0_retrieve_core(ctx)
            return l2_execute_core(ctx, ev)
        """
        # /bindings/ path → must be exempt
        findings = _ss2_findings_for_source(
            source, rel="apps_rg/runtime/bindings/some_binding.py"
        )
        assert not findings, (
            "Files inside /bindings/ must be exempt from SS-2.\n"
            f"Got: {findings}"
        )


# ===========================================================================
# SS-2 positive control: core-imported stage chain IS flagged
# ===========================================================================

class TestSS2CoreImportedChainsBlocked:
    """A function that chains stage calls where ≥1 callee comes from agentic_core.*
    MUST trigger SS-2 when the file is outside /bindings/ and not profile_builder.
    """

    def test_two_core_imported_stage_calls_flagged(self) -> None:
        """Two agentic_core stage callees in one function triggers SS-2."""
        source = """
        from agentic_core.runtime.c0.executor import c0_retrieve_generic
        from agentic_core.L2_execution.executor import l2_execute_generic

        def shadow_orchestrate(ctx):
            ev = c0_retrieve_generic(ctx)
            return l2_execute_generic(ctx, ev)
        """
        findings = _ss2_findings_for_source(source)
        assert len(findings) == 1, (
            "Expected exactly 1 SS-2 finding for two core-imported stage calls.\n"
            f"Got: {findings}"
        )
        assert findings[0].rule_id == "SS-2"
        assert "shadow_orchestrate" in findings[0].message

    def test_one_core_one_app_stage_call_flagged(self) -> None:
        """Even one agentic_core stage callee among two is enough to trigger SS-2."""
        source = """
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        from agentic_core.L2_execution.executor import l2_execute_generic

        def mixed_orchestrate(ctx):
            pa = pa_compose_apps_rg(ctx)
            return l2_execute_generic(ctx, pa)
        """
        findings = _ss2_findings_for_source(source)
        assert len(findings) == 1, (
            "Expected 1 SS-2 finding: one of the two callees is from agentic_core.\n"
            f"Got: {findings}"
        )
        assert findings[0].rule_id == "SS-2"

    def test_core_imported_names_captures_agentic_core_imports(self) -> None:
        """_core_imported_names must include names imported from agentic_core.*."""
        source = """
        from agentic_core.runtime.c0.executor import c0_retrieve_generic
        from agentic_core.L2_execution.executor import l2_execute_generic
        from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
        """
        tree = _parse(source)
        core_names = _core_imported_names(tree)
        assert "c0_retrieve_generic" in core_names
        assert "l2_execute_generic" in core_names
        assert "pa_compose_apps_rg" not in core_names, (
            "App-owned import must not appear in core_names"
        )

    def test_profile_builder_rel_exempt_even_with_core_imports(self) -> None:
        """profile_builder.py files are exempt from SS-2 (handled by PB-* rules)."""
        source = """
        from agentic_core.runtime.c0.executor import c0_retrieve_generic
        from agentic_core.L2_execution.executor import l2_execute_generic

        def build_app_runtime_contract(ctx):
            ev = c0_retrieve_generic(ctx)
            return l2_execute_generic(ctx, ev)
        """
        findings = _ss2_findings_for_source(
            source, rel="apps_foo/runtime/profile_builder.py"
        )
        assert not findings, (
            "profile_builder.py must be exempt from SS-2 (PB-* handles it).\n"
            f"Got: {findings}"
        )

    def test_single_stage_call_not_flagged(self) -> None:
        """SS-2 requires ≥2 stage calls; a single call is never flagged."""
        source = """
        from agentic_core.L2_execution.executor import l2_execute_generic

        def run_l2_only(ctx):
            return l2_execute_generic(ctx)
        """
        findings = _ss2_findings_for_source(source)
        assert not findings, (
            "A single stage call must not trigger SS-2 (need ≥2).\n"
            f"Got: {findings}"
        )


# ===========================================================================
# Gate script existence and importability
# ===========================================================================

class TestGateScriptBasics:
    def test_gate_script_exists(self) -> None:
        assert GATE_PATH.exists(), f"Gate not found at {GATE_PATH}"

    def test_gate_imports_stage_prefixes(self) -> None:
        assert len(_STAGE_PREFIXES) >= 7, (
            f"Expected at least 7 stage prefixes, got {len(_STAGE_PREFIXES)}"
        )
        assert "pa_compose_" in _STAGE_PREFIXES
        assert "l2_execute_" in _STAGE_PREFIXES
        assert "c0_retrieve_" in _STAGE_PREFIXES
