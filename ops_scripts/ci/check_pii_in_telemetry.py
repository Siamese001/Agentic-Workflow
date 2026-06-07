#!/usr/bin/env python3
"""PII-in-telemetry CI gate — block PII-shaped variable names from leaking
through telemetry / logging / OTEL emit call sites.

Closes a gap surfaced by the apps_underwriting_ai and apps_lic threat models
(Boundary 2 in both). Both apps handle regulated PII; both currently rely on
"don't put PII in telemetry" as a convention rather than a CI invariant.

This gate enforces that invariant statically. It walks Python files in
``apps_*`` + ``agentic_core/`` looking for calls to known telemetry sinks
where a positional or keyword argument matches a PII-shaped name pattern.
Fail-closed by default; per-line waivable via ``# pii: allow-<reason>``
comments.

Telemetry sinks scanned:
  - logger.{info,warning,error,exception,debug}
  - logging.{info,warning,error,exception,debug}
  - print  (logs to stdout — same risk surface)
  - _emit_*  (lifecycle_trace_contract emit functions)
  - span.set_attribute / span.add_event  (OTEL spans)
  - record_*  (QwenInferenceTelemetry-style recorders)

PII-shaped name patterns (case-insensitive):
  ssn, email, phone, dob, date_of_birth, full_name, last_name, first_name,
  address, street, zip_code, postal_code, account_number, routing_number,
  credit_card, card_number, cvv, password, api_key, secret, tax_id, ein,
  passport, drivers_license

Plan: .claude/plans/apps-svp-plus-hardening-7c4e3a.md (P3 NEXT_STEP)
"""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = REPO_ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "pii_telemetry_violations.jsonl"


# Substring patterns — any var/key name CONTAINING these (case-insensitive)
# triggers a violation when used as a telemetry argument.
_PII_PATTERNS: tuple[str, ...] = (
    "ssn",
    "email",
    "phone",
    "dob",
    "date_of_birth",
    "full_name",
    "last_name",
    "first_name",
    "address",
    "street",
    "zip_code",
    "postal_code",
    "account_number",
    "routing_number",
    "credit_card",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "secret",
    "tax_id",
    "ein",
    "passport",
    "drivers_license",
)

# Known telemetry-sink call patterns. Match by attribute name (last segment
# of `obj.method`) OR by exact function name.
_TELEMETRY_ATTRS: frozenset[str] = frozenset({
    "info", "warning", "error", "exception", "debug",
    "set_attribute", "add_event",
})

_TELEMETRY_FN_PREFIXES: tuple[str, ...] = (
    "_emit_",
    "record_",
)

_TELEMETRY_FN_NAMES: frozenset[str] = frozenset({
    "print",
})

# Security-audit sinks that are DESIGNED to record metadata about secret
# access. These functions intentionally take ``secret_name``, ``api_key_name``,
# etc. as parameters — not the secret values themselves. Excluding them
# from the scan because they ARE the audit trail; logging-vs-not-logging
# them is a different controls problem (controlled access to the audit
# log itself).
_SECURITY_AUDIT_SINKS: frozenset[str] = frozenset({
    "record_access",
    "record_denied",
    "record_grant",
    "record_revoke",
    "record_secret_access",
    "record_credential_access",
    "_emit_credential_access",
    "_emit_secret_access",
})

# Files to scan (positive set) — keep narrow to avoid scanning huge tooling.
_SCAN_DIRS: tuple[str, ...] = (
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_underwriting_ai",
    "apps_shared",
    "agentic_core",
)

# Skip patterns — tests, archived code, vendored libs, the gate itself.
_SKIP_PARTS: frozenset[str] = frozenset({
    "tests", "_archived_obsolete", "archives", "vendor", "node_modules",
})


@dataclass
class Violation:
    file: str
    line: int
    col: int
    sink: str
    pii_token: str
    snippet: str


