"""Auto-merge green, north-star-relevant PRs via the GitHub REST API.

This is the CLOUD-FLOW complement to the LOCAL worktree auto-deliver enforcement
(``.claude/hooks/auto_deliver_on_scope_complete.py`` → ``tools/git/deliver_worktree.py``).
Where the local hook pushes a *completed worktree* to the trunk when the assistant
declares ``SCOPE_COMPLETE``, this tool closes the loop on the GitHub side: it scans the
*open PRs already on GitHub* and merges the ones that are both GREEN and ON the north star,
so relevance-gated delivery is enforced on the cloud flow too — not just locally.

How it plugs into the relevance-gated delivery policy
-----------------------------------------------------
The local ``pre_write_north_star_gate.py`` already makes "does this edit advance the north
star?" the centerpiece of the *edit* decision. This tool applies the SAME relevance
primitive to the *merge* decision: a PR is auto-merged only when its head branch targets a
north-star surface (``_NORTH_PREFIXES``, mirrored from that gate) AND
``config/north_star_state.json`` reports ``enabled == true``. Off-north-star,
governance/meta, drafty, conflicting, or red PRs are SKIPPED with a reason and routed to
manual merge — exactly the lanes-first discipline the local gate enforces.

Why squash is FORBIDDEN
-----------------------
Operator directive (``memory/MEMORY.md``): merge PRs with ``merge`` or ``rebase``, NEVER
``squash``. A squash-merge rewrites the commits, so the PR branch tip is no longer an
ancestor of ``main``. The worktree auto-reaper
(``.claude/hooks/prune_merged_chat_worktrees.py``) decides "merged?" by ancestry; a squash
defeats it, leaving orphaned ``chat/*`` worktrees forever. This tool DEFAULTS to ``merge``,
accepts ``rebase``, and HARD-REFUSES ``squash`` (usage error → exit 2).

Fail-soft contract (mirrors the local auto-deliver hook)
--------------------------------------------------------
Self-contained, no new deps (stdlib ``urllib.request`` only), precise exceptions, every
HTTP call wrapped with a timeout. Missing token → BLOCKED message, exit 0. Any operational
problem → SKIP/BLOCKED with a reason and exit 0. The ONLY non-zero exit is ``--method
squash`` (a usage error, exit 2). Never crashes the caller.

Auth: reads ``GITHUB_TOKEN`` or ``GH_TOKEN`` from the environment. No token is ever
hardcoded; absence is fail-soft (BLOCKED, exit 0).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_STATE_REL = "config/north_star_state.json"

# North-star relevance — mirrored VERBATIM from .claude/hooks/pre_write_north_star_gate.py
# ``_NORTH_PREFIXES``. Kept as a literal copy (that hook lives under .claude/hooks/ and is not
# a cleanly-importable package module), so we replicate the single source of truth here with
# this pointer. If the gate's tuple changes, update this one to match. See that file for the
# authoritative definition.
_NORTH_PREFIXES = (
    "apps_rg/", "apps_lic/", "apps_eval/",
    "tests/unit/apps_rg", "tests/apps_rg",
    "tests/unit/apps_lic", "tests/apps_lic",
    "tests/unit/apps_eval", "tests/apps_eval",
)

# PRs carrying any of these labels route to MANUAL merge (never auto-merged).
_MANUAL_LABELS = frozenset({"meta", "governance", "hold", "do-not-merge"})

_FORBIDDEN_METHOD = "squash"
_DEFAULT_OWNER = "Siamese001"
_DEFAULT_REPO = "Agentic-Workflow"
_API_ROOT = "https://api.github.com"
_HTTP_TIMEOUT = 30


# --------------------------------------------------------------------------- #
# Relevance / state helpers
# --------------------------------------------------------------------------- #
# Branch-name tokens DERIVED from _NORTH_PREFIXES (single source of truth above). The gate's
# prefixes are slash-terminated FILE-PATH prefixes (``apps_rg/``), but PR branch refs encode the
# surface with hyphens/underscores far more often than slashes (``claude/apps_rg-lane-fix``). So
# for branch matching we strip the trailing slash and match the bare token (``apps_rg``) anywhere
# in the ref — derived, not re-invented, so the relevance definition stays singular.
_NORTH_BRANCH_TOKENS = tuple(sorted({p.rstrip("/").split("/")[-1].lower() for p in _NORTH_PREFIXES}))


def is_north_star_branch(head_ref: str) -> bool:
    """True when a PR head branch targets a north-star surface.

    Branch refs commonly encode the surface (e.g. ``claude/apps_rg-lane-fix`` or
    ``apps_rg/...``); we treat the ref as north-star if any north token appears in it.
    """
    if not head_ref:
        return False
    low = head_ref.lower()
    return any(tok in low for tok in _NORTH_BRANCH_TOKENS)


def load_north_star_state(state_path: Path | None = None) -> dict:
    """Load config/north_star_state.json. Returns {} on any read/parse error (fail-soft)."""
    sp = state_path or (REPO_ROOT / _STATE_REL)
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def north_star_enabled(state: dict) -> bool:
    return bool(state.get("enabled", False))


# --------------------------------------------------------------------------- #
# GitHub REST (stdlib urllib only)
# --------------------------------------------------------------------------- #
def get_token(env: dict | None = None) -> str | None:
    env = env if env is not None else os.environ
    tok = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")
    tok = (tok or "").strip()
    return tok or None


def _request(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, object]:
    """Perform one GitHub API request. Returns (status_code, parsed_json_or_text).

    Fully fail-soft: any network/parse error maps to a synthetic (status, payload) so callers
    never see an exception. status 0 == transport failure.
    """
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url=url, method=method, data=data)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "auto-merge-north-star-prs")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode()
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except (OSError, ValueError):
            raw = ""
        try:
            return exc.code, json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}
    except (urllib.error.URLError, OSError) as exc:
        return 0, {"error": str(exc)}
    try:
        return status, json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return status, {"raw": raw}


def list_open_prs(owner: str, repo: str, token: str) -> list[dict]:
    url = f"{_API_ROOT}/repos/{owner}/{repo}/pulls?state=open&per_page=100"
    status, payload = _request("GET", url, token)
    if status == 200 and isinstance(payload, list):
        return payload
    return []


def get_pr_detail(owner: str, repo: str, number: int, token: str) -> dict:
    """Single-PR fetch — the list endpoint omits ``mergeable``/``mergeable_state``."""
    url = f"{_API_ROOT}/repos/{owner}/{repo}/pulls/{number}"
    status, payload = _request("GET", url, token)
    return payload if (status == 200 and isinstance(payload, dict)) else {}


def get_combined_status(owner: str, repo: str, sha: str, token: str) -> dict:
    url = f"{_API_ROOT}/repos/{owner}/{repo}/commits/{sha}/status"
    status, payload = _request("GET", url, token)
    return payload if (status == 200 and isinstance(payload, dict)) else {}


def get_check_runs(owner: str, repo: str, sha: str, token: str) -> dict:
    url = f"{_API_ROOT}/repos/{owner}/{repo}/commits/{sha}/check-runs"
    status, payload = _request("GET", url, token)
    return payload if (status == 200 and isinstance(payload, dict)) else {}


def merge_pr(owner: str, repo: str, number: int, method: str, token: str) -> tuple[bool, str]:
    """PUT the merge. Returns (merged?, message). ``method`` is never 'squash' (guarded upstream)."""
    url = f"{_API_ROOT}/repos/{owner}/{repo}/pulls/{number}/merge"
    status, payload = _request("PUT", url, token, body={"merge_method": method})
    if status == 200 and isinstance(payload, dict) and payload.get("merged"):
        return True, str(payload.get("message") or "merged")
    msg = ""
    if isinstance(payload, dict):
        msg = str(payload.get("message") or payload.get("error") or payload.get("raw") or "")
    return False, f"merge HTTP {status}: {msg}".strip()


# --------------------------------------------------------------------------- #
# CI aggregation
# --------------------------------------------------------------------------- #
def checks_all_green(combined: dict, check_runs: dict) -> tuple[bool, str]:
    """All commit statuses AND check-runs must be success/skipped — none pending/failed.

    Returns (green?, reason-when-not-green).
    """
    # Legacy commit statuses
    statuses = combined.get("statuses") if isinstance(combined, dict) else None
    for st in statuses or []:
        if not isinstance(st, dict):
            continue
        state = str(st.get("state") or "").lower()
        if state == "pending":
            return False, f"status '{st.get('context')}' pending"
        if state != "success":
            return False, f"status '{st.get('context')}' = {state or 'unknown'}"

    # Check-runs (GitHub Actions etc.)
    runs = check_runs.get("check_runs") if isinstance(check_runs, dict) else None
    for run in runs or []:
        if not isinstance(run, dict):
            continue
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()
        if status != "completed":
            return False, f"check '{run.get('name')}' not completed ({status or 'unknown'})"
        if conclusion not in ("success", "skipped", "neutral"):
            return False, f"check '{run.get('name')}' = {conclusion or 'unknown'}"
    return True, ""


# --------------------------------------------------------------------------- #
# Per-PR decision
# --------------------------------------------------------------------------- #
def evaluate_pr(pr: dict, detail: dict, combined: dict, check_runs: dict, state: dict) -> tuple[str, str]:
    """Decide one PR. Returns (decision, reason) where decision in {merge, skip}."""
    number = pr.get("number")
    if pr.get("draft"):
        return "skip", f"PR #{number}: draft"

    labels = {str((lbl or {}).get("name") or "").lower() for lbl in (pr.get("labels") or [])}
    manual = labels & _MANUAL_LABELS
    if manual:
        return "skip", f"PR #{number}: labeled {sorted(manual)} → manual merge"

    head_ref = str(((pr.get("head") or {}).get("ref")) or "")
    if not is_north_star_branch(head_ref):
        return "skip", f"PR #{number}: head '{head_ref}' is not north-star-relevant"

    if not north_star_enabled(state):
        return "skip", f"PR #{number}: north_star_state.enabled != true"

    mergeable = detail.get("mergeable")
    mergeable_state = str(detail.get("mergeable_state") or "").lower()
    if mergeable is False:
        return "skip", f"PR #{number}: not mergeable (conflicts)"
    if mergeable is None:
        return "skip", f"PR #{number}: mergeability unknown (GitHub still computing) — retry later"
    if mergeable_state and mergeable_state != "clean":
        return "skip", f"PR #{number}: mergeable_state = {mergeable_state}"

    green, why = checks_all_green(combined, check_runs)
    if not green:
        return "skip", f"PR #{number}: CI not green ({why})"

    return "merge", f"PR #{number}: green + north-star ('{head_ref}')"


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def _progress(total: int, label: str):
    """Return a ProgressReporter when iterating >10 items (constitutional §16), else None."""
    if total <= 10:
        return None
    try:
        from tools.progress_display import ProgressReporter

        return ProgressReporter(total=total, label=label)
    except Exception:  # guardian: allow-broad-exception -- progress display is best-effort, never fatal
        return None


def run(owner: str, repo: str, method: str, dry_run: bool, token: str, state: dict | None = None) -> dict:
    """Core loop. Returns a structured summary dict. Never raises."""
    state = state if state is not None else load_north_star_state()
    prs = list_open_prs(owner, repo, token)
    summary: dict = {"merged": [], "skipped": [], "blocked": [], "dry_run": dry_run}

    reporter = _progress(len(prs), "Scanning open PRs")
    for pr in prs:
        number = pr.get("number")
        head = pr.get("head") or {}
        sha = str(head.get("sha") or "")
        # Need detail (mergeable/mergeable_state — absent on the list endpoint) + CI to decide.
        detail = get_pr_detail(owner, repo, int(number), token) if number is not None else {}
        combined = get_combined_status(owner, repo, sha, token) if sha else {}
        check_runs = get_check_runs(owner, repo, sha, token) if sha else {}

        decision, reason = evaluate_pr(pr, detail, combined, check_runs, state)
        if decision == "merge":
            if dry_run:
                summary["merged"].append({"number": number, "reason": reason + " [DRY-RUN: not merged]"})
            else:
                ok, msg = merge_pr(owner, repo, int(number), method, token)
                if ok:
                    summary["merged"].append({"number": number, "reason": f"{reason} via {method}: {msg}"})
                else:
                    summary["blocked"].append({"number": number, "reason": f"{reason} BUT {msg}"})
        else:
            summary["skipped"].append({"number": number, "reason": reason})

        if reporter is not None:
            reporter.update(label=f"PR #{number}")
    if reporter is not None:
        reporter.done()
    return summary


def print_summary(summary: dict, owner: str, repo: str, method: str) -> None:
    mode = "DRY-RUN (nothing merged)" if summary.get("dry_run") else f"LIVE (merge_method={method})"
    print(f"\n=== auto_merge_north_star_prs :: {owner}/{repo} :: {mode} ===")
    merged = summary.get("merged", [])
    skipped = summary.get("skipped", [])
    blocked = summary.get("blocked", [])
    print(f"MERGED  ({len(merged)}):")
    for m in merged:
        print(f"  - #{m['number']}: {m['reason']}")
    print(f"SKIPPED ({len(skipped)}):")
    for s in skipped:
        print(f"  - {s['reason']}")
    print(f"BLOCKED ({len(blocked)}):")
    for b in blocked:
        print(f"  - #{b['number']}: {b['reason']}")
    print("=== end ===")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="auto_merge_north_star_prs",
        description="Auto-merge green, north-star-relevant open PRs (cloud-flow complement to "
        "local worktree auto-deliver). Defaults to 'merge'; 'squash' is FORBIDDEN.",
    )
    p.add_argument("--owner", default=_DEFAULT_OWNER, help=f"GitHub owner (default {_DEFAULT_OWNER})")
    p.add_argument("--repo", default=_DEFAULT_REPO, help=f"GitHub repo (default {_DEFAULT_REPO})")
    p.add_argument(
        "--method",
        default="merge",
        choices=("merge", "rebase", "squash"),
        help="Merge method (default 'merge'; 'rebase' allowed; 'squash' is REJECTED — it breaks "
        "the worktree auto-reaper's ancestry check).",
    )
    p.add_argument("--trunk", default="main", help="Trunk/base branch (default 'main')")
    p.add_argument("--dry-run", action="store_true", help="Report what WOULD merge; merge nothing.")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.method == _FORBIDDEN_METHOD:
        print(
            "ERROR: --method squash is FORBIDDEN. A squash-merge rewrites commits so the PR "
            "branch is no longer an ancestor of the trunk, defeating the worktree auto-reaper. "
            "Use 'merge' (default) or 'rebase'.",
            file=sys.stderr,
        )
        return 2  # usage error — the ONLY non-zero exit

    token = get_token()
    if not token:
        print(
            "BLOCKED: no GitHub token in environment (set GITHUB_TOKEN or GH_TOKEN). "
            "Nothing scanned or merged. Fail-soft exit 0.",
            file=sys.stderr,
        )
        return 0

    summary = run(args.owner, args.repo, args.method, args.dry_run, token)
    print_summary(summary, args.owner, args.repo, args.method)
    return 0  # always fail-soft


if __name__ == "__main__":
    raise SystemExit(main())
