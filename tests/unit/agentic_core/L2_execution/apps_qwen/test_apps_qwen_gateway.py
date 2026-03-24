from __future__ import annotations

import asyncio

from agentic_core.L2_execution.apps_qwen.apps_qwen_gateway import (
    AppsQwenGateway,
    AppsQwenRequest,
)


def test_apps_qwen_gateway_health_check() -> None:
    gateway = AppsQwenGateway()
    health = gateway.health_check()

    assert health["status"] == "healthy"
    assert health["model_id"] == "Qwen/Qwen2.5-7B-Instruct"
    assert isinstance(health["gpu_utilization"], float)


def test_apps_qwen_gateway_infer_success() -> None:
    gateway = AppsQwenGateway()
    request = AppsQwenRequest(
        app_name="apps_eval",
        prompt="Review this function for potential bugs.",
    )

    response = asyncio.run(gateway.infer(request))

    assert response.success is True
    assert response.model_used == "Qwen/Qwen2.5-7B-Instruct"
    assert response.response is not None
    assert response.confidence > 0.0
    assert response.latency_ms >= 0.0
