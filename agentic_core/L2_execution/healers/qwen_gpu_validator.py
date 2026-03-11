"""
Qwen GPU Validation - Fail-Fast GPU Capability Checking

Provides hard validation of GPU capabilities before model loading.
Ensures Qwen models only run on compatible hardware.
"""

from __future__ import annotations

import logging
import subprocess
from typing import Literal

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class QwenGPUCapabilityError(RuntimeError):
    """Raised when GPU capabilities are insufficient for Qwen model."""

    def __init__(self, requirement: str, current: str, model: str):
        self.requirement = requirement
        self.current = current
        self.model = model
        super().__init__(f"QwenGPUCapabilityError: {model} requires {requirement}, but system has {current}")


def get_gpu_memory_gb() -> float:
    """Get available GPU memory in GB."""
    try:
        # Use nvidia-smi to get GPU memory - guardian: allow-magic-configuration
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,  # guardian: allow-magic-configuration
        )
        if result.returncode == 0:
            memory_mb = float(result.stdout.strip())
            return memory_mb / 1024  # Convert to GB
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: assume insufficient memory
    return 0.0


def get_cuda_version() -> str:
    """Get CUDA version from nvcc or nvidia-smi."""
    try:
        # Try nvcc first
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "release" in line.lower():
                    # Extract version from "release 11.8, V11.8.89"
                    import re

                    match = re.search(r"release (\d+\.\d+)", line)
                    if match:
                        return match.group(1)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Fallback to nvidia-smi
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.returncode == 0:
            # Extract CUDA version from nvidia-smi output
            import re

            match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
            if match:
                return match.group(1)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


def get_compute_capability() -> float:
    """Get GPU compute capability."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            cap_str = result.stdout.strip()
            # Convert "8.6" to 8.6
            return float(cap_str)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    return 0.0


def get_nvidia_driver_version() -> str:
    """Get NVIDIA driver version."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


def version_parse(version: str) -> tuple[int, ...]:
    """Parse version string into comparable tuple."""
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return (0, 0)


def validate_qwen_gpu_capabilities(model_size: Literal["7B", "14B"]) -> None:
    """Hard fail on GPU capability mismatch BEFORE model load."""
    logger.info(f"Validating GPU capabilities for Qwen2.5-{model_size}")

    # 1. VRAM threshold validation
    required_vram = {"7B": 16, "14B": 32}[model_size]
    available_vram = get_gpu_memory_gb()
    if available_vram < required_vram:
        raise QwenGPUCapabilityError(
            f"VRAM >= {required_vram}GB", f"{available_vram:.1f}GB", f"Qwen2.5-{model_size}"
        )

    # 2. CUDA version validation
    min_cuda = "11.8" if model_size == "7B" else "12.0"
    current_cuda = get_cuda_version()
    if current_cuda == "unknown" or version_parse(current_cuda) < version_parse(min_cuda):
        raise QwenGPUCapabilityError(f"CUDA >= {min_cuda}", current_cuda, f"Qwen2.5-{model_size}")

    # 3. Compute capability validation
    min_compute = 7.0
    current_compute = get_compute_capability()
    if current_compute < min_compute:
        raise QwenGPUCapabilityError(
            f"Compute >= {min_compute}", str(current_compute), f"Qwen2.5-{model_size}"
        )

    # 4. Driver version validation
    min_driver = "525.60.13"
    current_driver = get_nvidia_driver_version()
    if current_driver == "unknown" or version_parse(current_driver) < version_parse(min_driver):
        raise QwenGPUCapabilityError(f"Driver >= {min_driver}", current_driver, f"Qwen2.5-{model_size}")

    logger.info(f"GPU validation passed for Qwen2.5-{model_size}")


def start_qwen_server_safely(model_size: Literal["7B", "14B"]) -> None:
    """Enforce validation order: validate BEFORE start."""
    validate_qwen_gpu_capabilities(model_size)  # Fail fast
    # TODO: Implement start_vllm_server() call
    logger.info(f"Starting vLLM server for Qwen2.5-{model_size}")


__all__ = [
    "QwenGPUCapabilityError",
    "validate_qwen_gpu_capabilities",
    "start_qwen_server_safely",
    "get_gpu_memory_gb",
    "get_cuda_version",
    "get_compute_capability",
    "get_nvidia_driver_version",
]
