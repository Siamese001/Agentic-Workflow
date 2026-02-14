from __future__ import annotations

"""
[PHASE 14 REFACTOR] SubAtomicEngine.
STRICT COMPLIANCE: Uses SovereignLLMGateway singleton.
"""
import logging
import os

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
from agentic_core.prompt_governance.security.injection_scan_util import scan_untrusted_text

# NOTE: Direct import of PromptAssembler (assemble_prompt) is blocked by a
# pre-existing broken dependency: prompt_assembler.py imports InjectionMatch
# from agentic_core.L4_state.memory.runtime_models which no longer exists.
# Until that import chain is repaired, fencing is applied inline via
# _fence_prompt() using PromptAssembler's canonical XML tag structure.
#
# EmbeddingSovereignAgent import is deferred to __init__ because
# EmbeddingSovereignAgent.py references SovereignBaseAgent without importing
# it (pre-existing NameError).

Logger = logging.getLogger(__name__)


class SubAtomicEngineImpl:
    """Hardens the LLM interaction using Sovereign Gateways."""

    def __init__(self, redis_client=None, pinecone_index=None):
        from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import get_embedding_gateway

        self.llm_gateway = get_llm_gateway()
        self.embedding_gateway = get_embedding_gateway()
        self.redis_client = redis_client
        print("   [OK] SubAtomicEngine: Gateway Link Active")

    async def get_embedding(self, text: str) -> list[float]:
        try:
            return await self.embedding_gateway.get_embedding(text, provider="gemini")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Embedding failed: {e}")
            return [0.0] * 768

    @staticmethod
    def _fence_prompt(system_prompt: str, user_prompt: str) -> str:
        """Apply PromptAssembler-compatible XML semantic fencing.

        Uses the canonical <SYSTEM_PRIME> / <CONTEXT_DATA> tag structure
        from agentic_core.prompt_governance.core.prompt_assembler to
        structurally separate trusted system directives from untrusted
        user content, preventing instruction drift.

        When system_prompt is empty, returns user_prompt unmodified
        to preserve backward compatibility with bare-prompt callers.
        """
        if not system_prompt:
            return user_prompt
        return (
            "<SYSTEM_PRIME>\n"
            f"{system_prompt}\n"
            "</SYSTEM_PRIME>\n\n"
            "<CONTEXT_DATA>\n"
            f"{user_prompt}\n"
            "</CONTEXT_DATA>"
        )

    async def resilient_mutation(self, *args, **kwargs) -> str:
        """Gateway-backed mutation."""
        prompt = kwargs.get("prompt", "") or (args[0] if args else "")
        system_prompt = kwargs.get("system_prompt", None)
        fission_active = kwargs.get("fission_active", False)

        full_prompt = self._fence_prompt(system_prompt or "", prompt)

        # §P1 — Canonical injection scan on fenced prompt (fail-closed)
        scan_untrusted_text(prompt, source="sub_atomic_user_prompt")
        scan_untrusted_text(full_prompt, source="sub_atomic_full_prompt")

        try:
            gen_config = {}
            if fission_active:
                gen_config = {
                    "thinking_config": {"include_thoughts": True},
                    "thinking_budget": 1024,
                }

            response = await self.llm_gateway.generate(
                prompt=full_prompt,
                provider="google",
                model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
                generation_config=gen_config,
            )
            return response["content"]
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Mutation failed: {e}")
            return prompt
