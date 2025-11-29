import inspect
from agentic_core.l2_execution.lic_k2_insights import LIC_K2_Insights

def test_class_exists():
    assert inspect.isclass(LIC_K2_Insights)

def test_required_methods():
    required = [
        "execute",
        "score_individual_claim",
        "calculate_aggregate_confidence",
        "validate_confidence_thresholds",
        "extract_key_insights",
    ]
    for m in required:
        assert hasattr(LIC_K2_Insights, m)
