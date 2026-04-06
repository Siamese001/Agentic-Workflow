"""Tests for new antipattern detectors in _AntipatternVisitor.

Tests:
- blocking_call_in_async: time.sleep in async def → fires; dict.get() in async def → no fire
- global_state_mutation: _CACHE = value in function body → fires; lazy-init guard → no fire
- retry_without_backoff: for i in range(3): try/except → fires; for item in collection → no fire
"""

import ast

import pytest

from agentic_core.adg.extraction.visitors import _AntipatternVisitor, VisitorContext


def _parse_and_visit(code: str, source_file: str = "test.py") -> list[tuple[int, str, str]]:
    """Helper: parse code and run _AntipatternVisitor, return antipattern list."""
    ctx = VisitorContext(
        module_adg_name="test_module",
        source_file=source_file,
    )
    visitor = _AntipatternVisitor(ctx)
    tree = ast.parse(code, filename=source_file)
    visitor.visit(tree)
    # Extract from edges
    return [
        (edge.line_no, edge.edge_kind, edge.symbol)
        for edge in visitor.extract_edges()
        if edge.relation_type == "antipattern"
    ]


class TestBlockingCallInAsync:
    """Test blocking_call_in_async detector."""

    def test_time_sleep_in_async_fires(self) -> None:
        code = """
async def foo():
    time.sleep(1)
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "blocking_call_in_async" and "time.sleep" in sym
            for _, cat, sym in antipatterns
        )

    def test_requests_get_in_async_fires(self) -> None:
        code = """
async def foo():
    requests.get("https://example.com")
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "blocking_call_in_async" and "requests.get" in sym
            for _, cat, sym in antipatterns
        )

    def test_dict_get_in_async_no_fire(self) -> None:
        code = """
async def foo():
    data = cache.get("key")
"""
        antipatterns = _parse_and_visit(code)
        assert not any(
            cat == "blocking_call_in_async" for _, cat, _ in antipatterns
        )

    def test_subprocess_run_in_async_fires(self) -> None:
        code = """
async def foo():
    subprocess.run(["ls"])
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "blocking_call_in_async" and "subprocess.run" in sym
            for _, cat, sym in antipatterns
        )


class TestGlobalStateMutation:
    """Test global_state_mutation detector."""

    def test_uppercase_assignment_fires(self) -> None:
        code = """
def foo():
    GLOBAL_CACHE = {}
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "global_state_mutation" and "GLOBAL_CACHE" in sym
            for _, cat, sym in antipatterns
        )

    def test_lowercase_assignment_no_fire(self) -> None:
        code = """
def foo():
    local_var = {}
"""
        antipatterns = _parse_and_visit(code)
        assert not any(
            cat == "global_state_mutation" for _, cat, _ in antipatterns
        )

    # Note: Lazy-init guard detection requires parent tracking (TODO)
    # For now, we fire on all UPPER_CASE assignments


class TestRetryWithoutBackoff:
    """Test retry_without_backoff detector."""

    def test_for_range_with_try_except_fires(self) -> None:
        code = """
for i in range(3):
    try:
        do_something()
    except Exception:
        pass
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "retry_without_backoff" and "for_retry" in sym
            for _, cat, sym in antipatterns
        )

    def test_for_collection_no_fire(self) -> None:
        code = """
for item in items:
    try:
        do_something()
    except Exception:
        pass
"""
        antipatterns = _parse_and_visit(code)
        # Should not fire because it's not a range() loop
        assert not any(
            cat == "retry_without_backoff" for _, cat, _ in antipatterns
        )

    def test_for_range_with_sleep_no_fire(self) -> None:
        code = """
for i in range(3):
    try:
        do_something()
    except Exception:
        pass
    time.sleep(1)
"""
        antipatterns = _parse_and_visit(code)
        # Should not fire because has backoff
        assert not any(
            cat == "retry_without_backoff" for _, cat, _ in antipatterns
        )

    def test_while_with_try_except_fires(self) -> None:
        code = """
while True:
    try:
        do_something()
        break
    except Exception:
        pass
"""
        antipatterns = _parse_and_visit(code)
        assert any(
            cat == "retry_without_backoff" and "while_retry" in sym
            for _, cat, sym in antipatterns
        )
