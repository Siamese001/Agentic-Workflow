"""Smoke test for the MCP threading fix (check_same_thread=False + self-heal + watchdog)."""

from __future__ import annotations

import sqlite3
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

print("=== test 1: modules import cleanly ===")
from tools.adg.core.sqlite_backend import SQLiteBackend  # noqa: E402
from tools.adg.core.graph_projection_backend import GraphProjectionBackend  # noqa: E402
from tools.adg.mcp.runtime import ADGServerRuntime  # noqa: E402

print(
    f"  OK: imports fine.  SQLiteBackend has _lifecycle_lock attr: {hasattr(SQLiteBackend, '_lifecycle_lock')}"
)

print("\n=== test 2: SQLiteBackend has self-heal in _require_conn ===")
import inspect  # noqa: E402

src = inspect.getsource(SQLiteBackend._require_conn)
assert "self-heal" in src.lower() or "self_heal" in src.lower() or "ProgrammingError" in src
assert "check_same_thread" in inspect.getsource(SQLiteBackend._connect)
print("  OK: _require_conn contains self-heal logic and _connect uses check_same_thread=False")

print("\n=== test 3: construct backend + query from TWO different threads ===")
backend = SQLiteBackend()
results: dict[str, int | str] = {}


def query_thread(tid: str) -> None:
    try:
        conn = backend._require_conn()
        row = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()
        results[tid] = row[0]
    except Exception as exc:
        results[tid] = f"ERROR: {type(exc).__name__}: {exc}"


t1 = threading.Thread(target=query_thread, args=("t1",))
t2 = threading.Thread(target=query_thread, args=("t2",))
t1.start()
t2.start()
t1.join()
t2.join()
print(f"  t1 result: {results['t1']}")
print(f"  t2 result: {results['t2']}")
assert isinstance(results["t1"], int), f"t1 failed: {results['t1']}"
assert isinstance(results["t2"], int), f"t2 failed: {results['t2']}"
assert results["t1"] == results["t2"]
print(f"  OK: both threads got {results['t1']} nodes without threading error")

print("\n=== test 4: reopen from ONE thread, query from ANOTHER (the failure mode we fixed) ===")
reopen_thread = threading.Thread(target=backend.reopen)
reopen_thread.start()
reopen_thread.join()
# Now query from main thread
conn = backend._require_conn()
count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
print(f"  main-thread query after cross-thread reopen: {count} nodes")
assert isinstance(count, int) and count > 0
print("  OK: no threading error post-reopen")

print("\n=== test 5: self-heal triggers on artificial ProgrammingError ===")
# Poison the connection by manually rebinding it to a new thread
poison_box: list[sqlite3.Connection] = []


def make_conn_on_other_thread() -> None:
    c = sqlite3.connect(":memory:", check_same_thread=True)  # strict!
    poison_box.append(c)


t = threading.Thread(target=make_conn_on_other_thread)
t.start()
t.join()
# Swap in the poisoned connection
original = backend._conn
backend._conn = poison_box[0]
# Query — should trigger self-heal
try:
    conn = backend._require_conn()
    # If self-heal fired, _conn should now be a fresh connection (not the poisoned one)
    assert backend._conn is not poison_box[0], "self-heal did NOT replace the poisoned connection"
    print("  OK: self-heal replaced poisoned connection without raising to caller")
except sqlite3.ProgrammingError as exc:
    print(f"  FAIL: threading error leaked to caller: {exc}")
    raise
finally:
    # Restore original for clean teardown
    if backend._conn is not original and backend._conn is not None:
        try:
            backend._conn.close()
        except Exception:
            pass
    backend._conn = original

print("\n=== test 6: runtime.reopen_connections no longer uses ThreadPoolExecutor ===")
rt_src = inspect.getsource(ADGServerRuntime.reopen_connections)
# "ThreadPoolExecutor" may appear in RCA comment + docstring prose. Only the
# ACTUAL INSTANTIATION is forbidden. Check for "with ... ThreadPoolExecutor"
# which is the only legitimate way to use one as a context manager.
lines = [ln for ln in rt_src.splitlines() if not ln.strip().startswith("#")]
nc_src = "\n".join(lines)
assert "with _cf.ThreadPoolExecutor" not in nc_src, "ThreadPool context-manager still in use!"
assert "ex.submit(service.reopen)" not in nc_src, "ThreadPool submit pattern still in use!"
assert "adg-reopen-watchdog" in rt_src, "Watchdog naming missing"
assert "threading.Thread" in rt_src and "threading.Event" in rt_src, "Watchdog pattern missing"
print("  OK: runtime.reopen_connections uses watchdog-thread pattern, not ThreadPoolExecutor")

backend.close()
print("\nALL THREADING SMOKE TESTS PASSED")
