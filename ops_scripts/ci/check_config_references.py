"""CI gate: env-flag reference integrity between code and .env.example.

Purpose
-------
ADG catches structural negatives (forbidden imports, orphan adapters).
Expected-wiring catches behavioural positives ("X must call Y"). Neither can
see a typo in an environment-flag name, or a flag that is read but never
declared in any config SSOT. That class of bug produced the entire semantic-
cache incident (`SEMANTIC_CACHE_D2_ENABLED`, `SEMANTIC_CACHE_PROMOTE_ENABLED`,
`SEMANTIC_CACHE_L1_WARMUP_LIMIT` were all lived-in-code but never declared in
`.env.example`, so nobody knew how to turn them on).

Scope
-----
AST-scan every tracked .py file under known code roots for string-literal flag
reads:

- ``os.getenv("FLAG")`` / ``os.getenv("FLAG", default)``
- ``os.environ.get("FLAG")``
- ``os.environ["FLAG"]`` (subscript)

Cross-reference against:

- Declared keys in ``.env.example`` (the SSOT the gate treats as canonical)
- An allowlist at ``config/config_references_allowlist.yaml`` for flags that
  are legitimately external (OS-provided, CI-runner-provided, provider SDKs
  that read their own env vars). Allowlist entries are simple strings.

Reports two asymmetries:

1. ``undeclared_reads`` — flag read in code, absent from .env.example and
   allowlist. Default: **FAIL**.
2. ``unreferenced_keys`` — flag in .env.example with zero code reads.
   Default: WARN only (tooling, CI, or runbook commands may read it).

Exits 0 on clean, 1 on undeclared reads.

Run
---
    python ops_scripts/ci/check_config_references.py
    python ops_scripts/ci/check_config_references.py --allow-unreferenced
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("[check_config_references] PyYAML required\n")
    raise SystemExit(2) from None

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **_):  # type: ignore[no-redef]
        return iterable


REPO = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = REPO / ".env.example"
ALLOWLIST_PATH = REPO / "config" / "config_references_allowlist.yaml"
BASELINE_PATH = REPO / "ops_scripts" / "ci" / "baselines" / "config_references_baseline.json"

# Directories to scan. Tests and archives are excluded — tests may legitimately
# reference arbitrary env flags for stubbing, and archives are frozen.
SCAN_ROOTS = [
    REPO / "agentic_core",
    REPO / "apps_eval",
    REPO / "apps_exec",
    REPO / "apps_lic",
    REPO / "apps_research",
    REPO / "apps_rg",
    REPO / "apps_shared",
    REPO / "apps_underwriting_ai",
    REPO / "infrastructure",
    REPO / "ops_scripts",
    REPO / "system_learning",
    REPO / "tools",
]

# Directories within scanned roots to skip. Import canonical SSOT from
# path_constants and extend with frozen-archive-specific dirnames that apply
# only to this gate's scope.
try:
    from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS

    _CANONICAL_SKIPS: frozenset[str] = GLOBAL_EXCLUDED_DIRS
except ImportError as _exc:
    # No fallback literal set — would shadow the canonical SSOT per R3 gate.
    # If agentic_core is unimportable, fail loudly so the operator fixes it.
    sys.stderr.write(f"[check_config_references] cannot import canonical GLOBAL_EXCLUDED_DIRS: {_exc}\n")
    raise SystemExit(2) from _exc

# Gate-specific additions: frozen code subtrees that live under tools/ and
# ops_scripts/. These are NOT architectural exclusions — just this gate's
# legacy-debt scope boundary.
_FROZEN_SUBTREES: frozenset[str] = frozenset(
    {"archives", "archive", "_deleted", "tools_graveyard_w5.12", "v15_legacy", "seq_thinking_k25"}
)
SKIP_DIR_NAMES = _CANONICAL_SKIPS | _FROZEN_SUBTREES


def _load_declared_flags() -> set[str]:
    if not ENV_EXAMPLE.is_file():
        return set()
    flags: set[str] = set()
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key:
            flags.add(key)
    return flags


def _load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.is_file():
        return set()
    data = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return set()
    entries = data.get("allowed_external_flags", []) or []
    return {str(x) for x in entries if isinstance(x, str)}


def _str_literal(node: ast.AST) -> str | None:
    """Return the string value if ``node`` is a string Constant, else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_env_read(call: ast.Call) -> str | None:
    """If ``call`` is an os.getenv / os.environ.get call, return flag name."""
    func = call.func
    if not isinstance(func, ast.Attribute):
        return None
    attr = func.attr
    # os.getenv("X")
    if attr == "getenv" and call.args:
        return _str_literal(call.args[0])
    # os.environ.get("X")
    if attr == "get" and isinstance(func.value, ast.Attribute) and func.value.attr == "environ":
        if call.args:
            return _str_literal(call.args[0])
    return None


def _extract_env_subscript(node: ast.Subscript) -> str | None:
    """If ``node`` is os.environ["X"], return flag name."""
    value = node.value
    if not isinstance(value, ast.Attribute) or value.attr != "environ":
        return None
    # Python 3.9+: node.slice is the key directly (not wrapped in Index)
    return _str_literal(node.slice)


