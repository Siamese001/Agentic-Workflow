"""P0/W0.2 — Contract test harness for context engineering call-path modules.

Validates that all canonical modules, classes, and callables on the
subatomic prompt-assembly / LLM-boundary path exist and expose the
expected public surface.  Tests-only; no production code is modified.
"""

from __future__ import annotations

import importlib
import inspect
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]


def _importorskip_strict(module_name: str, reason: str = "optional dependency missing"):
    """Skip on ImportError/ModuleNotFoundError only; re-raise everything else.

    Unlike pytest.importorskip this is a strict policy: NameError,
    AttributeError, or any other runtime exception during import is a
    genuine contract breach and must surface as a test FAILURE.
    """
    try:
        return importlib.import_module(module_name)
    except (ImportError, ModuleNotFoundError):
        pytest.skip(f"{reason}: ImportError importing {module_name}")


# ── 1. SubAtomicEngineImpl ──────────────────────────────────────────────


class TestSubAtomicEngineImplContract:
    """Contract: agentic_core.L3_orchestration.engines.sub_atomic_engine_impl"""

    MODULE = "agentic_core.L3_orchestration.engines.sub_atomic_engine_impl"

    def test_module_importable(self):
        mod = importlib.import_module(self.MODULE)
        assert mod is not None

    def test_class_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "SubAtomicEngineImpl"), f"{self.MODULE} must export SubAtomicEngineImpl"

    def test_resilient_mutation_exists(self):
        mod = importlib.import_module(self.MODULE)
        cls = mod.SubAtomicEngineImpl
        assert hasattr(cls, "resilient_mutation"), "SubAtomicEngineImpl must have resilient_mutation method"

    def test_fence_prompt_removed(self):
        mod = importlib.import_module(self.MODULE)
        cls = mod.SubAtomicEngineImpl
        assert not hasattr(cls, "_fence_prompt"), (
            "SubAtomicEngineImpl must NOT have _fence_prompt stopgap "
            "(replaced by PromptAssembler wiring in P2/W2.3)"
        )

    def test_uses_prompt_assembler_import(self):
        src = (
            REPO_ROOT / "agentic_core" / "L3_orchestration" / "engines" / "sub_atomic_engine_impl.py"
        ).read_text(encoding="utf-8")
        assert "from agentic_core.prompt_governance.core.prompt_assembler import" in src, (
            "sub_atomic_engine_impl.py must import from prompt_assembler"
        )


# ── 2. SovereignLLMGateway ──────────────────────────────────────────────


class TestSovereignLLMGatewayContract:
    """Contract: agentic_core.L2_execution.enforcement.SovereignLLMGateway"""

    MODULE = "agentic_core.L2_execution.enforcement.SovereignLLMGateway"

    def test_module_importable(self):
        mod = importlib.import_module(self.MODULE)
        assert mod is not None

    def test_class_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "SovereignLLMGateway"), f"{self.MODULE} must export SovereignLLMGateway"

    def test_get_llm_gateway_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "get_llm_gateway"), f"{self.MODULE} must export get_llm_gateway"
        assert callable(mod.get_llm_gateway), "get_llm_gateway must be callable"


# ── 3. PromptAssembler ──────────────────────────────────────────────────


class TestPromptAssemblerContract:
    """Contract: agentic_core.prompt_governance.core.prompt_assembler"""

    MODULE = "agentic_core.prompt_governance.core.prompt_assembler"

    def test_module_importable(self):
        mod = importlib.import_module(self.MODULE)
        assert mod is not None

    def test_class_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "PromptAssembler"), f"{self.MODULE} must export PromptAssembler"

    def test_get_prompt_assembler_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "get_prompt_assembler"), f"{self.MODULE} must export get_prompt_assembler"
        assert callable(mod.get_prompt_assembler), "get_prompt_assembler must be callable"

    def test_assemble_prompt_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "assemble_prompt"), f"{self.MODULE} must export assemble_prompt"
        assert callable(mod.assemble_prompt), "assemble_prompt must be callable"


# ── 4. InstructionalInjectionMixin ──────────────────────────────────────


