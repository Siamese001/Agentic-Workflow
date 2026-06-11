"""Clean duplicate Claude-owned MCP process cohorts.

The audit helper is intentionally read-only. This companion script is the
guarded write-side operation for a narrow runtime hygiene case: multiple Claude
Code parent processes each own a full copy of the repo MCP launch tree.

Default mode is dry-run. Use ``--apply`` to terminate duplicate child MCP
processes. The script never terminates Claude parent processes and only targets
matching MCP descendants of Claude parents.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from typing import Any


TARGET_MARKERS = [
    "gk.exe mcp",
    "tools.mcp.launch_adg_sqlite_mcp",
    "tools.adg.mcp.server",
    "tools/adg/mcp/server.py",
    "adg_memory_server.py",
    "vector_db_server.py",
    "@notionhq/notion-mcp-server",
    "notion-mcp-server",
    "@upstash/context7-mcp",
    "context7-mcp",
    "@playwright/mcp",
    "playwright-mcp",
]


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    ppid: int
    name: str
    cmdline: tuple[str, ...]
    create_time: float

    @property
    def normalized_cmdline(self) -> str:
        return " ".join(self.cmdline).lower().replace("\\", "/")


def _matches_marker(record: ProcessRecord) -> bool:
    text = f"{record.name} {record.normalized_cmdline}".lower()
    return any(marker in text for marker in TARGET_MARKERS)


def _is_claude_parent(record: ProcessRecord) -> bool:
    return record.name.lower() == "claude.exe"


def select_duplicate_targets(
    records: list[ProcessRecord],
    keep_parent_pid: int | None = None,
) -> dict[str, Any]:
    """Select duplicate MCP descendants to terminate.

    When ``keep_parent_pid`` is omitted, the newest Claude parent with matching
    MCP descendants is kept. All matching MCP descendants under older Claude
    parents are selected.
    """
    by_pid = {record.pid: record for record in records}
    children: dict[int, list[ProcessRecord]] = {}
    for record in records:
        children.setdefault(record.ppid, []).append(record)

    claude_parents = [record for record in records if _is_claude_parent(record)]
    parent_targets: dict[int, list[ProcessRecord]] = {}
    for parent in claude_parents:
        stack = list(children.get(parent.pid, []))
        descendants: list[ProcessRecord] = []
        while stack:
            child = stack.pop()
            if _is_claude_parent(child):
                continue
            descendants.append(child)
            stack.extend(children.get(child.pid, []))
        targets = [record for record in descendants if _matches_marker(record)]
        if targets:
            parent_targets[parent.pid] = targets

    if not parent_targets:
        return {
            "keep_parent_pid": keep_parent_pid,
            "duplicate_parent_pids": [],
            "target_pids": [],
            "targets": [],
            "reason": "no claude-owned MCP cohorts found",
        }

    if keep_parent_pid is None:
        keep_parent_pid = max(parent_targets, key=lambda pid: by_pid[pid].create_time)

    duplicate_parent_pids = sorted(pid for pid in parent_targets if pid != keep_parent_pid)
    targets = [
        record
        for parent_pid in duplicate_parent_pids
        for record in parent_targets[parent_pid]
    ]
    targets.sort(key=lambda record: (record.create_time, record.pid))

    return {
        "keep_parent_pid": keep_parent_pid,
        "duplicate_parent_pids": duplicate_parent_pids,
        "target_pids": [record.pid for record in targets],
        "targets": [
            {
                "pid": record.pid,
                "ppid": record.ppid,
                "name": record.name,
                "cmdline": list(record.cmdline),
                "create_time": record.create_time,
            }
            for record in targets
        ],
    }


def _snapshot_processes() -> list[ProcessRecord]:
    import psutil  # type: ignore[import-not-found]

    records: list[ProcessRecord] = []
    current_pid = os.getpid()
    for proc in psutil.process_iter(["pid", "ppid", "name", "cmdline", "create_time"]):
        try:
            info = proc.info
            pid = int(info["pid"])
            if pid == current_pid:
                continue
            records.append(
                ProcessRecord(
                    pid=pid,
                    ppid=int(info.get("ppid") or 0),
                    name=str(info.get("name") or ""),
                    cmdline=tuple(str(part) for part in (info.get("cmdline") or ())),
                    create_time=float(info.get("create_time") or 0.0),
                )
            )
        except Exception:
            continue
    return records


def _terminate_targets(target_pids: list[int], timeout: float = 5.0) -> dict[str, Any]:
    import psutil  # type: ignore[import-not-found]

    procs = []
    for pid in target_pids:
        try:
            procs.append(psutil.Process(pid))
        except psutil.NoSuchProcess:
            pass

    for proc in procs:
        try:
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    gone, alive = psutil.wait_procs(procs, timeout=timeout)
    for proc in alive:
        try:
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if alive:
        psutil.wait_procs(alive, timeout=timeout)

    remaining = []
    for pid in target_pids:
        if psutil.pid_exists(pid):
            remaining.append(pid)
    return {
        "terminated_or_missing": len(target_pids) - len(remaining),
        "remaining_target_pids": remaining,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Terminate selected duplicate MCP child processes.")
    parser.add_argument("--keep-parent-pid", type=int, default=None, help="Claude parent PID to keep. Defaults to newest MCP-owning Claude parent.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    records = _snapshot_processes()
    selection = select_duplicate_targets(records, args.keep_parent_pid)
    result: dict[str, Any] = {
        "mode": "apply" if args.apply else "dry-run",
        "selection": selection,
    }
    if args.apply:
        result["termination"] = _terminate_targets(selection["target_pids"])

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"mode: {result['mode']}")
        print(f"keep_parent_pid: {selection.get('keep_parent_pid')}")
        print(f"duplicate_parent_pids: {selection.get('duplicate_parent_pids')}")
        print(f"target_pids: {selection.get('target_pids')}")
        if args.apply:
            print(f"termination: {result['termination']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
