"""CPU Optimization Module for AMD Processors — Workload-Aware Implementation.

Maximizes CPU utilization safely through:
- Workload-class worker policies (not one-size-fits-all)
- Temperature guardrails for AMD 9950X3D (95°C max, 90°C sustained threshold)
- ProcessPoolExecutor for GIL-bound Python tasks
- CPU affinity tuning for AMD architectures
- Parallel file processing with batch sizing

Optimized for AMD Ryzen 9 9950X3D (16-core / 32-thread Zen 5 with 3D V-Cache).
Safe baseline: 16 workers for pure Python, 24 for pytest, 20 for native compute.
"""

from __future__ import annotations

import concurrent.futures
import enum
import logging
import multiprocessing as mp
import os
import platform
import time
from dataclasses import dataclass, replace
from typing import Any, Callable, Iterator, TypeVar

import psutil

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Safety guardrails for AMD 9950X3D
MAX_OPERATING_TEMP_C = 95  # AMD official spec
SUSTAINED_TEMP_THRESHOLD_C = 90  # Stop benchmark if sustained above this
INTERACTIVE_THREAD_RESERVE = 4  # Reserve for OS, browser, background tools
BATCH_THREAD_RESERVE = 2  # Minimal reserve for batch mode


class WorkloadClass(enum.Enum):
    """Workload classification for worker policy selection.

    Each class maps to an executor model and safe worker bands based on:
    - GIL behavior (CPython threads don't parallelize CPU-bound bytecode)
    - Memory sharing requirements
    - Fixture/setup overhead characteristics
    """
    PYTHON_CPU = "python_cpu"  # Pure Python compute (GIL-bound) -> processes
    NATIVE_CPU = "native_cpu"  # NumPy, pandas, etc. (releases GIL) -> threads or processes
    PYTEST_MIXED = "pytest_mixed"  # General pytest suite -> xdist processes
    PYTEST_FIXTURE_HEAVY = "pytest_fixture_heavy"  # Expensive fixtures -> loadscope
    NETWORK_IO = "network_io"  # API calls, embedding services -> async/threadpool
    DISK_IO = "disk_io"  # File processing -> threadpool


class OperatingProfile(enum.Enum):
    """Operating profile for machine resource allocation.

    INTERACTIVE: Desktop in use — reserve threads for responsiveness
    BATCH: Dedicated execution window — use full recommended defaults
    """
    INTERACTIVE = "interactive"
    BATCH = "batch"


# Worker band configuration for AMD 9950X3D
# Format: (safe_start, default_target, test_ceiling)
WORKLOAD_BANDS: dict[WorkloadClass, tuple[int, int, int]] = {
    # Pure Python: processes only, 16 is the safe sweet spot (reserves 16 threads for system)
    WorkloadClass.PYTHON_CPU: (14, 16, 16),
    # Native code: can use threads, higher ceiling due to GIL release
    WorkloadClass.NATIVE_CPU: (16, 20, 32),
    # Pytest mixed: good xdist scaling with worksteal
    WorkloadClass.PYTEST_MIXED: (20, 24, 28),
    # Fixture-heavy: lower count to avoid fixture duplication overhead
    WorkloadClass.PYTEST_FIXTURE_HEAVY: (16, 18, 24),
    # Network I/O: concurrency limited by connection pools, not cores
    WorkloadClass.NETWORK_IO: (16, 16, 32),
    # Disk I/O: diminishing returns after 16-20 threads
    WorkloadClass.DISK_IO: (12, 16, 24),
}


@dataclass(frozen=True)
class CPUConfig:
    """CPU optimization configuration."""
    max_workers: int | None = None  # None = auto-detect from workload class
    chunk_size: int = 100
    use_processes: bool | None = None  # None = auto-detect
    cpu_affinity: bool = True
    batch_size: int = 1000
    workload_class: WorkloadClass = WorkloadClass.PYTHON_CPU
    profile: OperatingProfile = OperatingProfile.BATCH
    # Safety guardrails
    enable_temp_guardrail: bool = True
    temp_check_interval_s: float = 5.0


@dataclass(frozen=True)
class WorkerRecommendation:
    """Complete worker recommendation for a workload."""
    workers: int
    use_processes: bool
    pytest_dist: str | None  # --dist value for pytest-xdist, None if not pytest
    pytest_loadscope: bool  # Whether to use --dist=loadscope
    reserved_threads: int
    workload_class: WorkloadClass
    profile: OperatingProfile


