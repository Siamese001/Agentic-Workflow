## §11 — GitKraken

**Upstream:** https://help.gitkraken.com/mcp/mcp-getting-started/. **Sole authority** for git state, PRs, cross-provider issues.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| `git status` / list changes | ✅ Yes | — |
| Commit | ✅ Yes | — |
| Review log/diff | ✅ Yes | — |
| Open PR | ✅ Yes | — |
| Create/list issues | ✅ Yes | — |
| Read repo source | ❌ No | native `read_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| `git status` | `git_status` |
| Stage + commit | `git_add_or_commit` |
| Log/diff | `git_log_or_diff` |
| Blame | `git_blame` |
| Branch list/create | `git_branch` |
| Switch branch | `git_checkout` |
| Push | `git_push` |
| Stash | `git_stash` |
| Worktree | `git_worktree` |
| Create PR | `pull_request_create` |
| Get PR details | `pull_request_get_detail` |
| PR comments | `pull_request_get_comments` |
| Create review | `pull_request_create_review` |
| Issues | `issues_assigned_to_me` / `issues_get_detail` / `issues_add_comment` |
| File from branch/SHA | `repository_get_file_content` |
| Commit composer | `gitlens_commit_composer` |
| PR triage | `gitlens_launchpad` |
| AI PR review | `gitlens_start_review` |
| Branch from issue | `gitlens_start_work` |

### Hard Rules
1. **No `git` via `run_command`** for state queries
2. **Never amend/force-push** without explicit user direction
3. **Issue provider required** — `github`/`gitlab`/`jira`/`azure`/`linear`
4. **Azure/Bitbucket**: `repository_organization` + `repository_name` mandatory

---
