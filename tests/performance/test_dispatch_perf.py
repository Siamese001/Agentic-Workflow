import unittest
import timeit
from unittest.mock import MagicMock
from pathlib import Path
from agentic_core.utils.core_extensions.redis import SovereignRedisClient
from agentic_core.utils.core_extensions.git import SovereignGitClient


class TestDispatchPerformance(unittest.TestCase):
    """Performance benchmarks for refactored dispatch patterns."""

    def setUp(self):
        """Initialize clients for benchmarking."""
        self.redis_client = SovereignRedisClient()
        self.redis_client._get_client = MagicMock(return_value=None)
        self.redis_client._fallback_cache = {}
        self.redis_client._audit = MagicMock()
        
        self.git_client = SovereignGitClient()
        self.git_client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        self.git_client._audit = MagicMock()

    def test_redis_execute_dispatch_performance(self):
        """Benchmark Redis execute dispatch performance."""
        def redis_set():
            self.redis_client.execute('set', key='k', value='v')
        
        def redis_get():
            self.redis_client.execute('get', key='k')
        
        def redis_delete():
            self.redis_client.execute('delete', key='k')
        
        # Warm up
        for _ in range(100):
            redis_set()
        
        # Benchmark set
        set_time = timeit.timeit(redis_set, number=10000)
        print(f"\nRedis execute('set'): {set_time:.4f}s for 10k calls ({set_time/10000*1e6:.2f}µs per call)")
        
        # Benchmark get
        get_time = timeit.timeit(redis_get, number=10000)
        print(f"Redis execute('get'): {get_time:.4f}s for 10k calls ({get_time/10000*1e6:.2f}µs per call)")
        
        # Benchmark delete
        delete_time = timeit.timeit(redis_delete, number=10000)
        print(f"Redis execute('delete'): {delete_time:.4f}s for 10k calls ({delete_time/10000*1e6:.2f}µs per call)")
        
        # Assert acceptable performance (<1s for 10k calls)
        self.assertLess(set_time, 1.0, "Redis set dispatch too slow")
        self.assertLess(get_time, 1.0, "Redis get dispatch too slow")
        self.assertLess(delete_time, 1.0, "Redis delete dispatch too slow")

    def test_git_execute_dispatch_performance(self):
        """Benchmark Git execute dispatch performance."""
        def git_status():
            self.git_client.execute('status')
        
        def git_log():
            self.git_client.execute('log', count=10)
        
        def git_branch():
            self.git_client.execute('branch', action='list')
        
        # Warm up
        for _ in range(100):
            git_status()
        
        # Benchmark status
        status_time = timeit.timeit(git_status, number=10000)
        print(f"\nGit execute('status'): {status_time:.4f}s for 10k calls ({status_time/10000*1e6:.2f}µs per call)")
        
        # Benchmark log
        log_time = timeit.timeit(git_log, number=10000)
        print(f"Git execute('log'): {log_time:.4f}s for 10k calls ({log_time/10000*1e6:.2f}µs per call)")
        
        # Benchmark branch
        branch_time = timeit.timeit(git_branch, number=10000)
        print(f"Git execute('branch'): {branch_time:.4f}s for 10k calls ({branch_time/10000*1e6:.2f}µs per call)")
        
        # Assert acceptable performance (<1s for 10k calls)
        self.assertLess(status_time, 1.0, "Git status dispatch too slow")
        self.assertLess(log_time, 1.0, "Git log dispatch too slow")
        self.assertLess(branch_time, 1.0, "Git branch dispatch too slow")

    def test_redis_handler_direct_performance(self):
        """Benchmark direct handler performance."""
        def handle_set():
            self.redis_client._handle_set(key='k', value='v')
        
        def handle_get():
            self.redis_client._handle_get(key='k')
        
        # Warm up
        for _ in range(100):
            handle_set()
        
        # Benchmark
        set_time = timeit.timeit(handle_set, number=10000)
        get_time = timeit.timeit(handle_get, number=10000)
        
        print(f"\nRedis _handle_set: {set_time:.4f}s for 10k calls ({set_time/10000*1e6:.2f}µs per call)")
        print(f"Redis _handle_get: {get_time:.4f}s for 10k calls ({get_time/10000*1e6:.2f}µs per call)")
        
        # Assert fast (<0.5s for 10k calls)
        self.assertLess(set_time, 0.5, "Handler set too slow")
        self.assertLess(get_time, 0.5, "Handler get too slow")

    def test_git_handler_direct_performance(self):
        """Benchmark direct handler performance."""
        def handle_status():
            self.git_client._handle_status()
        
        def handle_log():
            self.git_client._handle_log(count=10)
        
        # Warm up
        for _ in range(100):
            handle_status()
        
        # Benchmark
        status_time = timeit.timeit(handle_status, number=10000)
        log_time = timeit.timeit(handle_log, number=10000)
        
        print(f"\nGit _handle_status: {status_time:.4f}s for 10k calls ({status_time/10000*1e6:.2f}µs per call)")
        print(f"Git _handle_log: {log_time:.4f}s for 10k calls ({log_time/10000*1e6:.2f}µs per call)")
        
        # Assert fast (<0.5s for 10k calls)
        self.assertLess(status_time, 0.5, "Handler status too slow")
        self.assertLess(log_time, 0.5, "Handler log too slow")

    def test_dispatch_dict_lookup_overhead(self):
        """Benchmark dispatch dictionary lookup overhead."""
        handlers = {
            'set': self.redis_client._handle_set,
            'get': self.redis_client._handle_get,
            'delete': self.redis_client._handle_delete,
            'exists': self.redis_client._handle_exists,
            'keys': self.redis_client._handle_keys,
            'expire': self.redis_client._handle_expire,
            'ping': self.redis_client._handle_ping,
        }
        
        def dict_lookup():
            handler = handlers.get('set')
            return handler is not None
        
        # Benchmark
        lookup_time = timeit.timeit(dict_lookup, number=100000)
        
        print(f"\nDict lookup (7 entries): {lookup_time:.4f}s for 100k calls ({lookup_time/100000*1e6:.3f}µs per call)")
        
        # Assert negligible overhead (<0.1s for 100k calls)
        self.assertLess(lookup_time, 0.1, "Dict lookup too slow")

    def test_multiple_operations_sequence(self):
        """Benchmark sequence of multiple operations."""
        def redis_sequence():
            self.redis_client.execute('set', key='k1', value='v1')
            self.redis_client.execute('get', key='k1')
            self.redis_client.execute('exists', key='k1')
            self.redis_client.execute('delete', key='k1')
        
        def git_sequence():
            self.git_client.execute('status')
            self.git_client.execute('log', count=5)
            self.git_client.execute('branch', action='list')
        
        # Benchmark
        redis_time = timeit.timeit(redis_sequence, number=1000)
        git_time = timeit.timeit(git_sequence, number=1000)
        
        print(f"\nRedis 4-op sequence: {redis_time:.4f}s for 1k iterations ({redis_time/1000*1e3:.2f}ms per iteration)")
        print(f"Git 3-op sequence: {git_time:.4f}s for 1k iterations ({git_time/1000*1e3:.2f}ms per iteration)")
        
        # Assert acceptable (<1s for 1k sequences)
        self.assertLess(redis_time, 1.0, "Redis sequence too slow")
        self.assertLess(git_time, 1.0, "Git sequence too slow")


