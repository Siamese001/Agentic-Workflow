"""Performance tests for cache throughput."""
from __future__ import annotations
import time
from runtime.shared.cache import generate_llm_cache_key, generate_llm_cache_key_with_fingerprint, should_invalidate_cache

class TestCacheKeyThroughput:
    def test_cache_key_throughput_10k_per_second(self):
        """Can generate at least 10k cache keys per second."""
        messages = [{"role": "user", "content": "Test"}]
        iterations = 10000

        start = time.perf_counter()
        for i in range(iterations):
            generate_llm_cache_key(model="gpt-4o", messages=messages)
        elapsed = time.perf_counter() - start

        throughput = iterations / elapsed
        assert throughput >= 10000, f"Throughput: {throughput:.0f}/s"

    def test_fingerprint_key_throughput(self):
        """Fingerprinted keys maintain high throughput."""
        messages = [{"role": "user", "content": "Test"}]
        iterations = 5000

        start = time.perf_counter()
        for i in range(iterations):
            generate_llm_cache_key_with_fingerprint(
                model="gpt-4o",
                messages=messages,
                fingerprint=f"fp_{i}",
            )
        elapsed = time.perf_counter() - start

        throughput = iterations / elapsed
        assert throughput >= 5000, f"Throughput: {throughput:.0f}/s"

class TestBatchProcessingThroughput:
    def test_batch_key_generation(self):
        """Batch key generation has no pathological overhead."""
        batch_sizes = [10, 100, 1000]
        times_per_item = []

        for batch_size in batch_sizes:
            messages = [{"role": "user", "content": f"Msg {i}"} for i in range(batch_size)]
            start = time.perf_counter()
            for msg_list in [[m] for m in messages]:
                generate_llm_cache_key(model="gpt-4o", messages=msg_list)
            elapsed = time.perf_counter() - start
            times_per_item.append(elapsed / batch_size)

        # Per-item time should not increase significantly with batch size
        ratio = times_per_item[-1] / times_per_item[0]
        assert ratio < 2.0, f"Per-item time ratio: {ratio:.2f}"
