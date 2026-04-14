"""Quick smoke test for DeferredLoader.call_serialized hang diagnosis."""

import sys, os, time, threading

sys.path.insert(0, r"C:\Git\Agentic-Workflow")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONUNBUFFERED"] = "1"

from tools.mcp.mcp_deferred_loader import DeferredLoader

print("=== T1: Basic get() ===")
dl = DeferredLoader("basic", lambda: 42, timeout=5)
v = dl.get()
print(f"  get() returned: {v}")
assert v == 42, f"Expected 42, got {v}"
print("  PASS")

print("\n=== T2: call_serialized basic ===")
dl2 = DeferredLoader("serial", lambda: 100, timeout=5)
v2 = dl2.get()
print(f"  get() returned: {v2}")
result = dl2.call_serialized(lambda r: r * 2, call_timeout=3, op_name="double")
print(f"  call_serialized returned: {result}")
assert result == 200, f"Expected 200, got {result}"
print("  PASS")

print("\n=== T3: call_serialized with wait_timeout=0 (model loaded) ===")
dl3 = DeferredLoader("loaded", lambda: 50, timeout=5)
dl3.get()  # ensure loaded
result3 = dl3.call_serialized(lambda r: r + 1, wait_timeout=0, call_timeout=3, op_name="inc")
print(f"  call_serialized returned: {result3}")
assert result3 == 51, f"Expected 51, got {result3}"
print("  PASS")

print("\n=== T4: call_serialized with wait_timeout=0 (model NOT loaded) ===")
dl4 = DeferredLoader("slow", lambda: (time.sleep(10), 99)[1], timeout=15)
# Don't call get() — model NOT loaded
t0 = time.monotonic()
try:
    result4 = dl4.call_serialized(lambda r: r, wait_timeout=0, call_timeout=3, op_name="fast-fail")
    print(f"  UNEXPECTED: returned {result4}")
except RuntimeError as e:
    elapsed = time.monotonic() - t0
    print(f"  RuntimeError in {elapsed:.2f}s: {e}")
    if elapsed < 1.0:
        print("  PASS (fail-fast)")
    else:
        print("  FAIL (took too long to fail)")
except TimeoutError as e:
    elapsed = time.monotonic() - t0
    print(f"  TimeoutError in {elapsed:.2f}s: {e}")
    print("  FAIL (should have been RuntimeError, not TimeoutError)")

print("\n=== T5: 3 concurrent call_serialized (serialization check) ===")
dl5 = DeferredLoader("concurrent", lambda: "model", timeout=5)
dl5.get()  # ensure loaded
results = []
errors = []


def serial_call(idx):
    try:
        r = dl5.call_serialized(
            lambda m: (time.sleep(0.3), f"{m}-{idx}")[1],
            call_timeout=5,
            op_name=f"concurrent-{idx}",
        )
        results.append((idx, r))
    except (RuntimeError, TimeoutError) as e:
        errors.append((idx, e))


t0 = time.monotonic()
threads = [threading.Thread(target=serial_call, args=(i,)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=10)
elapsed = time.monotonic() - t0
print(f"  {len(results)} results, {len(errors)} errors in {elapsed:.2f}s")
for idx, r in sorted(results):
    print(f"    [{idx}] = {r}")
for idx, e in sorted(errors):
    print(f"    [{idx}] ERROR = {e}")
if len(results) == 3 and elapsed >= 0.9:
    print("  PASS (serialized — 3 x 0.3s = ~0.9s)")
elif len(results) == 3 and elapsed < 0.9:
    print("  WARNING (ran concurrently, not serialized)")
else:
    print("  FAIL")

print("\n=== T6: readiness-like tool (no model call) ===")
dl6_chroma = DeferredLoader("chroma-test", lambda: "chroma_client", timeout=5)
dl6_model = DeferredLoader("model-test", lambda: (time.sleep(2), "model_obj")[1], timeout=10)
# Start model load in background
dl6_model.get(wait_timeout=0)
# Immediately check readiness flags (should be instant)
t0 = time.monotonic()
chroma_loaded = dl6_chroma.is_loaded()
model_loaded = dl6_model.is_loaded()
model_loading = dl6_model.is_loading()
elapsed = time.monotonic() - t0
print(f"  chroma_loaded={chroma_loaded}, model_loaded={model_loaded}, model_loading={model_loading}")
print(f"  Elapsed: {elapsed:.4f}s")
if elapsed < 0.01:
    print("  PASS (instant flag read)")
else:
    print("  FAIL (flag read should be instant)")

print("\n=== ALL TESTS DONE ===")
