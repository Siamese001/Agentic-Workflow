"""
Profiling Utilities for InferenceEngine Optimization

Provides profiling decorators and measurement tools for identifying
latency bottlenecks in reasoning engines.
"""

from __future__ import annotations
import cProfile
import pstats
import time
import functools
from io import StringIO
from typing import Callable, Any, Dict, List
from pathlib import Path
from datetime import datetime


class ProfileResult:
    """Container for profiling results."""
    
    def __init__(self, function_name: str, total_time: float, call_count: int, hotspots: List[Dict]):
        """Initialize profile result."""
        self.function_name = function_name
        self.total_time = total_time
        self.call_count = call_count
        self.hotspots = hotspots
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function": self.function_name,
            "total_time": self.total_time,
            "call_count": self.call_count,
            "avg_time": self.total_time / self.call_count if self.call_count > 0 else 0,
            "hotspots": self.hotspots,
            "timestamp": self.timestamp
        }


class ReasoningProfiler:
    """Profiler for reasoning engine methods."""
    
    def __init__(self, log_dir: str = "agentic_core/L0_maintenance/logs"):
        """Initialize profiler."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ProfileResult] = []
    
    def profile_function(self, func: Callable, *args, **kwargs) -> tuple:
        """
        Profile a function execution.
        
        Returns:
            (result, profile_result)
        """
        pr = cProfile.Profile()
        pr.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        total_time = time.time() - start_time
        
        pr.disable()
        
        # Extract hotspots
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20
        
        hotspots = self._extract_hotspots(pr)
        profile_result = ProfileResult(
            func.__name__,
            total_time,
            pr.total_calls,
            hotspots
        )
        
        self.results.append(profile_result)
        return result, profile_result
    
    def _extract_hotspots(self, pr: cProfile.Profile) -> List[Dict]:
        """Extract top hotspots from profile."""
        hotspots = []
        for func, (cc, nc, tt, ct, callers) in pr.timings.items():
            if tt > 0:  # Only include functions with time
                hotspots.append({
                    "function": f"{func[0]}:{func[1]}",
                    "cumulative_time": ct,
                    "total_time": tt,
                    "call_count": nc
                })
        
        # Sort by cumulative time
        hotspots.sort(key=lambda x: x["cumulative_time"], reverse=True)
        return hotspots[:20]  # Top 20
    
    def save_report(self, filename: str = "l1_inference_profile.txt"):
        """Save profiling report."""
        report_path = self.log_dir / filename
        
        with open(report_path, 'w') as f:
            f.write("# L1 InferenceEngine Profiling Report\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            
            for result in self.results:
                f.write(f"## Function: {result.function_name}\n")
                f.write(f"Total Time: {result.total_time:.4f}s\n")
                f.write(f"Call Count: {result.call_count}\n")
                f.write(f"Avg Time: {result.total_time / result.call_count:.6f}s\n\n")
                
                f.write("### Top Hotspots:\n")
                for i, hotspot in enumerate(result.hotspots[:10], 1):
                    f.write(f"{i}. {hotspot['function']}\n")
                    f.write(f"   Cumulative: {hotspot['cumulative_time']:.4f}s\n")
                    f.write(f"   Total: {hotspot['total_time']:.4f}s\n")
                    f.write(f"   Calls: {hotspot['call_count']}\n\n")
        
        return report_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Get profiling summary."""
        if not self.results:
            return {"status": "no_results"}
        
        total_time = sum(r.total_time for r in self.results)
        total_calls = sum(r.call_count for r in self.results)
        
        return {
            "total_functions_profiled": len(self.results),
            "total_time": total_time,
            "total_calls": total_calls,
            "avg_call_time": total_time / total_calls if total_calls > 0 else 0,
            "functions": [r.to_dict() for r in self.results]
        }


def profile_reasoning(func: Callable) -> Callable:
    """Decorator for profiling reasoning functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        profiler = ReasoningProfiler()
        result, profile_result = profiler.profile_function(func, *args, **kwargs)
        
        # Log profile result
        print(f"\n=== Profiling: {func.__name__} ===")
        print(f"Total Time: {profile_result.total_time:.4f}s")
        print(f"Call Count: {profile_result.call_count}")
        print(f"Avg Time: {profile_result.total_time / profile_result.call_count:.6f}s")
        print("\nTop Hotspots:")
        for i, hotspot in enumerate(profile_result.hotspots[:5], 1):
            print(f"{i}. {hotspot['function']}: {hotspot['cumulative_time']:.4f}s")
        
        # Save report
        report_path = profiler.save_report(f"l1_{func.__name__}_profile.txt")
        print(f"\nProfile saved to: {report_path}\n")
        
        return result
    
    return wrapper


def time_operation(operation_name: str) -> Callable:
    """Decorator for timing operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"{operation_name}: {elapsed:.4f}s")
            return result
        return wrapper
    return decorator
