#!/usr/bin/env python3
"""
CPU Usage Test for ADG Generation
Compares CPU usage before and after optimization.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil


def measure_cpu_during_adg_generation():
    """Measure CPU usage during ADG generation"""

    print("Starting CPU usage measurement...")
    print("=" * 60)

    # Initialize CPU monitoring
    cpu_samples = []
    memory_samples = []
    start_time = time.time()

    # Start ADG generation process
    print("Launching ADG generation...")
    process = subprocess.Popen(
        [sys.executable, "tools/generate_full_adg.py", "--force"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )

    # Monitor CPU while process runs
    try:
        while process.poll() is None:
            # Sample CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_info = psutil.virtual_memory()

            cpu_samples.append(
                {
                    "timestamp": time.time() - start_time,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_info.percent,
                    "memory_used_gb": memory_info.used / (1024**3),
                }
            )

            if len(cpu_samples) % 10 == 0:
                print(
                    f"  Sample {len(cpu_samples)}: CPU={cpu_percent:.1f}%, Memory={memory_info.percent:.1f}%"
                )
    except KeyboardInterrupt:
        process.terminate()
        raise

    end_time = time.time()
    duration = end_time - start_time

    # Calculate statistics
    if cpu_samples:
        avg_cpu = sum(s["cpu_percent"] for s in cpu_samples) / len(cpu_samples)
        max_cpu = max(s["cpu_percent"] for s in cpu_samples)
        avg_memory = sum(s["memory_percent"] for s in cpu_samples) / len(cpu_samples)
        max_memory = max(s["memory_percent"] for s in cpu_samples)
    else:
        avg_cpu = max_cpu = avg_memory = max_memory = 0

    results = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "cpu_metrics": {
            "average_percent": round(avg_cpu, 2),
            "max_percent": round(max_cpu, 2),
            "samples_count": len(cpu_samples),
        },
        "memory_metrics": {
            "average_percent": round(avg_memory, 2),
            "max_percent": round(max_memory, 2),
            "peak_used_gb": round(max(s["memory_used_gb"] for s in cpu_samples), 2) if cpu_samples else 0,
        },
        "samples": cpu_samples[:100],  # Store first 100 samples for analysis
    }

    # Save results
    output_path = Path("artifacts/adg/cpu_usage_test.json")
    output_path.write_text(json.dumps(results, indent=2))

    print("=" * 60)
    print("CPU USAGE TEST COMPLETE")
    print("=" * 60)
    print(f"Duration: {duration:.1f} seconds")
    print(f"CPU - Average: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")
    print(f"Memory - Average: {avg_memory:.1f}%, Max: {max_memory:.1f}%")
    print(f"Peak Memory Used: {results['memory_metrics']['peak_used_gb']:.2f} GB")
    print(f"Results saved to: {output_path}")

    return results


if __name__ == "__main__":
    results = measure_cpu_during_adg_generation()
    sys.exit(0)
