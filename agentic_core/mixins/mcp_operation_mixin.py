"""
MCPOperationMixin - Unified MCP Access for Agents

[PHASE 3 MIGRATION] Provides single interface to all MCP operations.
[MIXIN REFACTOR] Merged hardened call logic (retry, backoff, audit, idempotency)
from mcp_hardened_mixin.py. That file is now a backwards-compat shim.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class MCPOperationMixin:
    """
    Mixin providing unified MCP gateway access with hardened call semantics.

    Features:
    - Lazy-loaded MCP gateway singleton
    - Exponential backoff with jitter on retries
    - Idempotency keys to prevent double-writes
    - Structured audit log (bounded ring buffer)

    Usage:
        class MyAgent(MCPOperationMixin, SovereignBaseAgent):
            async def process(self):
                result = await self.mcp_llm_route("prompt")
    """

    _mcp_gateway = None
    _mcp_audit_log: list[dict[str, Any]] | None = None
    _MCP_AUDIT_LOG_MAX = 100

    @property
    def mcp_gateway(self):
        """Lazy-load MCP gateway singleton."""
        if self._mcp_gateway is None:
            from agentic_core.L2_execution.enforcement.SovereignMCPGateway import get_mcp_gateway

            self._mcp_gateway = get_mcp_gateway()
        return self._mcp_gateway

    @property
    def mcp_audit_log(self) -> list[dict[str, Any]]:
        """Bounded ring-buffer audit log for MCP calls."""
        if self._mcp_audit_log is None:
            self._mcp_audit_log = []
        return self._mcp_audit_log

    # ── Hardened call layer ──────────────────────────────────────────

    async def safe_mcp_call(
        self,
        tool_name: str,
        args: dict,
        *,
        retry_count: int = 3,
        base_delay: float = 0.5,
        idempotency_key: str | None = None,
    ) -> Any:
        """Execute an MCP tool call with retry, backoff, idempotency, and audit.

        Args:
            tool_name: MCP tool identifier.
            args: Arguments to pass to the tool.
            retry_count: Max attempts before raising.
            base_delay: Base delay in seconds (doubles each retry + jitter).
            idempotency_key: Optional key to prevent duplicate writes.
                             Auto-generated from tool_name + args hash if None.
        """
        if idempotency_key is None:
            idempotency_key = self._generate_idempotency_key(tool_name, args)

        audit_context_id = str(uuid.uuid4())
        last_exception: Exception | None = None

        for attempt in range(retry_count):
            start = time.monotonic()
            try:
                result = await self.mcp_gateway.call_tool(
                    tool_name,
                    args,
                    idempotency_key=idempotency_key,
                )
                duration_ms = (time.monotonic() - start) * 1000
                self._audit_mcp(tool_name, "SUCCESS", duration_ms, audit_context_id, attempt)
                return result
            except Exception as e:
                duration_ms = (time.monotonic() - start) * 1000
                last_exception = e
                self._audit_mcp(tool_name, "RETRY", duration_ms, audit_context_id, attempt)
                logger.warning(
                    "MCP call %s failed (attempt %d/%d): %s",
                    tool_name, attempt + 1, retry_count, e,
                )
                if attempt < retry_count - 1:
                    delay = base_delay * (2 ** attempt) + (time.monotonic() % 0.1)
                    await asyncio.sleep(delay)

        self._audit_mcp(tool_name, "FAILED", 0, audit_context_id, retry_count)
        raise RuntimeError(
            f"MCP call '{tool_name}' failed after {retry_count} attempts"
        ) from last_exception

    # ── Gateway convenience methods ──────────────────────────────────

    async def mcp_llm_route(self, prompt: str, **kwargs) -> dict:
        """Route LLM request through MCP gateway."""
        return await self.mcp_gateway.llm_route(prompt, **kwargs)

    async def mcp_kg_query(self, query: str, **kwargs) -> dict:
        """Query knowledge graph through MCP gateway."""
        return await self.mcp_gateway.kg_query(query, **kwargs)

    async def mcp_archive_op(self, operation: str, **kwargs) -> dict:
        """Execute archive operation through MCP gateway."""
        return await self.mcp_gateway.archive_operation(operation, **kwargs)

    # ── Internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _generate_idempotency_key(tool_name: str, args: dict) -> str:
        """Deterministic idempotency key from tool + args."""
        raw = f"{tool_name}:{sorted(args.items())}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _audit_mcp(
        self,
        tool: str,
        status: str,
        duration_ms: float,
        audit_context_id: str,
        attempt: int,
    ) -> None:
        """Append structured audit entry to bounded ring buffer."""
        entry = {
            "tool": tool,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "audit_context_id": audit_context_id,
            "attempt": attempt,
            "ts": time.time(),
        }
        log = self.mcp_audit_log
        log.append(entry)
        if len(log) > self._MCP_AUDIT_LOG_MAX:
            log.pop(0)
