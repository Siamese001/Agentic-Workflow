---
name: gitkraken
description: Git operations, GitLens-grade history/blame/worktree analysis, pull request creation/review, and issue management across GitHub/GitLab/Bitbucket/Azure DevOps/Jira/Linear via the GitKraken MCP server. Invoke when the user asks for git status, commits, branches, log/diff, blame, worktrees, pull requests, code reviews, or cross-provider issue tracking. Distinguishes GitKraken's unified PR/issue surface from raw git CLI use. Adapts upstream GitKraken MCP guidance (https://help.gitkraken.com/mcp/mcp-getting-started/) to the Windsurf MCP architecture.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §11

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §11 — GitKraken (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.windsurf/skills/mcp-integration/SKILL.md` §11 for current guidance.

---

# GitKraken Skill (Legacy)

GitKraken MCP is the **sole authority** for git state, PRs, and cross-provider issues per AGENTS.md routing. Do not invoke `git` via `run_command` for state-inspection tasks when GitKraken can answer.

**Upstream:** https://help.gitkraken.com/mcp/mcp-getting-started/

## When To Use This MCP

| User intent | Use GitKraken MCP? | Alternative |
|---|---|---|
| `git status` / list changes | ✅ Yes | — |
| Commit a change | ✅ Yes | — |
| Review log / diff | ✅ Yes | — |
| Open a PR | ✅ Yes | — |
| Read PR comments / files | ✅ Yes | — |
| Create / list issues | ✅ Yes | — |
| Start a worktree | ✅ Yes | — |
| Author a multi-commit refactor (Commit Composer) | ✅ Yes | `gitlens_commit_composer` |
| Read repo source by path | ❌ No | native `read_file` |

## Tool Routing — Pick the Right GitKraken Tool

| Goal | Tool |
|---|---|
| `git status` | `git_status` |
| Stage + commit (single op) | `git_add_or_commit` |
| Show log or diff | `git_log_or_diff` |
| Blame a file | `git_blame` |
| List/create branches | `git_branch` |
| Switch branch | `git_checkout` |
| Push | `git_push` |
| Stash | `git_stash` |
| Worktree list/add | `git_worktree` |
| Create PR | `pull_request_create` |
| Get PR details | `pull_request_get_detail` |
| List PR comments | `pull_request_get_comments` |
| Create review | `pull_request_create_review` |
| Get assigned issues | `issues_assigned_to_me` |
| Issue detail | `issues_get_detail` |
| Comment on issue | `issues_add_comment` |
| Read file from any branch/SHA | `repository_get_file_content` |
| Smart commit organization | `gitlens_commit_composer` |
| Triage open PRs | `gitlens_launchpad` |
| AI PR review in worktree | `gitlens_start_review` |
| Branch from issue | `gitlens_start_work` |

## Hard Rules

1. **No `git` via `run_command`** for state queries. Use the MCP. (Direct shell git is allowed for niche operations the MCP doesn't expose, but is rare.)
2. **Never amend or force-push without explicit user direction.** Constitutional safety.
3. **Issue provider is required** for issue tools — `github` / `gitlab` / `jira` / `azure` / `linear`.
4. **For Azure DevOps and Bitbucket**, `repository_organization` + `repository_name` (and `azure_project` for Azure) are mandatory parameters.

## Common Workflows

**Commit a change:**
1. `git_status` → confirm staged set
2. `git_add_or_commit(action='commit', message='...')`
3. `git_push`

**Open a PR after a feature branch:**
1. `git_status` → confirm clean
2. `git_log_or_diff(action='log', revision_range='main..HEAD')` → confirm commits
3. `pull_request_create(...)`

**Review an inbound PR:**
1. `pull_request_get_detail(pull_request_files=true)`
2. `pull_request_get_comments`
3. `pull_request_create_review(approve=true|false, review='...')`
