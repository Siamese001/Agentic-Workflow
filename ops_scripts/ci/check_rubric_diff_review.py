"""CI gate: enforce ADR-053/054 H7 rubric-diff review rules.

Invariants enforced when a rubric under ``config/exit_eval_rubrics/``
is modified in the staged diff:

1. **Version must increment.** ``X1D@v3 → X1D@v4`` OK; bumping without
   incrementing the ``version:`` field FAILS.
2. **`abstain_allowed` only becomes more permissive.** Flipping
   ``abstain_allowed: true`` → ``false`` on a model-based dimension is
   FORBIDDEN (removes the safety valve).
3. **Threshold loosening requires justification.** Dropping any
   dimension's ``threshold:`` or the ``aggregate_threshold:`` on the
   same rubric version is FORBIDDEN; it requires a version bump AND a
   commit message / PR body note containing ``RUBRIC_LOOSENING:``.
4. **Dimension removal requires an ADR.** If any dimension present in
   the previous version is absent in the new version, the commit must
   reference an ADR (``ADR-\\d+``) in the message.

Runs via pre-commit or as a manual gate:

    python ops_scripts/ci/check_rubric_diff_review.py --staged
    python ops_scripts/ci/check_rubric_diff_review.py --from HEAD~1

Exit codes:
    0 — OK or no rubric files in diff.
    1 — violation.
    2 — infrastructure error (git unavailable, malformed rubric).

Fail-open when git is unavailable — this gate is advisory infrastructure,
not a runtime blocker. Missing files are treated as "no rubric diff"
(exit 0).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
RUBRIC_DIR_REL = Path("config") / "exit_eval_rubrics"


def _git(*args: str, cwd: Path | None = None) -> str:
    """Invoke git with a hard timeout. No shell=True. Fail-open on error."""
    try:
        result = subprocess.run(
            ("git", *args),
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def _staged_rubric_files() -> list[Path]:
    out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [
        REPO_ROOT / line.strip()
        for line in out.splitlines()
        if line.strip().startswith(str(RUBRIC_DIR_REL).replace("\\", "/"))
        and line.strip().endswith((".yaml", ".yml"))
    ]


def _diff_range_rubric_files(rev_range: str) -> list[Path]:
    out = _git("diff", "--name-only", "--diff-filter=ACMR", rev_range)
    return [
        REPO_ROOT / line.strip()
        for line in out.splitlines()
        if line.strip().startswith(str(RUBRIC_DIR_REL).replace("\\", "/"))
        and line.strip().endswith((".yaml", ".yml"))
    ]


def _show_at(rev: str, rel_path: str) -> str | None:
    out = _git("show", f"{rev}:{rel_path}")
    return out if out else None


def _parse_yaml(text: str, path: str) -> dict[str, Any]:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: top-level must be a mapping")
    return parsed


def _dims_by_name(rubric: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for dim in rubric.get("dimensions") or ():
        if not isinstance(dim, dict):
            continue
        name = str(dim.get("name", ""))
        if name:
            out[name] = dim
    return out


def _version_suffix_int(version: str) -> int | None:
    # Accept "X1D@v3" or "v3"; return 3. Return None if unrecognized.
    match = re.search(r"v(\d+)$", str(version).strip())
    return int(match.group(1)) if match else None


def _commit_message_tail(staged: bool) -> str:
    """Best-effort capture of the in-progress commit message.

    For --staged runs we rely on ``.git/COMMIT_EDITMSG`` (populated by
    ``-m`` or the editor). For history runs we use the HEAD commit
    message. Never blocks if unavailable.
    """
    if staged:
        path = REPO_ROOT / ".git" / "COMMIT_EDITMSG"
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                return ""
        return ""
    return _git("log", "-1", "--pretty=%B")


# --------------------------------------------------------------------- #
# Rule implementations
# --------------------------------------------------------------------- #


def _check_version_bumped(old: dict[str, Any], new: dict[str, Any], path: str) -> list[str]:
    old_v = str(old.get("version", ""))
    new_v = str(new.get("version", ""))
    if old_v == new_v:
        return [f"{path}: rubric modified but version unchanged ({old_v!r})"]
    old_n = _version_suffix_int(old_v)
    new_n = _version_suffix_int(new_v)
    if old_n is not None and new_n is not None and new_n <= old_n:
        return [f"{path}: version must increase ({old_v!r} → {new_v!r})"]
    return []


def _check_abstain_monotonic(old: dict[str, Any], new: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    old_dims = _dims_by_name(old)
    new_dims = _dims_by_name(new)
    for name, old_dim in old_dims.items():
        new_dim = new_dims.get(name)
        if new_dim is None:
            continue
        old_abstain = bool(old_dim.get("abstain_allowed", False))
        new_abstain = bool(new_dim.get("abstain_allowed", False))
        if old_abstain and not new_abstain:
            errors.append(
                f"{path}: dimension {name!r} removed abstain_allowed "
                "(forbidden — would remove the safety valve)"
            )
    return errors


def _check_threshold_loosening(
    old: dict[str, Any], new: dict[str, Any], path: str, commit_msg: str
) -> list[str]:
    errors: list[str] = []
    allows_loose = "RUBRIC_LOOSENING:" in commit_msg

    old_agg = old.get("aggregate_threshold")
    new_agg = new.get("aggregate_threshold")
    if (
        isinstance(old_agg, (int, float))
        and isinstance(new_agg, (int, float))
        and float(new_agg) < float(old_agg)
        and not allows_loose
    ):
        errors.append(
            f"{path}: aggregate_threshold dropped "
            f"({old_agg} → {new_agg}) without RUBRIC_LOOSENING: "
            "justification in commit body"
        )

    old_dims = _dims_by_name(old)
    new_dims = _dims_by_name(new)
    for name, old_dim in old_dims.items():
        new_dim = new_dims.get(name)
        if new_dim is None:
            continue
        old_t = old_dim.get("threshold")
        new_t = new_dim.get("threshold")
        if (
            isinstance(old_t, (int, float))
            and isinstance(new_t, (int, float))
            and float(new_t) < float(old_t)
            and not allows_loose
        ):
            errors.append(
                f"{path}: dimension {name!r} threshold dropped ({old_t} → {new_t}) without RUBRIC_LOOSENING:"
            )
    return errors


def _check_dimension_removal(
    old: dict[str, Any], new: dict[str, Any], path: str, commit_msg: str
) -> list[str]:
    errors: list[str] = []
    old_names = set(_dims_by_name(old))
    new_names = set(_dims_by_name(new))
    removed = old_names - new_names
    if not removed:
        return []
    if not re.search(r"ADR-\d+", commit_msg):
        errors.append(
            f"{path}: removed dimensions {sorted(removed)} requires ADR "
            "reference in commit body (pattern ADR-NNN)"
        )
    return errors


# --------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------- #


def _audit(files: Iterable[Path], base_rev: str, staged: bool) -> list[str]:
    errors: list[str] = []
    commit_msg = _commit_message_tail(staged)
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        old_text = _show_at(base_rev, rel)
        if old_text is None:
            # New file — nothing to compare. Only check the version field is present.
            try:
                new_blob = _parse_yaml(path.read_text(encoding="utf-8"), rel)
            except (OSError, ValueError) as exc:
                errors.append(f"{rel}: {exc}")
                continue
            if not new_blob.get("version"):
                errors.append(f"{rel}: new rubric missing 'version' key")
            continue
        try:
            old_blob = _parse_yaml(old_text, f"{base_rev}:{rel}")
            new_blob = _parse_yaml(path.read_text(encoding="utf-8"), rel)
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")
            continue

        errors.extend(_check_version_bumped(old_blob, new_blob, rel))
        errors.extend(_check_abstain_monotonic(old_blob, new_blob, rel))
        errors.extend(_check_threshold_loosening(old_blob, new_blob, rel, commit_msg))
        errors.extend(_check_dimension_removal(old_blob, new_blob, rel, commit_msg))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect staged diff vs HEAD")
    parser.add_argument(
        "--from",
        dest="from_rev",
        help="Inspect diff from REV..HEAD (e.g. 'HEAD~1')",
    )
    args = parser.parse_args()

    if args.staged:
        files = _staged_rubric_files()
        base_rev = "HEAD"
    elif args.from_rev:
        files = _diff_range_rubric_files(f"{args.from_rev}..HEAD")
        base_rev = args.from_rev
    else:
        print("ERROR: pass --staged or --from REV", file=sys.stderr)
        return 2

    if not files:
        return 0

    errors = _audit(files, base_rev, staged=args.staged)
    if errors:
        print("Rubric-diff review violations:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(
            "\nFix by: (1) incrementing `version:`; (2) keeping abstain_allowed "
            "non-regressive; (3) adding `RUBRIC_LOOSENING:` to commit body for "
            "threshold drops; (4) referencing an ADR for dimension removals.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
