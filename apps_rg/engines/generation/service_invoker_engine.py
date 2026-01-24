"""
Service Invoker Engine - Hardened Executor for LLM Service Invocation
Refactored from InvokeGenerationService.py
Following Batch 3 specifications
"""

from __future__ import annotations
from typing import Any
import time
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ServiceInvokerEngine(BaseRGEngine):
    """
    Hardened Executor for LLM Service Invocation.
    Ports legacy InvokeGenerationService.py logic into Sovereign Architecture.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SERVICE.INVOKER")
        # self.timeout from config lookup

    async def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a remote generation action with telemetry.
        """
        start_time = time.time()
        self._mcp_audit("service_invoke_start", {"action": action})

        try:
            # Logic ported from InvokeGenerationService.py
            # but using BaseRGEngine.call_llm for unified tracking
            prompt = params.get("prompt")
            if not prompt:
                raise ValueError("Missing prompt for service invocation")

            response = await self.call_llm(prompt)

            duration_ms = (time.time() - start_time) * 1000

            if not response:
                self.record_fail(f"Service {action} returned empty response")
                return {"success": False, "error": "Empty response"}

            self.record_pass(f"Service {action} completed", data={"duration_ms": duration_ms})

            return {"success": True, "output": response, "duration_ms": duration_ms}

        except Exception as e:
            Logger.error(f"Service Invocation Failure: {e}")
            self.record_fail(
                str(e), signal="SERVICE_TIMEOUT" if "timeout" in str(e).lower() else None
            )
            return {"success": False, "error": str(e)}
