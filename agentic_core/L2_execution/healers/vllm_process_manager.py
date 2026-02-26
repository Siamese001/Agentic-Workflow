"""
Qwen Process Manager - vLLM Server Lifecycle Management

Provides isolated process management for vLLM server with proper
startup, shutdown, and health monitoring capabilities.
"""

from __future__ import annotations

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class VLLMProcessManager:
    """Manage isolated vLLM server process."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.start_time: float | None = None
        self.base_url: str = "http://localhost:8000/v1"

    def start_server(self, model_config: dict) -> int:
        """Start vLLM server with specified model configuration."""
        if self.process and self.process.poll() is None:
            raise RuntimeError("vLLM server is already running")

        model_id = model_config.get("model_id", "Qwen/Qwen2.5-7B-Instruct")

        # Build vLLM command
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
            "0.85",
        ]

        logger.info(f"Starting vLLM server with command: {' '.join(cmd)}")

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.start_time = time.time()

            # Wait a moment for startup
            time.sleep(5)

            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"vLLM server failed to start: {stderr}")

            logger.info(f"vLLM server started with PID: {self.process.pid}")
            return self.process.pid

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

            # Try graceful shutdown first
            self.process.terminate()

            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=10)
                logger.info("vLLM server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                logger.warning("vLLM server did not stop gracefully, force killing")
                self.process.kill()
                self.process.wait()
                logger.info("vLLM server force killed")

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
            import requests

            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
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
                timeout=10,
            )
            if result.returncode == 0:
                used, total = map(int, result.stdout.strip().split(", "))
                return {"used_mb": used, "total_mb": total, "utilization_percent": (used / total) * 100}
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
        return time.time() - self.start_time


# Global process manager instance
vllm_process_manager = VLLMProcessManager()


def get_model_config(model_size: str = "7B") -> dict:
    """Get model configuration for specified model size."""
    configs = {
        "7B": {"model_id": "Qwen/Qwen2.5-7B-Instruct", "max_model_len": 8192, "gpu_memory_utilization": 0.85},
        "14B": {
            "model_id": "Qwen/Qwen2.5-14B-Instruct",
            "max_model_len": 4096,
            "gpu_memory_utilization": 0.85,
        },
    }

    return configs.get(model_size, configs["7B"])


__all__ = [
    "VLLMProcessManager",
    "vllm_process_manager",
    "get_model_config",
]
