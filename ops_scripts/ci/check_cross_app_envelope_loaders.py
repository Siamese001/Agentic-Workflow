"""CI gate: new `from_apps_*.py` consumer loaders MUST use CrossAppEnvelope.

Plan: apps-cross-app-precursors-c94c71 Wave 7.

Scans `apps_qna/integrations/from_apps_*.py` (and any future siblings named
from_apps_<producer>.py in any apps_*/integrations/ directory) and flags
files that do NOT import from `apps_shared.contracts.cross_app`.

Existing 4 consumers (from_apps_shared, from_apps_research, from_apps_exec,
from_apps_rg) are dual-write compliant as of Wave 4 — they import the
envelope module AND retain a regex/raw-JSON fallback with DeprecationWarning
during the mandated dual-write window. This gate catches NEW loaders that
skip the envelope path entirely.

Allowlist: `config/cross_app_envelope_loader_allowlist.yaml` (optional) for
loaders that MUST remain raw (e.g., loader for a non-cross-app local file).

Exit codes:
    0 -- clean (all `from_apps_*.py` files import the envelope module)
    1 -- violation detected
    2 -- config malformed
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = REPO_ROOT / "config" / "cross_app_envelope_loader_allowlist.yaml"

ENVELOPE_MODULE = "apps_shared.contracts.cross_app"


def _load_allowlist() -> set[str]:
    """Return set of repo-relative paths (forward-slash) exempted from the gate."""
    if not ALLOWLIST_PATH.is_file():
        return set()
    raw = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
    entries = raw.get("allowed_loaders") or []
    if not isinstance(entries, list):
        raise ValueError("allowed_loaders must be a list")
    out: set[str] = set()
    for entry in entries:
        path = entry.get("path", "")
        reason = (entry.get("reason") or "").strip()
        if not path or not reason:
            raise ValueError(
                f"Allowlist entry missing path/reason: {entry!r}"
            )
        out.add(path)
    return out


def _imports_envelope(py_file: Path) -> bool:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and (
                node.module == ENVELOPE_MODULE
                or node.module.startswith(ENVELOPE_MODULE + ".")
            ):
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == ENVELOPE_MODULE or alias.name.startswith(
                    ENVELOPE_MODULE + "."
                ):
                    return True
    return False


def _find_loaders() -> list[Path]:
    """All apps_*/integrations/from_apps_*.py files."""
    hits: list[Path] = []
    for apps_dir in sorted(REPO_ROOT.glob("apps_*")):
        integ = apps_dir / "integrations"
        if not integ.is_dir():
            continue
        for py_file in integ.glob("from_apps_*.py"):
            hits.append(py_file)
    return hits


def scan() -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    try:
        allowlist = _load_allowlist()
    except ValueError as exc:
        return [], [f"Allowlist malformed: {exc}"]

    violations: list[dict] = []
    for py_file in _find_loaders():
        rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel in allowlist:
            continue
        if not _imports_envelope(py_file):
            violations.append(
                {
                    "path": rel,
                    "reason": (
                        f"does not import from {ENVELOPE_MODULE}; "
                        "cross-app consumers MUST use typed envelopes"
                    ),
                }
            )
    return violations, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    violations, errors = scan()
    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    if args.json:
        import json as _json

        print(_json.dumps(violations, indent=2))

    if violations:
        print(
            f"FAIL: {len(violations)} from_apps_*.py loader(s) do not use "
            f"{ENVELOPE_MODULE}:",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  {v['path']}  -- {v['reason']}", file=sys.stderr)
        print(
            "\nCross-app consumers MUST load typed CrossAppEnvelope JSON with a "
            "regex/raw fallback emitting DeprecationWarning.\n"
            "See apps_shared/contracts/cross_app/ and plan "
            "apps-cross-app-precursors-c94c71.md Wave 4 for precedent.",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: all {len(_find_loaders())} from_apps_*.py loader(s) import "
        f"{ENVELOPE_MODULE}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
