"""apps_rg AgentSpec root — prompt-reception wiring anchor.

Plan: apps-core-contract-rectification-a8f3c2 Phase 2.3 (AEH2 gate).

apps_rg domain profiles and contracts remain under ``config/domain_contract/``.
This module provides the shared :class:`PromptReceptionSpec` fields so the
reception pipeline can resolve ``adapter_version`` and ``exemplar_task_class``
uniformly with other ``apps_*`` surfaces.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class RgDomainContractSpec(BaseModel):
    """Lightweight anchor pointing at the on-disk domain contract bundle."""

    domain_contract_dir: str = Field(
        default="apps_rg/config/domain_contract",
        description="Relative path to YAML/JSON contract artifacts",
    )


class RgAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_rg."""

    version: str = "1.0.0"
    domain_contract: RgDomainContractSpec = Field(default_factory=RgDomainContractSpec)


__all__ = ["RgAgentSpecs", "RgDomainContractSpec"]
