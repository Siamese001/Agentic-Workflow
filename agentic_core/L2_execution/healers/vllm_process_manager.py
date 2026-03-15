"""
Qwen Process Manager - vLLM Server Lifecycle Management

Provides isolated process management for vLLM server with proper
startup, shutdown, and health monitoring capabilities.
"""

from __future__ import annotations

import logging
import subprocess
import time

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP, DEFAULT_TIMEOUT
from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "vllm_process_manager", "p0_governance")
_emit_snapshots_state("p0", "vllm_process_manager", "state_snapshot")

logger = logging.getLogger(__name__)


class VLLMProcessManager:
    """Manage isolated vLLM server process."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.start_time: float | None = None
        self.base_url: str = "http://localhost:8000/v1"

    def start_server(self, model_config: dict) -> int:
        """Start vLLM server with specified model configuration."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VLLMProcessManager.start_server")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMProcessManager.start_server".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.process and self.process.poll() is None:
            raise RuntimeError("vLLM server is already running")
        model_id = model_config.get("model_id", "Qwen/Qwen2.5-7B-Instruct")
        cmd = [
            "python",
            "-m",
            "vllm.entrypoints.openai.api_server",
            "--model",
            model_id,
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--trust-remote-code",
            "--max-model-len",
            "8192",
            "--gpu-memory-utilization",
            str(QWEN_GPU_MEM_UTIL),
        ]
        logger.info(f"Starting vLLM server with command: {' '.join(cmd)}")
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.start_time = get_clock().now_epoch()
            time.sleep(DEFAULT_SLEEP)
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"vLLM server failed to start: {stderr}")
            logger.info(f"vLLM server started with PID: {self.process.pid}")
            return self.process.pid
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.error(f"Failed to start vLLM server: {exc}")
            self.process = None
            raise

    def stop_server(self) -> None:
        """Stop vLLM server gracefully."""
        if not self.process:
            logger.info("vLLM server is not running")
            return
        try:
            logger.info(f"Stopping vLLM server PID: {self.process.pid}")
            self.process.terminate()
            try:
                self.process.wait(timeout=DEFAULT_TIMEOUT)
                logger.info("vLLM server stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("vLLM server did not stop gracefully, force killing")
                self.process.kill()
                self.process.wait()
                logger.info("vLLM server force killed")
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.error(f"Error stopping vLLM server: {exc}")
        finally:
            self.process = None
            self.start_time = None

    def health_check(self) -> bool:
        """Check if vLLM server is healthy and responding."""
        if not self.process or self.process.poll() is not None:
            return False
        try:
            import urllib.request as _urllib_request

            with _urllib_request.urlopen(f"{self.base_url}/health", timeout=DEFAULT_TIMEOUT) as _resp:  # noqa: S310
                return _resp.status == 200
        # guardian: allow-silent-swallow
        except Exception:
            return False

    def get_memory_usage(self) -> dict:
        """Get GPU memory usage statistics."""
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                used, total = map(int, result.stdout.strip().split(", "))
                return {"used_mb": used, "total_mb": total, "utilization_percent": used / total * 100}
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return {"used_mb": 0, "total_mb": 0, "utilization_percent": 0.0}

    def get_pid(self) -> int | None:
        """Get vLLM process ID."""
        return self.process.pid if self.process else None

    def is_running(self) -> bool:
        """Check if vLLM process is running."""
        return self.process is not None and self.process.poll() is None

    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        if not self.start_time:
            return 0.0
        return get_clock().now_epoch() - self.start_time


vllm_process_manager = VLLMProcessManager()


def get_model_config(model_size: str = "7B") -> dict:
    """Get model configuration for specified model size."""
    configs = {
        "7B": {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_model_len": 8192,
            "gpu_memory_utilization": QWEN_GPU_MEM_UTIL,
        },
        "14B": {
            "model_id": "Qwen/Qwen2.5-14B-Instruct",
            "max_model_len": 4096,
            "gpu_memory_utilization": QWEN_GPU_MEM_UTIL,
        },
    }
    return configs.get(model_size, configs["7B"])


__all__ = ["VLLMProcessManager", "vllm_process_manager", "get_model_config"]
