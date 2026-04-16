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


def build_config(source_file: str) -> OTelServerConfig:
    source_path = Path(source_file).resolve()
    repo_root = source_path.parents[2]
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
    )
