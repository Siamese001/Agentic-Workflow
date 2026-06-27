"""Clean duplicate MCP process cohorts with host-attachment guards.

The audit helper is intentionally read-only. This companion script is the
guarded write-side operation for a narrow runtime hygiene case: multiple legacy
host parent processes each own a full copy of the repo MCP launch tree.

Default mode is dry-run. Use ``--apply`` to terminate duplicate child MCP
processes. The script never terminates host parent processes and only targets
matching MCP descendants of those parents.

Codex-owned MCP children are different: stdio transport attachment is owned by
the Codex host, and the attached process cannot be inferred safely from a plain
OS process table. Codex duplicate cohorts are therefore reported but blocked
from cleanup unless the caller supplies explicit attached PID proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from typing import Any


TARGET_SERVER_MARKERS = {
    "GitKraken": ["gk.exe mcp"],
    "adg_sqlite": [
        "tools.mcp.launch_adg_sqlite_mcp",
        "tools.adg.mcp.server",
        "tools/adg/mcp/server.py",
    ],
    "memory": ["adg_memory_server.py"],
    "vector_db": ["vector_db_server.py"],
    "notion": ["@notionhq/notion-mcp-server", "notion-mcp-server"],
    "context7": ["@upstash/context7-mcp", "context7-mcp"],
    "playwright": ["@playwright/mcp", "playwright-mcp"],
}
DIRECT_ARG_SERVER_IDS = frozenset({"adg_sqlite", "memory", "vector_db"})


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


def _normalize_marker_text(value: str) -> str:
    return value.strip().strip("\"'").lower().replace("\\", "/")


def _cmdline_matches_direct_marker(cmdline: tuple[str, ...], markers: list[str]) -> bool:
    normalized_markers = tuple(_normalize_marker_text(marker) for marker in markers)
    for raw_part in cmdline:
        part = _normalize_marker_text(str(raw_part))
        for marker in normalized_markers:
            if not marker:
                continue
            if "/" in marker:
                part_without_suffix = part[:-3] if part.endswith(".py") else part
                marker_without_suffix = marker[:-3] if marker.endswith(".py") else marker
                if part_without_suffix == marker_without_suffix or part_without_suffix.endswith(
                    f"/{marker_without_suffix}"
                ):
                    return True
                continue
            if part == marker or part.endswith(f"/{marker}"):
                return True
    return False


def _matches_marker(record: ProcessRecord) -> bool:
    return _server_id(record) is not None


def _server_id(record: ProcessRecord) -> str | None:
    text = f"{record.name} {record.normalized_cmdline}".lower()
    for server_id, markers in TARGET_SERVER_MARKERS.items():
        if server_id in DIRECT_ARG_SERVER_IDS:
            if _cmdline_matches_direct_marker(record.cmdline, markers):
                return server_id
            continue
        if any(marker in text for marker in markers):
            return server_id
    return None


def _is_legacy_parent(record: ProcessRecord) -> bool:
    return record.name.lower() == "claude.exe"


def _is_codex_parent(record: ProcessRecord) -> bool:
    return record.name.lower() == "codex.exe"


def _ancestor_chain(record: ProcessRecord, by_pid: dict[int, ProcessRecord]) -> list[ProcessRecord]:
    ancestors: list[ProcessRecord] = []
    seen = {record.pid}
    parent = by_pid.get(record.ppid)
    while parent and parent.pid not in seen:
        ancestors.append(parent)
        seen.add(parent.pid)
        parent = by_pid.get(parent.ppid)
    return ancestors


def _is_codex_owned(record: ProcessRecord, by_pid: dict[int, ProcessRecord]) -> bool:
    return any(_is_codex_parent(ancestor) for ancestor in _ancestor_chain(record, by_pid))


def _matching_server_root(
    record: ProcessRecord,
    server_id: str,
    by_pid: dict[int, ProcessRecord],
) -> ProcessRecord:
    """Return the topmost same-server ancestor for one launch tree."""
    root = record
    seen = {record.pid}
    parent = by_pid.get(record.ppid)
    while parent and parent.pid not in seen:
        seen.add(parent.pid)
        if _server_id(parent) == server_id:
            root = parent
        parent = by_pid.get(parent.ppid)
    return root


def _attached_pids_from_env() -> dict[str, int]:
    attached: dict[str, int] = {}
    for server_id in TARGET_SERVER_MARKERS:
        key = f"CODEX_MCP_ATTACHED_{server_id.upper()}_PID"
        value = os.environ.get(key)
        if value:
            try:
                attached[server_id] = int(value)
            except ValueError:
                continue
    return attached


def _parse_attached_pid_args(values: list[str]) -> dict[str, int]:
    attached: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"expected SERVER=PID, got {value!r}")
        server_id, raw_pid = value.split("=", 1)
        server_id = server_id.strip()
        if server_id not in TARGET_SERVER_MARKERS:
            raise ValueError(f"unknown server id {server_id!r}")
        try:
            attached[server_id] = int(raw_pid.strip())
        except ValueError as exc:
            raise ValueError(f"invalid PID for {server_id!r}: {raw_pid!r}") from exc
    return attached


def select_duplicate_targets(
    records: list[ProcessRecord],
    keep_parent_pid: int | None = None,
) -> dict[str, Any]:
    """Select duplicate MCP descendants to terminate.

    When ``keep_parent_pid`` is omitted, the newest legacy parent with matching
    MCP descendants is kept. All matching MCP descendants under older legacy
    parents are selected.
    """
    by_pid = {record.pid: record for record in records}
    children: dict[int, list[ProcessRecord]] = {}
    for record in records:
        children.setdefault(record.ppid, []).append(record)

    legacy_parents = [record for record in records if _is_legacy_parent(record)]
    parent_targets: dict[int, list[ProcessRecord]] = {}
    for parent in legacy_parents:
        stack = list(children.get(parent.pid, []))
        descendants: list[ProcessRecord] = []
        while stack:
            child = stack.pop()
            if _is_legacy_parent(child):
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
            "reason": "no legacy-owned MCP cohorts found",
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


def select_codex_guarded_targets(
    records: list[ProcessRecord],
    attached_pids: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Select Codex-owned duplicate MCP targets only when attachment proof exists.

    ``attached_pids`` maps server IDs, such as ``memory`` or ``adg_sqlite``, to
    the PID proven by the Codex host to own the active stdio transport. Without
    that proof, Codex-owned duplicate cohorts are reported as blocked and no
    process is selected.
    """
    attached_pids = attached_pids or {}
    by_pid = {record.pid: record for record in records}
    groups: dict[str, dict[int, list[ProcessRecord]]] = {}
    for record in records:
        server_id = _server_id(record)
        if not server_id or not _is_codex_owned(record, by_pid):
            continue
        root = _matching_server_root(record, server_id, by_pid)
        groups.setdefault(server_id, {}).setdefault(root.pid, []).append(record)

    duplicate_groups = {
        server_id: {
            root_pid: sorted(rows, key=lambda record: (record.create_time, record.pid))
            for root_pid, rows in sorted(root_groups.items())
        }
        for server_id, root_groups in groups.items()
        if len(root_groups) > 1
    }
    blocked: list[dict[str, Any]] = []
    targets: list[ProcessRecord] = []
    for server_id, root_groups in sorted(duplicate_groups.items()):
        root_pids = sorted(root_groups)
        attached_pid = attached_pids.get(server_id)
        if attached_pid is None:
            blocked.append(
                {
                    "server_id": server_id,
                    "reason": "attached_pid_required",
                    "candidate_pids": root_pids,
                }
            )
            continue
        attached_root_pid = next(
            (
                root_pid
                for root_pid, rows in root_groups.items()
                if attached_pid == root_pid or any(record.pid == attached_pid for record in rows)
            ),
            None,
        )
        if attached_root_pid is None:
            blocked.append(
                {
                    "server_id": server_id,
                    "reason": "attached_pid_not_in_duplicate_group",
                    "attached_pid": attached_pid,
                    "candidate_pids": root_pids,
                }
            )
            continue
        targets.extend(
            record
            for root_pid, rows in root_groups.items()
            if root_pid != attached_root_pid
            for record in rows
        )

    if blocked:
        status = "blocked"
    elif targets:
        status = "ready"
    else:
        status = "no_codex_duplicates"

    return {
        "status": status,
        "attached_pids": dict(sorted(attached_pids.items())),
        "duplicate_server_ids": sorted(duplicate_groups),
        "blocked": blocked,
        "target_pids": [record.pid for record in targets],
        "targets": [
            {
                "pid": record.pid,
                "ppid": record.ppid,
                "server_id": _server_id(record),
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
        except (
            KeyError,
            TypeError,
            ValueError,
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            OSError,
        ):
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Terminate selected duplicate MCP child processes.")
    parser.add_argument("--keep-parent-pid", type=int, default=None, help="Legacy parent PID to keep. Defaults to newest MCP-owning legacy parent.")
    parser.add_argument(
        "--codex-attached-pid",
        action="append",
        default=[],
        metavar="SERVER=PID",
        help="Codex host-attached MCP PID proof. Repeat for each duplicate Codex server before applying Codex cleanup.",
    )
    parser.add_argument(
        "--ignore-codex-duplicates",
        action="store_true",
        help="Allow --apply to clean legacy-owned cohorts even when Codex-owned duplicates are blocked.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    records = _snapshot_processes()
    attached_pids = _attached_pids_from_env()
    try:
        attached_pids.update(_parse_attached_pid_args(args.codex_attached_pid))
    except ValueError as exc:
        parser.error(str(exc))
    selection = select_duplicate_targets(records, args.keep_parent_pid)
    codex_selection = select_codex_guarded_targets(records, attached_pids)
    result: dict[str, Any] = {
        "mode": "apply" if args.apply else "dry-run",
        "selection": selection,
        "codex_selection": codex_selection,
    }
    exit_code = 0
    if args.apply:
        if codex_selection["status"] == "blocked" and not args.ignore_codex_duplicates:
            result["termination"] = {
                "status": "blocked",
                "reason": "codex_attached_pid_required",
                "message": "Refusing cleanup because Codex-owned duplicate MCP cohorts lack host-attached PID proof.",
            }
            exit_code = 2
        else:
            target_pids = list(selection["target_pids"]) + list(codex_selection["target_pids"])
            result["termination"] = _terminate_targets(target_pids)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"mode: {result['mode']}")
        print(f"keep_parent_pid: {selection.get('keep_parent_pid')}")
        print(f"duplicate_parent_pids: {selection.get('duplicate_parent_pids')}")
        print(f"target_pids: {selection.get('target_pids')}")
        print(f"codex_selection_status: {codex_selection.get('status')}")
        print(f"codex_target_pids: {codex_selection.get('target_pids')}")
        if codex_selection.get("blocked"):
            print(f"codex_blocked: {codex_selection.get('blocked')}")
        if args.apply:
            print(f"termination: {result['termination']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