class TestInstructionalInjectionMixinContract:
    """Contract: agentic_core.mixins.instructional_injection_mixin"""

    MODULE = "agentic_core.mixins.instructional_injection_mixin"

    def test_module_importable(self):
        mod = importlib.import_module(self.MODULE)
        assert mod is not None

    def test_class_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "InstructionalInjectionMixin"), (
            f"{self.MODULE} must export InstructionalInjectionMixin"
        )

    def test_inject_all_layers_exists(self):
        mod = importlib.import_module(self.MODULE)
        cls = mod.InstructionalInjectionMixin
        assert hasattr(cls, "inject_all_layers"), (
            "InstructionalInjectionMixin must have inject_all_layers method"
        )


# ── 5. SovereignBaseAgent ───────────────────────────────────────────────


class TestSovereignBaseAgentContract:
    """Contract: agentic_core.base_agents.SovereignBaseAgent"""

    MODULE = "agentic_core.base_agents.SovereignBaseAgent"

    def test_module_importable(self):
        mod = importlib.import_module(self.MODULE)
        assert mod is not None

    def test_class_exists(self):
        mod = importlib.import_module(self.MODULE)
        assert hasattr(mod, "SovereignBaseAgent"), f"{self.MODULE} must export SovereignBaseAgent"

    def test_prepare_messages_for_llm_exists(self):
        mod = importlib.import_module(self.MODULE)
        cls = mod.SovereignBaseAgent
        assert hasattr(cls, "prepare_messages_for_llm"), (
            "SovereignBaseAgent must have prepare_messages_for_llm method"
        )


# ── 6. prompt_injection_loader_config (apply_injections) ────────────────


class TestPromptInjectionLoaderContract:
    """Contract: agentic_core.runtime.config.prompt_injection_loader_config

    Deterministic predicate: the module must expose ``apply_injections``
    as either a module-level callable or as an attribute on any
    module-level object.
    """

    MODULE = "agentic_core.runtime.config.prompt_injection_loader_config"

    def _import(self):
        return _importorskip_strict(self.MODULE)

    def test_module_importable(self):
        mod = self._import()
        assert mod is not None

    def test_apply_injections_reachable(self):
        mod = self._import()

        # Case (a): module-level callable
        if hasattr(mod, "apply_injections") and callable(mod.apply_injections):
            return  # PASS

        # Case (b): attribute on any module-level object (class or instance)
        for name in dir(mod):
            obj = getattr(mod, name, None)
            if obj is None:
                continue
            if inspect.isclass(obj) or (not inspect.ismodule(obj) and not inspect.isbuiltin(obj)):
                if hasattr(obj, "apply_injections"):
                    return  # PASS

        pytest.fail(
            f"{self.MODULE} must expose apply_injections as a module-level "
            "callable or as an attribute on a module-level object"
        )


# ── 7. prompt_enhancer_config (apps_shared) ─────────────────────────────


class TestPromptEnhancerConfigContract:
    """Contract: apps_shared.config.prompt_enhancer_config (optional dependency)."""

    def test_prompt_assembler_obtainable(self):
        mod = pytest.importorskip("apps_shared.config.prompt_enhancer_config")

        # Lightweight check: the module references get_prompt_assembler
        # or makes PromptAssembler obtainable.
        has_get = hasattr(mod, "get_prompt_assembler")
        has_class = hasattr(mod, "PromptAssembler")

        # Also check if any class in the module stores a prompt_assembler attribute
        has_attr = any(
            hasattr(getattr(mod, n, None), "prompt_assembler")
            for n in dir(mod)
            if inspect.isclass(getattr(mod, n, None))
        )

        assert has_get or has_class or has_attr, (
            "apps_shared.config.prompt_enhancer_config must reference "
            "get_prompt_assembler, export PromptAssembler, or have a class "
            "with a prompt_assembler attribute"
        )


# ── 8. Instructional Injection Pattern Data Files ───────────────────────


