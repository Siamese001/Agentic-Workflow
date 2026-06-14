---
plan_format: v2
slug: worktree-deliver-reap-b3f7d1
status: Completed
dod_exempt: true
---

# Worktree deliver-and-reap automation — atomic deliver + auto-cleanup

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
TOTAL_WAVES: 2
LAST_UPDATED: 2026-06-14

## Context (SCQA)

**Situation:** After a pass landed on `main`, the `feat/*` worktree + branch were left behind — every
delivery step was manual.
**Complication (RCA):** delivery is user-gated-manual (operating contract "push only when asked");
the only cleanup automation (`prune_merged_chat_worktrees.py`) runs at SessionStart and reaps `chat/*`
only — `feat/*` is the deliberately long-lived prefix, never auto-reaped. The two are un-bridged, so a
`feat/*` worktree (chosen for mid-session safety vs the chat reap-race) is delivered by hand then
orphaned. `tools/git/deliver_worktree.py` already does fetch→rebase→test→push/PR but **stops after the
push without reaping.**
**Question:** how to make deliver + cleanup one reliable action without auto-pushing every green
checkpoint?
**Answer (user-approved):** keep delivery an explicit trigger, but make that ONE action atomic
(rebase→push→reap worktree→delete branch), and extend the SessionStart reaper to also auto-reap
merged+clean `feat/*` leftovers. No auto-push on prose `STATUS: PASS`.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | deliver_worktree.py post-push reap | ~10k | push-mode means branch == trunk tip (merged); reap runs from the primary checkout | DONE | `--mode push` reaps worktree + local/remote branch after a clean push; `--mode pr` does not |
| W2 | P2 | reaper feat/* default + doctrine + test | ~12k | merged+clean+grace guards protect unmerged/in-progress work | DONE | delivered `feat/*` reaped at SessionStart; deliver `--reap` integration test passes |

### Phase Progress
| Phase | Status |
|---|---|
| P1 — deliver post-push reap | DONE |
| P2 — reaper default + doctrine + test | DONE |

## Wave 1 — deliver_worktree.py post-push reap

WAVE_STATUS: DONE
WAVE_COMPLETE: YES

Add `--reap` / `--no-reap` (default reap ON). After a successful `--mode push` (HEAD:trunk — the branch
is now the trunk tip, i.e. merged), run cleanup FROM THE PRIMARY CHECKOUT (cwd cannot be the worktree
being removed): verify `merge-base --is-ancestor branch origin/trunk`, `git worktree remove` (+ `--force`
fallback), `git branch -d` (safe, merged), best-effort `git push origin --delete <branch>`. Skip reap
for `--mode pr` (branch not merged yet — the SessionStart reaper cleans it post-merge). Update docstring
+ dry-run output. Never force-push; fail-soft on the remote delete.

## Wave 2 — reaper default + doctrine + test

WAVE_STATUS: DONE
WAVE_COMPLETE: YES

`prune_merged_chat_worktrees._DEFAULT_REAP_PREFIXES` → `("chat/", "feat/")` so delivered `feat/*`
worktrees are auto-reaped at the next SessionStart (backstop for PR-merged or `--no-reap` deliveries);
the existing merged+clean+grace guards already protect unmerged/in-progress work. Document the
deliver+reap flow in `.claude/rules/git-branch-per-chat.md` (NO new skill — document in the rule to
avoid skill bloat). Add `tests/unit/tools/git/test_deliver_worktree.py`: build a temp git repo + bare
remote, deliver `--mode push --reap`, assert the worktree dir and branch are gone; assert `--mode pr`
and `--no-reap` do not reap.

## Definition of Done
| # | Criterion | Verify |
|---|---|---|
| 1 | `--mode push` (default reap) removes worktree + branch after a clean push | integration test |
| 2 | `--mode pr` does NOT reap (branch unmerged) | test |
| 3 | `--no-reap` disables reap | test |
| 4 | reaper default reaps merged+clean `feat/*` | read prefixes + reaper dry-run |
| 5 | `git-branch-per-chat.md` documents the deliver+reap flow | read rule |
| 6 | new test passes; existing `tests/unit/tools/git` still pass | pytest |

Verification-vs-Deferral: all six verified this session; nothing deferred.
