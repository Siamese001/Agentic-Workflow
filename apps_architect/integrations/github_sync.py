"""GitHub API integration — README sync via PR creation.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W4.P2.

Flow: detect drift → create branch → commit README → open PR.
Uses GitHub REST API with token resolved via CredentialManager.
"""

from __future__ import annotations

import logging
import urllib.request
import json as _json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_architect.config.credential_manager import CredentialManager

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GITHUB_API = "https://api.github.com"


def _github_request(
    method: str,
    path: str,
    data: dict[str, Any] | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    token = token or os.environ.get("GITHUB_TOKEN", "")
    url = f"{_GITHUB_API}{path}"
    body = _json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "apps_architect")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return _json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode() if exc.fp else str(exc)
        _log.error("GitHub API %s %s → %s: %s", method, path, exc.code, err_body[:200])
        return {"error": str(exc), "status": exc.code}
    except Exception as exc:
        _log.error("GitHub API request failed: %s", exc)
        return {"error": str(exc)}


def _get_repo_info(creds: CredentialManager) -> tuple[str, str] | None:
    """Derive owner/repo from GITHUB_REPOSITORY env var."""
    repo = creds.get("GITHUB_REPOSITORY", "")
    if "/" in repo:
        owner, _, name = repo.partition("/")
        return owner, name
    return None


class GitHubSync:
    """Syncs README changes to GitHub via PR."""

    def __init__(self, token: str | None = None, creds: CredentialManager | None = None) -> None:
        self._creds = creds or CredentialManager()
        self._token = token or self._creds.get("GITHUB_TOKEN")

    @property
    def configured(self) -> bool:
        return bool(self._token)

    @property
    def token_masked(self) -> str:
        return self._creds.mask("GITHUB_TOKEN")

    def create_pr(
        self,
        readme_content: str,
        base_branch: str = "main",
        dry_run: bool = True,
    ) -> dict[str, Any]:
        if not self._token:
            return {"error": "GITHUB_TOKEN not set", "dry_run": dry_run}

        repo = _get_repo_info(self._creds)
        if not repo:
            return {"error": "Cannot determine repo; set GITHUB_REPOSITORY", "dry_run": dry_run}

        owner, name = repo
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        branch = f"architect/update-{ts}"
        title = f"docs: architect pattern sync {ts}"
        body = (
            f"## Architect Pattern Sync\n\n"
            f"Auto-generated README update from apps_architect scan.\n\n"
            f"Review the pattern catalog, delta summary, and hardening backlog below."
        )

        if dry_run:
            return {
                "dry_run": True,
                "owner": owner,
                "repo": name,
                "branch": branch,
                "title": title,
                "content_length": len(readme_content),
            }

        # Get default branch SHA
        ref_resp = _github_request(
            "GET", f"/repos/{owner}/{name}/git/ref/heads/{base_branch}", token=self._token
        )
        base_sha = ref_resp.get("object", {}).get("sha", "")
        if not base_sha:
            return {"error": f"Cannot resolve base branch: {base_branch}"}

        # Create branch
        _github_request(
            "POST",
            f"/repos/{owner}/{name}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": base_sha},
            token=self._token,
        )

        # Get README (if exists)
        readme_resp = _github_request(
            "GET", f"/repos/{owner}/{name}/contents/README.md?ref={branch}", token=self._token
        )
        readme_sha = readme_resp.get("sha", "")

        # Commit README
        import base64
        commit_resp = _github_request(
            "PUT",
            f"/repos/{owner}/{name}/contents/README.md",
            {
                "message": title,
                "content": base64.b64encode(readme_content.encode()).decode(),
                "branch": branch,
                "sha": readme_sha or None,
            },
            token=self._token,
        )

        # Create PR
        pr_resp = _github_request(
            "POST",
            f"/repos/{owner}/{name}/pulls",
            {"title": title, "head": branch, "base": base_branch, "body": body},
            token=self._token,
        )

        return {
            "dry_run": False,
            "pr_url": pr_resp.get("html_url", ""),
            "branch": branch,
            "commit": commit_resp.get("commit", {}).get("sha", ""),
        }


__all__ = ["GitHubSync"]
