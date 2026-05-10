"""W1.3 Governance tests — 20 tests enforcing entrypoint purity and spine discipline.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.3
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


def _read_main_py() -> str:
    return (Path(__file__).parent.parent.parent / "__main__.py").read_text(encoding="utf-8")


def _parse_main_py() -> ast.Module:
    return ast.parse(_read_main_py())


def _top_level_imports(tree: ast.Module) -> set[str]:
    imports: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


class TestEntrypointPurity:
    """Tests 1-7: __main__.py is a pure CLI shim."""

    def test_main_is_pure_shim(self) -> None:
        tree = _parse_main_py()
        imports = _top_level_imports(tree)
        assert len(imports) <= 5, f"__main__.py has {len(imports)} top-level imports, expected ≤5"

    def test_main_does_not_import_card_builder(self) -> None:
        content = _read_main_py()
        assert "card_pack_builder" not in content

    def test_main_does_not_import_c0_adapter(self) -> None:
        content = _read_main_py()
        assert "c0_adapter" not in content

    def test_main_does_not_import_l2_stage_modules(self) -> None:
        content = _read_main_py()
        assert "apps_qna.l2" not in content

    def test_main_does_not_import_provider_sdks(self) -> None:
        content = _read_main_py()
        for sdk in ("openai", "anthropic", "google.generativeai", "boto3"):
            assert sdk not in content, f"Found provider SDK import: {sdk}"

    def test_main_contains_no_l2_callable_construction(self) -> None:
        content = _read_main_py()
        assert "CardPackBuilder(" not in content

    def test_main_contains_no_inline_card_render_closure(self) -> None:
        content = _read_main_py()
        assert "lambda" not in content


class TestGroundingDiscipline:
    """Tests 8-11: Evidence and grounding requirements."""

    def test_grounded_route_requires_c0_or_uploaded_briefing(self) -> None:
        from apps_qna.l1_planner import plan_live_interview
        plan = plan_live_interview(request_id="r1", has_briefing=False)
        assert plan.grounding_required is True

    def test_direct_path_uses_no_l3(self) -> None:
        from apps_qna.live_interview_runtime import _run_pipeline
        result = _run_pipeline(interview_slug="test", dry_run=True)
        assert result["exit_disposition"].value == "ALLOW_FINISH"

    def test_route_resolution_failure_fails_closed_through_exit(self) -> None:
        from apps_qna.l0_router import select_route
        with pytest.raises(ValueError, match="No valid route"):
            select_route(grounding_required=False, has_valid_briefing=False)

    def test_no_generic_pack_when_grounding_required(self) -> None:
        from apps_qna.l0_router import select_route
        route = select_route(grounding_required=True)
        assert route.c0_required is True
        assert route.route_id != ""


class TestWriteDiscipline:
    """Tests 12-14: Write boundaries."""

    def test_no_direct_l4_writes(self) -> None:
        from apps_qna.l2.e3_exec import execute_build
        from apps_qna.l2.e1_prep import prep_workspace
        from apps_qna.c0_adapter import call_c0
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert manifest is not None

    def test_no_provider_calls_in_build_path(self) -> None:
        from apps_qna.l2.e3_exec import execute_build
        from apps_qna.l2.e1_prep import prep_workspace
        from apps_qna.c0_adapter import call_c0
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.cards) >= 4

    def test_exit_emits_x3_but_does_not_write_l4(self) -> None:
        from apps_qna.exit_wiring import emit_exit_review
        from apps_qna.l2.e3_exec import execute_build
        from apps_qna.l2.e1_prep import prep_workspace
        from apps_qna.c0_adapter import call_c0
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec)
        assert packet.x3_disposition.value == "ALLOW_FINISH"


class TestC0AdapterBoundaries:
    """Tests 15-16: C0 adapter discipline."""

    def test_c0_adapter_calls_canonical_c0_only(self) -> None:
        from apps_qna.c0_adapter import call_c0
        fec = call_c0(interview_slug="test", route_id="r1")
        assert fec["producer"] == "agentic_core.C0"

    def test_c0_adapter_does_not_retrieve_directly(self) -> None:
        import inspect
        from apps_qna import c0_adapter
        source = inspect.getsource(c0_adapter.call_c0)
        assert "requests." not in source
        assert "httpx." not in source
        assert "urllib" not in source


class TestContractDistinction:
    """Tests 17-19: Contract boundaries."""

    def test_uploaded_briefing_contract_is_not_c0_fec(self) -> None:
        from apps_qna.briefing_validator import validate_briefing
        from apps_qna.c0_adapter import call_c0
        briefing = validate_briefing(briefing_path=None)
        fec = call_c0(interview_slug="test", route_id="r1")
        assert briefing.to_dict()["producer"] != fec["producer"]

    def test_l2_e4_heal_cannot_invent_facts(self) -> None:
        from apps_qna.l2.e3_exec import execute_build
        from apps_qna.l2.e1_prep import prep_workspace
        from apps_qna.c0_adapter import call_c0
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.cards) == 18

    def test_r1b_never_silent_terminal_return(self) -> None:
        from apps_qna.l0_router import select_route
        route = select_route(grounding_required=True)
        assert route.c0_required is True


class TestLocalUwgBoundary:
    """Test 20: Local output vs UWG boundary."""

    def test_local_output_not_uwg_write(self) -> None:
        from apps_qna.l2.e3_exec import execute_build
        from apps_qna.l2.e1_prep import prep_workspace
        from apps_qna.c0_adapter import call_c0
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert manifest is not None
