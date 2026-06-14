# Worktree-Per-Chat — Never Edit The Primary Checkout On `main`

> ⛔ Every chat/feature works in its own fresh **git worktree** cut from the
> default branch (`main`). Direct edits to the primary checkout while it is on
> `main`/`master` are blocked. Each conversation's work is isolated in its own
> working directory + branch, reviewable as a single PR.
>
> (Renamed from "branch-per-chat" 2026-06-08 per user directive: isolate each
> chat in a dedicated worktree, not just a branch switch in the primary checkout.)

## The Invariant

1. At **session start**, if HEAD is on a protected branch (`main`/`master`),
   a new worktree is created at `<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`
   on a fresh `chat/<UTC-stamp>-<session-hex>` branch cut from the current tip.
   The assistant is instructed (via `SessionStart` `additionalContext`) to perform
   all work for the chat **inside that worktree** (`cd` in; target files there).
2. **Edit/Write/MultiEdit is gated per-file by the owning working tree's branch.**
   Edits whose owning worktree is on a non-protected branch (i.e. inside the chat
   worktree) are allowed; edits to the primary checkout while it is on a protected
   branch are refused (exit 2) with remediation pointing at the worktree.
3. A chat already operating on a non-protected branch/worktree is left alone.

> **Known constraint (accepted):** a `SessionStart` hook is a subprocess and
> **cannot relocate the running session's CWD** into the new worktree. It creates
> the worktree and emits instructions; the assistant must `cd` into it. The
> edit-gate's per-file branch resolution is what enforces that work lands in the
> worktree, not the primary checkout. The entire `.claude/` governance tree still
> resolves from the primary `$CLAUDE_PROJECT_DIR`; worktrees contain their own
> copy of the tracked tree.

## Enforcement Layers

| Layer | Mechanism | File |
|---|---|---|
| Proactive (auto-worktree, cut-from-`origin/main`, link, sync, divergence) | `SessionStart` hook | `.claude/hooks/session_start_branch_guard.py` |
| Hard block (per-file edit gate) | `PreToolUse` Edit\|Write\|MultiEdit hook | `.claude/hooks/before_file_edit_branch_guard.py` |
| Lifecycle cleanup (auto-reap merged) | `SessionStart` hook | `.claude/hooks/prune_merged_chat_worktrees.py` |
| Auto-deliver on `SCOPE_COMPLETE` | `Stop` hook | `.claude/hooks/auto_deliver_on_scope_complete.py` |
| Runtime-cache linker (SSOT) | imported by the create hook + doctor | `tools/git/worktree_runtime_links.py` |
| Doctor (classify / report / `--link`) | CLI | `tools/git/worktree_doctor.py` |
| Deliver (rebase → retest → push/PR) | CLI | `tools/git/deliver_worktree.py` |
| Registration | `.claude/settings.json` `env` + `hooks.SessionStart` + `hooks.PreToolUse` + `hooks.Stop` | — |

Both hooks are **self-contained** (no `lib.claude_hook_common` dependency) and fail
**soft** when git is unavailable / no branch resolves; the edit gate blocks **hard**
only when the file's owning working tree is genuinely on a protected branch. The runtime
linker / divergence notice are best-effort and never block session start.

## Configuration

