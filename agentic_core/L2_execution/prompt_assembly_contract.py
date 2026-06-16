"""Prompt Assembly Contract Producer — AG-RGGOV-W6 Core Contract

Prompt Assembly emits CompiledPromptArtifact when model_generation_required = true.

Responsibilities:
- Consume FinalEvidenceContract when model_generation_required = true
- Assemble prompt from evidence and user intent
- Emit CompiledPromptArtifact for L2 execution

Hard Constraints:
- Only emit when model_generation_required = true
- Core owns all prompt assembly
- apps_rg does not assemble prompts
- Contract dataclasses are defined in runtime/contracts/, imported here
- Prompt Assembly is NOT L2 — this is a separate core surface
"""

from __future__ import annotations

from datetime import datetime, timezone

from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.route_contract import RouteContract


class PromptAssembler:
    """Prompt assembly layer for apps_rg tasks.

    Emits CompiledPromptArtifact when model_generation_required = true.
    """

    def assemble(
        self,
        evidence_contract: FinalEvidenceContract,
        route: RouteContract,
    ) -> CompiledPromptArtifact:
        """Assemble prompt from evidence and emit CompiledPromptArtifact.

        Args:
            evidence_contract: C0 evidence output
            route: L0 routing output with execution flags

        Returns:
            CompiledPromptArtifact with assembled prompt
        """
        # Build prompt blocks from evidence
        prompt_blocks = self._build_prompt_blocks(evidence_contract)

        # Compute compilation hash
        import hashlib
        import json

        compilation_hash = hashlib.sha256(
            json.dumps({
                "request_id": evidence_contract.request_id,
                "blocks": [(b.role, b.content) for b in prompt_blocks],
            }, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return CompiledPromptArtifact(
            request_id=evidence_contract.request_id,
            run_id=evidence_contract.run_id,
            app_id=evidence_contract.app_id,
            trace_id=evidence_contract.trace_id,
            prompt_blocks=tuple(prompt_blocks),
            system_preamble=self._build_system_preamble(),
            user_instruction=self._build_user_instruction(evidence_contract),
            assembly_timestamp=datetime.now(timezone.utc).isoformat(),
            assembly_version="W6.0",
            target_model=QWEN_LOCAL_MODEL_ID,
            target_provider="vllm",
            evidence_digest=evidence_contract.compilation_hash,
            compilation_hash=compilation_hash,
            max_tokens=4096,
            temperature=0.7,
        )

    def _build_prompt_blocks(
        self, evidence_contract: FinalEvidenceContract
    ) -> list[PromptBlock]:
        """Build prompt blocks from evidence."""
        blocks: list[PromptBlock] = []
        block_idx = 0

        # System preamble
        blocks.append(
            PromptBlock(
                role="system",
                content=self._build_system_preamble(),
                block_index=block_idx,
            )
        )
        block_idx += 1

        # Evidence context from each item
        for item in evidence_contract.evidence_items:
            blocks.append(
                PromptBlock(
                    role="user",
                    content=f"Evidence from {item.source}: {item.content}",
                    block_index=block_idx,
                )
            )
            block_idx += 1

        # Final user instruction
        blocks.append(
            PromptBlock(
                role="user",
                content=self._build_user_instruction(evidence_contract),
                block_index=block_idx,
            )
        )

        return blocks

    def _build_system_preamble(self) -> str:
        """Build system preamble for resume generation."""
        return (
            "You are an expert resume writer specializing in technology leadership roles. "
            "Generate compelling, achievement-focused resumes tailored to specific companies."
        )

    def _build_user_instruction(self, evidence_contract: FinalEvidenceContract) -> str:
        """Build final user instruction."""
        return (
            f"Generate a tailored resume using the evidence provided above. "
            f"Request ID: {evidence_contract.request_id}"
        )
