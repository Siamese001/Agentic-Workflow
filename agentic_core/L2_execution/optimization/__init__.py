"""CPU Optimization Module for AMD Processors.

Provides high-performance parallel processing capabilities:
- ProcessPoolExecutor for GIL-bound CPU tasks
- CPU affinity tuning for AMD architectures
- Parallel file processing
- Batch processing utilities

Usage:
    from agentic_core.L2_execution.optimization import (
        get_cpu_optimizer,
        get_file_processor,
        BatchProcessor,
    )

    # CPU-optimized parallel processing
    optimizer = get_cpu_optimizer()
    results = optimizer.map_parallel(process_func, items)

    # Parallel file processing
    processor = get_file_processor()
    results = processor.process_files(file_paths, parse_json_file)
"""

from __future__ import annotations

# CPU Optimizer
from agentic_core.L2_execution.optimization.cpu_optimizer import (
    AMD9950X3DOptimizer,
    CPUConfig,
    OperatingProfile,
    WorkloadClass,
    WorkerRecommendation,
    get_cpu_optimizer,
    get_recommended_defaults,
    shutdown_cpu_optimizer,
    MAX_OPERATING_TEMP_C,
    SUSTAINED_TEMP_THRESHOLD_C,
    INTERACTIVE_THREAD_RESERVE,
    BATCH_THREAD_RESERVE,
)

# Parallel File Processor
from agentic_core.L2_execution.optimization.parallel_file_processor import (
    ParallelFileProcessor,
    FileTask,
    FileResult,
    get_file_processor,
    shutdown_file_processor,
    read_file_utf8,
    parse_json_file,
    compute_file_hash,
)

# Batch Processor
from agentic_core.L2_execution.optimization.batch_processor import (
    BatchProcessor,
    StreamingBatchProcessor,
    BatchResult,
    BatchMetrics,
    JSONBatchProcessor,
    FileHashBatchProcessor,
)

__version__ = "1.0.0"

__all__ = [
    # CPU Optimizer
    "AMD9950X3DOptimizer",
    "CPUConfig",
    "OperatingProfile",
    "WorkloadClass",
    "WorkerRecommendation",
    "get_cpu_optimizer",
    "get_recommended_defaults",
    "shutdown_cpu_optimizer",
    # Safety constants
    "MAX_OPERATING_TEMP_C",
    "SUSTAINED_TEMP_THRESHOLD_C",
    "INTERACTIVE_THREAD_RESERVE",
    "BATCH_THREAD_RESERVE",
    # Parallel File Processor
    "ParallelFileProcessor",
    "FileTask",
    "FileResult",
    "get_file_processor",
    "shutdown_file_processor",
    "read_file_utf8",
    "parse_json_file",
    "compute_file_hash",
    # Batch Processor
    "BatchProcessor",
    "StreamingBatchProcessor",
    "BatchResult",
    "BatchMetrics",
    "JSONBatchProcessor",
    "FileHashBatchProcessor",
]
