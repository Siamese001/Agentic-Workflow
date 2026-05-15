#!/usr/bin/env python3
"""Fort Knox pre-write guard — Constitutional §32.

Fires on every Windsurf `pre_write_code` event. Blocks (exit 2) when
Cursor Agent attempts to write to a compiler-output artifact or to inject
hand-authored assertions that bypass the hostile verifier.

Blocking conditions (fail-closed):
1. Direct write to any `final_requirement_signoff_report.{json,sha256,
   merkle.json,signature.json}` under `artifacts/certification/`.
2. Write to any `*.xlsx` under `certification/` (XLSX outputs are
   read-only views emitted by the compiler, never authored).
3. Append to `certification/evidence_assertions.jsonl` without the
   emitter-signature header comment:
       # emitted-by: tools/cert/<name>.py
       # emitted-by: scripts/verify_<name>.py
   or from any runtime code path (`agentic_core/*`, `apps_*/*`,
   `system_learning/*`).

Bypass: `FORTKNOX_DISCIPLINE_BYPASS=1` (logged to stderr).

Input: Windsurf passes the candidate write target on stdin as JSON
`{"path": "<relpath>", "content": "<body>"}`, or falls back to
`sys.argv[1]` for path-only invocations.

Exit codes:
  0 — permitted
  2 — blocked
  1 — internal error (fail-open by default to avoid masking real work;
      stderr carries the reason)

Advisory rule: `.windsurf/rules/fortknox-certification-discipline.md`.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


_BLOCKED_REPORT_NAMES = {
    "final_requirement_signoff_report.json",
    "final_requirement_signoff_report.sha256",
    "final_requirement_signoff_report.merkle.json",
    "final_requirement_signoff_report.signature.json",
}

_EMITTER_HEADER_RE = re.compile(
    r"^#\s*emitted-by:\s*(tools/cert/|scripts/verify_)",
    re.MULTILINE,
)

_RUNTIME_FORBIDDEN_PREFIXES = ("agentic_core/", "apps_", "system_learning/")


def _posix(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _load_payload() -> tuple[str | None, str | None]:
    """Return (path, content) from Windsurf stdin JSON or argv fallback."""
    data = sys.stdin.read() if not sys.stdin.isatty() else ""
    if data.strip():
        try:
            blob = json.loads(data)
            return blob.get("path"), blob.get("content")
        except ValueError:
            pass
    if len(sys.argv) >= 2:
        return sys.argv[1], None
    return None, None


def _block(reason: str) -> int:
    print(f"[pre_write_fortknox_guard] BLOCK: {reason}", file=sys.stderr)
    print(
        "[pre_write_fortknox_guard] Bypass if intentional: "
        "FORTKNOX_DISCIPLINE_BYPASS=1",
        file=sys.stderr,
    )
    return 2


def check(path: str | None, content: str | None) -> int:
    if not path:
        return 0
    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[pre_write_fortknox_guard] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)", file=sys.stderr)
        return 0

    posix = _posix(path)
    name = Path(posix).name

    # 1. Compiler-output artifacts.
    if (
        posix.startswith("artifacts/certification/")
        and name in _BLOCKED_REPORT_NAMES
    ):
        return _block(
            f"{posix} is a compiler output. Re-run "
            "scripts/compile_requirement_signoff.py instead of editing by hand."
        )

    # 2. XLSX under certification/ (compiler-only output).
    if posix.startswith("certification/") and posix.lower().endswith(".xlsx"):
        return _block(
            f"{posix} is a read-only XLSX export. "
            "XLSX files under certification/ are compiler outputs."
        )

    # 3. Atomic assertions JSONL — require emitter signature header.
    if posix == "certification/evidence_assertions.jsonl" and content is not None:
        if not _EMITTER_HEADER_RE.search(content):
            return _block(
                "certification/evidence_assertions.jsonl requires an "
                "emitter-signature header '# emitted-by: tools/cert/... '"
                " or '# emitted-by: scripts/verify_...'"
            )

    # 4. Runtime-path emitters writing to the JSONL — forbidden regardless.
    if posix == "certification/evidence_assertions.jsonl" and content:
        # Scan for explicit forbidden emitter paths in the body.
        for prefix in _RUNTIME_FORBIDDEN_PREFIXES:
            needle = f"emitted-by: {prefix}"
            if needle in content:
                return _block(
                    f"assertions emitter path '{prefix}...' is forbidden; "
                    "runtime code paths may not emit atomic assertions."
                )

    return 0


def main() -> int:
    try:
        path, content = _load_payload()
        return check(path, content)
    except (OSError, ValueError) as exc:  # fail-open on internal error
        print(f"[pre_write_fortknox_guard] WARN: internal error {exc!r} — fail-open", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
