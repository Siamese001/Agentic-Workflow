from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OTelServerConfig:
    """Resolved runtime configuration for the OTel MCP server."""

    source_file: Path
    repo_root: Path
    runtime_adg_dir: Path
    cache_max_traces: int
    allow_mock_traces: bool
    server_pid: int
    server_start_time: float
    server_source_mtime: float
    status_store_timeout_seconds: float = 8.0
    status_tracer_timeout_seconds: float = 10.0
    max_spans_per_ingest: int = 1000
    mcp_server_name: str = "otel-mcp"
    tool_transport: str = "stdio"
    metrics_initial_last_updated: int = field(default_factory=lambda: int(time.time()))
    # Anthropic-alignment knobs (ADR-027)
    log_tool_content: bool = False
    span_attr_max_bytes: int = 60_000
    service_name: str = "otel-mcp"
    service_version: str = "unknown"
    deployment_environment: str = "unknown"


def build_config(source_file: str) -> OTelServerConfig:
    source_path = Path(source_file).resolve()
    repo_root = source_path.parents[2]
    # Path-resolution precedence (high to low):
    #   1. OTEL_MCP_RUNTIME_ADG_DIR — explicit operator override. Lets a
    #      single otel_mcp_server.py serve traces from a different repo
    #      than where its source file lives. Required when Windsurf launches
    #      the MCP from one workspace clone but the active Cascade session
    #      writes traces to a sibling clone (precedent: 2026-04-30 apps_rg
    #      trace-visibility blackout — server ran from
    #      C:\Git\Agentic-Workflow while pipeline wrote to
    #      C:\Git\Agentic-Workflow-FRESH).
    #   2. parents[2] of source_file (in-process default). This is correct
    #      for both the MCP server (its source_file is in its own repo) and
    #      the in-process otel_lifecycle_bridge (its source_file is in the
    #      pipeline's repo). Never honor AGENTIC_REPO_ROOT here — Windsurf
    #      may set that to a different clone than the running Python process,
    #      which causes the in-process bridge to write to the wrong store and
    #      fail L4 compliance validation.
    explicit_dir = os.environ.get("OTEL_MCP_RUNTIME_ADG_DIR")
    if explicit_dir:
        runtime_adg_dir = Path(explicit_dir).expanduser().resolve()
    else:
        runtime_adg_dir = repo_root / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    return OTelServerConfig(
        source_file=source_path,
        repo_root=repo_root,
        runtime_adg_dir=runtime_adg_dir,
        cache_max_traces=max(16, int(os.environ.get("OTEL_MCP_MAX_TRACE_CACHE", "256"))),
        allow_mock_traces=os.environ.get("OTEL_MCP_ALLOW_MOCK_TRACES", "0") == "1",
        server_pid=os.getpid(),
        server_start_time=time.time(),
        server_source_mtime=source_path.stat().st_mtime,
        log_tool_content=os.environ.get("OTEL_MCP_LOG_TOOL_CONTENT", "0") == "1",
        span_attr_max_bytes=max(1024, int(os.environ.get("OTEL_MCP_SPAN_ATTR_MAX_BYTES", "60000"))),
        service_name=os.environ.get("OTEL_SERVICE_NAME", "otel-mcp"),
        service_version=os.environ.get("OTEL_SERVICE_VERSION", "unknown"),
        deployment_environment=os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT", "unknown"),
    )
