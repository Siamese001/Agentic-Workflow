from __future__ import annotations

from pydantic import BaseModel

from meta.schema_validation import validate_schema_version
from models import (
    StrategyPlan,
    StrategyResult,
    DraftingPlan,
    DraftingResult,
    QAPlan,
    QAResult,
    SafetyPlan,
    SafetyResult,
    WorkflowPlanBundle,
    RAGPlan,
    RAGResult,
    L2ResultBundle,
)


def test_core_models_have_v1_schema_version_defaults():
    # Simple models with safe defaults can be instantiated without args.
    simple_plans = [StrategyPlan, DraftingPlan, QAPlan, SafetyPlan, RAGPlan]
    for cls in simple_plans:
        obj = cls()  # type: ignore[call-arg]
        assert getattr(obj, "schema_version", "v1") == "v1"

    # Results require required list fields.
    strategy_res = StrategyResult(branches=[])
    assert strategy_res.schema_version == "v1"
    drafting_res = DraftingResult(sections=[])
    assert drafting_res.schema_version == "v1"
    qa_res = QAResult(findings=[])
    assert qa_res.schema_version == "v1"
    safety_res = SafetyResult(findings=[])
    assert safety_res.schema_version == "v1"
    rag_res = RAGResult(evidence=[], used_hyde=False)
    assert rag_res.schema_version == "v1"

    # WorkflowPlanBundle and L2ResultBundle require explicit nested models.
    bundle = WorkflowPlanBundle(
        strategy=StrategyPlan(),
        rag=RAGPlan(),
        drafting=DraftingPlan(),
        qa=QAPlan(),
        safety=SafetyPlan(),
    )
    assert bundle.schema_version == "v1"

    l2_result = L2ResultBundle(
        strategy=StrategyResult(branches=[]),
        rag=RAGResult(evidence=[], used_hyde=False),
        drafting=DraftingResult(sections=[]),
        qa=QAResult(findings=[]),
        safety=SafetyResult(findings=[]),
    )
    assert l2_result.schema_version == "v1"


def test_validate_schema_version_accepts_matching_models():
    bundle = WorkflowPlanBundle(
        strategy=StrategyPlan(),
        rag=RAGPlan(),
        drafting=DraftingPlan(),
        qa=QAPlan(),
        safety=SafetyPlan(),
    )

    # Should not raise for matching version.
    validate_schema_version(bundle, model_type=WorkflowPlanBundle)


def test_validate_schema_version_rejects_mismatched_version():
    class DummyModel(BaseModel):
        schema_version: str = "v2"  # wrong version

    m = DummyModel()
    try:
        validate_schema_version(m)
    except ValueError as exc:
        assert "Unexpected schema_version" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("validate_schema_version did not reject mismatched version")