class AMD9950X3DOptimizer:
    """AMD Ryzen 9 9950X3D workload-aware optimizer.

    Safety-first approach:
    - Stock settings only (no PBO, manual OC, undervolt during baseline)
    - Temperature guardrails (90°C sustained threshold, 95°C hard ceiling)
    - Workload-class worker bands (not blind 32 workers everywhere)
    - Reserve threads for system responsiveness in interactive mode

    9950X3D Architecture Notes:
    - 16 cores / 32 threads (Zen 5)
    - Dual CCD with 3D V-Cache
    - CPython GIL prevents thread-level parallelism for pure Python
    - Native libraries (NumPy, etc.) can release GIL and scale higher
    """

    def __init__(self, config: CPUConfig | None = None):
        self.config = config or CPUConfig()
        self._executor: concurrent.futures.Executor | None = None
        self._cpu_count = psutil.cpu_count(logical=True) or 32
        self._physical_cores = psutil.cpu_count(logical=False) or 16
        self._is_amd = self._detect_amd()
        self._is_windows = platform.system().lower() == "windows"
        self._last_temp_check: float = 0.0
        self._temp_check_result: float = 0.0

        # Auto-configure use_processes based on workload class and platform
        if self.config.use_processes is None:
            use_procs = self._should_use_processes(self.config.workload_class)
            self.config = replace(self.config, use_processes=use_procs)
            logger.info(
                f"Auto-configured: workload={self.config.workload_class.value}, "
                f"use_processes={use_procs}"
            )

    def _detect_amd(self) -> bool:
        """Detect if running on AMD processor."""
        try:
            processor = platform.processor()
            return "AMD" in processor.upper()
        except Exception:
            return False

    def _should_use_processes(self, workload_class: WorkloadClass) -> bool:
        """Determine if workload should use processes vs threads.

        Key insight: CPython threads don't parallelize CPU-bound Python code
        due to GIL. Use processes for pure Python, threads for I/O or native.
        """
        process_workloads = {
            WorkloadClass.PYTHON_CPU,
            WorkloadClass.PYTEST_MIXED,
            WorkloadClass.PYTEST_FIXTURE_HEAVY,
        }
        return workload_class in process_workloads

    def get_recommendation(
        self,
        workload_class: WorkloadClass | None = None,
        profile: OperatingProfile | None = None,
    ) -> WorkerRecommendation:
        """Get complete worker recommendation for workload and profile.

        Args:
            workload_class: Override default workload class
            profile: Override default operating profile

        Returns:
            WorkerRecommendation with workers, executor type, pytest settings
        """
        wl = workload_class or self.config.workload_class
        prof = profile or self.config.profile

        safe_start, default_target, _ = WORKLOAD_BANDS.get(wl, (14, 16, 16))

        # Apply profile-based thread reservation
        if prof == OperatingProfile.INTERACTIVE:
            reserved = INTERACTIVE_THREAD_RESERVE
        else:
            reserved = BATCH_THREAD_RESERVE

        # Cap workers to available threads minus reserve
        available = max(1, self._cpu_count - reserved)
        workers = min(default_target, available)

        # Ensure we don't go below safe start unless necessary
        workers = max(min(workers, default_target), min(safe_start, available))

        use_processes = self._should_use_processes(wl)

        # Pytest distribution strategy
        pytest_dist: str | None = None
        pytest_loadscope = False

        if wl == WorkloadClass.PYTEST_MIXED:
            pytest_dist = "worksteal"
        elif wl == WorkloadClass.PYTEST_FIXTURE_HEAVY:
            pytest_dist = "loadscope"
            pytest_loadscope = True
        elif wl in (WorkloadClass.PYTHON_CPU, WorkloadClass.NATIVE_CPU):
            pytest_dist = "loadfile"

        return WorkerRecommendation(
            workers=workers,
            use_processes=use_processes,
            pytest_dist=pytest_dist,
            pytest_loadscope=pytest_loadscope,
            reserved_threads=reserved,
            workload_class=wl,
            profile=prof,
        )

    def get_optimal_workers(
        self,
        workload_class: WorkloadClass | None = None,
        profile: OperatingProfile | None = None,
    ) -> int:
        """Calculate optimal worker count for workload and profile.

        Legacy compatibility: returns simple worker count.
        For full recommendation, use get_recommendation().
        """
        rec = self.get_recommendation(workload_class, profile)
        return rec.workers

    def check_temperature(self) -> tuple[float, str]:
        """Check CPU temperature and return status.

        Returns:
            Tuple of (temperature_c, status)
            Status: "ok", "warning" (approaching 90°C), "critical" (>=90°C)
        """
        if not self.config.enable_temp_guardrail:
            return 0.0, "disabled"

        # Rate limit temperature checks
        now = time.time()
        if now - self._last_temp_check < self.config.temp_check_interval_s:
            return self._temp_check_result, "cached"

        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return 0.0, "unavailable"

            # Find CPU package temperature
            cpu_temp: float | None = None
            for name, entries in temps.items():
                if "cpu" in name.lower() or "k10" in name.lower() or "zen" in name.lower():
                    for entry in entries:
                        if entry.current:
                            cpu_temp = entry.current
                            break
                if cpu_temp is not None:
                    break

            if cpu_temp is None:
                # Fallback: take highest temperature from any sensor
                for entries in temps.values():
                    for entry in entries:
                        if entry.current and (cpu_temp is None or entry.current > cpu_temp):
                            cpu_temp = entry.current

            if cpu_temp is None:
                return 0.0, "unavailable"

            self._temp_check_result = cpu_temp
            self._last_temp_check = now

            if cpu_temp >= SUSTAINED_TEMP_THRESHOLD_C:
                return cpu_temp, "critical"
            elif cpu_temp >= SUSTAINED_TEMP_THRESHOLD_C - 5:
                return cpu_temp, "warning"
            else:
                return cpu_temp, "ok"

        except Exception as e:
            logger.warning(f"Failed to check temperature: {e}")
            return 0.0, "error"

    def should_stop_for_temperature(self) -> bool:
        """Check if execution should stop due to temperature.

        Returns True if sustained temperature exceeds 90°C threshold.
        """
        temp, status = self.check_temperature()
        if status == "critical":
            logger.error(
                f"CPU temperature {temp:.1f}°C exceeds {SUSTAINED_TEMP_THRESHOLD_C}°C threshold. "
                f"Stopping execution to prevent thermal damage."
            )
            return True
        elif status == "warning":
            logger.warning(
                f"CPU temperature {temp:.1f}°C approaching threshold. "
                f"Consider reducing worker count or improving cooling."
            )
        return False

    def set_cpu_affinity(self, pid: int | None = None, cores: list[int] | None = None) -> bool:
        """Set CPU affinity for a process."""
        if not self.config.cpu_affinity:
            return False

        try:
            pid = pid or os.getpid()
            process = psutil.Process(pid)

            if cores is None:
                # Auto-assign to available cores
                cores = list(range(self._cpu_count))

            process.cpu_affinity(cores)
            logger.debug(f"Set CPU affinity for PID {pid} to cores: {cores}")
            return True
        except Exception as e:
            logger.warning(f"Failed to set CPU affinity: {e}")
            return False

    def get_executor(self, workload_class: WorkloadClass | None = None) -> concurrent.futures.Executor:
        """Get or create executor pool for workload class."""
        rec = self.get_recommendation(workload_class)
        workers = rec.workers
        use_processes = rec.use_processes

        if self._executor is None:
            if use_processes:
                # Unix: Use fork context (fast)
                ctx = mp.get_context('fork') if not self._is_windows else mp.get_context('spawn')
                self._executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers,
                    mp_context=ctx,
                )
                logger.info(f"Created ProcessPoolExecutor with {workers} workers")
            else:
                self._executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers,
                    thread_name_prefix="cpu_opt_",
                )
                logger.info(f"Created ThreadPoolExecutor with {workers} workers")

        return self._executor

    def shutdown(self) -> None:
        """Shutdown executor pool."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
            logger.info("Executor shutdown complete")

    def map_parallel(
        self,
        func: Callable[[T], Any],
        items: list[T],
        chunk_size: int | None = None,
        workload_class: WorkloadClass | None = None,
    ) -> Iterator[Any]:
        """Parallel map operation across CPU cores."""
        if not items:
            return iter([])

        rec = self.get_recommendation(workload_class)
        chunk = chunk_size or self.config.chunk_size

        # Create fresh executor per workload class
        if rec.use_processes:
            ctx = mp.get_context('fork') if not self._is_windows else mp.get_context('spawn')
            executor: concurrent.futures.Executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=rec.workers,
                mp_context=ctx,
            )
        else:
            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=rec.workers,
                thread_name_prefix="cpu_opt_",
            )

        try:
            futures = [executor.submit(func, item) for item in items]

            for future in concurrent.futures.as_completed(futures):
                # Check temperature periodically
                if self.should_stop_for_temperature():
                    # Cancel pending futures
                    for f in futures:
                        f.cancel()
                    raise RuntimeError(
                        f"Execution stopped: CPU temperature exceeded {SUSTAINED_TEMP_THRESHOLD_C}°C"
                    )

                try:
                    yield future.result()
                except Exception as e:
                    logger.error(f"Parallel task failed: {e}")
                    raise
        finally:
            executor.shutdown(wait=True)

    def process_batches(
        self,
        func: Callable[[list[T]], list[Any]],
        items: list[T],
        batch_size: int | None = None,
    ) -> list[Any]:
        """Process items in batches for efficiency."""
        if not items:
            return []

        batch_size = batch_size or self.config.batch_size
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = func(batch)
            results.extend(batch_results)

            logger.debug(f"Processed batch {i // batch_size + 1}: {len(batch)} items")

        return results

    def get_cpu_metrics(self) -> dict[str, Any]:
        """Get current CPU metrics including temperature."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            temp, temp_status = self.check_temperature()
            rec = self.get_recommendation()

            return {
                "cpu_percent_per_core": cpu_percent,
                "cpu_percent_avg": sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0,
                "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
                "cpu_count_logical": self._cpu_count,
                "cpu_count_physical": self._physical_cores,
                "is_amd": self._is_amd,
                "workers_configured": rec.workers,
                "workload_class": rec.workload_class.value,
                "profile": rec.profile.value,
                "temperature_c": temp,
                "temperature_status": temp_status,
                "reserved_threads": rec.reserved_threads,
                "pytest_dist": rec.pytest_dist,
                "use_processes": rec.use_processes,
            }
        except Exception as e:
            logger.warning(f"Failed to get CPU metrics: {e}")
            return {"error": str(e)}

    def get_pytest_args(self, workload_class: WorkloadClass | None = None) -> list[str]:
        """Get recommended pytest-xdist arguments for workload.

        Returns:
            List of command-line arguments for pytest
        """
        rec = self.get_recommendation(workload_class)
        args = ["-n", str(rec.workers)]

        if rec.pytest_dist:
            args.extend(["--dist", rec.pytest_dist])
        if rec.pytest_loadscope:
            args.append("--dist=loadscope")

        return args


