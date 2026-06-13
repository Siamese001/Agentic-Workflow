# Outcome-Frame Enforcement — Feasibility & Options

**Question:** Can the mandatory refactor-turn **Outcome frame** (rule
[`001-cursor-runtime-seam-execution.md`](../../../.claude/rules/001-cursor-runtime-seam-execution.md)
§ *Runtime failure ⇒ RCA mandatory*; constitutional §37) be enforced more strongly than the
current advisory audit?

**TL;DR — YES, and the mechanism is already running in this repo.** A Claude Code **Stop hook can
block the turn from ending** (`{"decision":"block","reason":...}` + exit 2) and force the model to
re-compose. [`.claude/hooks/stop_task_audit.py`](../../../.claude/hooks/stop_task_audit.py) already
does exactly this for the `STATUS:`/proof contract. The Outcome-frame check can be promoted from
*advisory-log* to *blocking* the same way. **Correction:** an earlier claim in the originating
session — "Claude Code hooks can't enforce at Stop time, it's advisory only" — was **wrong**; Stop
hooks block via a documented decision, proven by `stop_task_audit.py`.

> Scope: the **strongest available lever is a forced re-compose** (block the stop → model continues
> with feedback). There is **no** hook that silently rewrites the already-composed message before the
> user sees it. "Enforcement" therefore means *the turn cannot end non-compliant*, not *the text is
> edited in place*.

---

## Current state (advisory)

| Layer | File | Behavior |
|---|---|---|
| Rule (SSOT) | `001-cursor-runtime-seam-execution.md` §; constitutional §37 | Describes the frame; always-on, shapes behavior |
| Audit | `.claude/governance/scripts/post_agent_runtime_rca_audit.py` | Detects `missing_refactor_outcome` / `missing_rca` / `incomplete_rca` / `status_signal_mismatch` / `shallow_rca` |
| Dispatch | `.claude/hooks/after_agent_governance_dispatch.py` | Runs the audit as a subprocess and **always `return 0`** → log-only to `artifacts/governance/runtime_rca_violations.jsonl` |

The audit is correct; it just never *acts* on its verdict. The forcing function today is the
always-on rule + a post-hoc JSONL row nobody is blocked by.

---

## Claude Code hook capabilities (grounded)

| Hook | Can block? | Can inject context? | Can rewrite final msg? | Fit for this |
|---|---|---|---|---|
| **Stop** | **YES** — `decision:block`+exit 2 forces continue with `reason` | reason is fed back | No (already in transcript) | **Best lever** |
| UserPromptSubmit | blocks the *prompt* | `additionalContext` before model responds | No | Nudge only — can't see the turn's output |
| PreToolUse (Edit/Write) | blocks the *tool call* | `additionalContext` | input only | Nudge only — fires mid-turn, can't verify final output |
| PostToolUse | feedback after a tool | `additionalContext` | No | Nudge only |
| MessageDisplay | No | No | display-only (not saved, can't block) | Not enforcement |

**In-repo proof the Stop-block works:** `stop_task_audit.py` is the **first** Stop hook (registered
in `.claude/settings.json` `hooks.Stop` ahead of the advisory dispatch). It `raise SystemExit(block(
reason))` when a repo-work response lacks `STATUS:` or a PASS lacks proof sections — and the model
is forced to revise. Same lever, same helper (`lib.claude_hook_common.block`).

**Unknowns (flagged):** `stop_hook_active` (a documented loop-guard field) could not be confirmed in
the current docs — do **not** rely on it; use explicit per-session block-count state. There is no
documented hook that intercepts/rewrites the final assistant text before display.

---

## Options

| # | Lever | Strength | False-positive cost | Effort |
|---|---|---|---|---|
| **A** | **Stop-block on high-confidence `missing_refactor_outcome`** (recommended) | **Hard** — turn can't end without the frame | High if matcher is loose → keep it conservative | Small (reuse `detect()` + `block()`) |
| B | UserPromptSubmit reminder on refactor-looking prompts | Soft nudge | Low | Small |
| C | PreToolUse-on-Edit/Write reminder | Soft nudge | Medium (noisy, fires every edit) | Small |
| D | SKILL/template that makes the frame the default composition shape | Soft (advisory) — but improves *correct* emission | Low | Small |
| E | Status quo (advisory log only) | None | None | Zero |

B/C/D are **complements**, not enforcement — none can verify the final output. A is the only true
forcing function.

---

## Recommended design — hybrid, narrow Stop-block

Keep the advisory audit (full telemetry, all 5 kinds) **and** add a **narrow blocking layer** for the
single highest-confidence, lowest-false-positive case.

1. **Block only on `missing_refactor_outcome`** (frame entirely absent) — not on `shallow_rca` /
   `incomplete_rca` (those are heuristic depth judgments; a false block there is very annoying).
   Promote others to blocking later only if advisory data shows a low false-positive rate.
2. **High-confidence refactor-turn signal.** For the blocking layer, prefer *actual edit tool-use this
   turn* (read the Stop `transcript_path` for `Edit`/`Write`/`MultiEdit`/`NotebookEdit` tool calls
   since the last user message) over the advisory audit's text heuristic (`FILES_CHANGED` + code-file
   extension). Tool-use is unambiguous; text can false-match prose.
