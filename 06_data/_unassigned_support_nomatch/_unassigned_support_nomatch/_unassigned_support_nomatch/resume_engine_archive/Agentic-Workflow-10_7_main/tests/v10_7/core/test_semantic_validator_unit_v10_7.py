from core_v10_7 import MetricsCollector, SemanticValidator


def _validator() -> SemanticValidator:
    metrics = MetricsCollector()
    return SemanticValidator(metrics_collector=metrics)


def test_word_count_within_range_passes():
    validator = _validator()
    ok, message = validator.check_word_count("a b c d", min_words=2, max_words=10)
    assert ok is True
    assert "Word count OK" in message


def test_word_count_out_of_range_fails():
    validator = _validator()
    ok, message = validator.check_word_count("one", min_words=2, max_words=5)
    assert ok is False
    assert "FAILED" in message


def test_llm_reported_count_discrepancy_logs_metric():
    metrics = MetricsCollector()
    validator = SemanticValidator(metrics_collector=metrics)
    validator.check_word_count("token token", min_words=1, max_words=10, llm_reported_count=100, workflow_id="wf-123")
    assert any(m["task_name"] == "word_count_discrepancy" for m in metrics.metrics)
