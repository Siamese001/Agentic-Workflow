"""
Full 3-tier smoke test for Sequential Thinking MCP server.
Tests: handshake, single thought, multi-step chain, branch + revision.
"""

import json
import subprocess
import sys
import threading
import time

NODE = r"C:\Users\amita\AppData\Roaming\fnm\node-versions\v24.13.0\installation\node.exe"
SERVER = r"C:\Users\amita\AppData\Roaming\fnm\node-versions\v24.13.0\installation\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js"
CWD = r"C:\Users\amita\AppData\Roaming\fnm\node-versions\v24.13.0\installation\node_modules\@modelcontextprotocol\server-sequential-thinking"


def main():
    proc = subprocess.Popen(
        [NODE, SERVER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=CWD,
        env={
            "DISABLE_THOUGHT_LOGGING": "true",
            "PATH": "",
            "SystemRoot": r"C:\Windows",
        },
    )
    time.sleep(1.5)

    msg_id = [0]

    def next_id():
        msg_id[0] += 1
        return msg_id[0]

    def send(msg):
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line.encode())
        proc.stdin.flush()

    def read(timeout=5):
        result = [None]

        def reader():
            try:
                line = proc.stdout.readline()
                if line:
                    result[0] = json.loads(line.decode().strip())
            except Exception as e:
                result[0] = {"_error": str(e)}

        t = threading.Thread(target=reader, daemon=True)
        t.start()
        t.join(timeout)
        if result[0] is None:
            return {"_error": "TIMEOUT"}
        return result[0]

    results = {}
    PASS = 0
    FAIL = 0

    def check(name, resp, assertion_fn):
        nonlocal PASS, FAIL
        ok = False
        detail = ""
        try:
            ok = assertion_fn(resp)
            detail = "OK"
        except Exception as e:
            detail = str(e)
        if ok:
            PASS += 1
            results[name] = "PASS"
            print(f"  [PASS] {name}")
        else:
            FAIL += 1
            results[name] = f"FAIL: {detail}"
            print(f"  [FAIL] {name} -- {detail}")
        return ok

    # ========== HANDSHAKE ==========
    print("=" * 60)
    print("HANDSHAKE: initialize -> initialized -> tools/list")
    print("=" * 60)

    rid = next_id()
    send(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "smoke-test", "version": "1.0"},
            },
        },
    )
    init_resp = read(5)
    check(
        "init_response",
        init_resp,
        lambda r: r.get("result", {}).get("serverInfo", {}).get("name") == "sequential-thinking-server",
    )
    check(
        "init_protocol",
        init_resp,
        lambda r: r.get("result", {}).get("protocolVersion") == "2024-11-05",
    )
    check(
        "init_capabilities",
        init_resp,
        lambda r: "tools" in r.get("result", {}).get("capabilities", {}),
    )

    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    time.sleep(0.3)

    rid = next_id()
    send({"jsonrpc": "2.0", "id": rid, "method": "tools/list", "params": {}})
    list_resp = read(5)
    tools = [t["name"] for t in list_resp.get("result", {}).get("tools", [])] if list_resp else []
    check("tools_list_returns", list_resp, lambda r: "_error" not in r)
    check(
        "tool_sequentialthinking_present",
        tools,
        lambda t: "sequentialthinking" in t,
    )

    # ========== TIER 1: Single thought ==========
    print()
    print("=" * 60)
    print("TIER 1: Single thought")
    print("=" * 60)

    rid = next_id()
    send(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {
                "name": "sequentialthinking",
                "arguments": {
                    "thought": "Break 144 into prime factors: 144 = 2^4 * 3^2",
                    "nextThoughtNeeded": False,
                    "thoughtNumber": 1,
                    "totalThoughts": 1,
                },
            },
        },
    )
    t1 = read(5)
    t1_content = {}
    try:
        t1_content = json.loads(t1["result"]["content"][0]["text"])
    except Exception:
        pass
    check("tier1_response", t1, lambda r: "result" in r)
    check("tier1_thought_num", t1_content, lambda c: c.get("thoughtNumber") == 1)
    check("tier1_not_needed", t1_content, lambda c: c.get("nextThoughtNeeded") is False)
    check("tier1_history_len", t1_content, lambda c: c.get("thoughtHistoryLength") == 1)
    print(f"  Result: {json.dumps(t1_content)}")

    # ========== TIER 2: Multi-step chain (4 thoughts) ==========
    print()
    print("=" * 60)
    print("TIER 2: Multi-step chain (4 thoughts)")
    print("=" * 60)

    thoughts = [
        "Step 1: Define the problem - find shortest path in weighted graph with negative edges",
        "Step 2: Dijkstra fails with negative edges. Need Bellman-Ford algorithm.",
        "Step 3: Bellman-Ford relaxes all edges V-1 times. Time complexity O(VE).",
        "Step 4: Can also detect negative cycles by running one more iteration.",
    ]
    for i, thought in enumerate(thoughts):
        rid = next_id()
        is_last = i == 3
        send(
            {
                "jsonrpc": "2.0",
                "id": rid,
                "method": "tools/call",
                "params": {
                    "name": "sequentialthinking",
                    "arguments": {
                        "thought": thought,
                        "nextThoughtNeeded": not is_last,
                        "thoughtNumber": i + 1,
                        "totalThoughts": 4,
                    },
                },
            },
        )
        resp = read(5)
        content = {}
        try:
            content = json.loads(resp["result"]["content"][0]["text"])
        except Exception:
            pass
        expected_history = 1 + (i + 1)  # 1 from tier1 + current
        check(
            f"tier2_step{i + 1}_num",
            content,
            lambda c, exp=i + 1: c.get("thoughtNumber") == exp,
        )
        check(
            f"tier2_step{i + 1}_history",
            content,
            lambda c, exp=expected_history: c.get("thoughtHistoryLength") == exp,
        )
        hl = content.get("thoughtHistoryLength")
        nn = content.get("nextThoughtNeeded")
        print(f"  Step {i + 1}: historyLen={hl}, nextNeeded={nn}")

    # ========== TIER 3: Branch + Revision ==========
    print()
    print("=" * 60)
    print("TIER 3: Branch + Revision")
    print("=" * 60)

    # Branch from thought 2
    rid = next_id()
    send(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {
                "name": "sequentialthinking",
                "arguments": {
                    "thought": "BRANCH: What if we use Floyd-Warshall instead for all-pairs shortest paths?",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 5,
                    "totalThoughts": 7,
                    "branchFromThought": 2,
                    "branchId": "floyd-alt",
                },
            },
        },
    )
    branch_resp = read(5)
    branch_content = {}
    try:
        branch_content = json.loads(branch_resp["result"]["content"][0]["text"])
    except Exception:
        pass
    check("tier3_branch_response", branch_resp, lambda r: "result" in r)
    check(
        "tier3_branch_id_tracked",
        branch_content,
        lambda c: "floyd-alt" in c.get("branches", []),
    )
    br = branch_content.get("branches")
    hl = branch_content.get("thoughtHistoryLength")
    print(f"  Branch: branches={br}, historyLen={hl}")

    # Revision of thought 3
    rid = next_id()
    send(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {
                "name": "sequentialthinking",
                "arguments": {
                    "thought": "REVISION: Actually Bellman-Ford time is O(VE) but with early termination it can be faster in practice.",
                    "nextThoughtNeeded": False,
                    "thoughtNumber": 6,
                    "totalThoughts": 7,
                    "isRevision": True,
                    "revisesThought": 3,
                },
            },
        },
    )
    rev_resp = read(5)
    rev_content = {}
    try:
        rev_content = json.loads(rev_resp["result"]["content"][0]["text"])
    except Exception:
        pass
    check("tier3_revision_response", rev_resp, lambda r: "result" in r)
    check(
        "tier3_revision_history",
        rev_content,
        lambda c: c.get("thoughtHistoryLength") == 7,
    )
    check(
        "tier3_branches_preserved",
        rev_content,
        lambda c: "floyd-alt" in c.get("branches", []),
    )
    hl = rev_content.get("thoughtHistoryLength")
    br = rev_content.get("branches")
    print(f"  Revision: historyLen={hl}, branches={br}")

    # ========== SUMMARY ==========
    print()
    print("=" * 60)
    print(f"SUMMARY: {PASS} PASSED, {FAIL} FAILED out of {PASS + FAIL} checks")
    print("=" * 60)
    for name, status in results.items():
        print(f"  {status:6s} | {name}")

    proc.terminate()
    stderr_out = proc.stderr.read().decode()[:300]
    if stderr_out.strip():
        print(
            f"\nSTDERR (should be minimal with DISABLE_THOUGHT_LOGGING=true):\n  {stderr_out.strip()[:200]}",
        )

    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
