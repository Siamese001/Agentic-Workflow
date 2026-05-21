"""RgResumeOrchestrator — lightweight local-first Qwen orchestration façade for tests."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.types.local_first_disposition import LocalFirstDisposition

from apps_rg.reasoning.rg_agent_base import RGAgentBase

# Module-level knobs patched by unit tests (``patch("...RgResumeOrchestrator._X")``).
_QWEN_AVAILABLE = True


class RepoSignalService:
    """Placeholder — production wiring hooks repo signals when enabled."""

    def __init__(self, *_a: Any, **_k: Any) -> None:
        pass

    def collect(self) -> RepoSignalService:
        return self

    def as_dict(self) -> dict[str, Any]:
        return {}


class AppsQwenGateway:
    """Placeholder Qwen façade — exercised via test patches."""

    def __init__(self, *_a: Any, **_k: Any) -> None:
        pass


apps_qwen_telemetry = None


@dataclass
class RgResumeOrchestrator(RGAgentBase):
    master_resume: dict[str, Any]
    qwen_enabled: bool = True
    enable_repo_signals: bool = True
    test_mode: bool = False
    _qwen_gateway: Any = field(init=False, default=None)
    _qwen_init_error: str | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._repo_service = (
            RepoSignalService() if self.enable_repo_signals else None
        )
        self._qwen_gateway = None
        self._qwen_init_error = None

        if not self.qwen_enabled or not globals().get("_QWEN_AVAILABLE", True):
            return

        try:
            self._qwen_gateway = AppsQwenGateway(dict(self.master_resume or {}))
        except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            self._qwen_gateway = None
            self._qwen_init_error = str(exc)

    async def generate_resume_with_qwen(self, job_prompt: str) -> dict[str, Any]:
        """Async hook — tests replace with ``AsyncMock``."""
        del job_prompt
        if self._qwen_gateway is None:
            return {}
        return {"success": False, "content": ""}

    def _enterprise_repo_signal_fixture(self, job_prompt: str) -> dict[str, Any]:
        """Deterministic enrichment envelope for scripted enterprise/unit probes."""
        del job_prompt
        return {
            "status": "success",
            "checkpoints": ["HOP-ENRICH"],
            "repo_signals": {
                "adg": {"available": True, "nodes_count": 200_000},
                "tests": {"inventory_available": True, "inventory_entries": 2_500},
                "ci": {"workflow_count": 45},
                "governance": {
                    "denominator_baseline_available": True,
                    "market_fit": {},
                },
            },
        }

    async def _async_execute(self, job_prompt: str) -> dict[str, Any]:
        if self.test_mode:
            return self._enterprise_repo_signal_fixture(job_prompt)

        from agentic_core.L4_state.config.vllm_routing_predicates import (  # noqa: PLC0415
            evaluate,
        )

        routing_ctx = {
            "requires_policy_read": False,
            "iteration_count": 0,
            "max_iterations": 100,
            "invalid_ast": False,
            "jd_text": job_prompt,
        }
        routing_decision = evaluate(routing_ctx)
        pv = getattr(routing_decision.provider, "value", str(routing_decision.provider))
        orchestrator_name = type(self).__name__
        run_id = str(uuid.uuid4())
        pred_hash = getattr(routing_decision, "predicate_evaluation_hash", "") or ""

        if pv == "opus":
            dsp = LocalFirstDisposition.for_skip(
                orchestrator=orchestrator_name,
                run_id=run_id,
                provider_value="OPUS",
                predicate_hash=pred_hash,
                reason_code="predicate_selected_opus",
            )
            return {"status": "success", "local_first_disposition": dsp.as_dict()}

        from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (  # noqa: PLC0415
            VLLMGatewayAdapter,
        )

        adapter = VLLMGatewayAdapter()
        gw = adapter.evaluate(
            prompt=str(job_prompt),
            task_class="resume_generation",
            severity="medium",
        )
        telemetry = gw.telemetry.as_dict()

        if gw.route_to_gemini:
            dsp = LocalFirstDisposition.for_escalate(
                orchestrator=orchestrator_name,
                run_id=run_id,
                predicate_hash=pred_hash,
                telem=telemetry,
            )
            return {"status": "success", "local_first_disposition": dsp.as_dict()}

        # LOCAL routing + adapter allow path
        if self._qwen_init_error:
            raise RuntimeError(
                f"LOCAL_VLLM selected but Qwen init failed: {self._qwen_init_error}"
            )

        if self._qwen_gateway is None:
            dsp = LocalFirstDisposition.for_skip(
                orchestrator=orchestrator_name,
                run_id=run_id,
                provider_value="LOCAL_VLLM",
                predicate_hash=pred_hash,
                reason_code="gateway_not_initialized",
            )
            return {"status": "success", "local_first_disposition": dsp.as_dict()}

        try:
            qwen_result = await self.generate_resume_with_qwen(job_prompt)
            adapter.record_local_success(severity="medium")
            dsp = LocalFirstDisposition.for_allow(
                orchestrator=orchestrator_name,
                run_id=run_id,
                predicate_hash=pred_hash,
                telem=telemetry,
                qwen_result_present=bool(qwen_result),
            )
            return {
                "status": "success",
                "qwen_resume_content": qwen_result,
                "local_first_disposition": dsp.as_dict(),
            }
        except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            adapter.record_local_failure(severity="medium")
            raise

    def run(self, job_prompt: str) -> dict[str, Any]:
        """Synchronous façade around the async inference hop."""
        return asyncio.run(self._async_execute(job_prompt))


__all__ = [
    "AppsQwenGateway",
    "RGAgentBase",
    "RepoSignalService",
    "RgResumeOrchestrator",
    "apps_qwen_telemetry",
]
