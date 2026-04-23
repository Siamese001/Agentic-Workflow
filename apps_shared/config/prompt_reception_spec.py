"""Prompt-reception shared AgentSpec fields.

Plan: prompt-reception-followups-a7b3c4, phase RH5B.1.

Provides a ``PromptReceptionSpec`` Pydantic mixin carrying the two fields
that every ``apps_*`` AgentSpec must surface so the reception pipeline can:

1. Route prompt assembly through the correct provider adapter
   (``adapter_version``, default ``v2`` matching the W8 provider-aware
   adapters landed by the parent plan).
2. Declare whether the app's primary task class is exemplar-eligible per
   ``config/prompt_governance/exemplar_eligibility.yaml``
   (``exemplar_task_class``, nullable — set when the app opts into E0).

Rationale for shared mixin (not per-app duplication)
---------------------------------------------------
Every app previously carried domain-specific AgentSpec models with no
reception-pipeline vocabulary. Duplicating two fields across 5+ config
classes is noise; collecting them here keeps the reception contract a
single point of authority. Any future field (e.g. per-app secret budget,
per-app injection-scan thresholds) can join this mixin without touching
five downstream models.

Usage
-----
Downstream AgentSpec root models inherit from this mixin in addition to
``pydantic.BaseModel``::

    class ResearchAgentSpecs(PromptReceptionSpec, BaseModel):
        ...

The mixin itself does NOT inherit ``BaseModel`` so it is compatible with
models that already have competing MRO paths.

Apps currently wired (all 7)
----------------------------

- ``apps_research.config.agent_spec_config.ResearchAgentSpecs``
- ``apps_eval.config.agent_spec_config.EvalAgentSpecs``
- ``apps_exec.config.agent_spec_config.ExecAgentSpecs``
- ``apps_rfp.config.agent_spec_config.RfpAgentSpecs``
- ``apps_rg.config.agent_spec_config.RGAgentSpecs``
- ``apps_lic.config.agent_spec_config.LicAgentSpecs`` (minimal scaffolding)
- ``apps_underwriting_ai.config.agent_spec_config.UnderwritingAgentSpecs``
  (minimal scaffolding)

For ``apps_lic`` and ``apps_underwriting_ai``, the AgentSpec root is
intentionally minimal — it carries only the reception-pipeline fields.
Domain configuration for those apps continues to live in their existing
per-component Pydantic modules / YAML files. Consolidating that domain
config into the new root is explicitly out of scope for the reception
plan.
"""

from __future__ import annotations

from typing import Literal


AdapterVersion = Literal["v1", "v2"]


class PromptReceptionSpec:
    """Shared Pydantic-compatible fields for prompt-reception wiring.

    When inherited alongside ``pydantic.BaseModel``, Pydantic picks up the
    type-annotated class attributes as fields with the declared defaults.

    Attributes
    ----------
    adapter_version : Literal["v1", "v2"]
        Which provider-aware adapter pipeline to use when assembling
        prompts for this app. Defaults to ``"v2"`` (the structured
        reception pipeline landed in W8 of the parent plan). Set to
        ``"v1"`` only when an app needs the legacy flat-string adapter.
    exemplar_task_class : str | None
        The app's primary ``task_class`` for exemplar eligibility lookup.
        When set, must match an entry in
        ``config/prompt_governance/exemplar_eligibility.yaml`` or the CI
        gate ``check_exemplar_coverage`` will fail. Nullable: apps that
        do not opt into E0 leave this unset.
    """

    adapter_version: AdapterVersion = "v2"
    exemplar_task_class: str | None = None


__all__ = ["AdapterVersion", "PromptReceptionSpec"]