def _is_telemetry_call(node: ast.Call) -> str | None:
    """Return a string name describing the sink, or None if not a sink.

    Security-audit sinks are excluded — they are designed to record secret
    metadata for compliance (the audit log itself is the controls boundary).
    """
    func = node.func
    if isinstance(func, ast.Attribute):
        name = func.attr
        if name in _SECURITY_AUDIT_SINKS:
            return None
        if name in _TELEMETRY_ATTRS:
            return name
        if name.startswith(_TELEMETRY_FN_PREFIXES):
            return name
    elif isinstance(func, ast.Name):
        name = func.id
        if name in _SECURITY_AUDIT_SINKS:
            return None
        if name in _TELEMETRY_FN_NAMES:
            return name
        if name.startswith(_TELEMETRY_FN_PREFIXES):
            return name
    return None


def _name_contains_pii(name: str) -> str | None:
    """Return the matched PII token, or None."""
    lower = name.lower()
    for pattern in _PII_PATTERNS:
        if pattern in lower:
            return pattern
    return None


def _line_is_waived(source_lines: list[str], *linenos: int) -> bool:
    """Honor `# pii: allow-<reason>` waiver comment on ANY of the supplied lines.

    Multi-line calls put the sink on one line and arg references on others;
    the waiver may sit on the call's opening line — check both.
    """
    for lineno in linenos:
        if 1 <= lineno <= len(source_lines):
            if "# pii: allow-" in source_lines[lineno - 1]:
                return True
    return False


def _scan_call(call: ast.Call, source_lines: list[str]) -> list[Violation]:
    sink = _is_telemetry_call(call)
    if not sink:
        return []
    violations: list[Violation] = []

    def _check_name(name: str, lineno: int, col: int) -> None:
        # Check the arg line, the call's start line, AND the previous line
        # (waiver comment can sit immediately before the call).
        if _line_is_waived(source_lines, lineno, call.lineno, call.lineno - 1):
            return
        token = _name_contains_pii(name)
        if token is None:
            return
        snippet = (
            source_lines[lineno - 1].rstrip()
            if 1 <= lineno <= len(source_lines)
            else ""
        )
        violations.append(
            Violation(
                file="",  # filled by caller
                line=lineno,
                col=col,
                sink=sink,
                pii_token=token,
                snippet=snippet[:200],
            )
        )

    # Positional args: variable references (Name) and dict-literal keys.
    for arg in call.args:
        if isinstance(arg, ast.Name):
            _check_name(arg.id, arg.lineno, arg.col_offset)
        elif isinstance(arg, ast.Dict):
            for key in arg.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    _check_name(key.value, key.lineno, key.col_offset)
        elif isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name):
            # e.g. logger.info(user.email)
            _check_name(arg.attr, arg.lineno, arg.col_offset)

    # Keyword args.
    for kw in call.keywords:
        if kw.arg is None:
            continue  # **kwargs — opaque to static scan
        _check_name(kw.arg, kw.value.lineno if hasattr(kw.value, "lineno") else 0,
                    kw.value.col_offset if hasattr(kw.value, "col_offset") else 0)

    return violations


def scan_file(path: Path) -> list[Violation]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    source_lines = source.splitlines()
    violations: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for v in _scan_call(node, source_lines):
                v.file = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
                violations.append(v)
    return violations


def _should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & _SKIP_PARTS:
        return True
    if path.name == Path(__file__).name:
        return True
    return False


def main() -> int:
    violations: list[Violation] = []
    for top in _SCAN_DIRS:
        root = REPO_ROOT / top
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            if _should_skip(py):
                continue
            violations.extend(scan_file(py))

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if violations:
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            for v in violations:
                fh.write(json.dumps(asdict(v)) + "\n")

    if violations:
        print(
            f"[B_pii_in_telemetry] tier=B status=fail violations={len(violations)}"
        )
        # Print up to 20 for visibility.
        for v in violations[:20]:
            print(
                f"  {v.file}:{v.line}:{v.col} sink={v.sink} pii={v.pii_token}\n"
                f"    {v.snippet}"
            )
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
        return 1

    print("[B_pii_in_telemetry] tier=B status=pass violations=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