def _scan_file(path: Path) -> list[tuple[str, int]]:
    """Return list of ``(flag_name, lineno)`` read in ``path``."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []
    hits: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _extract_env_read(node)
            if name:
                hits.append((name, getattr(node, "lineno", 0)))
        elif isinstance(node, ast.Subscript):
            name = _extract_env_subscript(node)
            if name:
                hits.append((name, getattr(node, "lineno", 0)))
    return hits


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            parts = set(path.parts)
            if parts & SKIP_DIR_NAMES:
                continue
            files.append(path)
    return files


def _load_baseline() -> set[str]:
    if not BASELINE_PATH.is_file():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    entries = data.get("accepted_undeclared", []) if isinstance(data, dict) else []
    return {str(x) for x in entries if isinstance(x, str)}


def _write_baseline(flags: set[str]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_doc": (
            "Accepted legacy-debt env flags read in code but not declared in "
            ".env.example. The ratchet fails only on flags NOT in this list. "
            "Shrink this over time; do NOT grow it except via approved debt row."
        ),
        "accepted_undeclared": sorted(flags),
        "count": len(flags),
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-unreferenced",
        action="store_true",
        help="Do not warn about keys declared in .env.example with zero code reads.",
    )
    parser.add_argument(
        "--regenerate-baseline",
        action="store_true",
        help="Overwrite the baseline snapshot with current undeclared set (operator opt-in).",
    )
    args = parser.parse_args()

    declared = _load_declared_flags()
    allowlist = _load_allowlist()
    baseline = _load_baseline()
    if not declared:
        print(f"[check_config_references] SKIP: no declared keys in {ENV_EXAMPLE}")
        return 0

    files = _iter_python_files()
    reads: dict[str, list[tuple[Path, int]]] = {}
    for path in tqdm(files, desc="scan env reads", unit="file"):
        for name, lineno in _scan_file(path):
            reads.setdefault(name, []).append((path, lineno))

    # Undeclared reads: read in code, not in .env.example, not allowlisted.
    undeclared_all = {k: v for k, v in reads.items() if k not in declared and k not in allowlist}

    if args.regenerate_baseline:
        _write_baseline(set(undeclared_all.keys()))
        print(
            f"[check_config_references] BASELINE REGENERATED — "
            f"{len(undeclared_all)} flag(s) written to "
            f"{BASELINE_PATH.relative_to(REPO).as_posix()}"
        )
        return 0

    # Ratchet: only NEW undeclared flags fail. Baseline items warn but do not
    # block — they represent pre-existing debt that must shrink over time.
    new_undeclared = {k: v for k, v in undeclared_all.items() if k not in baseline}
    baseline_still_present = {k: v for k, v in undeclared_all.items() if k in baseline}
    baseline_gone = sorted(baseline - set(undeclared_all.keys()))

    # Unreferenced keys: declared in .env.example but no code reads.
    unreferenced = sorted(declared - set(reads.keys()))

    exit_code = 0

    if new_undeclared:
        print(
            f"[check_config_references] FAIL — {len(new_undeclared)} NEW undeclared "
            f"env flag(s) read in code (not in baseline, not in allowlist, not in .env.example):"
        )
        for name in sorted(new_undeclared):
            sites = new_undeclared[name]
            print(f"  - {name}  ({len(sites)} site(s))")
            for path, lineno in sites[:3]:
                rel = path.relative_to(REPO).as_posix()
                print(f"      {rel}:{lineno}")
            if len(sites) > 3:
                print(f"      ... and {len(sites) - 3} more")
        print(
            "\nFix options:"
            f"\n  1. Declare the flag in .env.example with a documented default."
            f"\n  2. Add to {ALLOWLIST_PATH.relative_to(REPO).as_posix()} under "
            "allowed_external_flags (with comment) if OS/CI/provider-SDK owned."
            "\n  3. (Debt row) regenerate baseline with "
            "`python ops_scripts/ci/check_config_references.py --regenerate-baseline`."
        )
        exit_code = 1

    if baseline_gone:
        print(
            f"[check_config_references] RATCHET-DOWN — {len(baseline_gone)} baseline flag(s) "
            "no longer read; consider removing them from baseline:"
        )
        for name in baseline_gone:
            print(f"  - {name}")

    if unreferenced and not args.allow_unreferenced:
        print(
            f"[check_config_references] WARN — {len(unreferenced)} key(s) in .env.example "
            "with zero code reads (tooling may still read them):"
        )
        for name in unreferenced[:10]:
            print(f"  - {name}")
        if len(unreferenced) > 10:
            print(f"  ... and {len(unreferenced) - 10} more")

    if exit_code == 0:
        print(
            f"[check_config_references] PASS — "
            f"{len(reads)} distinct flag(s) read; "
            f"{len(baseline_still_present)} legacy-debt (baseline), "
            f"0 new undeclared"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
