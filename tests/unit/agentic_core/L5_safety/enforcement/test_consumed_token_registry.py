"""
Tests for G07 ConsumedTokenRegistry — single-use enforcement (P8.07).
"""

from __future__ import annotations

import threading

import pytest

from agentic_core.L5_safety.enforcement.consumed_token_registry import (
    ConsumptionRecord,
    InMemoryConsumedTokenRegistry,
    SqliteConsumedTokenRegistry,
    TokenAlreadyConsumedError,
)


@pytest.fixture
def in_memory() -> InMemoryConsumedTokenRegistry:
    return InMemoryConsumedTokenRegistry()


@pytest.fixture
def sqlite_registry(tmp_path) -> SqliteConsumedTokenRegistry:
    return SqliteConsumedTokenRegistry(tmp_path / "consumed.sqlite")


# Parametrize over both backends so contract is identical
@pytest.fixture(params=["in_memory", "sqlite_registry"])
def registry(request, in_memory, sqlite_registry):
    return {"in_memory": in_memory, "sqlite_registry": sqlite_registry}[request.param]


def test_first_consume_succeeds(registry) -> None:
    record = registry.consume("tok-1", consumed_by="agent-A")
    assert isinstance(record, ConsumptionRecord)
    assert record.token_id == "tok-1"
    assert record.consumed_by == "agent-A"
    assert record.consumed_at > 0


def test_second_consume_raises(registry) -> None:
    registry.consume("tok-1", consumed_by="agent-A")
    with pytest.raises(TokenAlreadyConsumedError, match=r"tok-1"):
        registry.consume("tok-1", consumed_by="agent-B")


def test_replay_by_same_actor_still_blocked(registry) -> None:
    """Even the same actor cannot replay — single_use means single, period."""
    registry.consume("tok-1", consumed_by="agent-A")
    with pytest.raises(TokenAlreadyConsumedError):
        registry.consume("tok-1", consumed_by="agent-A")


def test_has_been_consumed_reflects_state(registry) -> None:
    assert registry.has_been_consumed("tok-X") is False
    registry.consume("tok-X", consumed_by="agent-A")
    assert registry.has_been_consumed("tok-X") is True


def test_distinct_tokens_independent(registry) -> None:
    registry.consume("tok-1", consumed_by="agent-A")
    registry.consume("tok-2", consumed_by="agent-A")
    assert registry.has_been_consumed("tok-1") is True
    assert registry.has_been_consumed("tok-2") is True
    assert registry.has_been_consumed("tok-3") is False


def test_in_memory_concurrent_consume_only_one_wins() -> None:
    """Threading stress: 50 threads racing on the same token; exactly 1 succeeds."""
    reg = InMemoryConsumedTokenRegistry()
    successes: list[str] = []
    failures: list[str] = []
    lock = threading.Lock()

    def attempt(idx: int) -> None:
        try:
            reg.consume("tok-race", consumed_by=f"agent-{idx}")
            with lock:
                successes.append(f"agent-{idx}")
        except TokenAlreadyConsumedError:
            with lock:
                failures.append(f"agent-{idx}")

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(successes) == 1, f"Expected exactly 1 winner, got {len(successes)}: {successes}"
    assert len(failures) == 49


def test_sqlite_persistence_across_instances(tmp_path) -> None:
    """Token consumed by one SqliteConsumedTokenRegistry instance is visible to another
    pointing at the same db path — durable across processes."""
    db_path = tmp_path / "persistent.sqlite"
    reg1 = SqliteConsumedTokenRegistry(db_path)
    reg1.consume("tok-persistent", consumed_by="agent-A")

    # Fresh registry instance, same backing file
    reg2 = SqliteConsumedTokenRegistry(db_path)
    assert reg2.has_been_consumed("tok-persistent") is True
    with pytest.raises(TokenAlreadyConsumedError):
        reg2.consume("tok-persistent", consumed_by="agent-B")
