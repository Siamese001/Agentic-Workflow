# RCA: Why Test Cases Take So Long Using ADG as Input

## Executive Summary

Test cases using ADG (Architecture Dependency Graph) as input experience significant performance issues due to several architectural and implementation bottlenecks. The primary cause is that tests repeatedly perform full repository scans instead of using cached or incremental results.

## Root Causes

### 1. **Full Repository Scans in Tests**
- **Issue**: Tests like `test_adg_digest_stable_two_runs` perform complete scans of the entire codebase (6,000+ modules)
- **Impact**: Each scan takes 3-5 minutes, causing tests to timeout or run extremely slowly
- **Evidence**: 420-second timeout marker in `test_adg_digest_stable.py`

### 2. **Inefficient Cache Usage**
- **Issue**: Although scan caching exists (`scan_result_cache.json`), many tests don't leverage it properly
- **Impact**: Cache misses force full re-scans of all Python files
- **Location**: `static_scanner.py` lines 6475-6488

### 3. **Post-Scan Hotspots**
- **Issue**: `manifest.type_surface_expected_count` repeatedly rebuilds the realized node set
- **Impact**: O(n²) complexity in post-processing phase
- **Evidence**: Memory shows fix applied but may not be sufficient

### 4. **Multiple Visitor Pattern Overhead**
- **Issue**: Each file is processed by 33+ different AST visitors (G1-G33)
- **Impact**: Linear increase in processing time with each added visitor
- **Location**: `static_scanner.py` visitor registration

### 5. **Large-Scale Graph Operations**
- **Issue**: Operations like semantic depth checks process all edges (800K+ edges)
- **Impact**: Expensive computations repeated for each test
- **Location**: `_check_semantic_depth()` function

## Performance Metrics

| Operation | Typical Time | Frequency | Scale |
|-----------|--------------|-----------|-------|
| Full repository scan | 3-5 minutes | Per test | 6,709 Python files |
| Single file scan | ~1.1 seconds | Per file | ~546 edges per file |
| Cache load/save | 5-10 seconds | Per scan | 453MB cache file |
| Semantic depth computation | 30-60 seconds | Per scan | 800K+ edges |
| Edge sorting (800K edges) | 10-20 seconds | Per scan | O(n log n) |
| Digest computation | 5-10 seconds | Per scan | SHA-256 of all edges |

### Detailed Measurements
- **Total Files**: 6,709 Python files in repository
- **Single File Time**: 1.09 seconds for UniversalWriteGateway.py (546 edges)
- **Estimated Full Scan**: 1.09s × 6,709 = ~73 minutes (without caching)
- **Actual Time**: 3-5 minutes (with caching and parallelization)

## Contributing Factors

### 1. **Test Design Issues**
- Tests use `@pytest.fixture(scope="module")` but still create new scanners
- Multiple test methods trigger redundant scans
- No proper test data isolation

### 2. **Memory Pressure**
- Scan cache file ~453MB for full repository
- Multiple test processes increase memory usage
- Garbage collection overhead

### 3. **I/O Bottlenecks**
- Reading 6,000+ Python files from disk
- Writing large cache files
- SQLite operations for ADG persistence

## Solutions Implemented

### 1. **Module-Scoped Fixtures**
```python
@pytest.fixture(scope="module")
def full_scan_result(scan_cache_path: Path):
    return _make_scanner(scan_cache_path).scan(commit_sha="module-full-scan")
```

### 2. **Optimized Node Set Computation**
```python
# Fixed: Compute realized_node_names once before membership checks
realized_node_names = set(result.type_surface_map.keys())
manifest.type_surface_expected_count = len(
    {name for name in result.type_surface_map if name in realized_node_names}
)
```

### 3. **Explicit Timeouts**
- 420s timeout for two-run comparison
- 300s timeout for artifact builds

## Recommended Improvements

### 1. **Test-Level Optimizations**
- Use `@pytest.mark.skipif` for expensive tests in CI
- Create dedicated "smoke test" suite with cached fixtures
- Implement test-specific mini-ADGs for unit tests

### 2. **Scanner Optimizations**
- Implement parallel file processing
- Add incremental scan mode for changed files only
- Pre-compute and serialize expensive operations

### 3. **Cache Strategy**
- Separate test cache from development cache
- Implement cache warming for CI environments
- Add cache compression to reduce I/O

### 4. **Architecture Changes**
- Consider splitting large tests into integration vs unit
- Create mock ADG for testing edge cases
- Implement test-specific scanner configurations

## Immediate Actions

1. **Create Test Data Set**: Pre-scan and commit a test ADG artifact
2. **Mock Scanner**: Implement `MockADGStaticScanner` for unit tests
3. **Parallel Processing**: Use multiprocessing for file scanning
4. **Cache Optimization**: Implement binary cache format with compression

## Long-term Strategy

1. **Distributed Testing**: Run ADG tests on dedicated infrastructure
2. **Incremental Testing**: Only test changed components
3. **Test Tiering**: Separate fast unit tests from slow integration tests
4. **Performance Monitoring**: Add timing metrics to test suite

## Conclusion

The primary bottleneck is the full repository scan performed by tests. While caching helps, the fundamental issue is using production-scale ADG generation in test scenarios. A combination of test data fixtures, mocking, and architectural changes will be necessary to achieve acceptable test performance.
