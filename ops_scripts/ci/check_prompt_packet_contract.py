"""C5 PA conformance CI gate (fail-closed).

Scans JSON-serialized PromptEnvelope packets and runs the C5 PA linter.
Fails the build on any PA.0 / PA.1a / PA.1b / PA.2a / PA.3a violation.

Packet sources (in order):
  1. Paths passed as CLI arguments (globs allowed).
  2. The default fixture directory if nothing passed: artifacts/prompt_packets/

Exit codes:
  0  every packet passes every contract (or no packets found)
  1  at least one packet has a PA-contract violation
  2  invalid input (non-JSON file, malformed packet, etc.)

Usage:
  python ops_scripts/ci/check_prompt_packet_contract.py
  python ops_scripts/ci/check_prompt_packet_contract.py path/to/packet.json ...
  python ops_scripts/ci/check_prompt_packet_contract.py --staged
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover

    def tqdm(iterable, **_kwargs):  # type: ignore[no-redef]
        return iterable


_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.linters.prompt_packet_linter import (  # noqa: E402
    LintReport,
    PromptPacketLintError,
    lint_prompt_packet,
)

_DEFAULT_FIXTURE_DIR = _ROOT / "artifacts" / "prompt_packets"


def _iter_staged_json() -> list[Path]:
    """Return staged .json files that look like prompt packets."""
    try:
        proc = subprocess.run(  # noqa: S603 — git invocation, bounded
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=str(_ROOT),
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[WARN] cannot query git staged files: {exc}", file=sys.stderr)
        return []
    paths: list[Path] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.endswith(".json"):
            continue
        if "prompt_packet" not in line and "prompt_envelope" not in line:
            continue
        paths.append(_ROOT / line)
    return paths


def _load_packet(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PromptPacketLintError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PromptPacketLintError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PromptPacketLintError(f"{path}: expected JSON object, got {type(data).__name__}")
    return data


def _collect_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.staged:
        paths.extend(_iter_staged_json())
    for raw in args.paths or []:
        p = Path(raw)
        if not p.is_absolute():
            p = _ROOT / p
        if p.is_dir():
            paths.extend(sorted(p.rglob("*.json")))
        elif p.exists():
            paths.append(p)
        else:
            print(f"[WARN] skipping missing path: {raw}", file=sys.stderr)
    if not paths and not args.staged and not args.paths:
        if _DEFAULT_FIXTURE_DIR.is_dir():
            paths.extend(sorted(_DEFAULT_FIXTURE_DIR.rglob("*.json")))
    return paths


def _lint_one(path: Path) -> tuple[Path, LintReport | None, str | None]:
    try:
        data = _load_packet(path)
        report = lint_prompt_packet(data)
    except PromptPacketLintError as exc:
        return path, None, str(exc)
    return path, report, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="packet JSON file or directory")
    parser.add_argument("--staged", action="store_true", help="lint staged *.json")
    parser.add_argument("--verbose", "-v", action="store_true", help="print OK lines for clean packets")
    args = parser.parse_args(argv)

    paths = _collect_paths(args)
    if not paths:
        print("[OK] no prompt packets to lint (nothing matched)")
        return 0

    total_violations = 0
    errors = 0
    for path in tqdm(paths, desc="Linting prompt packets", unit="packet"):
        _, report, error = _lint_one(path)
        try:
            rel = path.relative_to(_ROOT) if path.is_absolute() else path
        except ValueError:
            rel = path
        if error is not None:
            print(f"[ERROR] {rel}: {error}", file=sys.stderr)
            errors += 1
            continue
        assert report is not None
        if report.is_clean:
            if args.verbose:
                print(f"[OK] {rel} packet_id={report.packet_id}")
            continue
        total_violations += len(report.violations)
        print(f"[FAIL] {rel}", file=sys.stderr)
        for v in report.violations:
            loc = f" @ {v.path}" if v.path else ""
            print(
                f"  - {v.contract} {v.code}: {v.message}{loc}",
                file=sys.stderr,
            )

    if errors:
        print(
            f"\n[FAIL] {errors} packet(s) could not be parsed",
            file=sys.stderr,
        )
        return 2
    if total_violations:
        print(
            f"\n[FAIL] {total_violations} C5 PA contract violation(s) across {len(paths)} packet(s)",
            file=sys.stderr,
        )
        return 1
    print(f"[OK] {len(paths)} packet(s) passed all C5 PA contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
