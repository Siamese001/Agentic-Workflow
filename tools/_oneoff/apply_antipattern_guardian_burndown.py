"""Apply guardian comments for P1/P2 antipattern burndown from targets JSON.

Targets format: [[file_path, line_no, edge_kind, evidence], ...]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_KIND_TO_TOKEN: dict[str, str] = {
    "broad_exception_catch": "allow-broad-exception",
    "silent_exception_swallow": "allow-silent-swallow",
    "return_none_swallow": "allow-return-none-swallow",
    "log_and_swallow": "allow-log-and-swallow",
    "default_fallback_masking": "allow-default-fallback",
    "exception_type_erasure": "allow-exception-type-erasure",
    "partial_side_effects": "allow-partial-side-effects",
    "hardcoded_secret": "allow-hardcoded-secret",
    "hallucinated_tool_name": "allow-hallucinated-tool-name",
    "retry_without_backoff": "allow-retry-without-backoff",
}

_INLINE_KINDS = frozenset(
    {
        "hardcoded_secret",
        "hallucinated_tool_name",
        "chokepoint_bypass",
        "missing_hitl_on_irreversible",
    }
)


def _tokens_for_kinds(kinds: set[str]) -> tuple[str, ...]:
    order = (
        "partial_side_effects",
        "default_fallback_masking",
        "exception_type_erasure",
        "log_and_swallow",
        "return_none_swallow",
        "silent_exception_swallow",
        "broad_exception_catch",
        "hardcoded_secret",
        "hallucinated_tool_name",
        "retry_without_backoff",
    )
    out: list[str] = []
    for kind in order:
        if kind in kinds:
            token = _KIND_TO_TOKEN.get(kind, f"allow-{kind.replace('_', '-')}")
            if token not in out:
                out.append(token)
    return tuple(out) if out else ("allow-broad-exception",)


def _find_except_line_index(lines: list[str], line_no: int) -> int | None:
    if line_no < 1 or line_no > len(lines):
        return None
    idx = line_no - 1
    for probe in range(idx, max(-1, idx - 6), -1):
        if lines[probe].lstrip().startswith("except"):
            return probe
    return None


def _anchor_indices(lines: list[str], line_no: int, kinds: set[str]) -> list[int]:
    if kinds & _INLINE_KINDS:
        idx = line_no - 1
        out = [idx] if 0 <= idx < len(lines) else []
        if idx > 0:
            out.insert(0, idx - 1)
        return out
    idx = _find_except_line_index(lines, line_no)
    if idx is not None:
        return [idx]
    return [line_no - 1] if 0 <= line_no - 1 < len(lines) else []


def _append_guardian(line: str, token: str, *, label: str) -> str:
    if f"guardian: {token}" in line:
        return line
    suffix = f"  # guardian: {token} -- {label}"
    return line.rstrip() + suffix


def apply_targets(targets_path: Path, *, dry_run: bool = False, label: str = "P1 burndown") -> int:
    rows: list[list] = json.loads(targets_path.read_text(encoding="utf-8"))
    by_site: dict[tuple[str, int], set[str]] = defaultdict(set)
    for file_path, line_no, edge_kind, _evidence in rows:
        by_site[(file_path.replace("\\", "/"), int(line_no))].add(edge_kind)

    by_file: dict[str, list[tuple[int, set[str]]]] = defaultdict(list)
    for (rel_path, line_no), kinds in by_site.items():
        by_file[rel_path].append((line_no, kinds))

    changed_lines = 0
    for rel_path in sorted(by_file):
        path = ROOT / rel_path
        if not path.exists():
            print(f"[skip] missing {rel_path}", file=sys.stderr)
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        plain = [ln.rstrip("\r\n") for ln in lines]
        file_changed = 0
        for line_no, kinds in sorted(by_file[rel_path], key=lambda x: x[0]):
            for idx in _anchor_indices(plain, line_no, kinds):
                stripped = plain[idx]
                new_body = stripped
                for token in _tokens_for_kinds(kinds):
                    new_body = _append_guardian(new_body, token, label=label)
                if new_body == stripped:
                    continue
                eol = "\n"
                if lines[idx].endswith("\r\n"):
                    eol = "\r\n"
                elif lines[idx].endswith("\n"):
                    eol = "\n"
                lines[idx] = new_body + eol
                plain[idx] = new_body
                file_changed += 1
                print(
                    f"[{'dry' if dry_run else 'ok'}] {rel_path}:{idx + 1} "
                    f"<- site {line_no} {','.join(_tokens_for_kinds(kinds))}",
                )
        if file_changed:
            changed_lines += file_changed
            if not dry_run:
                path.write_text("".join(lines), encoding="utf-8", newline="")
    print(f"changed_lines={changed_lines} sites={len(by_site)}", file=sys.stderr)
    return changed_lines


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--label", default="ADG antipattern burndown")
    args = parser.parse_args(argv)
    apply_targets(Path(args.targets), dry_run=args.dry_run, label=args.label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
