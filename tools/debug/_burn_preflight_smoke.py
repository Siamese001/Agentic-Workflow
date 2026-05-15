"""Smoke test — preflight gate + audit hook."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
hb_path = repo / "artifacts" / "windsurf" / "mcp_health_heartbeat.json"
vl_path = repo / "artifacts" / "windsurf" / "mcp_preflight_violations.jsonl"


def _run_pre(payload: dict) -> subprocess.CompletedProcess:
    script = repo / ".windsurf" / "scripts" / "pre_mcp_gate.py"
    env = os.environ.copy()
    env.pop("MCP_PREFLIGHT_BYPASS", None)
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )


def _load_post_module():
    spec = importlib.util.spec_from_file_location(
        "post_cursor_agent_mcp_preflight_audit",
        str(repo / ".windsurf" / "scripts" / "post_cursor_agent_mcp_preflight_audit.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


print("=== test 1: module imports ===")
_ = _load_post_module()
import importlib

spec = importlib.util.spec_from_file_location(
    "pre_mcp_gate", str(repo / ".windsurf" / "scripts" / "pre_mcp_gate.py")
)
pre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pre)
assert "adg_close_connections" in pre._DESTRUCTIVE_PREFLIGHT_TOOLS
print("  OK: pre_mcp_gate exposes _DESTRUCTIVE_PREFLIGHT_TOOLS")

print("\n=== test 2: destructive call BLOCKED without heartbeat ===")
# Wipe heartbeat to force stale
if hb_path.exists():
    hb_path.unlink()
# First call: grace window — allow
res = _run_pre({"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_close_connections"}})
print(f"  first call rc={res.returncode} (expect 0 — grace)")
assert res.returncode == 0, res.stderr
assert "PREFLIGHT_GRACE" in res.stderr
# Second call: synthetic heartbeat written as stale — should BLOCK
res = _run_pre({"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_close_connections"}})
print(f"  second call rc={res.returncode} (expect 2 — blocked)")
assert res.returncode == 2, f"expected block, got {res.returncode}\nstderr={res.stderr}"
assert "BLOCKED" in res.stderr

print("\n=== test 3: fresh heartbeat ALLOWS destructive call ===")
import time

hb_path.write_text(json.dumps({"adg_sqlite": time.time()}), encoding="utf-8")
res = _run_pre({"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_close_connections"}})
print(f"  rc={res.returncode} (expect 0 — fresh heartbeat)")
assert res.returncode == 0, res.stderr

print("\n=== test 4: bypass env var allows ===")
script = repo / ".windsurf" / "scripts" / "pre_mcp_gate.py"
env = os.environ.copy()
env["MCP_PREFLIGHT_BYPASS"] = "1"
hb_path.write_text(json.dumps({"adg_sqlite": 0.0}), encoding="utf-8")  # stale
res2 = subprocess.run(
    [sys.executable, str(script)],
    input=json.dumps(
        {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_close_connections"}}
    ),
    capture_output=True,
    text=True,
    timeout=10,
    env=env,
)
print(f"  rc={res2.returncode} (expect 0 — bypass)")
assert res2.returncode == 0, res2.stderr

print("\n=== test 5: non-destructive calls PASS without heartbeat ===")
if hb_path.exists():
    hb_path.unlink()
res = _run_pre({"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}})
print(f"  rc={res.returncode} (expect 0 — non-destructive)")
# may still block on unrelated grounds (health check), but preflight itself must pass
# We accept either 0 (all gates pass) or 2 only if NOT because of preflight
if res.returncode == 2:
    assert "destructive" not in res.stderr.lower() or "PREFLIGHT" not in res.stderr
    print(f"  (blocked by another gate, not preflight — OK) stderr: {res.stderr[:200]}")

print("\n=== test 6: post-hook detects violation in response ===")
post = _load_post_module()
# Simulate a response with a destructive call and no prior health
response = """
<function_calls>
<invoke name="mcp1_adg_close_connections">
</invoke>
</function_calls>
"""
invocations = post._extract_tool_invocations(response)
assert invocations == [(0, "mcp1_adg_close_connections")], invocations
# stale heartbeat → should produce 1 violation
viols = post.detect_preflight_violations(invocations, {"adg_sqlite": 0.0})
assert len(viols) == 1, viols
assert viols[0]["server"] == "adg_sqlite"
print(f"  OK: detected {len(viols)} violation")

print("\n=== test 7: in-response health call absolves destructive ===")
response2 = """
<function_calls>
<invoke name="mcp1_adg_health">
</invoke>
</function_calls>
<function_calls>
<invoke name="mcp1_adg_close_connections">
</invoke>
</function_calls>
"""
invocations2 = post._extract_tool_invocations(response2)
viols2 = post.detect_preflight_violations(invocations2, {})  # no prior heartbeat
assert len(viols2) == 0, f"expected 0 violations (in-response health), got {viols2}"
print("  OK: in-response health absolves destructive call")

print("\nALL SMOKE TESTS PASSED")