3. **Modes (env):** `RUNTIME_RCA_ENFORCE=off|warn|block` (default `warn` = shadow: log "would block"
   without blocking). Promote to `block` after a shadow period. Honor existing
   `RUNTIME_RCA_AUDIT_BYPASS=1` (full skip for scripted/batch runs).
4. **Loop guard (don't trust `stop_hook_active`):** maintain a per-session block counter in a receipt
   file; block at most **once** per turn-cluster, then `allow()` with a logged
   `block_limit_reached` so a model that genuinely can't satisfy it is never trapped. The natural
   guard also holds: once the frame is added, the check passes and no block fires.
5. **Reuse, don't duplicate:** import `detect()` / `_OUTCOME_FRAME_RE` / `_is_refactor_turn` from
   `post_agent_runtime_rca_audit.py` so detection stays SSOT; the gate only adds the block decision +
   mode + loop guard.

### Implementation plan (small)

| Step | Change |
|---|---|
| 1 | New `.claude/hooks/post_agent_runtime_rca_gate.py` (blocking Stop hook). Reads payload via `lib.claude_hook_common`; imports `detect()` from the advisory audit; on `missing_refactor_outcome` with a confirmed edit-tool turn and `RUNTIME_RCA_ENFORCE=block`, emits `block(reason)` with the Outcome-frame template in the reason; else `warn()`/`allow()`. Loop guard via `write_receipt` + a session block-count file. |
| 2 | Register it in `.claude/settings.json` `hooks.Stop` (sibling of `stop_task_audit.py`). |
| 3 | Keep `post_agent_runtime_rca_audit.py` advisory and unchanged (it stays the telemetry SSOT; the gate reuses its `detect()`). |
| 4 | Tests `tests/unit/ops_scripts/hooks/cursor/test_post_agent_runtime_rca_gate.py`: warn-mode never blocks; block-mode blocks a frameless edit-turn; framed edit-turn allows; non-edit turn allows; bypass allows; loop guard stops after N. |
| 5 | Rollout: ship in `warn` (shadow) → review `runtime_rca_violations.jsonl` + receipts for false positives → flip default to `block`. |

Estimated footprint: ~1 new hook (~80 lines) + 1 settings entry + 1 test file. No change to the rule
text (the contract is already correct) or the advisory audit.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| False-positive block (model annoyed / wasted re-compose) | Conservative matcher (edit-tool-use only) + `warn` shadow period + block only `missing_refactor_outcome` |
| Infinite loop (model can't satisfy) | Per-session block counter → allow after 1; not dependent on undocumented `stop_hook_active` |
| Token cost of re-compose | One extra turn only; acceptable for the value; bypass for batch runs |
| Over-reach onto non-refactor turns | `.md`-only / doc turns are **not** refactor turns (audit's code-file extension list excludes docs); gate uses the same definition |
| Blocking on a genuinely-correct turn the heuristic misreads | Shadow data first; keep `RUNTIME_RCA_AUDIT_BYPASS=1` escape hatch |

---

## Honest verdict

- **Stronger-than-advisory enforcement IS feasible** and is the *same* mechanism already proven by
  `stop_task_audit.py`. The prior "advisory only / can't block at Stop" framing was incorrect.
- The strongest lever is a **forced re-compose** (block the stop), not an in-place rewrite — no hook
  can do the latter.
- Recommended path is the **hybrid**: advisory audit stays for full telemetry; a **narrow,
  shadow-first Stop-block** on `missing_refactor_outcome` (edit-tool turns) becomes the teeth.
- Residual uncertainty: exact loop-guard field (`stop_hook_active`) — sidestepped with explicit
  state. Verify on the live platform during the shadow rollout.
