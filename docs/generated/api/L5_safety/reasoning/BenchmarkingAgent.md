# API Documentation: BenchmarkingAgent

**Target Audience**: developers, api_users

# BenchmarkingAgent API Documentation

**File**: `BenchmarkingAgent.py`
**Classes**: 5
**Functions**: 33

## Classes

- **BenchmarkResult**
- **BenchmarkResultActual**
- **BenchmarkSuite**
- **BenchmarkingAgent** (inherits from SovereignBaseAgent)
- **BenchmarkContext**

## Functions

- **get_benchmarking_agent** -> BenchmarkingAgent
- **initialize_benchmarking** -> Any
- **benchmark** -> Any
- **benchmark_async** -> Any
- **BenchmarkContext** -> benchmark_context_manager
- **__init__**
- **to_dict** -> dict
- **__init__**
- **add_result** -> Any
- **_update_stats**
- **is_degraded** -> bool
- **get_summary** -> dict
- **heal** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **__init__**
- **benchmark** -> Any
- **benchmark_async** -> Any
- **start_timer** -> Any
- **end_timer** -> float
- **time_function** -> Any
- **record_result** -> Any
- **_alert_performance_degradation**
- **get_benchmark_summary** -> dict | None
- **get_all_summaries** -> dict[str, dict]
- **compare_benchmarks** -> dict
- **reset_benchmark** -> Any
- **reset_all** -> Any
- **__init__**
- **__enter__**
- **__exit__**
- **decorator** -> Callable
- **decorator** -> Callable
- **wrapper** -> Any


## Class: BenchmarkResult

**Description**: BenchmarkResult agent for autonomous operations.



## Class: BenchmarkResultActual

**Description**: Result of a single benchmark measurement.

### Methods

#### __init__
**Parameters**: self, name, duration_ms, metadata

#### to_dict
**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Class: BenchmarkSuite

**Description**: Collection of benchmarks for a specific operation.

### Methods

#### __init__
**Parameters**: self, name

#### add_result
**Parameters**: self, result
**Returns**: Any
**Description**: Add a benchmark result.

#### _update_stats
**Parameters**: self
**Description**: Update statistical measures.

#### is_degraded
**Parameters**: self, threshold
**Returns**: bool
**Description**: Check if performance has degraded.

#### get_summary
**Parameters**: self
**Returns**: dict
**Description**: Get benchmark summary.



## Class: BenchmarkingAgent

**Description**: 
    Measures and tracks performance metrics.

    Features:
    - Function timing with context manager
    - Performance history tracking
    - Degradation detection
    - Comparative analysis
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self
**Description**: Initialize the BenchmarkingAgent.

#### benchmark
**Parameters**: self, name, metadata
**Returns**: Any
**Description**: 
        Decorator to benchmark a function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        

#### benchmark_async
**Parameters**: self, name, metadata
**Returns**: Any
**Description**: 
        Decorator to benchmark an async function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        

#### start_timer
**Parameters**: self, name
**Returns**: Any
**Description**: 
        Start a manual timer.

        Args:
            name: Name for the benchmark
        

#### end_timer
**Parameters**: self, name, metadata
**Returns**: float
**Description**: 
        End a manual timer and record result.

        Args:
            name: Name of the benchmark
            metadata: Additional metadata

        Returns:
            Duration in milliseconds
        

#### time_function
**Parameters**: self, name, func, metadata
**Returns**: Any
**Description**: 
        Time a function execution.

        Args:
            name: Benchmark name
            func: Function to time
            metadata: Additional metadata
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        

#### record_result
**Parameters**: self, name, duration_ms, metadata
**Returns**: Any
**Description**: 
        Record a benchmark result.

        Args:
            name: Benchmark name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        

#### _alert_performance_degradation
**Parameters**: self, name, result
**Description**: Alert about performance degradation.

#### get_benchmark_summary
**Parameters**: self, name
**Returns**: dict | None
**Description**: Get summary for a specific benchmark.

#### get_all_summaries
**Parameters**: self
**Returns**: dict[str, dict]
**Description**: Get summaries for all benchmarks.

#### compare_benchmarks
**Parameters**: self, name1, name2
**Returns**: dict
**Description**: Compare two benchmarks.

#### reset_benchmark
**Parameters**: self, name
**Returns**: Any
**Description**: Reset all data for a benchmark.

#### reset_all
**Parameters**: self
**Returns**: Any
**Description**: Reset all benchmark data.



## Class: BenchmarkContext

**Description**: Context manager for benchmarking.

### Methods

