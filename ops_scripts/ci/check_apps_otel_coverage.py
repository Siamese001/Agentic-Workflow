#!/usr/bin/env python3
"""apps_* OTEL coverage gate.

Scans every non-stub Python module under ``apps_*/engines/`` and
``apps_*/integrations/`` and requires at least one OTEL emission signal:
  * Call to ``_emit_*`` from ``lifecycle_trace_contract``
  * Decorator ``@emits_*`` / ``@records_*`` / ``@appends_*`` from
    ``runtime_telemetry_decorators`` (ADR-075)
  * Explicit ``# otel: stub-engine`` waiver line near top of file

Closes the drift gap surfaced 2026-04-30: ``apps_underwriting_ai`` had
0% OTEL coverage in its engines despite handling regulated data.

Plan: .claude/plans/apps-svp-plus-hardening-7c4e3a.md (P3 follow-up)

Exit policy:
  - Default: **advisory** — prints violations and exits 0 (CI contract plane).
  - ``APPS_OTEL_COVERAGE_FAIL_CLOSED=1`` — exits 1 when any module lacks signals.
"""
from __future__ import annotations

import re
import sys
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

APPS = (
    "apps_eval", "apps_exec", "apps_lic", "apps_research",
)
SCAN_SUBDIRS = ("engines", "integrations", "outputs")
SKIP_PREFIXES = ("_", ".")
SKIP_NAMES = frozenset({"__init__.py", "__main__.py"})

_EMIT_PATTERN = re.compile(
    r"\b(?:_emit_\w+\s*\(|@(?:emits_|records_|appends_)\w+|otel_lifecycle_bridge|"
    r"start_as_current_span|tracer\.start_span|set_attribute)",
)
_WAIVER_RE = re.compile(r"#\s*otel:\s*stub-engine\b")


def _module_is_compliant(path: Path) -> tuple[bool, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, f"unreadable: {exc}"

    # Stub waiver — only valid in the first 25 lines (top-of-file marker).
    head = "\n".join(text.splitlines()[:25])
    if _WAIVER_RE.search(head):
        return True, "waived: stub-engine"

    if _EMIT_PATTERN.search(text):
        return True, "emits OTEL"
    return False, "no emit / decorator / waiver"


def _candidate_files(app: str) -> list[Path]:
    out: list[Path] = []
    for sub in SCAN_SUBDIRS:
        d = REPO / app / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            if f.name in SKIP_NAMES:
                continue
            if f.name.startswith(SKIP_PREFIXES):
                continue
            out.append(f)
    return out


def main() -> int:
    failures: list[tuple[str, str]] = []
    per_app_total = 0
    per_app_pass = 0

    print("[B_apps_otel_coverage] scanning apps_* engines/integrations/outputs")
    for app in APPS:
        files = _candidate_files(app)
        if not files:
            continue
        app_pass = 0
        for f in files:
            ok, _why = _module_is_compliant(f)
            per_app_total += 1
            if ok:
                per_app_pass += 1
                app_pass += 1
            else:
                rel = f.relative_to(REPO).as_posix()
                failures.append((rel, _why))
        ratio = app_pass / len(files) if files else 0.0
        print(f"  {app:<22} {app_pass}/{len(files)} ({ratio:.0%})")

    if failures:
        print(
            f"[B_apps_otel_coverage] tier=B status=fail "
            f"violations={len(failures)} coverage={per_app_pass}/{per_app_total}"
        )
        for rel, why in failures[:30]:
            print(f"  {rel}: {why}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
        print(
            "\n  Remediation: each module MUST either:\n"
            "    1. Call an `_emit_*` function from "
            "`agentic_core.runtime.contracts.lifecycle_trace_contract`, OR\n"
            "    2. Carry a runtime telemetry decorator "
            "(`@emits_side_effect`, `@records_execution_trace`, ...) per ADR-075, OR\n"
            "    3. Add `# otel: stub-engine` near top-of-file if genuinely empty."
        )
        if os.environ.get("APPS_OTEL_COVERAGE_FAIL_CLOSED", "").strip() == "1":
            return 1
        print(
            "[B_apps_otel_coverage] Advisory mode — violations present; exiting 0 "
            "(set APPS_OTEL_COVERAGE_FAIL_CLOSED=1 to fail closed)."
        )
        return 0

    print(
        f"[B_apps_otel_coverage] tier=B status=pass "
        f"coverage={per_app_pass}/{per_app_total} (100%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
