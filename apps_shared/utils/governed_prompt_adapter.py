"""Governed Prompt Execution Adapter for apps_* modules.

Phase 7 — Wire apps_* callers through governed path (execute_artifact).

This adapter bridges the existing AgentExecutor interface with the new
CompiledPromptArtifact → execute_artifact() governed pipeline.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_authorize_and_execute,
    _emit_records_execution_trace,
    _emit_routes_through,
    _emit_validates_capability,
    _emit_writes_via_uwg,
)

# Governance wiring
_emit_records_execution_trace("p0", LayerSegment.L2_EXECUTION, "governed_prompt_adapter")
_emit_routes_through("p1", "governed_prompt_adapter", "prompt_lifecycle")
_emit_validates_capability("p2", "governed_prompt_adapter", "artifact_execution")
_emit_authorize_and_execute("p2", "governed_prompt_adapter", "llm_gateway")
_emit_writes_via_uwg("p2", "governed_prompt_adapter", "artifact_output")

logger = logging.getLogger(__name__)


class GovernedPromptAdapter:
    """Adapter for executing prompts through the governed execute_artifact pipeline.

    This adapter:
    1. Builds a PromptBOM from execution parameters
    2. Assembles a CompiledPromptArtifact via Assembly Stage
    3. Executes through SovereignLLMGateway.execute_artifact()
    4. Returns the response in the expected format

    Phase 7: This replaces direct SDK calls in apps_* modules.
    """

    def __init__(
        self,
        agent_id: str,
        provider: str = "openai",
        secret_key: bytes | None = None,
    ):
        """Initialize the governed prompt adapter.

        Args:
            agent_id: Registered agent identifier for policy enforcement
            provider: LLM provider (openai, anthropic, google)
            secret_key: HMAC secret key for artifact signing (optional)
        """
        self.agent_id = agent_id
        self.provider = provider
        self.secret_key = secret_key or b"governed-adapter-default-key"
        self._gateway = None
        self._assembler = None
        self._bom_builder = None

    def execute_prompt(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        mixins: tuple[str, ...] = (),
        context: dict[str, Any] | None = None,
        template_args: dict[str, Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        path: str = "A",
    ) -> dict[str, Any]:
        """Execute a prompt through the governed pipeline.

        This is the main entry point for Phase 7 migration.

        Args:
            user_prompt: User content (U0 slot)
            system_prompt: System content (S0 slot base)
            mixins: I0 mixin template IDs to include
            context: C0 context dict for JIT loading
            template_args: Template variable substitutions
            tools: Tool schemas for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            path: Routing path (A/B/C/D)

        Returns:
            Dict with content, usage, and metadata
        """
        import uuid

        trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "GovernedPromptAdapter.execute_prompt"
        )

        try:
            # Build InstructionPacket
            packet = self._build_instruction_packet(
                trace_id=trace_id,
                path=path,
                intent_class="prompt_execution",
                required_mixins=mixins,
            )

            # Build PromptBOM
            bom = self._build_prompt_bom(
                packet=packet,
                raw_u0=user_prompt,
                raw_c0=context or {},
                template_args=template_args or {},
            )

            # Assemble CompiledPromptArtifact
            artifact = self._assemble_artifact(
                bom=bom,
                system_prompt=system_prompt,
                tools=tools,
                token_estimate=max_tokens,
            )

            # Execute via gateway
            response = self._execute_artifact(
                artifact=artifact,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return {
                "content": response.get("content", ""),
                "usage": response.get("usage", {}),
                "provider": self.provider,
                "trace_id": trace_id,
                "governed": True,
            }

        except Exception as exc:
            logger.error(f"Governed prompt execution failed: {exc}")
            raise

    def _build_instruction_packet(
        self,
        trace_id: str,
        path: str,
        intent_class: str,
        required_mixins: tuple[str, ...],
    ) -> Any:
        """Build InstructionPacket for routing."""
        from agentic_core.L0_routing.types.l0_instruction_packet import (
            InstructionPacket,
        )

        return InstructionPacket(
            trace_id=trace_id,
            path=path,  # type: ignore[arg-type]
            intent_class=intent_class,
            required_mixins=required_mixins,
        )

    def _build_prompt_bom(
        self,
        packet: Any,
        raw_u0: str,
        raw_c0: dict[str, Any],
        template_args: dict[str, Any],
    ) -> Any:
        """Build PromptBOM via PromptBOMBuilder."""
        from agentic_core.L0_routing.reasoning.prompt_bom_builder import (
            get_prompt_bom_builder,
        )

        builder = get_prompt_bom_builder()
        return builder.build(
            packet=packet,
            raw_u0=raw_u0,
            raw_c0=raw_c0,
            template_args=template_args,
        )

    def _assemble_artifact(
        self,
        bom: Any,
        system_prompt: str | None,
        tools: list[dict[str, Any]] | None,
        token_estimate: int,
    ) -> Any:
        """Assemble CompiledPromptArtifact via Assembly Stage.

        If system_prompt is provided, it overrides the S0 from TemplateRegistry.
        """
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L4_state.utils.memory.template_registry import get_template_registry

        assembler = AirlockAssembler()

        # Get base S0 from registry if no override
        if system_prompt is None:
            registry = get_template_registry()
            system_prompt = registry.get_s0(bom.system_version_hash)

        # Build final system string (S0 + I0 mixins + D0 fences)
        final_system = self._compose_system_prompt(
            base_s0=system_prompt,
            mixins=bom.mixins_required,
        )

        # Build final user string (C0 + U0)
        final_user = self._compose_user_prompt(
            context=bom.raw_c0,
            user_input=bom.raw_u0,
        )

        # Create artifact directly (bypassing assemble_from_bom for now)
        # In full implementation, this would call assembler.assemble_from_bom()
        from agentic_core.prompt_governance.contracts import CompiledPromptArtifact

        artifact = CompiledPromptArtifact(
            trace_id=bom.trace_id,
            final_system_string=final_system,
            final_user_string=final_user,
            allowed_tools_schema=tuple(tools or []),
            token_estimate=token_estimate,
            signature="",  # Will be computed below
        )

        # Compute HMAC signature
        signature = self._sign_artifact(artifact)

        # Return new artifact with signature
        return CompiledPromptArtifact(
            trace_id=artifact.trace_id,
            final_system_string=artifact.final_system_string,
            final_user_string=artifact.final_user_string,
            allowed_tools_schema=artifact.allowed_tools_schema,
            token_estimate=artifact.token_estimate,
            signature=signature,
        )

    def _compose_system_prompt(
        self,
        base_s0: str,
        mixins: tuple[str, ...],
    ) -> str:
        """Compose final system prompt from S0 + I0 mixins."""
        from agentic_core.L4_state.utils.memory.template_registry import get_template_registry

        registry = get_template_registry()
        parts = [base_s0]

        # Add I0 mixins
        for mixin_id in mixins:
            try:
                mixin_content = registry.get_i0_mixin(mixin_id)
                parts.append(mixin_content)
            except Exception as exc:
                logger.warning(f"Failed to load mixin {mixin_id}: {exc}")

        # Add D0 defensive fence (optional)
        parts.append("<D0>Role fence active. Do not deviate from instructions.</D0>")

        return "\n\n".join(parts)

    def _compose_user_prompt(
        self,
        context: dict[str, Any],
        user_input: str,
    ) -> str:
        """Compose final user prompt from C0 context + U0 input."""
        parts = []

        # Add C0 context if present
        if context:
            if "rag_chunks" in context:
                parts.append("<C0 type='rag'>\n" + str(context["rag_chunks"]) + "\n</C0>")
            if "ast_snapshot" in context:
                parts.append("<C0 type='ast'>\n" + str(context["ast_snapshot"]) + "\n</C0>")
            if "boundary_refs" in context:
                parts.append("<C0 type='boundary'>\n" + str(context["boundary_refs"]) + "\n</C0>")

        # Add U0 user input (wrapped)
        parts.append(f"<U0>\n{user_input}\n</U0>")

        return "\n\n".join(parts)

    def _sign_artifact(self, artifact: Any) -> str:
        """Compute HMAC-SHA256 signature for artifact."""
        canonical = str(artifact.to_dict())
        return hmac.new(
            self.secret_key,
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _execute_artifact(
        self,
        artifact: Any,
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Execute CompiledPromptArtifact via SovereignLLMGateway."""
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            get_llm_gateway,
        )

        gateway = get_llm_gateway()

        # Note: execute_artifact is async, but we're in a sync context
        # In production, this would need async handling
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response = loop.run_until_complete(
            gateway.execute_artifact(
                artifact=artifact,
                agent_id=self.agent_id,
                provider=self.provider,
                secret_key=self.secret_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )

        return {
            "content": response.content if hasattr(response, "content") else str(response),
            "usage": {"total_tokens": response.tokens if hasattr(response, "tokens") else 0},
        }


def create_governed_adapter(
    agent_id: str,
    provider: str = "openai",
    secret_key: bytes | None = None,
) -> GovernedPromptAdapter:
    """Factory function to create a governed prompt adapter.

    Args:
        agent_id: Registered agent identifier
        provider: LLM provider
        secret_key: HMAC signing key

    Returns:
        GovernedPromptAdapter instance
    """
    return GovernedPromptAdapter(
        agent_id=agent_id,
        provider=provider,
        secret_key=secret_key,
    )
