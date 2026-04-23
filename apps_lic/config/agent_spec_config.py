"""apps_lic AgentSpec root — prompt-reception wiring anchor.

Plan: prompt-reception-followups-a7b3c4 (delta fix for phase RH5B.1).

apps_lic historically shipped per-component Pydantic configs
(``archetype_indicator_config.py``, ``loader_config.py``,
``reasoning_toggles_config.py``, etc.) with no single AgentSpec root
model. This file introduces the minimal root ``LicAgentSpecs`` class that
inherits the shared :class:`PromptReceptionSpec` mixin so the prompt
reception pipeline can query ``adapter_version`` and
``exemplar_task_class`` uniformly across all 7 app families.

Intentionally minimal
---------------------
This root is **intentionally scaffolding**. It carries only the
reception-pipeline fields today. Downstream apps_lic callers that need
domain-specific settings should continue to use the existing per-component
config modules; consolidation of those into this root is out of scope for
the reception plan and would belong in a dedicated apps_lic config
consolidation plan.
"""

from __future__ import annotations

from pydantic import BaseModel

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class LicAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_lic (minimal scaffolding).

    Inherits :class:`PromptReceptionSpec` fields:

    - ``adapter_version: Literal['v1', 'v2']`` (default ``'v2'``)
    - ``exemplar_task_class: str | None`` (default ``None``)
    """

    version: str = "1.0.0"


__all__ = ["LicAgentSpecs"]
