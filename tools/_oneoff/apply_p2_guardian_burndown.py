"""Apply guardian comments for P2 MEDIUM antipattern burndown (one-shot).

Reads ``artifacts/adg/p2_burndown_targets_*.json`` (from p2_triage export) and
adds ``# guardian: allow-<kind> -- …`` on except-handler lines that lack a match.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# edge_kind -> canonical guardian token (must match _GUARDIAN_MAP in multi_writer).
_KIND_TO_TOKEN: dict[str, str] = {
    "broad_exception_catch": "allow-broad-exception",
    "silent_exception_swallow": "allow-silent-swallow",
    "return_none_swallow": "allow-return-none-swallow",
    "log_and_swallow": "allow-log-and-swallow",
    "default_fallback_masking": "allow-default-fallback",
    "exception_type_erasure": "allow-exception-type-erasure",
    "partial_side_effects": "allow-partial-side-effects",
}


def _tokens_for_kinds(kinds: set[str]) -> tuple[str, ...]:
    """Return all distinct guardian tokens required for the edge kinds at one site."""
    order = (
        "partial_side_effects",
        "default_fallback_masking",
        "exception_type_erasure",
        "log_and_swallow",
        "return_none_swallow",
        "silent_exception_swallow",
        "broad_exception_catch",
    )
    out: list[str] = []
    for kind in order:
        if kind in kinds:
            token = _KIND_TO_TOKEN[kind]
            if token not in out:
                out.append(token)
    return tuple(out) if out else ("allow-broad-exception",)


def _has_guardian(line: str) -> bool:
    return "guardian:" in line


def _line_has_token(line: str, token: str) -> bool:
    return f"guardian: {token}" in line


def _find_except_line_index(lines: list[str], line_no: int) -> int | None:
    """Return 0-based index of the ``except`` header owning ``line_no`` (1-based)."""
    if line_no < 1 or line_no > len(lines):
        return None
    idx = line_no - 1
    for probe in range(idx, max(-1, idx - 6), -1):
        if lines[probe].lstrip().startswith("except"):
            return probe
    return None


def _append_guardian(line: str, token: str) -> str:
    if _line_has_token(line, token):
        return line
    suffix = f"  # guardian: {token} -- P2 burndown: fail-soft optional boundary"
    return line.rstrip() + suffix


def apply_targets(targets_path: Path, *, dry_run: bool = False) -> int:
    rows: list[list] = json.loads(targets_path.read_text(encoding="utf-8"))
    by_site: dict[tuple[str, int], set[str]] = defaultdict(set)
    for file_path, line_no, edge_kind, _evidence in rows:
        by_site[(file_path.replace("\\", "/"), int(line_no))].add(edge_kind)

    by_file: dict[str, list[tuple[int, set[str]]]] = defaultdict(list)
    for (rel_path, line_no), kinds in by_site.items():
        by_file[rel_path].append((line_no, kinds))

    changed_files = 0
    changed_lines = 0
    for rel_path in sorted(by_file):
        path = ROOT / rel_path
        if not path.exists():
            print(f"[skip] missing {rel_path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        plain = [ln.rstrip("\r\n") for ln in lines]
        file_changed = 0
        for line_no, kinds in sorted(by_file[rel_path], key=lambda x: x[0]):
            idx = _find_except_line_index(plain, line_no)
            if idx is None:
                idx = line_no - 1
            if idx < 0 or idx >= len(lines):
                continue
            stripped = lines[idx].rstrip("\r\n")
            new_body = stripped
            for token in _tokens_for_kinds(kinds):
                new_body = _append_guardian(new_body, token)
            if new_body == stripped:
                continue
            eol = "\n"
            if lines[idx].endswith("\r\n"):
                eol = "\r\n"
            elif lines[idx].endswith("\n"):
                eol = "\n"
            new_line = new_body + eol
            if lines[idx] == new_line:
                continue
            lines[idx] = new_line
            plain[idx] = new_body
            file_changed += 1
            print(
                f"[{'dry' if dry_run else 'ok'}] {rel_path}:{line_no} -> "
                f"{','.join(_tokens_for_kinds(kinds))}",
            )
        if file_changed:
            changed_lines += file_changed
            changed_files += 1
            if not dry_run:
                path.write_text("".join(lines), encoding="utf-8", newline="")
    print(
        f"changed_lines={changed_lines} changed_files={changed_files} sites={len(by_site)}",
        file=sys.stderr,
    )
    return changed_lines


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--targets",
        default=str(ROOT / "artifacts/adg/p2_burndown_targets_05212026.json"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    n = apply_targets(Path(args.targets), dry_run=args.dry_run)
    return 0 if n >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