class TestInstructionalInjectionPatternDataContract:
    """Contract: canonical instructional injection pattern data files exist
    and contain all 30 patterns across 6 layers.

    Sources:
      - data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
    """

    V5_DATA = (
        REPO_ROOT
        / "data"
        / "prompt_governance"
        / "prompt_injections"
        / "Instructional_Injection_Enhanced_v5.md"
    )

    EXPECTED_LAYERS = [
        "Framing Layer",
        "Context Layer",
        "Reasoning Layer",
        "Tooling Layer",
        "Safety Layer",
        "Output Layer",
    ]

    def test_v5_data_file_exists(self):
        assert self.V5_DATA.is_file(), f"Missing: {self.V5_DATA.relative_to(REPO_ROOT)}"

    def test_v5_contains_all_30_patterns(self):
        content = self.V5_DATA.read_text(encoding="utf-8")
        for pattern_num in range(1, 31):
            assert f"**{pattern_num}**" in content, f"Pattern #{pattern_num} missing from v5 data file"

    def test_v5_contains_all_6_layers(self):
        content = self.V5_DATA.read_text(encoding="utf-8")
        for layer in self.EXPECTED_LAYERS:
            assert layer in content, f"Layer '{layer}' missing from v5 data file"


# ── 9. No-Naive-Concat Regression Guard ─────────────────────────────────


class TestNoNaiveConcatRegression:
    """Deterministic regression guard: sub_atomic_engine_impl.py must never
    revert to naive f-string concatenation of system_prompt + user prompt.

    Reads the source file from disk (no import needed) and asserts:
      - forbidden concat patterns are absent
      - a recognised fencing mechanism is present
    """

    SOURCE = REPO_ROOT / "agentic_core" / "L3_orchestration" / "engines" / "sub_atomic_engine_impl.py"

    def _read_source(self) -> str:
        assert self.SOURCE.is_file(), f"Missing: {self.SOURCE.relative_to(REPO_ROOT)}"
        return self.SOURCE.read_text(encoding="utf-8")

    def test_no_fstring_concat(self):
        src = self._read_source()
        forbidden = 'f"{system_prompt}\\n\\n{prompt}"'
        assert forbidden not in src, (
            "sub_atomic_engine_impl.py must not contain naive f-string "
            "concatenation of system_prompt and prompt"
        )

    def test_no_plus_concat(self):
        src = self._read_source()
        assert "system_prompt +" not in src, (
            "sub_atomic_engine_impl.py must not concatenate system_prompt with '+' operator"
        )

    def test_fencing_mechanism_present(self):
        src = self._read_source()
        has_assemble_prompt = "assemble_prompt(" in src
        has_prompt_assembler = "PromptAssembler" in src
        assert has_assemble_prompt or has_prompt_assembler, (
            "sub_atomic_engine_impl.py must use PromptAssembler fencing: "
            "assemble_prompt() or PromptAssembler (stopgap _fence_prompt is forbidden)"
        )

    def test_no_stopgap_fence_prompt(self):
        src = self._read_source()
        assert "_fence_prompt" not in src, (
            "sub_atomic_engine_impl.py must not contain the _fence_prompt stopgap "
            "(replaced by PromptAssembler in P2/W2.3)"
        )

    def test_no_mode_in_injection_call(self):
        src = self._read_source()
        for line in src.splitlines():
            if "inject_all_layers(" in line:
                assert "mode=" not in line, (
                    "inject_all_layers call must not contain mode= "
                    "(provider-steering flags are forbidden on the deterministic hot path)"
                )


# ── 10. InstructionalInjection Integration (monkeypatch) ────────────────


