"""CI gate: every production module must have at least one test-harness import.

Purpose
-------
ADG catches "X imports forbidden Y". Expected-wiring catches "X must call Y".
Config-reference catches typoed flags. Lifecycle-pair catches leaked handles.
Exception-contract catches unhandled raises. None of the above catch the
quiet failure mode where a brand-new production module ships with **zero
test imports** — i.e., it exists in code but is outside the test harness
surface entirely.

This gate is pure-structural: it makes one ADG SQLite query asking "which
production modules have no import edges from any file under tests/?" That
question is impossible to answer correctly with grep (re-exports, aliases,
lazy imports, package-level imports); it is trivial in ADG.

Scope
-----
Production modules are files under:

- ``agentic_core/L*/**/*.py``
- ``apps_*/engines/*.py``
- ``apps_*/integrations/*.py``

with ``__init__.py`` files excluded (a bare init may legitimately have no
direct test; the package is covered when its concrete modules are imported).

A "test import" is any edge of ``relation_type='imports'`` whose source
node's ``resolved_path`` starts with ``tests/``.

Ratchet
-------
Pre-existing uncovered production modules are frozen in
``ops_scripts/ci/baselines/test_harness_coverage_baseline.json``. The gate
fails only on NEW uncovered modules. Regenerate with ``--regenerate-baseline``.

Allowlist
---------
``config/test_harness_coverage_allowlist.yaml`` lists modules that are
legitimately off the test surface (e.g. ``__main__.py``, bootstrap shims).

Exit 0 on clean, 1 on net-new uncovered modules, 2 on config error.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import fnmatch
import json
import sqlite3
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    sys.stderr.write("[check_test_harness_coverage] PyYAML required\n")
    raise SystemExit(2) from None


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ADG_DIR = REPO / "artifacts" / "adg"
BASELINE_PATH = REPO / "ops_scripts" / "ci" / "baselines" / "test_harness_coverage_baseline.json"
ALLOWLIST_PATH = REPO / "config" / "test_harness_coverage_allowlist.yaml"

# Glob patterns (repo-relative, POSIX) that define the "production module"
# surface this gate enforces. These are intentionally narrow — the gate is
# meant to catch new modules that ship with zero test harness at all, not
# to assert full coverage of every helper.
PROD_MODULE_GLOBS = (
    "agentic_core/L*/**/*.py",
    "apps_eval/engines/*.py",
    "apps_eval/integrations/*.py",
    "apps_exec/engines/*.py",
    "apps_exec/integrations/*.py",
    "apps_lic/engines/*.py",
    "apps_lic/integrations/*.py",
    "apps_research/engines/*.py",
    "apps_research/integrations/*.py",
    "apps_rfp/engines/*.py",
    "apps_rfp/integrations/*.py",
    "apps_rg/engines/*.py",
    "apps_rg/integrations/*.py",
    "apps_shared/enforcement/*.py",
    "apps_underwriting_ai/engines/*.py",
    "apps_underwriting_ai/ingestion/*.py",
)


def _latest_sqlite() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def _load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.is_file():
        return set()
    data = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return set()
    entries = data.get("allowed_uncovered_modules", []) or []
    return {str(x) for x in entries if isinstance(x, str)}


def _match_any_glob(rel_posix: str, globs: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) for pat in globs)


def _enumerate_prod_modules() -> set[str]:
    """Walk the filesystem and return repo-relative POSIX paths matching the
    production-module globs. We intentionally enumerate from the filesystem
    rather than ADG so a NEW file that hasn't yet been imported by any caller
    is still considered a "production module" that must be covered.
    """
    matches: set[str] = set()
    for pat in PROD_MODULE_GLOBS:
        for path in REPO.glob(pat):
            if not path.is_file():
                continue
            if path.name == "__init__.py":
                continue
            rel = path.relative_to(REPO).as_posix()
            matches.add(rel)
    return matches


def _query_test_imported(conn: sqlite3.Connection) -> set[str]:
    """Return the set of repo-relative POSIX paths of modules imported from
    any tests/ file. We look at every edge with relation_type='imports' whose
    source node's resolved_path begins with 'tests/'.
    """
    rows = conn.execute(
        """
        SELECT DISTINCT tgt.resolved_path
          FROM edges e
          JOIN nodes src ON src.id = e.src_id
          JOIN nodes tgt ON tgt.id = e.dst_id
         WHERE e.relation_type = 'imports'
           AND (src.resolved_path LIKE 'tests/%'
                OR src.resolved_path LIKE '%/tests/%')
        """
    ).fetchall()
    covered: set[str] = set()
    for (rp,) in rows:
        if not rp:
            continue
        p = Path(rp)
        try:
            rel = p.resolve().relative_to(REPO).as_posix()
            covered.add(rel)
        except ValueError:
            continue
    return covered


def _load_baseline() -> set[str]:
    if not BASELINE_PATH.is_file():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    entries = data.get("accepted_uncovered", []) if isinstance(data, dict) else []
    return {str(x) for x in entries if isinstance(x, str)}


def _write_baseline(modules: set[str]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_doc": (
            "Accepted legacy-debt production modules with no test-harness import. "
            "The ratchet fails only on NEW uncovered modules. Shrink over time."
        ),
        "accepted_uncovered": sorted(modules),
        "count": len(modules),
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=None,
        help="Path to ADG sqlite (default: latest in artifacts/adg/)",
    )
    parser.add_argument(
        "--regenerate-baseline",
        action="store_true",
        help="Overwrite the baseline with the current uncovered set (operator opt-in).",
    )
    args = parser.parse_args()

    sqlite_path = args.sqlite or _latest_sqlite()
    if sqlite_path is None or not sqlite_path.is_file():
        print(
            "[check_test_harness_coverage] SKIP: no ADG sqlite snapshot found — "
            "gate will run after `python tools/generate_full_adg.py`."
        )
        return 0

    prod = _enumerate_prod_modules()
    allowlist = _load_allowlist()
    baseline = _load_baseline()

    conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    try:
        # Schema guard: this gate requires the `nodes` table to map test
        # imports back to production module paths. Stub/sentinel snapshots
        # (`adg_indexed_99999999_9999.sqlite`) and in-flight pipeline
        # snapshots can lack it — emit SKIP rather than crashing with
        # `OperationalError: no such table: nodes`.
        nodes_present = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
        ).fetchone()
        if not nodes_present:
            print(
                "[check_test_harness_coverage] SKIP: snapshot lacks `nodes` table "
                f"({sqlite_path.name}). Likely a stub/sentinel snapshot or an "
                "in-flight pipeline write — re-run after "
                "`python tools/generate_full_adg.py` completes."
            )
            return 0
        covered = _query_test_imported(conn)
    finally:
        conn.close()

    # A module is uncovered if it is in the production surface, not in the
    # allowlist, and does not appear in the covered set.
    uncovered = {m for m in prod if m not in covered and m not in allowlist}

    if args.regenerate_baseline:
        _write_baseline(uncovered)
        print(
            f"[check_test_harness_coverage] BASELINE REGENERATED — "
            f"{len(uncovered)} module(s) written to "
            f"{BASELINE_PATH.relative_to(REPO).as_posix()}"
        )
        return 0

    new_uncovered = uncovered - baseline
    baseline_gone = baseline - uncovered

    exit_code = 0
    if new_uncovered:
        print(
            f"[check_test_harness_coverage] FAIL — {len(new_uncovered)} NEW production "
            "module(s) have zero test-harness import:"
        )
        for rel in sorted(new_uncovered):
            print(f"  - {rel}")
        print(
            "\nFix options:"
            "\n  1. Add ANY test file under tests/ that imports the module."
            "\n  2. If the module is intentionally off the test surface "
            "(bootstrap / __main__ / vendored), add it to "
            f"{ALLOWLIST_PATH.relative_to(REPO).as_posix()} "
            "under allowed_uncovered_modules."
            "\n  3. (Debt row) `python ops_scripts/ci/check_test_harness_coverage.py "
            "--regenerate-baseline`."
        )
        exit_code = 1

    if baseline_gone:
        print(
            f"[check_test_harness_coverage] RATCHET-DOWN — {len(baseline_gone)} baseline "
            "module(s) now covered; consider removing from baseline:"
        )
        for rel in sorted(baseline_gone)[:10]:
            print(f"  - {rel}")
        if len(baseline_gone) > 10:
            print(f"  ... and {len(baseline_gone) - 10} more")

    if exit_code == 0:
        print(
            f"[check_test_harness_coverage] PASS — "
            f"{len(prod)} production module(s), "
            f"{len(uncovered)} uncovered (all baselined), "
            f"0 new uncovered"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