# Singleton instance
_cpu_optimizer: AMD9950X3DOptimizer | None = None


def get_cpu_optimizer(config: CPUConfig | None = None) -> AMD9950X3DOptimizer:
    """Get or create singleton CPU optimizer."""
    global _cpu_optimizer
    if _cpu_optimizer is None:
        _cpu_optimizer = AMD9950X3DOptimizer(config)
    return _cpu_optimizer


def shutdown_cpu_optimizer() -> None:
    """Shutdown singleton CPU optimizer."""
    global _cpu_optimizer
    if _cpu_optimizer:
        _cpu_optimizer.shutdown()
        _cpu_optimizer = None


def get_recommended_defaults() -> dict[str, Any]:
    """Get the recommended production defaults for AMD 9950X3D.

    Safe baseline per optimization plan:
    - python_cpu = 16
    - native_cpu = 20
    - pytest_mixed = 24
    - pytest_fixture_heavy = 18
    - network_io = 16
    - interactive_reserve = 4 logical threads
    - batch_reserve = 2 logical threads
    """
    return {
        "python_cpu": 16,
        "native_cpu": 20,
        "pytest_mixed": 24,
        "pytest_fixture_heavy": 18,
        "network_io": 16,
        "disk_io": 16,
        "interactive_reserve": INTERACTIVE_THREAD_RESERVE,
        "batch_reserve": BATCH_THREAD_RESERVE,
        "max_operating_temp_c": MAX_OPERATING_TEMP_C,
        "sustained_temp_threshold_c": SUSTAINED_TEMP_THRESHOLD_C,
    }


__all__ = [
    "AMD9950X3DOptimizer",
    "CPUConfig",
    "WorkloadClass",
    "OperatingProfile",
    "WorkerRecommendation",
    "get_cpu_optimizer",
    "shutdown_cpu_optimizer",
    "get_recommended_defaults",
    # Safety constants
    "MAX_OPERATING_TEMP_C",
    "SUSTAINED_TEMP_THRESHOLD_C",
    "INTERACTIVE_THREAD_RESERVE",
    "BATCH_THREAD_RESERVE",
]
