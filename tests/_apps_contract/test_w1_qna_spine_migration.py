"""W1 apps_qna one-spine migration contract tests.

Verifies:
1. AppRuntimeProfile exists and all 7 bindings are present (non-None)
2. profile_version is "2" (not the old all-None "1")
3. __main__ product and live paths call AppIngressRunner (not shadow spine)
4. live_interview_runtime cannot bypass the spine (callable only via L2 binding)
5. governed_run / _run_live_cert is post-run receipt decoration only
6. No qna binding hides an old orchestrator/dispatch shadow spine
7. Contract-chain proof for the qna route:
   ValidatedRequest -> L1PlanContract -> RouteContract -> fec -> QnaPromptArtifact
   -> SealedQnaArtifact -> QnaExitResult
8. No direct L4/write path is introduced by the bindings
10. _run_build is EXEMPT_DOCUMENTED (W1 corrective patch): structural proof that
    it is a build-time compiler path, not a governed slug runtime path, and that
    __main__ product/live paths cannot reach it.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P4
"""
from __future__ import annotations

import inspect
import types
from typing import Any
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# 1. AppRuntimeProfile exists and all 7 bindings are present
# ---------------------------------------------------------------------------

class TestAppRuntimeProfileW1:
    def test_profile_has_all_7_bindings(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        profile = build_app_runtime_contract()
        for stage in ("u0", "l1", "l0", "c0", "pa", "l2", "exit"):
            binding = getattr(profile, stage)
            assert callable(binding), (
                f"profile.{stage} must be a callable binding, got {binding!r}"
            )

    def test_profile_version_is_2(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        profile = build_app_runtime_contract()
        assert profile.profile_version == "2", (
            f"profile_version must be '2' (W1 wired), got {profile.profile_version!r}"
        )

    def test_profile_app_id(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        profile = build_app_runtime_contract()
        assert profile.app_id == "apps_qna"

    def test_profile_required_fields_contains_interview_slug(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        profile = build_app_runtime_contract()
        assert "interview_slug" in profile.required_fields

    def test_profile_parse_is_callable(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        profile = build_app_runtime_contract()
        assert callable(profile.parse)

    def test_binding_modules_importable(self):
        from apps_qna.runtime.bindings.u0_binding import qna_u0
        from apps_qna.runtime.bindings.l1_binding import qna_l1
        from apps_qna.runtime.bindings.l0_binding import qna_l0
        from apps_qna.runtime.bindings.c0_binding import qna_c0
        from apps_qna.runtime.bindings.pa_binding import qna_pa
        from apps_qna.runtime.bindings.l2_binding import qna_l2
        from apps_qna.runtime.bindings.exit_binding import qna_exit
        for fn in (qna_u0, qna_l1, qna_l0, qna_c0, qna_pa, qna_l2, qna_exit):
            assert callable(fn), f"{fn} must be callable"

    def test_profile_bindings_match_binding_module_functions(self):
        from apps_qna.runtime.profile_builder import build_app_runtime_contract
        from apps_qna.runtime.bindings.u0_binding import qna_u0
        from apps_qna.runtime.bindings.l1_binding import qna_l1
        from apps_qna.runtime.bindings.l0_binding import qna_l0
        from apps_qna.runtime.bindings.c0_binding import qna_c0
        from apps_qna.runtime.bindings.pa_binding import qna_pa
        from apps_qna.runtime.bindings.l2_binding import qna_l2
        from apps_qna.runtime.bindings.exit_binding import qna_exit

        profile = build_app_runtime_contract()
        assert profile.u0 is qna_u0
        assert profile.l1 is qna_l1
        assert profile.l0 is qna_l0
        assert profile.c0 is qna_c0
        assert profile.pa is qna_pa
        assert profile.l2 is qna_l2
        assert profile.exit is qna_exit


# ---------------------------------------------------------------------------
# 2. AppIngressRunner accepts the qna profile without error
# ---------------------------------------------------------------------------

class TestAppIngressRunnerProfilePath:
    def test_runner_accepts_profile(self):
        from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
        from apps_qna.runtime.profile_builder import build_app_runtime_contract

        profile = build_app_runtime_contract()
        runner = AppIngressRunner(profile=profile)
        assert runner._profile is profile
        assert runner._dispatch is None  # profile path, not legacy path

    def test_runner_clarification_on_missing_slug(self):
        from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
        from agentic_core.L5_safety.enforcement.ingress import ClarificationRequired
        from apps_qna.runtime.profile_builder import build_app_runtime_contract

        profile = build_app_runtime_contract()
        runner = AppIngressRunner(profile=profile)
        result = runner.run({})
        assert isinstance(result, ClarificationRequired), (
            "Missing interview_slug must yield ClarificationRequired"
        )

    def test_runner_clarification_on_empty_slug(self):
        from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
        from agentic_core.L5_safety.enforcement.ingress import ClarificationRequired
        from apps_qna.runtime.profile_builder import build_app_runtime_contract

        profile = build_app_runtime_contract()
        runner = AppIngressRunner(profile=profile)
        result = runner.run({"interview_slug": ""})
        assert isinstance(result, ClarificationRequired)


# ---------------------------------------------------------------------------
# 3. __main__ product and live paths use AppIngressRunner (source inspection)
# ---------------------------------------------------------------------------

class TestMainEntrypointUsesAppIngressRunner:
    def test_run_product_build_imports_app_ingress_runner(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_product_build)
        assert "AppIngressRunner" in src, (
            "_run_product_build must call AppIngressRunner on spine path"
        )
        assert "build_app_runtime_contract" in src, (
            "_run_product_build must call build_app_runtime_contract()"
        )

    def test_run_live_interview_imports_app_ingress_runner(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_live_interview)
        assert "AppIngressRunner" in src, (
            "_run_live_interview must call AppIngressRunner on spine path"
        )
        assert "build_app_runtime_contract" in src, (
            "_run_live_interview must call build_app_runtime_contract()"
        )

    def test_run_product_build_does_not_call_governed_run_for_execution(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_product_build)
        # Check for actual import/call, not just docstring mention
        assert "import governed_run" not in src, (
            "_run_product_build must not import governed_run (shadow spine)"
        )
        assert "from apps_shared.spine_emission import governed_run" not in src, (
            "_run_product_build must not import governed_run (shadow spine)"
        )

    def test_run_live_interview_does_not_import_live_interview_runtime(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_live_interview)
        # Check for actual import statement, not docstring mention
        assert "from apps_qna.live_interview_runtime import" not in src, (
            "_run_live_interview must not import from live_interview_runtime (shadow spine)"
        )
        assert "import live_interview_runtime" not in src, (
            "_run_live_interview must not import live_interview_runtime (shadow spine)"
        )


# ---------------------------------------------------------------------------
# 4. live_interview_runtime cannot bypass the spine
#    — its run_live_interview function must NOT be directly called from __main__
# ---------------------------------------------------------------------------

class TestLiveInterviewRuntimeIsNotShadowSpine:
    def test_main_does_not_directly_call_run_live_interview(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_live_interview)
        assert "from apps_qna.live_interview_runtime import run_live_interview" not in src, (
            "_run_live_interview must not import run_live_interview from live_interview_runtime"
        )
        assert "run_live_interview(argv)" not in src, (
            "_run_live_interview must not delegate to live_interview_runtime.run_live_interview"
        )

    def test_l2_binding_owns_e1_e2_e3_calls(self):
        from apps_qna.runtime.bindings import qna_l2
        src = inspect.getsource(qna_l2)
        assert "prep_workspace" in src
        assert "validate_build_inputs" in src
        assert "execute_build" in src

    def test_live_interview_runtime_not_imported_by_any_binding(self):
        import apps_qna.runtime.bindings.u0_binding as u0
        import apps_qna.runtime.bindings.l1_binding as l1
        import apps_qna.runtime.bindings.l0_binding as l0
        import apps_qna.runtime.bindings.c0_binding as c0
        import apps_qna.runtime.bindings.pa_binding as pa
        import apps_qna.runtime.bindings.l2_binding as l2
        import apps_qna.runtime.bindings.exit_binding as ex
        # Check for actual import statements, not just mentions in docstrings
        forbidden_patterns = (
            "from apps_qna.live_interview_runtime",
            "import live_interview_runtime",
        )
        for mod in (u0, l1, l0, c0, pa, l2, ex):
            src = inspect.getsource(mod)
            for pat in forbidden_patterns:
                assert pat not in src, (
                    f"{mod.__name__} must not contain '{pat}' (shadow spine import)"
                )


# ---------------------------------------------------------------------------
# 5. governed_run is post-run receipt only — not a current-run authority
# ---------------------------------------------------------------------------

class TestGovernedRunIsPostRunReceiptOnly:
    def test_run_live_cert_uses_governed_run_only(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_live_cert)
        assert "governed_run" in src, "_run_live_cert must use governed_run"
        assert "AppIngressRunner" not in src, (
            "_run_live_cert (cert mode) must not use AppIngressRunner — "
            "cert is post-run receipt only"
        )

    def test_run_live_cert_does_not_call_execute_build(self):
        import apps_qna.__main__ as main_mod
        src = inspect.getsource(main_mod._run_live_cert)
        assert "execute_build" not in src, (
            "_run_live_cert must not call execute_build (execution ownership)"
        )
        assert "prep_workspace" not in src
        assert "run_live_interview" not in src


# ---------------------------------------------------------------------------
# 6. No binding hides an old orchestrator/dispatch shadow spine
# ---------------------------------------------------------------------------

class TestNoBindingHidesShadowSpine:
    def _get_binding_srcs(self):
        import apps_qna.runtime.bindings.u0_binding as u0
        import apps_qna.runtime.bindings.l1_binding as l1
        import apps_qna.runtime.bindings.l0_binding as l0
        import apps_qna.runtime.bindings.c0_binding as c0
        import apps_qna.runtime.bindings.pa_binding as pa
        import apps_qna.runtime.bindings.l2_binding as l2
        import apps_qna.runtime.bindings.exit_binding as ex
        return {mod.__name__: inspect.getsource(mod) for mod in (u0, l1, l0, c0, pa, l2, ex)}

    def test_no_binding_calls_governed_run(self):
        for name, src in self._get_binding_srcs().items():
            assert "governed_run" not in src, (
                f"{name} must not call governed_run (shadow orchestration)"
            )

    def test_no_binding_calls_rfp_orchestrator(self):
        for name, src in self._get_binding_srcs().items():
            assert "RfpOrchestrator" not in src, (
                f"{name} must not call RfpOrchestrator"
            )

    def test_no_binding_calls_apps_rg_dispatch(self):
        for name, src in self._get_binding_srcs().items():
            assert "apps_rg_dispatch" not in src, (
                f"{name} must not call apps_rg_dispatch"
            )

    def test_l2_binding_does_not_call_live_interview_runtime(self):
        from apps_qna.runtime.bindings.l2_binding import qna_l2
        src = inspect.getsource(qna_l2)  # check function body only, not module docstring
        assert "_run_pipeline" not in src, (
            "qna_l2 function must not call _run_pipeline (live_interview_runtime shadow)"
        )


# ---------------------------------------------------------------------------
# 7. Contract-chain proof: each binding emits/consumes expected type
# ---------------------------------------------------------------------------

class TestContractChainProof:
    """Verify that each binding function returns the expected type."""

    def test_u0_returns_validated_request(self):
        from apps_qna.runtime.bindings.u0_binding import qna_u0
        from apps_qna.runtime.profile_builder import parse_payload

        envelope = parse_payload({"interview_slug": "test-slug"})
        assert envelope is not None, "parse_payload must return RequestEnvelope for valid slug"

        result = qna_u0(envelope)
        from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
        assert isinstance(result, ValidatedRequest), (
            f"qna_u0 must return ValidatedRequest, got {type(result)}"
        )

    def test_l1_returns_l1_plan_contract(self):
        from apps_qna.runtime.bindings.l1_binding import qna_l1
        from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
        from apps_qna.u0_intake import intake_interview_request

        validated = intake_interview_request(interview_slug="test-slug")
        result = qna_l1(validated)

        from agentic_core.L1_cognition.types.plan_contract_types import L1PlanContract
        assert isinstance(result, L1PlanContract), (
            f"qna_l1 must return L1PlanContract, got {type(result)}"
        )
        assert hasattr(result, "grounding_required")

    def test_l0_returns_route_with_model_generation_required(self):
        from apps_qna.runtime.bindings.l0_binding import qna_l0, QnaRouteContract
        from apps_qna.l1_planner import plan_live_interview

        l1_plan = plan_live_interview(request_id="test-req")
        result = qna_l0(l1_plan)

        assert isinstance(result, QnaRouteContract), (
            f"qna_l0 must return QnaRouteContract, got {type(result)}"
        )
        assert result.model_generation_required is True, (
            "qna_l0 must set model_generation_required=True"
        )
        assert hasattr(result, "grounding_required")

    def test_c0_returns_dict(self):
        from apps_qna.runtime.bindings.c0_binding import qna_c0
        from apps_qna.runtime.bindings.l0_binding import QnaRouteContract
        from apps_qna.u0_intake import intake_interview_request

        route = QnaRouteContract(
            route_id="apps_qna.test_route",
            grounding_required=True,
            interview_slug="test-slug",
        )
        validated = intake_interview_request(interview_slug="test-slug")

        # C0 may fail if index is not available; patch call_c0 at its source module
        with patch("apps_qna.c0_adapter.call_c0") as mock_c0:
            mock_c0.return_value = {
                "evidence_sufficiency": "template_only",
                "grounded": False,
                "retrieval_sources": [],
            }
            result = qna_c0(route, validated)

        assert isinstance(result, dict), f"qna_c0 must return dict, got {type(result)}"

    def test_pa_returns_truthy_artifact(self):
        from apps_qna.runtime.bindings.pa_binding import qna_pa, QnaPromptArtifact
        from apps_qna.runtime.bindings.l0_binding import QnaRouteContract
        from apps_qna.l1_planner import plan_live_interview
        from apps_qna.u0_intake import intake_interview_request

        route = QnaRouteContract(
            route_id="apps_qna.test_route",
            grounding_required=False,
            model_generation_required=True,
        )
        l1_plan = plan_live_interview(request_id="test-req")
        fec = {"evidence_sufficiency": "template_only", "grounded": False}
        validated = intake_interview_request(interview_slug="test-slug")

        with patch("apps_qna.card_context.pa_adapter.run_pa_for_card_context") as mock_pa:
            from apps_qna.card_context.pa_adapter import PAAdapterResult
            mock_pa.return_value = PAAdapterResult(
                dispatchable=True, dispatch_disposition="PASS"
            )
            result = qna_pa(route, l1_plan, fec, validated)

        assert isinstance(result, QnaPromptArtifact), (
            f"qna_pa must return QnaPromptArtifact, got {type(result)}"
        )
        assert bool(result) is True, "QnaPromptArtifact must be truthy"

    def test_l2_returns_sealed_artifact(self):
        from apps_qna.runtime.bindings.l2_binding import qna_l2, SealedQnaArtifact
        from apps_qna.runtime.bindings.pa_binding import QnaPromptArtifact

        artifact = QnaPromptArtifact(
            interview_slug="test-slug",
            route_id="apps_qna.test_route",
            evidence_contract={"evidence_sufficiency": "template_only"},
            pa_dispatchable=True,
            pa_disposition="PASS",
        )
        result = qna_l2(artifact)

        assert isinstance(result, SealedQnaArtifact), (
            f"qna_l2 must return SealedQnaArtifact, got {type(result)}"
        )

    def test_exit_returns_result_with_disposition(self):
        from apps_qna.runtime.bindings.exit_binding import qna_exit, QnaExitResult
        from apps_qna.runtime.bindings.l2_binding import SealedQnaArtifact
        from apps_qna.types.spine_contracts import CardPackManifestExtended

        manifest = CardPackManifestExtended(
            interview_slug="test-slug",
            built_at="",
            builder_version="0.1.0",
            template_set_version="v2",
            cards=("CARD_A.md",),
            routes_covered=("test_route",),
            interviewers=(),
            pasted_cards=("CARD_A.md",),
            paste_exceeds_chatgpt_limit=False,
            evidence_refs=("test",),
            tiering={"CARD_A.md": "tier_1"},
            card_hashes={"CARD_A.md": "abc123"},
            source_register=(),
        )
        sealed = SealedQnaArtifact(
            manifest=manifest,
            evidence_contract={"evidence_sufficiency": "template_only"},
            build_valid=True,
            interview_slug="test-slug",
            route_id="apps_qna.test_route",
        )
        result = qna_exit(sealed, "TestCo", "VP Eng", None, None)

        assert isinstance(result, QnaExitResult), (
            f"qna_exit must return QnaExitResult, got {type(result)}"
        )
        assert result.disposition is not None, "QnaExitResult.disposition must be set"
        assert hasattr(result, "exit_packet")

    def test_full_chain_sealed_to_allow_finish(self):
        """Integration: valid build → ALLOW_FINISH disposition."""
        from apps_qna.runtime.bindings.exit_binding import qna_exit, QnaExitResult
        from apps_qna.runtime.bindings.l2_binding import SealedQnaArtifact
        from apps_qna.types.spine_contracts import CardPackManifestExtended, X3Disposition

        manifest = CardPackManifestExtended(
            interview_slug="test-slug",
            built_at="",
            builder_version="0.1.0",
            template_set_version="v2",
            cards=("CARD_A.md",),
            routes_covered=("test_route",),
            interviewers=(),
            pasted_cards=("CARD_A.md",),
            paste_exceeds_chatgpt_limit=False,
            evidence_refs=("test",),
            tiering={"CARD_A.md": "tier_1"},
            card_hashes={"CARD_A.md": "abc123"},
            source_register=(),
        )
        sealed = SealedQnaArtifact(
            manifest=manifest,
            evidence_contract={"evidence_sufficiency": "template_only"},
            build_valid=True,
            interview_slug="test-slug",
            route_id="apps_qna.test_route",
        )
        result = qna_exit(sealed, "", "", None, None)
        assert result.disposition == X3Disposition.ALLOW_FINISH


# ---------------------------------------------------------------------------
# 8. No direct L4/write path introduced by bindings
# ---------------------------------------------------------------------------

class TestNoDirectL4WriteInBindings:
    def test_bindings_do_not_import_durable_write_gateway(self):
        import apps_qna.runtime.bindings.u0_binding as u0
        import apps_qna.runtime.bindings.l1_binding as l1
        import apps_qna.runtime.bindings.l0_binding as l0
        import apps_qna.runtime.bindings.c0_binding as c0
        import apps_qna.runtime.bindings.pa_binding as pa
        import apps_qna.runtime.bindings.l2_binding as l2
        import apps_qna.runtime.bindings.exit_binding as ex
        for mod in (u0, l1, l0, c0, pa, l2, ex):
            src = inspect.getsource(mod)
            assert "DurableWriteGateway" not in src, (
                f"{mod.__name__} must not import DurableWriteGateway (direct L4 write)"
            )
            assert "CommitRequest" not in src, (
                f"{mod.__name__} must not import CommitRequest (direct L4 write)"
            )

    def test_exit_binding_does_not_call_uwg(self):
        import apps_qna.runtime.bindings.exit_binding as ex
        src = inspect.getsource(ex)
        assert "emit_uwg_pack_record" not in src, (
            "exit_binding must not call emit_uwg_pack_record (direct L4 write in binding)"
        )


# ---------------------------------------------------------------------------
# 9. parse_payload produces valid RequestEnvelope
# ---------------------------------------------------------------------------

class TestParsePayload:
    def test_parse_with_slug(self):
        from apps_qna.runtime.profile_builder import parse_payload
        result = parse_payload({"interview_slug": "test-slug"})
        assert result is not None
        assert result.tenant_id == "apps_qna"

    def test_parse_missing_slug_returns_none(self):
        from apps_qna.runtime.profile_builder import parse_payload
        result = parse_payload({})
        assert result is None

    def test_parse_empty_slug_returns_none(self):
        from apps_qna.runtime.profile_builder import parse_payload
        result = parse_payload({"interview_slug": ""})
        assert result is None


# ---------------------------------------------------------------------------
# 10. _run_build EXEMPT_DOCUMENTED (W1 corrective patch)
#
# W0 classified _run_build as MUST_ROUTE. W1 corrective patch amends this to
# EXEMPT_DOCUMENTED. These tests structurally prove the disposition is safe:
# - __main__ product/live paths do NOT import or call _run_build
# - _run_build does NOT import AppIngressRunner (not a governed runtime path)
# - _run_build does NOT sequence agentic_core stage-prefixed symbols (no shadow spine)
# - _run_build is guarded with EXEMPT_DOCUMENTED rationale comment
# ---------------------------------------------------------------------------

class TestRunBuildExemptDocumented:
    """Structural proof that _run_build is a build-time compiler path, not
    a governed slug runtime path, and cannot shadow AppIngressRunner.

    Uses AST / import inspection — does not rely on docstring text alone.
    """

    def _run_qna_tree(self):
        import ast
        from pathlib import Path
        src = Path(__file__).resolve().parents[2] / "apps_qna" / "scripts" / "run_qna.py"
        return ast.parse(src.read_text(encoding="utf-8"), filename=str(src))

    def _main_tree(self):
        import ast
        from pathlib import Path
        src = Path(__file__).resolve().parents[2] / "apps_qna" / "__main__.py"
        return ast.parse(src.read_text(encoding="utf-8"), filename=str(src))

    def test_run_build_has_exempt_documented_marker(self):
        """_run_build docstring must contain EXEMPT_DOCUMENTED marker."""
        import ast
        tree = self._run_qna_tree()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_build":
                doc = ast.get_docstring(node) or ""
                assert "EXEMPT_DOCUMENTED" in doc, (
                    "_run_build must contain 'EXEMPT_DOCUMENTED' in its docstring "
                    "(W1 corrective patch disposition marker)"
                )
                return
        raise AssertionError("_run_build not found in apps_qna/scripts/run_qna.py")

    def test_run_build_does_not_import_app_ingress_runner(self):
        """_run_build must not import AppIngressRunner — it is a build-time path."""
        import ast
        tree = self._run_qna_tree()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_build":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.ImportFrom):
                        names = [a.name for a in subnode.names]
                        assert "AppIngressRunner" not in names, (
                            "_run_build must not import AppIngressRunner — "
                            "it is EXEMPT_DOCUMENTED as a build-time compiler path"
                        )
                return
        raise AssertionError("_run_build not found in apps_qna/scripts/run_qna.py")

    def test_run_build_does_not_chain_agentic_core_stage_symbols(self):
        """_run_build must not call chained agentic_core stage-prefixed symbols.

        This is the structural check that the NO_SHADOW_SPINE scanner (SS-2)
        would apply. No agentic_core imports exist in run_qna.py at module level
        or inside _run_build, so there can be no shadow-spine stage sequencing.
        """
        import ast
        _STAGE_PREFIXES = (
            "u0_validate_", "l1_plan_", "l0_route_",
            "c0_retrieve_", "pa_compose_", "l2_execute_", "exit_emit_",
        )
        tree = self._run_qna_tree()
        # No agentic_core imports at module level
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("agentic_core"):
                raise AssertionError(
                    f"run_qna.py must not import from agentic_core: {node.module} "
                    "— would risk shadow-spine stage symbol exposure"
                )
        # _run_build body must not call stage-prefixed names
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_build":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        name = ""
                        if isinstance(subnode.func, ast.Name):
                            name = subnode.func.id
                        elif isinstance(subnode.func, ast.Attribute):
                            name = subnode.func.attr
                        if any(name.startswith(p) for p in _STAGE_PREFIXES):
                            raise AssertionError(
                                f"_run_build calls stage-prefixed symbol '{name}' — "
                                "this would be a shadow-spine violation"
                            )
                return
        raise AssertionError("_run_build not found in apps_qna/scripts/run_qna.py")

    def test_main_product_build_does_not_call_run_build(self):
        """__main__._run_product_build must not call _run_build.

        Product build routes through AppIngressRunner exclusively. If
        _run_build appears as a call target inside _run_product_build, that
        would reintroduce the bypass.
        """
        import ast
        tree = self._main_tree()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_product_build":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        if isinstance(subnode.func, ast.Name) and subnode.func.id == "_run_build":
                            raise AssertionError(
                                "__main__._run_product_build must not call _run_build — "
                                "product build routes through AppIngressRunner only"
                            )
                return
        raise AssertionError("_run_product_build not found in apps_qna/__main__.py")

    def test_main_live_interview_does_not_call_run_build(self):
        """__main__._run_live_interview must not call _run_build."""
        import ast
        tree = self._main_tree()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_live_interview":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        if isinstance(subnode.func, ast.Name) and subnode.func.id == "_run_build":
                            raise AssertionError(
                                "__main__._run_live_interview must not call _run_build — "
                                "live interview routes through AppIngressRunner only"
                            )
                return
        raise AssertionError("_run_live_interview not found in apps_qna/__main__.py")

    def test_main_delegates_to_run_qna_only_for_auxiliary_subcommands(self):
        """__main__.main() must only reach run_qna.main via the else/fallthrough branch.

        Checks that run_qna.main is NOT imported at module level — it must only
        be imported inside the auxiliary fallthrough branch (inside a function body).
        Only top-level (module-level) ImportFrom nodes are checked.
        """
        from pathlib import Path
        src = Path(__file__).resolve().parents[2] / "apps_qna" / "__main__.py"
        text = src.read_text(encoding="utf-8")
        import ast
        tree = ast.parse(text, filename=str(src))
        # Only check top-level statements (module body), not nested inside functions
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.module and "run_qna" in node.module:
                    names = [a.name for a in node.names]
                    if "main" in names:
                        raise AssertionError(
                            "run_qna.main must not be imported at module level in __main__.py — "
                            "it must only be imported inside the auxiliary fallthrough branch"
                        )

    def test_run_build_calls_build_pack_via_spine_not_app_ingress_runner(self):
        """_run_build must call build_pack_via_spine (build-time path), not AppIngressRunner.

        This is the positive control: the exempt path must use the documented
        build-time compiler function, not the governed runtime orchestrator.
        """
        import ast
        tree = self._run_qna_tree()
        found_build_pack = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_run_build":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        name = ""
                        if isinstance(subnode.func, ast.Name):
                            name = subnode.func.id
                        elif isinstance(subnode.func, ast.Attribute):
                            name = subnode.func.attr
                        if name == "AppIngressRunner":
                            raise AssertionError(
                                "_run_build must not instantiate AppIngressRunner — "
                                "it is EXEMPT_DOCUMENTED as a build-time compiler path"
                            )
                        if name == "build_pack_via_spine":
                            found_build_pack = True
                assert found_build_pack, (
                    "_run_build must call build_pack_via_spine (positive control: "
                    "confirms build-time compiler path, not runtime path)"
                )
                return
        raise AssertionError("_run_build not found in apps_qna/scripts/run_qna.py")
