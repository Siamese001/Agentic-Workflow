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

# Batch Processor
from agentic_core.L2_execution.optimization.batch_processor import (
    BatchMetrics,
    BatchProcessor,
    BatchResult,
    FileHashBatchProcessor,
    JSONBatchProcessor,
    StreamingBatchProcessor,
)

# CPU Optimizer
from agentic_core.L2_execution.optimization.cpu_optimizer import (
    BATCH_THREAD_RESERVE,
    INTERACTIVE_THREAD_RESERVE,
    MAX_OPERATING_TEMP_C,
    SUSTAINED_TEMP_THRESHOLD_C,
    AMD9950X3DOptimizer,
    CPUConfig,
    OperatingProfile,
    WorkerRecommendation,
    WorkloadClass,
    get_cpu_optimizer,
    get_recommended_defaults,
    shutdown_cpu_optimizer,
)

# Parallel File Processor
from agentic_core.L2_execution.optimization.parallel_file_processor import (
    FileResult,
    FileTask,
    ParallelFileProcessor,
    compute_file_hash,
    get_file_processor,
    parse_json_file,
    read_file_utf8,
    shutdown_file_processor,
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
