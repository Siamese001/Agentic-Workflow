"""apps_exec AgentSpec root — prompt-reception wiring anchor.

Plan: apps-core-contract-rectification-a8f3c2 Phase 2.3 (AEH2 gate).

Execution harness profiles live under ``config/domain_contract/``. This module
only carries the shared reception fields required by ``PromptReceptionSpec``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class ExecDomainContractSpec(BaseModel):
    """Pointer to the governed contract bundle for apps_exec."""

    domain_contract_dir: str = Field(
        default="apps_exec/config/domain_contract",
        description="Relative path to YAML contract artifacts",
    )


class ExecAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_exec."""

    version: str = "1.0.0"
    domain_contract: ExecDomainContractSpec = Field(default_factory=ExecDomainContractSpec)


__all__ = ["ExecAgentSpecs", "ExecDomainContractSpec"]