class TestInstructionalInjectionIntegration:
    """Verify that InstructionalInjectionMixin.inject_all_layers executes
    exactly once on the subatomic hot path, BEFORE assemble_prompt receives
    the prompt text.

    All external I/O (LLM gateway, embedding gateway) is stubbed out.
    """

    SENTINEL = "<<INJECTED>>"

    def test_injection_runs_before_assembly(self, monkeypatch):
        import asyncio

        from agentic_core.L3_orchestration.engines import sub_atomic_engine_impl as mod

        sentinel = self.SENTINEL

        # ── track inject_all_layers calls ──
        inject_calls: list[tuple] = []

        class _StubMixin:
            def inject_all_layers(self_, prompt, **kwargs):
                inject_calls.append((prompt, kwargs))
                return prompt + sentinel

        monkeypatch.setattr(mod, "get_instructional_injection_mixin", lambda: _StubMixin())

        # ── capture what assemble_prompt receives (stub — no real assembler) ──
        assemble_args: list[dict] = []

        def _spy_assemble(**kwargs):
            assemble_args.append(kwargs)
            return f"<ASSEMBLED>{kwargs.get('context_data', '')}</ASSEMBLED>"

        monkeypatch.setattr(mod, "assemble_prompt", _spy_assemble)

        # ── stub async LLM gateway ──
        class _StubGateway:
            async def generate(self_, **kwargs):
                return {"content": "stub-response"}

        # ── stub async embedding gateway ──
        class _StubEmbedding:
            async def get_embedding(self_, text, provider=None):
                return [0.0] * 768

        # Bypass __init__ side-effects by constructing manually
        engine = object.__new__(mod.SubAtomicEngineImpl)
        engine.llm_gateway = _StubGateway()
        engine.embedding_gateway = _StubEmbedding()
        engine.redis_client = None

        result = asyncio.run(engine.resilient_mutation(prompt="Fix this bug."))

        # inject_all_layers was called exactly once
        assert len(inject_calls) == 1, (
            f"inject_all_layers must be called exactly once; got {len(inject_calls)}"
        )
        # The original prompt was passed in
        assert inject_calls[0][0] == "Fix this bug."

        # kwargs must contain goal
        call_kwargs = inject_calls[0][1]
        assert "goal" in call_kwargs, "inject_all_layers must receive goal="

        # kwargs must NOT contain mode (provider-steering forbidden)
        assert "mode" not in call_kwargs, (
            "inject_all_layers must NOT receive mode= on the deterministic hot path "
            "(provider-steering flags are forbidden)"
        )

        # assemble_prompt received the injected text
        assert len(assemble_args) == 1
        assert sentinel in assemble_args[0]["context_data"], (
            "assemble_prompt must receive the output of inject_all_layers "
            "(sentinel not found in context_data)"
        )

        # LLM returned the stub
        assert result == "stub-response"


# ── 11. L3 ExecutionContext Semantic Handoff Fields ──────────────────────


class TestExecutionContextSemanticFields:
    """Verify that L3 ExecutionContext carries additive semantic handoff
    fields (P4/W4.1) and that builder methods preserve them.
    """

    SEMANTIC_FIELDS = (
        "task_description",
        "input_data",
        "expected_output_schema",
        "upstream_summary",
    )

    def _make_context(self, **overrides):
        from agentic_core.L3_orchestration.types.orchestrator_types import (
            ExecutionContext,
        )

        return ExecutionContext(**overrides)

    def test_fields_exist_on_class(self):
        import dataclasses

        from agentic_core.L3_orchestration.types.orchestrator_types import (
            ExecutionContext,
        )

        field_names = {f.name for f in dataclasses.fields(ExecutionContext)}
        for name in self.SEMANTIC_FIELDS:
            assert name in field_names, f"ExecutionContext must have field '{name}' (P4/W4.1)"

    def test_defaults_are_none(self):
        ctx = self._make_context()
        for name in self.SEMANTIC_FIELDS:
            assert getattr(ctx, name) is None, f"ExecutionContext.{name} must default to None"

    def test_with_depth_preserves_fields(self):
        ctx = self._make_context(
            task_description="td",
            input_data={"k": 1},
            expected_output_schema={"type": "object"},
            upstream_summary="us",
        )
        clone = ctx.with_depth(2)
        for name in self.SEMANTIC_FIELDS:
            assert getattr(clone, name) == getattr(ctx, name), f"with_depth must preserve {name}"

    def test_with_phase_preserves_fields(self):
        from agentic_core.L3_orchestration.types.orchestrator_types import (
            ExecutionPhase,
        )

        ctx = self._make_context(
            task_description="td",
            input_data={"k": 1},
            expected_output_schema={"type": "object"},
            upstream_summary="us",
        )
        clone = ctx.with_phase(ExecutionPhase.EXECUTION)
        for name in self.SEMANTIC_FIELDS:
            assert getattr(clone, name) == getattr(ctx, name), f"with_phase must preserve {name}"

    def test_with_accumulated_context_preserves_fields(self):
        ctx = self._make_context(
            task_description="td",
            input_data={"k": 1},
            expected_output_schema={"type": "object"},
            upstream_summary="us",
        )
        clone = ctx.with_accumulated_context({"extra": True})
        for name in self.SEMANTIC_FIELDS:
            assert getattr(clone, name) == getattr(ctx, name), (
                f"with_accumulated_context must preserve {name}"
            )
