from __future__ import annotations

from agentic_core.L2_execution.apps_qwen.apps_qwen_telemetry import AppsQwenTelemetry


def test_apps_qwen_telemetry_session_happy_path() -> None:
    telemetry = AppsQwenTelemetry()

    session_id = telemetry.start_session("apps_eval")
    telemetry.record_request_start(session_id, "apps_eval", "Qwen/Qwen2.5-7B-Instruct")
    telemetry.record_request_success(
        session_id=session_id,
        app_name="apps_eval",
        model_id="Qwen/Qwen2.5-7B-Instruct",
        latency_ms=125.0,
        confidence=0.82,
        tokens_used=42,
    )

    telemetry.end_session(session_id)
    summary = telemetry.get_session_summary(session_id)

    assert summary is not None
    assert summary["total_requests"] == 1
    assert summary["success_rate"] == 1.0
    assert summary["average_latency_ms"] == 125.0
    assert summary["total_tokens"] == 42