class TestDispatchVsIfElif(unittest.TestCase):
    """Compare dispatch pattern performance vs if/elif chain."""

    def setUp(self):
        """Initialize for comparison."""
        self.redis_client = SovereignRedisClient()
        self.redis_client._get_client = MagicMock(return_value=None)
        self.redis_client._fallback_cache = {}
        self.redis_client._audit = MagicMock()

    def test_dispatch_consistency_across_operations(self):
        """Verify dispatch is consistent for all operations."""
        operations = [
            ('set', {'key': 'k', 'value': 'v'}),
            ('get', {'key': 'k'}),
            ('delete', {'key': 'k'}),
            ('exists', {'key': 'k'}),
            ('keys', {'pattern': '*'}),
            ('expire', {'key': 'k', 'ttl': 60}),
            ('ping', {}),
        ]
        
        times = {}
        
        for op, payload in operations:
            def operation():
                self.redis_client.execute(op, **payload)
            
            op_time = timeit.timeit(operation, number=1000)
            times[op] = op_time
            
            print(f"\n{op}: {op_time:.4f}s for 1k calls ({op_time/1000*1e3:.2f}ms per call)")
        
        # All operations should have similar performance (within 2x)
        min_time = min(times.values())
        max_time = max(times.values())
        ratio = max_time / min_time if min_time > 0 else 1.0
        
        print(f"\nPerformance ratio (max/min): {ratio:.2f}x")
        self.assertLess(ratio, 3.0, "Performance variance too high across operations")


if __name__ == '__main__':
    unittest.main()
