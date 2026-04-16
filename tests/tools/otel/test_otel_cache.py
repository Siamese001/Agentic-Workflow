from tools.otel.otel_state import TraceCache


def test_trace_cache_is_bounded_lru():
    cache = TraceCache(max_traces=2)
    cache.put("a", {"trace_id": "a"})
    cache.put("b", {"trace_id": "b"})
    assert cache.get("a") == {"trace_id": "a"}
    cache.put("c", {"trace_id": "c"})

    assert cache.get("a") == {"trace_id": "a"}
    assert cache.get("b") is None
    assert cache.get("c") == {"trace_id": "c"}
