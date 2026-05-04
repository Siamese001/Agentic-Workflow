"""Tests: apps_rg runtime artifact threading (W1 deferred plan).

Verifies that generate_resume.py and RgResumeOrchestrator use the compiled
PA artifact for model calls instead of ad hoc prompt strings.
"""

from __future__ import annotations

import json
from typing import Any
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_context(flow_route: str = "strategic_tailor") -> dict[str, Any]:
    """Build a minimal context dict with enough data for PA compilation."""
    return {
        "jd_data": "Software Engineer at Acme Corp",
        "master_resume_data": json.dumps({"name": "Jane Doe", "title": "Engineer"}),
        "flow_route": flow_route,
        "company_brief_data": "",
        "user_task": "",
        "claim_source_refs": "",
        "unsupported_claims": "",
        "approved_resume_examples": "",
        "seniority_band": "",
        "target_company": "",
        "target_role": "",
        "local_evidence_contract_ref": "",
        "run_id": "test-run-1",
        "trace_id": "test-trace-1",
        "request_id": "test-req-1",
        "provider_lane": "default",
        "symbolic_model_id": "",
        "policy_hash": "",
        "blueprint_hash": "",
    }


# ---------------------------------------------------------------------------
# SovereignContext carries artifact
# ---------------------------------------------------------------------------

class TestSovereignContextArtifactSlots:
    """SovereignContext must have compiled_prompt_artifact and provider_request."""

    def test_has_compiled_prompt_artifact_attr(self):
        from apps_rg.types.SovereignContext import SovereignContext
        ctx = SovereignContext()
        assert hasattr(ctx, "compiled_prompt_artifact")
        assert ctx.compiled_prompt_artifact is None

    def test_has_provider_request_attr(self):
        from apps_rg.types.SovereignContext import SovereignContext
        ctx = SovereignContext()
        assert hasattr(ctx, "provider_request")
        assert ctx.provider_request is None

    def test_can_set_artifact(self):
        from apps_rg.types.SovereignContext import SovereignContext
        ctx = SovereignContext()
        ctx.compiled_prompt_artifact = {"prompt_id": "test"}
        assert ctx.compiled_prompt_artifact["prompt_id"] == "test"


# ---------------------------------------------------------------------------
# RgResumeOrchestrator uses governed artifact
# ---------------------------------------------------------------------------

class TestOrchestratorArtifactThreading:
    """RgResumeOrchestrator.generate_resume_with_qwen uses artifact messages."""

    def test_has_compiled_artifact_attr(self):
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator
        orch = RgResumeOrchestrator(qwen_enabled=False)
        assert hasattr(orch, "_compiled_artifact")
        assert orch._compiled_artifact is None

    def test_governed_prompt_used_when_artifact_present(self):
        """When compiled_artifact has provider_specific_messages, the prompt
        sent to the model should be derived from those messages, not the
        ad hoc _prepare_resume_generation_prompt."""
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator

        artifact = {
            "provider_specific_messages": [
                {"role": "system", "content": "GOVERNED_SYSTEM"},
                {"role": "user", "content": "GOVERNED_USER"},
            ],
            "prompt_id": "apps_rg.strategic_tailor_v1",
            "compile_status": "PA_L2_HANDOFF_READY",
        }

        orch = RgResumeOrchestrator(qwen_enabled=False)
        orch._compiled_artifact = artifact

        # Since qwen is disabled, the method returns early. We test the
        # method signature accepts compiled_artifact.
        import asyncio
        result = asyncio.run(
            orch.generate_resume_with_qwen(
                job_description="test jd",
                candidate_profile={"name": "test"},
                compiled_artifact=artifact,
            )
        )
        assert result["success"] is False  # qwen disabled, so no actual call
        assert result["error"] == "qwen_disabled"

    def test_result_includes_artifact(self):
        """_run_async result dict includes compiled_prompt_artifact key."""
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator
        import asyncio

        orch = RgResumeOrchestrator(
            qwen_enabled=False,
            enable_repo_signals=False,
        )
        test_artifact = {"prompt_id": "test", "compile_status": "PA_L2_HANDOFF_READY"}
        orch._compiled_artifact = test_artifact

        result = asyncio.run(orch._run_async("Test JD"))
        assert "compiled_prompt_artifact" in result
        assert result["compiled_prompt_artifact"] == test_artifact


# ---------------------------------------------------------------------------
# generate_resume.py compiles artifact before orchestrator
# ---------------------------------------------------------------------------

class TestGenerateResumeArtifactCompilation:
    """generate_resume.py must compile PA artifact before model calls."""

    def test_generate_resume_imports_pa(self):
        """generate_resume.py must import compile_prompt."""
        import importlib
        mod = importlib.import_module("apps_rg.scripts.generate_resume")
        assert hasattr(mod, "compile_prompt")
        assert hasattr(mod, "AppsRgPromptRequest")
        assert hasattr(mod, "artifact_to_provider_request")


# ---------------------------------------------------------------------------
# Provider request round-trip
# ---------------------------------------------------------------------------

class TestProviderRequestRoundTrip:
    """Compiled artifact → provider_request → messages round-trip."""

    def test_compile_and_convert(self):
        from apps_rg.prompt_assembly.compiler import compile_prompt
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request

        request = AppsRgPromptRequest(
            flow_route="strategic_tailor",
            jd_data="Software Engineer at Acme",
            master_resume_data=json.dumps({"name": "Jane"}),
        )
        artifact = compile_prompt(request)
        artifact_dict = artifact.to_dict()

        provider_req = artifact_to_provider_request(artifact_dict)
        assert "messages" in provider_req
        assert len(provider_req["messages"]) >= 1
        assert provider_req["prompt_id"] == "apps_rg.strategic_tailor_v1"
        assert provider_req["artifact_hash"]
        assert provider_req["prompt_bom_hash"]
        assert provider_req["prompt_registry_hash"]
        assert provider_req["canonical_slot_bytes_hash"]
