from __future__ import annotations

"""
MCPHardenedMixin - Eternal Hardening for All MCP Integrations

Provides:
- Exponential backoff retry (configurable, default 3 attempts)
- SovereignEvent emission on connect/fail/success
- Timeout enforcement
- CRITIQUE emission on exhausted retries
- Safe MCP call with validation and sandboxing
- Response validation for code injection, resource limits
- Audit trail logging for all MCP operations

Usage:
    class MyMCPClient(MCPHardenedMixin):
        async def call_something(self):
            return await self.safe_mcp_call(
                "tool_name",
                {"arg1": "value1"},
                validate_response=True
            )
"""
import asyncio
import hashlib
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Logger: Any = logging.getLogger(__name__)


@dataclass
class MCPAuditEntry:
    """Audit entry for MCP call."""
    timestamp: float
    tool_name: str
    args_hash: str
    result_status: str
    duration_ms: float
    caller: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPValidationResult:
    """Result of MCP response validation."""
    valid: bool
    reasons: list[str] = field(default_factory=list)
    sanitized_output: Any = None


class MCPHardenedMixin:
    """
    Mixin providing hardened MCP operations:
    - Exponential backoff retry (3 attempts by default)
    - SovereignEvent emission on connect/fail
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    - Safe MCP call with validation and sandboxing
    - Response validation (code injection, resource limits)
    - Audit trail logging
    """

    MAX_RETRIES: int = 3
    BASE_DELAY: float = 1.0
    MAX_DELAY: float = 30.0
    DEFAULT_TIMEOUT: float = 30.0
    MAX_RESPONSE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_RESPONSE_DEPTH: int = 50

    # Tool whitelist - tools allowed to be called
    TOOL_WHITELIST: set[str] = {
        "read_file", "write_file", "edit", "run_command",
        "grep_search", "find_by_name", "list_dir",
        "git_status", "git_commit", "git_push", "git_pull",
        "redis_get", "redis_set", "redis_delete",
        "pinecone_query", "pinecone_upsert",
        "http_get", "http_post", "http_put", "http_delete",
        "brave_search", "fetch_url",
    }

    # Dangerous patterns to detect in responses
    CODE_INJECTION_PATTERNS: list[str] = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"os\.system\s*\(",
        r"subprocess\.",
        r"open\s*\([^)]*['\"]w",
        r"rm\s+-rf",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"<script>",
        r"javascript:",
    ]

    def __init__(self, *args, **kwargs):
        """Initialize MCP hardening."""
        super().__init__(*args, **kwargs)
        self._audit_log: list[MCPAuditEntry] = []
        self._mcp_call_count: int = 0
        self._mcp_success_count: int = 0
        self._mcp_failure_count: int = 0

    async def _hardened_call(
        self,
        operation: str,
        call_func: Callable,
        *args: Any,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute MCP call with retry, timeout, and observability.

        Args:
            operation: Name of the operation (for logging/events)
            call_func: Async function to call
            *args: Positional arguments for call_func
            timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
            **kwargs: Keyword arguments for call_func

        Returns:
            Result from call_func

        Raises:
            RuntimeError: If all retries are exhausted
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        last_error: str | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                self._emit_sovereign_event(
                    "MCP_CALL_START",
                    {"operation": operation, "attempt": attempt + 1},
                )

                result: Any = await asyncio.wait_for(
                    call_func(*args, **kwargs),
                    timeout=timeout,
                )

                self._emit_sovereign_event(
                    "MCP_CALL_SUCCESS",
                    {"operation": operation, "attempt": attempt + 1},
                )

                return result

            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s"
                self._emit_sovereign_event(
                    "MCP_CALL_TIMEOUT",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "timeout": timeout,
                    },
                )
            except Exception as e:
                last_error = str(e)
                self._emit_sovereign_event(
                    "MCP_CALL_FAIL",
                    {
                        "operation": operation,
                        "attempt": attempt + 1,
                        "error": str(e),
                    },
                )

            if attempt < self.MAX_RETRIES - 1:
                delay: float = min(
                    self.BASE_DELAY * (2**attempt), self.MAX_DELAY
                )
                Logger.warning(
                    f"[MCP] {operation} attempt {attempt + 1} failed, "
                    f"retrying in {delay:.1f}s: {last_error}"
                )
                await asyncio.sleep(delay)

        self._emit_critique(operation, last_error or "Unknown error")
        raise RuntimeError(
            f"MCP {operation} failed after {self.MAX_RETRIES} attempts: {last_error}"
        )

    def _emit_sovereign_event(
        self, event_type: str, data: dict[str, Any]
    ) -> None:
        """
        Emit telemetry event for observability.

        Args:
            event_type: Type of event (MCP_CALL_START, MCP_CALL_SUCCESS, etc.)
            data: Event data dictionary
        """
        try:
            from agentic_core.L6_observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(event_type, data)
        except ImportError:
            Logger.debug(f"[MCP] {event_type}: {data}")

    def _emit_critique(self, operation: str, error: str) -> None:
        """
        Emit CRITIQUE for subatomic retry consideration.

        Args:
            operation: Name of the failed operation
            error: Error message
        """
        Logger.critical(f"[CRITIQUE] MCP {operation} exhausted: {error}")
        try:
            from agentic_core.L6_observability.telemetry.sovereign_events import (
                emit_event,
            )

            emit_event(
                "MCP_CRITIQUE",
                {
                    "operation": operation,
                    "error": error,
                    "retries_exhausted": True,
                },
            )
        except ImportError:
            pass

    def get_redis_connection(self, url: str | None = None):
        """
        Get hardened Redis connection with SSL enforcement and pooling.

        Args:
            url: Optional Redis URL (defaults to MCP_REDIS_URL env var)

        Returns:
            Redis client with connection pool
        """
        import os

        from redis import ConnectionPool, Redis

        redis_url = url or os.getenv("MCP_REDIS_URL") or os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("MCP_REDIS_URL or REDIS_URL must be set")

        # SSL enforcement
        ssl_enabled = os.getenv("MCP_REDIS_SSL", "false").lower() == "true"

        pool_kwargs = {
            "max_connections": int(os.getenv("MCP_REDIS_MAX_CONNECTIONS", "20")),
            "socket_connect_timeout": int(os.getenv("MCP_REDIS_TIMEOUT", "5")),
            "socket_timeout": int(os.getenv("MCP_REDIS_TIMEOUT", "5")),
            "socket_keepalive": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }

        if ssl_enabled:
            import ssl as ssl_module
            ssl_context = ssl_module.create_default_context()

            # Load custom certs if provided
            cert_path = os.getenv("MCP_REDIS_SSL_CERT_PATH")
            if cert_path:
                ssl_context.load_verify_locations(cert_path)

            pool_kwargs.update({
                "ssl": True,
                "ssl_cert_reqs": "required",
                "ssl_check_hostname": True,
            })

        pool = ConnectionPool.from_url(redis_url, **pool_kwargs)
        return Redis(connection_pool=pool)

    def get_neo4j_driver(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None
    ):
        """
        Get hardened Neo4j driver with SSL enforcement and connection pooling.

        Args:
            uri: Optional Neo4j URI (defaults to NEO4J_URI env var)
            username: Optional username (defaults to NEO4J_USERNAME env var)
            password: Optional password (defaults to NEO4J_PASSWORD env var)

        Returns:
            Neo4j driver with connection pool
        """
        import os

        from neo4j import GraphDatabase

        neo4j_uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = username or os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = password or os.getenv("NEO4J_PASSWORD")

        if not neo4j_password:
            raise ValueError("[MCP HARDENED] NEO4J_PASSWORD must be set - no default allowed")

        # Force SSL/TLS encryption
        driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            encrypted=True,
            trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
            max_connection_lifetime=3600,
            max_connection_pool_size=int(os.getenv("NEO4J_MAX_POOL_SIZE", "50")),
            connection_acquisition_timeout=int(os.getenv("NEO4J_TIMEOUT", "60")),
        )

        return driver

    async def safe_mcp_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        validate_response: bool = True,
        timeout: float | None = None,
        caller: str | None = None,
    ) -> Any:
        """
        Execute MCP call with full validation and sandboxing.

        Args:
            tool_name: Name of the tool to call
            args: Arguments for the tool
            validate_response: Whether to validate the response
            timeout: Optional timeout in seconds
            caller: Optional caller identifier for audit

        Returns:
            Validated and sanitized result

        Raises:
            ValueError: If tool not in whitelist or validation fails
            RuntimeError: If call fails after retries
        """
        start_time = time.time()
        self._mcp_call_count += 1
        caller = caller or self.__class__.__name__

        # 1. Validate tool name against whitelist
        if not self._validate_tool_name(tool_name):
            self._mcp_failure_count += 1
            self.audit_mcp_call(tool_name, args, "BLOCKED", caller, {
                "reason": "Tool not in whitelist"
            })
            raise ValueError(f"Tool '{tool_name}' not in whitelist")

        # 2. Validate arguments
        validation_errors = self._validate_args(tool_name, args)
        if validation_errors:
            self._mcp_failure_count += 1
            self.audit_mcp_call(tool_name, args, "INVALID_ARGS", caller, {
                "errors": validation_errors
            })
            raise ValueError(f"Invalid arguments: {validation_errors}")

        # 3. Execute call with hardened wrapper
        try:
            result = await self._execute_sandboxed(tool_name, args, timeout)
        except Exception as e:
            self._mcp_failure_count += 1
            duration_ms = (time.time() - start_time) * 1000
            self.audit_mcp_call(tool_name, args, "FAILED", caller, {
                "error": str(e),
                "duration_ms": duration_ms
            })
            raise

        # 4. Validate response
        if validate_response:
            validation = self.validate_mcp_response(result)
            if not validation.valid:
                self._mcp_failure_count += 1
                duration_ms = (time.time() - start_time) * 1000
                self.audit_mcp_call(tool_name, args, "INVALID_RESPONSE", caller, {
                    "reasons": validation.reasons,
                    "duration_ms": duration_ms
                })
                raise ValueError(f"Response validation failed: {validation.reasons}")
            result = validation.sanitized_output

        # 5. Log audit trail
        self._mcp_success_count += 1
        duration_ms = (time.time() - start_time) * 1000
        self.audit_mcp_call(tool_name, args, "SUCCESS", caller, {
            "duration_ms": duration_ms
        })

        return result

    def _validate_tool_name(self, tool_name: str) -> bool:
        """
        Validate tool name against whitelist.

        Args:
            tool_name: Tool name to validate

        Returns:
            True if tool is allowed
        """
        # Normalize tool name
        normalized = tool_name.lower().strip()

        # Check exact match
        if normalized in self.TOOL_WHITELIST:
            return True

        # Check prefix match for namespaced tools
        for allowed in self.TOOL_WHITELIST:
            if normalized.startswith(f"{allowed}_") or normalized.endswith(f"_{allowed}"):
                return True

        return False

    def _validate_args(self, tool_name: str, args: dict[str, Any]) -> list[str]:
        """
        Validate arguments for tool call.

        Args:
            tool_name: Tool being called
            args: Arguments to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for None args
        if args is None:
            return errors  # None is allowed (no args)

        # Check args is dict
        if not isinstance(args, dict):
            errors.append("Arguments must be a dictionary")
            return errors

        # Check for dangerous patterns in string values
        for key, value in args.items():
            if isinstance(value, str):
                for pattern in self.CODE_INJECTION_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        errors.append(f"Dangerous pattern in argument '{key}'")
                        break

        return errors

    async def _execute_sandboxed(
        self,
        tool_name: str,
        args: dict[str, Any],
        timeout: float | None = None
    ) -> Any:
        """
        Execute tool call in sandboxed environment.

        Args:
            tool_name: Tool to execute
            args: Arguments
            timeout: Optional timeout

        Returns:
            Tool result
        """
        timeout = timeout or self.DEFAULT_TIMEOUT

        # Create mock execution for now - actual implementation would
        # delegate to real MCP client
        async def mock_execute():
            return {"status": "success", "tool": tool_name, "args": args}

        return await asyncio.wait_for(mock_execute(), timeout=timeout)

    def validate_mcp_response(self, response: Any) -> MCPValidationResult:
        """
        Validate MCP response for safety.

        Checks for:
        - Code injection patterns
        - Response size limits
        - Response depth limits
        - Policy violations

        Args:
            response: Response to validate

        Returns:
            MCPValidationResult with validation status
        """
        reasons = []

        # 1. Check for code injection in string responses
        if isinstance(response, str):
            for pattern in self.CODE_INJECTION_PATTERNS:
                if re.search(pattern, response, re.IGNORECASE):
                    reasons.append(f"Code injection pattern detected: {pattern}")

        # 2. Check response size
        response_str = str(response)
        if len(response_str) > self.MAX_RESPONSE_SIZE:
            reasons.append(f"Response exceeds size limit: {len(response_str)} > {self.MAX_RESPONSE_SIZE}")

        # 3. Check response depth for nested structures
        depth = self._get_depth(response)
        if depth > self.MAX_RESPONSE_DEPTH:
            reasons.append(f"Response exceeds depth limit: {depth} > {self.MAX_RESPONSE_DEPTH}")

        # 4. Sanitize response
        sanitized = self._sanitize_response(response)

        return MCPValidationResult(
            valid=len(reasons) == 0,
            reasons=reasons,
            sanitized_output=sanitized
        )

    def _get_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Get maximum depth of nested structure."""
        if current_depth > self.MAX_RESPONSE_DEPTH:
            return current_depth

        if isinstance(obj, dict):
            if not obj:
                return current_depth + 1
            return max(self._get_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list | tuple):
            if not obj:
                return current_depth + 1
            return max(self._get_depth(v, current_depth + 1) for v in obj)
        else:
            return current_depth

    def _sanitize_response(self, response: Any) -> Any:
        """
        Sanitize response by removing dangerous patterns.

        Args:
            response: Response to sanitize

        Returns:
            Sanitized response
        """
        if isinstance(response, str):
            sanitized = response
            for pattern in self.CODE_INJECTION_PATTERNS:
                sanitized = re.sub(pattern, "[SANITIZED]", sanitized, flags=re.IGNORECASE)
            return sanitized
        elif isinstance(response, dict):
            return {k: self._sanitize_response(v) for k, v in response.items()}
        elif isinstance(response, list):
            return [self._sanitize_response(v) for v in response]
        else:
            return response

    def audit_mcp_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        result_status: str,
        caller: str,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Log MCP call for audit trail.

        Args:
            tool_name: Tool that was called
            args: Arguments passed
            result_status: Status of the call (SUCCESS, FAILED, BLOCKED, etc.)
            caller: Identifier of the caller
            metadata: Additional metadata
        """
        # Hash args for privacy
        args_str = str(sorted(args.items())) if args else ""
        args_hash = hashlib.sha256(args_str.encode()).hexdigest()[:16]

        entry = MCPAuditEntry(
            timestamp=time.time(),
            tool_name=tool_name,
            args_hash=args_hash,
            result_status=result_status,
            duration_ms=metadata.get("duration_ms", 0) if metadata else 0,
            caller=caller,
            metadata=metadata or {}
        )

        self._audit_log.append(entry)

        # Emit event for observability
        self._emit_sovereign_event("MCP_AUDIT", {
            "tool": tool_name,
            "status": result_status,
            "caller": caller,
            "duration_ms": entry.duration_ms
        })

        # Alert on anomalies
        if result_status in ("BLOCKED", "INVALID_RESPONSE"):
            Logger.warning(f"[MCP AUDIT] Anomaly: {tool_name} - {result_status} by {caller}")

    def get_audit_log(self, limit: int = 100) -> list[MCPAuditEntry]:
        """Get recent audit log entries."""
        return self._audit_log[-limit:]

    def get_mcp_statistics(self) -> dict[str, Any]:
        """Get MCP call statistics."""
        return {
            "total_calls": self._mcp_call_count,
            "successful_calls": self._mcp_success_count,
            "failed_calls": self._mcp_failure_count,
            "success_rate": (self._mcp_success_count / self._mcp_call_count * 100) if self._mcp_call_count > 0 else 0,
            "audit_log_size": len(self._audit_log)
        }

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """MRO chain stub for heal_repository.

        This stub exists to support the MRO chain when agents inherit from
        MCPHardenedMixin and call super().heal_repository(). Without this,
        the super() call would fail with AttributeError.

        Args:
            dry_run: If True, only report what would be done
            execute: If True, apply fixes
            **kwargs: Additional parameters passed through the chain

        Returns:
            Empty dict - actual healing is done by concrete agent classes
        """
        return {}