| Env var | Effect |
|---|---|
| `BRANCH_PER_CHAT_BYPASS=1` / `WORKTREE_PER_CHAT_BYPASS=1` | Disable the guard hooks (intentional on-primary change). Also disables auto-reap. |
| `BRANCH_PER_CHAT_PROTECTED=main,master,release` | Override the protected-branch set (csv). Default: `main,master`. |
| `CHAT_WORKTREE_ROOT=/abs/path` | Override the worktree root. Default: `<repo-parent>/.chat-worktrees`. |
| `WORKTREE_MERGE_CLEANUP_BYPASS=1` | Disable only the auto-reap (keep the create/edit guards on). |
| `WORKTREE_MERGE_CLEANUP_DRY_RUN=1` | Auto-reap reports which worktrees it *would* reap, deletes nothing. |
| `WORKTREE_CLEANUP_MIN_AGE_MINUTES=N` | Grace window — never reap a worktree newer than N minutes (recency = most recent of HEAD commit time **and** worktree creation mtime). **Default `30`** (item #1, raised from `0` to end the mid-session reap-race). |
| `WORKTREE_REAP_BRANCH_PREFIXES=chat/,feat/` | csv of branch prefixes eligible for auto-reap. **Default `chat/`** (unchanged). Non-chat prefixes may live anywhere (sibling worktrees) — opt-in only (item #4). |
| `.keep-worktree` (marker file, not env) | A `.keep-worktree` file in any worktree exempts it from auto-reap permanently (gitignored; item #4). |
| `WORKTREE_LINK_DIRS=a/b,c/d` / `WORKTREE_LINK_DIRS_DISABLE=1` | Override / disable the runtime-cache dirs junctioned into a new worktree. Default: `data/cache/{chromadb,sparse,r1b}` (item #2). |
| `WORKTREE_DIVERGENCE_NOTICE=0` / `WORKTREE_DIVERGENCE_FETCH=1` | Silence the trunk-divergence notice / fetch before counting (item #3). |
| `WORKTREE_CLEANUP_TRUNK_REF=origin/main` | The "merged into" / divergence trunk ref. Default `origin/main`. |
| `WORKTREE_AUTODELIVER=1\|pr\|dry\|0` | Auto-deliver mode for the `SCOPE_COMPLETE` Stop hook: `1`=push HEAD to trunk, `pr`=push+PR, `dry`=plan only, unset/`0`=disabled. |
| `WORKTREE_AUTODELIVER_TRUNK=main` | Trunk branch the auto-deliver pushes to. Default `main`. |
| `WORKTREE_AUTODELIVER_TIMEOUT=600` / `WORKTREE_AUTODELIVER_BYPASS=1` | Deliver subprocess timeout (s) / disable the Stop hook. |
| `WORKTREE_CUT_FROM_TRUNK=0` | Disable cutting new worktrees from `origin/<trunk>` (item #B; default ON — lanes start current). |
| `WORKTREE_SYNC_LOCAL_TRUNK=0` | Disable fast-forwarding local `main`→`origin/main` when the primary is clean (item #D; default ON). |

## Operating model — parallel lanes, current base, auto-deliver

> Adopted 2026-06-14 from the last-100-commit assessment (16-worktree pileup, local `main`
> 60 commits behind `origin/main`, one branch reused across ~20 PRs). Optimized for
> heavy-parallel work where many branches are in flight at once.

1. **One worktree per chat/scope** = one parallel lane. Spin up as many concurrent chats as
   you want; each is isolated and independently testable.
2. **Every new worktree is cut from `origin/main`** (item #B), and local `main` is
   fast-forwarded to `origin/main` when the primary is clean (item #D) — so lanes always
   start current and the "60-behind" drift cannot accumulate.
3. **Auto-deliver on scope completion (item #C):** when a scope is fully done **and tests
   pass**, emit a line-anchored marker as the last line of the response:

   ```
   SCOPE_COMPLETE: branch=<branch> [tests=<pytest-target>]
   ```

   The `Stop` hook `auto_deliver_on_scope_complete.py` resolves that branch's worktree and
   runs `deliver_worktree.py`: rebase on `origin/main` → optional `tests=` retest → **push
   `HEAD:main` to GitHub** (when `WORKTREE_AUTODELIVER=1`). Safety-gated by the deliver tool
   (refuses on a protected branch / dirty tree, aborts on rebase conflict, skips push on a
   failing retest, never force-pushes). Idempotent per `(branch, HEAD-sha)`; logs to
   `artifacts/governance/autodeliver/`. Emit the marker **only** when you have actually
   verified the scope is complete and green — it triggers a real push to the shared trunk.
4. **Aggressive auto-reap** (item #4 + config): `WORKTREE_REAP_BRANCH_PREFIXES=chat/,feat/,fix/,codex/`
   removes any merged+clean worktree (no pileup); `.keep-worktree` opts out the rare long-lived one.
5. **Conflict-tolerant:** with many lanes, rebase conflicts happen — they surface at deliver
   time (abort + message), you resolve in the worktree and re-emit the marker. Keep lanes
   small and orthogonal to make conflicts cheap.

## Naming

- Branch: `chat/<YYYYMMDD-HHMMSS>-<8-hex-of-session-id>` (stamp = session UTC clock).
- Worktree dir: `<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`.
- Collisions are uniquified with the hook PID.

## Lifecycle cleanup — auto-reap merged chat worktrees

> ⛔ Once a chat worktree's branch is fully **merged into `origin/main`** and its tree is
> **clean**, the worktree has served its purpose and is removed automatically at the next
> `SessionStart` (`git worktree remove` + `git branch -d`). Merged + clean ⇒ **zero committed
> work is ever lost** (everything is already on the trunk).

`prune_merged_chat_worktrees.py` reaps a worktree **only** when ALL hold — a hard safety envelope:

| Guard | A worktree is reaped only if… |
|---|---|
| Prefix | its branch matches an **enabled reap prefix** (`WORKTREE_REAP_BRANCH_PREFIXES`, default `chat/`). `chat/*` must also live under the chat root (`.chat-worktrees/`); opt-in non-chat prefixes may live anywhere. The primary checkout is **never** eligible. |
| Keep marker | it does **not** carry a `.keep-worktree` file (universal opt-out — kept regardless of merge/clean state). |
| Self | it is **not** the worktree the current session is running in. |
| Merged | its branch is an **ancestor of `origin/main`** (`git merge-base --is-ancestor`). Unmerged work is never touched. |
| Clean | its working tree is **clean** (`git status --porcelain` empty). Uncommitted work is never touched. |
| Age | it is older than `WORKTREE_CLEANUP_MIN_AGE_MINUTES` (default **`30`**) — recency is the **most recent of HEAD commit time and worktree creation mtime**, so a freshly-created empty worktree (HEAD on an old trunk tip) is still protected. |

It is **best-effort and fail-soft**: a fetch failure, a worktree-remove failure, or a non-git
environment never blocks session start (always exits 0). Run it on demand in dry-run with
`WORKTREE_MERGE_CLEANUP_DRY_RUN=1 python .claude/hooks/prune_merged_chat_worktrees.py`.

## Runtime-data junctions (item #2)

A fresh worktree checks out only **tracked** files, so the gitignored runtime caches
(`data/cache/chromadb`, `data/cache/sparse`, `data/cache/r1b`) are **absent** — the
documented cause of "C0.2 BM25 UNAVAILABLE on every lane" the first time apps_rg runs in a
new worktree. On worktree create, `session_start_branch_guard.py` **junctions** those dirs
back to the primary checkout (Windows `mklink /J`, POSIX symlink) via the SSOT
`tools/git/worktree_runtime_links.py`. Repair an existing worktree with:

```
python tools/git/worktree_doctor.py --link            # all worktrees
python tools/git/worktree_doctor.py --link <path>     # one worktree
```

The link is **never rebuilt** (linking, not copying); never deletes; idempotent.

## Trunk-divergence pre-flight (item #3)

When a worktree is cut from a **local** trunk that lags the remote, the new branch starts
behind. On create, the hook reports how far `origin/main` is ahead and advises a
`git rebase origin/main` before building. Silence with `WORKTREE_DIVERGENCE_NOTICE=0`;
fetch first with `WORKTREE_DIVERGENCE_FETCH=1`.

## Branch taxonomy (item #6)

Two canonical prefixes — keep the taxonomy small so the worktree set stays legible:

| Prefix | Meaning | Lifecycle |
|---|---|---|
| `chat/*` | ephemeral per-chat isolation (auto-created) | auto-reaped when merged+clean |
| `feat/*` | long-lived / human-named feature work | kept; remove manually or set a reap prefix |

`codex/*`, `fix/*`, and other prefixes are **non-canonical** — `worktree_doctor.py` flags
them. Migrate to `feat/*` or mark with `.keep-worktree`. **One branch per deliverable** —
do not reuse a single branch across many PRs (it defeats per-change review).

## Delivering a worktree (item #5)

Deliver a feature **from its own worktree**, never by merging in the primary checkout (the
primary often carries concurrent uncommitted work and the trunk moves mid-task). The
standard path — rebase on the trunk, retest, then push/PR — is codified in
`tools/git/deliver_worktree.py`:

```
python tools/git/deliver_worktree.py --dry-run                          # show plan + divergence
python tools/git/deliver_worktree.py --test "python -m pytest -q <scope>"   # PR mode (default)
python tools/git/deliver_worktree.py --mode push --test "<retest cmd>"      # direct-to-trunk (opt-in)
```

It refuses to run in the primary / on a protected branch, requires a clean tree, aborts on
rebase conflict, skips delivery if the retest fails, and never force-pushes.

## Notes

- The worktree + branch are local only; push/PR when ready via the normal `git`/PR flow,
  from inside the worktree.
- This rule governs **chat isolation**, not commit policy. Commit/push only when the user
  asks, per the operating contract.
- Worktrees are siblings of the primary clone. Merged+clean chat worktrees are reaped
  automatically (above); reap others manually with `git worktree remove <path>` /
  `git worktree prune`.
