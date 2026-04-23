"""apps_underwriting_ai AgentSpec root — prompt-reception wiring anchor.

Plan: prompt-reception-followups-a7b3c4 (delta fix for phase RH5B.1).

apps_underwriting_ai historically shipped configuration exclusively as
YAML (``covenant_templates.yaml``, ``industry_risk_weights.yaml``,
``policy_exception_rules.yaml``, ``financial_policy.yaml``) with no
Pydantic root model. This file introduces the minimal root
``UnderwritingAgentSpecs`` class that inherits the shared
:class:`PromptReceptionSpec` mixin so the prompt reception pipeline can
query ``adapter_version`` and ``exemplar_task_class`` uniformly across
all 7 app families.

Intentionally minimal
---------------------
This root is **intentionally scaffolding**. It carries only the
reception-pipeline fields today. Domain configuration remains in YAML.
Consolidating YAML schemas into this root is out of scope for the
reception plan and would belong in a dedicated underwriting-config
consolidation plan.
"""

from __future__ import annotations

from pydantic import BaseModel

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class UnderwritingAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_underwriting_ai (minimal scaffolding).

    Inherits :class:`PromptReceptionSpec` fields:

    - ``adapter_version: Literal['v1', 'v2']`` (default ``'v2'``)
    - ``exemplar_task_class: str | None`` (default ``None``)
    """

    version: str = "1.0.0"


__all__ = ["UnderwritingAgentSpecs"]
