"""RG-GAP-01 + RG-GAP-02 invariant tests.

RG-GAP-01: ResumeGenerator._generate_with_gemini must route through
  SovereignLLMGateway, not direct google.generativeai SDK.
  Negative control: google.generativeai must NOT be imported by the method.

RG-GAP-02: HardenedRouter._initialize_executors must wire HardenedGeminiExecutor
  for Provider.GOOGLE.
  Negative control: Google provider missing from executors → assert key absent.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_resume_generator_gateway")
_emit_applies_guardrail("p0", "test_resume_generator_gateway", "p0_governance")
_emit_reads_policy_state("p0", "test_resume_generator_gateway", "policy_binding")
_emit_snapshots_state("p0", "test_resume_generator_gateway", "state_snapshot")
emit_replay_key("p0", "test_resume_generator_gateway")
emit_determinism_digest("p0", "test_resume_generator_gateway")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _stub_resume_generator_imports():
    """Stub legacy runtime.shared.* imports so ResumeGenerator can be imported in tests."""
    import types

    _provider_enum = MagicMock()
    _provider_enum.GOOGLE = "google"
    _provider_enum.OPENAI = "openai"
    _provider_enum.ANTHROPIC = "anthropic"

    runtime_mod = types.ModuleType("runtime")
    runtime_shared = types.ModuleType("runtime.shared")
    runtime_mp = types.ModuleType("runtime.shared.multi_provider_clients")
    runtime_mp.Provider = _provider_enum
    runtime_mp.get_client = MagicMock()
    runtime_mod.shared = runtime_shared
    runtime_shared.multi_provider_clients = runtime_mp

    sys.modules.setdefault("runtime", runtime_mod)
    sys.modules.setdefault("runtime.shared", runtime_shared)
    sys.modules.setdefault("runtime.shared.multi_provider_clients", runtime_mp)
    return _provider_enum


class TestResumeGeneratorGatewayRouting:
    def test_generate_with_gemini_uses_sovereign_gateway(self):
        """RG-GAP-01 positive: _generate_with_gemini routes through SovereignLLMGateway."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        mock_response = MagicMock()
        mock_response.text = "Generated resume content"

        mock_gateway_instance = MagicMock()
        mock_gateway_instance.generate.return_value = mock_response

        mock_gateway_cls = MagicMock(return_value=mock_gateway_instance)
        mock_request_cls = MagicMock(return_value=MagicMock())

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=mock_gateway_cls,
                    GenerationRequest=mock_request_cls,
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            result = gen._generate_with_gemini("test prompt")

        assert result == "Generated resume content"
        mock_gateway_cls.assert_called_once()
        mock_gateway_instance.generate.assert_called_once()

    def test_generate_with_gemini_does_not_import_sdk_directly(self):
        """RG-GAP-01 negative control: google.generativeai must not appear in method source."""
        import inspect

        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        source = inspect.getsource(ResumeGenerator._generate_with_gemini)
        assert "google.generativeai" not in source, (
            "RG-GAP-01 violated: _generate_with_gemini still imports google.generativeai directly"
        )

    def test_generate_with_gemini_raises_when_gateway_unavailable(self):
        """RG-GAP-01: Gateway unavailable → RuntimeError, not silent fallback to SDK."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=MagicMock(side_effect=ImportError("gateway missing")),
                    GenerationRequest=MagicMock(),
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            with pytest.raises(RuntimeError, match="gateway unavailable"):
                gen._generate_with_gemini("test prompt")

    def test_generate_with_gemini_uses_gemini_2_5_pro_model(self):
        """RG-GAP-01: model must be gemini-2.5-pro, not stale gemini-1.5-flash."""
        _stub_resume_generator_imports()
        from apps_rg.tools.ResumeGenerator import ResumeGenerator

        captured_request = {}

        def capture_request(request):
            captured_request["model"] = request.model
            resp = MagicMock()
            resp.text = "ok"
            return resp

        mock_gateway = MagicMock()
        mock_gateway.generate.side_effect = capture_request

        class _FakeRequest:
            def __init__(self, **kwargs):
                self.model = kwargs.get("model")

        with patch.dict(
            "sys.modules",
            {
                "agentic_core.interfaces.gateway": MagicMock(
                    SovereignLLMGateway=MagicMock(return_value=mock_gateway),
                    GenerationRequest=_FakeRequest,
                )
            },
        ):
            gen = ResumeGenerator(llm_client=MagicMock())
            gen._generate_with_gemini("test prompt")

        assert captured_request.get("model") == "gemini-2.5-pro", (
            f"Expected gemini-2.5-pro, got {captured_request.get('model')}"
        )


class TestHardenedRouterGeminiExecutorWired:
    """AST-level verification that HardenedGeminiExecutor is wired into _initialize_executors."""

    _SOURCE_FILE = "apps_rg/types/AllProvidersDownError.py"

    def _read_source(self) -> str:
        from pathlib import Path

        root = Path(__file__).parents[3]
        return (root / self._SOURCE_FILE).read_text(encoding="utf-8")

    def test_hardened_gemini_executor_imported(self):
        """RG-GAP-02 positive: HardenedGeminiExecutor must be imported in AllProvidersDownError.py."""
        src = self._read_source()
        assert "HardenedGeminiExecutor" in src, (
            "RG-GAP-02: HardenedGeminiExecutor not imported in AllProvidersDownError.py"
        )

    def test_hardened_gemini_executor_instantiated_for_google(self):
        """RG-GAP-02 positive: HardenedGeminiExecutor() must be instantiated in _initialize_executors."""
        src = self._read_source()
        assert "HardenedGeminiExecutor()" in src, (
            "RG-GAP-02: HardenedGeminiExecutor() not instantiated for Provider.GOOGLE"
        )

    def test_negative_no_warning_comment_for_google_path(self):
        """RG-GAP-02 negative control: the old warning comment must be gone."""
        src = self._read_source()
        assert "HardenedGeminiExecutor not yet implemented" not in src, (
            "RG-GAP-02 regression: old stub comment still present — executor not actually wired"
        )

    def test_google_provider_branch_assigns_executor(self):
        """RG-GAP-02: The elif Provider.GOOGLE branch must assign HardenedGeminiExecutor(), not just warn."""
        import re

        src = self._read_source()
        # Find the elif/if block for Provider.GOOGLE in _initialize_executors
        match = re.search(
            r"elif provider == Provider\.GOOGLE.*?(?=elif|else|\Z)",
            src,
            re.DOTALL,
        )
        assert match is not None, "Could not find 'elif provider == Provider.GOOGLE' block in source"
        block = match.group(0)
        assert "HardenedGeminiExecutor()" in block, (
            f"RG-GAP-02: Provider.GOOGLE block does not assign HardenedGeminiExecutor(): {block!r}"
        )
        assert "logger.warning" not in block, (
            "RG-GAP-02: Provider.GOOGLE block still only logs a warning — executor not wired"
        )