#### __init__
**Parameters**: self, agent, name, metadata

#### __enter__
**Parameters**: self

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb



## Function: get_benchmarking_agent

**Returns**: BenchmarkingAgent
**Description**: Get or create the global BenchmarkingAgent instance.



## Function: initialize_benchmarking

**Returns**: Any
**Description**: Initialize the BenchmarkingAgent system.



## Function: benchmark

**Parameters**: name, metadata
**Returns**: Any
**Description**: Decorator to benchmark a function.



## Function: benchmark_async

**Parameters**: name, metadata
**Returns**: Any
**Description**: Decorator to benchmark an async function.



## Function: BenchmarkContext

**Parameters**: name, metadata
**Returns**: benchmark_context_manager
**Description**: Create a benchmark context manager.



## Function: __init__

**Parameters**: self, name, duration_ms, metadata


## Function: to_dict

**Parameters**: self
**Returns**: dict
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, name


## Function: add_result

**Parameters**: self, result
**Returns**: Any
**Description**: Add a benchmark result.



## Function: _update_stats

**Parameters**: self
**Description**: Update statistical measures.



## Function: is_degraded

**Parameters**: self, threshold
**Returns**: bool
**Description**: Check if performance has degraded.



## Function: get_summary

**Parameters**: self
**Returns**: dict
**Description**: Get benchmark summary.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self
**Description**: Initialize the BenchmarkingAgent.



## Function: benchmark

**Parameters**: self, name, metadata
**Returns**: Any
**Description**: 
        Decorator to benchmark a function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        



## Function: benchmark_async

**Parameters**: self, name, metadata
**Returns**: Any
**Description**: 
        Decorator to benchmark an async function.

        Args:
            name: Name for the benchmark
            metadata: Additional metadata to store

        Returns:
            Decorated function
        



## Function: start_timer

**Parameters**: self, name
**Returns**: Any
**Description**: 
        Start a manual timer.

        Args:
            name: Name for the benchmark
        



## Function: end_timer

**Parameters**: self, name, metadata
**Returns**: float
**Description**: 
        End a manual timer and record result.

        Args:
            name: Name of the benchmark
            metadata: Additional metadata

        Returns:
            Duration in milliseconds
        



## Function: time_function

**Parameters**: self, name, func, metadata
**Returns**: Any
**Description**: 
        Time a function execution.

        Args:
            name: Benchmark name
            func: Function to time
            metadata: Additional metadata
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        



## Function: record_result

**Parameters**: self, name, duration_ms, metadata
**Returns**: Any
**Description**: 
        Record a benchmark result.

        Args:
            name: Benchmark name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        



## Function: _alert_performance_degradation

**Parameters**: self, name, result
**Description**: Alert about performance degradation.



## Function: get_benchmark_summary

**Parameters**: self, name
**Returns**: dict | None
**Description**: Get summary for a specific benchmark.



## Function: get_all_summaries

**Parameters**: self
**Returns**: dict[str, dict]
**Description**: Get summaries for all benchmarks.



## Function: compare_benchmarks

**Parameters**: self, name1, name2
**Returns**: dict
**Description**: Compare two benchmarks.



## Function: reset_benchmark

**Parameters**: self, name
**Returns**: Any
**Description**: Reset all data for a benchmark.



## Function: reset_all

**Parameters**: self
**Returns**: Any
**Description**: Reset all benchmark data.



## Function: __init__

**Parameters**: self, agent, name, metadata


## Function: __enter__

**Parameters**: self


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb


## Function: decorator

**Parameters**: func
**Returns**: Callable
**Description**: Execute decorator operation.



## Function: decorator

**Parameters**: func
**Returns**: Callable
**Description**: Execute decorator operation.



## Function: wrapper

**Returns**: Any
**Description**: Execute wrapper operation.



## Usage Examples

### Class Usage

```python
# Using BenchmarkResult
benchmarkresult = BenchmarkResult()
```

```python
# Using BenchmarkResultActual
benchmarkresultactual = BenchmarkResultActual()
benchmarkresultactual.to_dict()
```

```python
# Using BenchmarkSuite
benchmarksuite = BenchmarkSuite()
benchmarksuite.add_result()
benchmarksuite.is_degraded()
```

### Function Usage

```python
# Using get_benchmarking_agent
result = get_benchmarking_agent()
```

```python
# Using initialize_benchmarking
result = initialize_benchmarking()
```

```python
# Using benchmark
result = benchmark(name, metadata)
```



---
**Generated**: 2026-03-26T09:39:05.054565
**Type**: api_reference
**Quality**: comprehensive
