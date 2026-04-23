"""Tests for the shared PromptReceptionSpec mixin (phase RH5B.1).

Plan: prompt-reception-followups-a7b3c4.
"""

from __future__ import annotations

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


def test_mixin_default_adapter_version_is_v2() -> None:
    assert PromptReceptionSpec.adapter_version == "v2"


def test_mixin_default_exemplar_task_class_is_none() -> None:
    assert PromptReceptionSpec.exemplar_task_class is None


def test_research_spec_inherits_reception_fields() -> None:
    from apps_research.config.agent_spec_config import ResearchAgentSpecs

    specs = ResearchAgentSpecs()
    assert specs.adapter_version == "v2"
    assert specs.exemplar_task_class is None
    # Override via constructor
    overridden = ResearchAgentSpecs(
        adapter_version="v1", exemplar_task_class="research_brief"
    )
    assert overridden.adapter_version == "v1"
    assert overridden.exemplar_task_class == "research_brief"


def test_eval_spec_inherits_reception_fields() -> None:
    from apps_eval.config.agent_spec_config import EvalAgentSpecs

    specs = EvalAgentSpecs()
    assert specs.adapter_version == "v2"
    assert specs.exemplar_task_class is None


def test_exec_spec_inherits_reception_fields() -> None:
    from apps_exec.config.agent_spec_config import ExecAgentSpecs

    specs = ExecAgentSpecs()
    assert specs.adapter_version == "v2"
    assert specs.exemplar_task_class is None


def test_rfp_spec_inherits_reception_fields() -> None:
    from apps_rfp.config.agent_spec_config import RfpAgentSpecs

    specs = RfpAgentSpecs()
    assert specs.adapter_version == "v2"
    assert specs.exemplar_task_class is None


def test_rg_spec_inherits_reception_fields() -> None:
    from apps_rg.config.agent_spec_config import RGAgentSpecs

    specs = RGAgentSpecs()
    assert specs.adapter_version == "v2"
    assert specs.exemplar_task_class is None


def test_adapter_version_rejects_invalid_value() -> None:
    """Literal['v1','v2'] is enforced by Pydantic at validation time."""
    import pytest
    from pydantic import ValidationError

    from apps_research.config.agent_spec_config import ResearchAgentSpecs

    with pytest.raises(ValidationError):
        ResearchAgentSpecs(adapter_version="v3")  # type: ignore[arg-type]
