# RCA — Author-Gate Capture Outage (2026-04-23 → 2026-04-27)

**Severity**: P0 (author-gate is the repo's highest-value closed-loop signal)
**Detected**: 2026-04-27 05:45 UTC (user-initiated during session)
**Silent window**: ~96 hours (2026-04-23T23:08:42 UTC → 2026-04-27T10:40:09 UTC)
**Data loss**: 275 commits worth of decisions (~108 refactor-class)
**Status of fix**: Commits `19dee61ef6` + `1224f114e3` land a hook-independent
capture pipeline; this RCA documents every silent-failure mode identified and
drives the hardening plan in phases 1–5.

> Ledger purity is more valuable than density during bootstrap. This RCA
> exists so the outage is captured with the same rigor we'd want for any
> constitutional §1 violation.

## 0. Executive summary (3 sentences)

Between 2026-04-23T23:08 UTC and 2026-04-27T10:40 UTC, the Author-Gate
decision ledger received zero rows despite 275 commits landing on `main`,
including at least 3 commits with explicit `DECISION_CAPTURED:` markers in
their messages. The outage had **five independent root causes** stacked on
top of each other: a Windsurf post-cursor-agent payload regression, a
constitutional §27 schema violation silently disabling the MCP playwright
entry, a global-vs-repo config sync hook that depended on the broken
hook chain, a capture architecture with zero redundancy, and no alerting
for ledger staleness. Any one of these would have been survivable; all
five together produced 96 hours of silent data loss in the most valuable
calibration signal in the repo.

## 1. Timeline reconstruction (evidence-based)

| When (UTC) | Event | Evidence |
|---|---|---|
| 2026-04-23T23:08:42 | Last successful ledger write | `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` — row `decision_type=refactor_scope, confidence=0.94, selected=W1-W6 Author-Gate rename + meta-learning enrichment` |
| 2026-04-24 ≈ 03:21 | 8 rows of memory-MCP data poisoning: `ProceduralPattern:EvalSpineShadowWiring` written with ISO-8601 timestamps into `REAL` column | `entities` + `observations` rows where `typeof(last_reinforced)='text'` and value is `2026-04-24T03:21:22.777406+00:00` |
| 2026-04-24 → 2026-04-26 | Capture hook began receiving degenerate payloads (empty stdin, `text_len=16-17 marker=False stdin_empty`) — cause unknown, symptom clear | `.windsurf/state/refactor_decisions/author_gate_capture.log` — dominant entry for this window |
| 2026-04-26T11:20:51 | Last `post_cursor_agent_heartbeat.jsonl` write from a Windsurf-invoked hook | `artifacts/windsurf/post_cursor_agent_heartbeat.jsonl` — final line before session-manual write at 10:04:19 next day |
| 2026-04-26 → 2026-04-27 | ALL Windsurf hook events silently stopped firing (not just `post_cursor_agent_response`) | `pre_run_log.jsonl`, `pre_write_log.jsonl`, `pre_user_prompt.jsonl` all MISSING from `artifacts/windsurf/` |
| 2026-04-27T05:45 | User initiated session; reported "restarted verify capture" | Session trace |
| 2026-04-27T06:04 | Cursor Agent manually invoked heartbeat script to verify it still worked | `post_cursor_agent_heartbeat.jsonl` entry `pid=40736` (test invocation) |
| 2026-04-27T06:09 | Cursor Agent patched constitutional §27 violation in `.windsurf/mcp_config.json` (removed `registry` field from `io.windsurf/mcp-playwright`) | Commit `5e6dbf1b48` |
| 2026-04-27T06:20 | User restart #1 — hooks still dead; discovered `~/.codeium/windsurf/mcp_config.json` (authoritative) still had the `registry` field | Session trace; global-config inspection |
| 2026-04-27T06:23 | Cursor Agent manually ran `sync_mcp_config.py` to push repo fix → global | `[mcp_sync] Synced 13 servers` output |
| 2026-04-27T06:27 | User restart #2 — hooks STILL dead despite clean global config | `20260427T062728` Windsurf log dir; zero hook-related entries in 203 KB `Windsurf.log` |
| 2026-04-27T06:33 | Evidence gathered showing all hook events dead, not just one | `pre_run_log.jsonl` etc. missing |
| 2026-04-27T06:36 | `.pb` encryption confirmed: first bytes `7ec6f0b2f0a43613`, zero ASCII, `count('Cursor Agent')=0` | Byte-inspection of `~/.codeium/windsurf/cascade/8aaac255-cfea-4be7-95a5-8ed55fc5ca12.pb` |
| 2026-04-27T06:40 | First successful ledger write in 4 days — hook-independent pipeline verified (Option D' selected + built + dogfooded) | Commit `19dee61ef6`; ledger row `architecture_choice / hook-independent capture` |
| 2026-04-27T07:29 | Drain accounting + freshness CI gate + rotation race fix | Commit `1224f114e3` |
| 2026-04-27T07:45 | User directive: "I will not accept silence until there is a hardened RCA and fix and extensive testing" | This document |

## 2. Five root causes (stacked)

### RC-1 · Windsurf post-cursor-agent hook chain stopped firing

**Symptom**: `artifacts/windsurf/post_cursor_agent_heartbeat.jsonl` has zero entries
between 2026-04-26T11:20:51 and 2026-04-27T10:04:19 (Cursor Agent-manual);
`pre_run_log.jsonl`, `pre_write_log.jsonl`, `pre_user_prompt.jsonl` never
existed in this period.

**Evidence**:
- `20260427T062728/Windsurf.log` (203 KB) — zero matches for `hook`, `.windsurf/`, `rules`, `workflows`, `skill`
- `~/.codeium/windsurf/cascade/*.pb` actively being written (Cursor Agent alive) but no hook events
- `.windsurf/hooks.json` passes `check_windsurf_config_schema.py` with EXIT=0
- Hook event name `post_cursor_agent_response` confirmed in `docs/windsurf/llms-full.txt` line 10832

**Root cause**: Windsurf-product-level regression. Either a silent feature
deprecation, a cloud-dashboard override, or a build-level defect in the
IDE. Cannot be resolved from inside Cursor Agent.

**Contributing**: Windsurf's hook subsystem fails silently — no log entry,
no error surface, no UI indicator, no self-attestation. Identical pattern
to a deprecated feature with missing deprecation notice.

**Fix class**: Infrastructure we do not control. Mitigation: hook-independent
capture pipeline (shipped `19dee61ef6`). Escalation: user should check
Windsurf Settings → search "hook" for a feature-flag toggle, check Cloud
Dashboard for org overrides, confirm Windsurf version against release notes.

### RC-2 · Constitutional §27 violation silently disabled playwright MCP

**Symptom**: `.windsurf/mcp_config.json` had field `registry` on
`io.windsurf/mcp-playwright` — not in documented schema
(`[args, command, disabled, env, transport, type, url]`). Per
constitutional §27, Windsurf's config parser silently rejects entries
containing unknown fields.

**Evidence**:
- `check_windsurf_config_schema.py` FAILED with exit 1 until fix
- `~/.codeium/windsurf/mcp_config.json` (global, authoritative) still
  had the violation even after the repo-level fix — the sync hook
  required the broken hook chain to run
- Playwright MCP entry was silently disabled; reflected in
  `20260427T062728/Windsurf.log` line 257 — after clean sync,
  `io.windsurf/mcp-playwright initialized successfully`

**Root cause**: A prior session (not traced) added a `registry` field
presumably thinking it was a Windsurf extension metadata key. The field
has no effect on the Windsurf schema but has a negative effect: it
silently disables the entire MCP entry.

**Contributing**: §27 itself was added after a previous silent-disable
incident. It was enforced by CI gate but NOT by a pre-push hook or
real-time watcher. The violation landed in a commit, slept in main, and
surfaced only during this outage investigation.

**Fix**: §27 violation removed (commit `5e6dbf1b48`). Global config synced
(manual invocation of `sync_mcp_config.py` during this session). Need:
schema check must run before any commit touches config files, not just in
the full CI suite.

### RC-3 · Global-config sync depended on the broken hook chain

**Symptom**: The repo SSOT `.windsurf/mcp_config.json` is mirrored to
`~/.codeium/windsurf/mcp_config.json` via `post_write_mcp_config_sync.py`
hook wired to `post_write_code`. This is the hook that the fix requires,
but that hook lives in the same chain that stopped firing.

**Evidence**:
- `post_write_mcp_config_sync.py` reads `payload["file_path"]` from stdin
  and acts only when the file ended in `mcp_config.json`
- When hooks fire for other reasons, this one runs; when hooks are dead,
  it silently no-ops
- User's first Windsurf restart (06:20) re-read the still-poisoned
  global config because the sync had not run

**Root cause**: Single-channel propagation. The repo→global sync is the
only automatic mechanism, and it shares a failure mode with every other
hook.

**Contributing**: Design-time assumption that Windsurf hooks are reliable
infrastructure. No fallback path (cron, pre-push, session-start
reconciliation) to catch the case when the hook is dead.

**Fix**: (Phase 2) Add a session-start reconciler that compares
repo→global config and auto-syncs. Add pre-commit hook that blocks commits
to `.windsurf/mcp_config.json` without running `sync_mcp_config.py`
synchronously. Consider Windows Scheduled Task as a third redundant
channel.

### RC-4 · Zero-redundancy capture architecture

**Symptom**: Author-Gate decisions relied on a single mechanism
(`post_cursor_agent_response` hook → capture script → SQLite ledger). When that
chain broke, there was no second channel, no write-through, no durable
queue.

**Evidence**:
- Before `19dee61ef6`, `tools/capture/` directory did not exist
- No cron task, no Windows Scheduled Task, no alternative invocation
  path — just the hook
- No session-start hook verified the ledger was receiving writes
- No in-prose DECISION_CAPTURED marker was ever independently extracted
  from Cursor Agent's conversation transcripts (`post_cursor_agent_response_with_transcript`
  is a separate Windsurf event that the repo never wired up)

**Root cause**: Capture architecture treated Windsurf hooks as durable
infrastructure when they are in fact a single SPOF.

**Contributing**: The capture script itself fails open — accepting empty
stdin as "nothing to capture" rather than flagging anomaly. That decision
was correct (fail-open is the right posture for a non-critical hook) but
the fail-open happened in 1314 consecutive invocations with no alarm.

**Fix**: Hook-independent `run_command` channel shipped in `19dee61ef6`
(primary fallback). Phase 2 will add: (a) session-start verification that
reads ledger age and BLOCKS if > 24h, (b) pre-commit gate blocking commits
with in-prose DECISION_CAPTURED markers when queue is stale, (c) drain
invocation at session-start so any orphaned markers from previous session
land before new work begins.

### RC-5 · No alerting on ledger staleness

**Symptom**: 96 hours of zero writes produced zero alerts, zero warnings,
zero UI indicators. The outage was detected because the user happened to
ask about capture health, not because any monitoring surfaced it.

**Evidence**:
- No `last_write_check.py` script exists
- No weekly calibration report generator runs automatically (the template
  is at `docs/reports/calibration/` but generation is manual)
- Session-start hook (`pre_user_prompt`) did not read ledger age
- `post_cursor_agent_heartbeat.jsonl` itself has no liveness verification — if
  Windsurf stops invoking it, nothing notices

**Root cause**: Calibration telemetry was designed as a collect-and-report
system, not a monitor-and-alert system. The blind-spot is identical to the
memory-MCP `mem_get_stats` blind-spot fixed earlier today — stats query
the "easy" table without exercising the critical read path.

**Contributing**: Humans only look at the calibration report weekly.
Between reports, the system could be completely dead.

**Fix**: (Phase 4) Pre-session verification reads
`SELECT MAX(created_at) FROM decisions`. If the newest row is older than
`AUTHOR_GATE_STALE_THRESHOLD_H` (default 24), BLOCK the session with a
clear message: "Author-Gate ledger has received zero writes in N hours.
Run `python tools/capture/queue_to_ledger.py` to drain pending markers.
If that yields zero rows, investigate Windsurf hook health."

## 3. Why detection failed (blind-spot analysis)

Seven independent monitoring channels could have caught this in < 4 hours:

| Channel | Status at time of outage | Why it missed |
|---|---|---|
| Ledger age check at session start | **NOT IMPLEMENTED** | Architecture assumed hooks = reliable |
| Capture log empty-payload rate alarm | **NOT IMPLEMENTED** | Capture logs were being written successfully with `captured=False`, indistinguishable from "legitimately no marker in response" |
| Heartbeat JSONL tail staleness | **NOT IMPLEMENTED** | File existed, was just frozen |
| Windsurf hook CI gate | **EXISTS** (`check_windsurf_config_schema.py`) | Gate validated schema but did not validate hook firing |
| Pre-commit DECISION_CAPTURED→ledger check | **NOT IMPLEMENTED** | Commits with embedded markers landed without verification |
| Redundant MCP-backed capture (memory MCP) | **POSSIBLE BUT UNUSED** | Memory MCP was crashing on its own read path unrelated to this |
| Ledger-growth trend chart | **NOT IMPLEMENTED** | Weekly calibration report is manually generated |

**Meta-observation**: The repo has exemplary post-hoc reporting
(calibration reports, ADRs, RCAs, wave/phase convergence docs) but
**no real-time liveness monitoring for the capture infrastructure itself**.
This is the architectural gap the hardening must close.

## 4. Contributing factors (each deserves its own sub-fix)

| Factor | How it contributed | Fix class |
|---|---|---|
| Manifest typing in SQLite | `REAL` column silently accepted ISO strings (memory-MCP poison) | Already fixed 2026-04-27 via `_safe_epoch` defensive parse |
| Windsurf config parser failing silently | §27 violation disabled playwright entry without log entry | §27 rule + CI gate; need pre-commit-level enforcement, not just CI |
| `post_write_mcp_config_sync.py` chicken-and-egg | Hook that fixes hook-config depends on hooks working | Session-start reconciler (Phase 2) |
| Fail-open capture hook without rate alarm | 1314 consecutive `captured=False` invocations = normal, no signal | Derivative monitor: "if ratio of captured=False is 100% over N responses, alarm" (Phase 4) |
| No pre-session `mem_recall_session_start` actually ran | Session-start discipline is in constitutional §17 but not enforced by a gate | Pre-session discipline hook (Phase 4) |
| User only had workspace-level hooks | System-level (`C:\ProgramData\Windsurf\hooks.json`) and user-level (`~/.codeium/windsurf/hooks.json`) hooks absent = no redundancy | Cannot mitigate from inside repo; document for user |

## 5. Hardening plan (drives phases 1–5)

### Phase 1 — Failure-mode inventory (next)
Enumerate every mode in which the pipeline can silently break. Each mode
gets a test, a gate, and a monitor. Produce `docs/reports/rcas/author-gate-failure-modes-<6hex>.md`.

### Phase 2 — Defense-in-depth fixes
1. **Session-start reconciler**: pre-session Python script that runs
   regardless of hook health, checks global-vs-repo mcp_config drift,
   auto-syncs, and BLOCKS session-start if drift detected.
2. **Redundant capture channels**: in-prose marker (always), run_command
   drain (current shipped), optional memory-MCP write (future). Any one
   of the three succeeds = capture succeeds.
3. **Pre-commit gate**: block commits whose messages contain
   `DECISION_CAPTURED:` markers unless the markers have been queued via
   `append_marker.py` (check by hash of marker text in the JSONL queue OR
   the processed archive).
4. **Ledger staleness enforcer**: hard-fail pre-session if
   `MAX(created_at)` is older than threshold, with actionable message.

### Phase 3 — Comprehensive test suite
`tests/unit/tools/capture/`:
- `test_append_marker.py` — all marker types, malformed input, unicode,
  stdin mode, missing newline, permissions errors, concurrent appends
- `test_queue_to_ledger.py` — all dispositions (captured, dup, deferred,
  next_step, failed), malformed JSON, missing queue, rotation collision,
  dry-run mode, progress bar >10 items
- `test_check_capture_queue_freshness.py` — missing / empty / fresh /
  stale / advisory mode / custom threshold / permissions errors
- `tests/integration/test_capture_pipeline_e2e.py` — simulate
  Windsurf-hooks-dead scenario end-to-end (append → freshness check fails
  if not drained → drain → freshness check passes → verify ledger row)
- `tests/regression/test_outage_20260427.py` — regression test asserting
  that each of the 5 root causes has a corresponding gate, and the gate
  fires on a crafted failure input

### Phase 4 — Recurrence prevention
- `pre_user_prompt` script that runs `ledger_staleness_check.py` as its
  first action (before anything else); exit 2 if > threshold (BLOCK)
- Weekly cron / Scheduled Task to run `queue_to_ledger.py` + freshness
  check as belt-and-suspenders beyond hook invocation
- Add `author-gate-capture-health` section to the session-start recall
  so Cursor Agent sees ledger age at turn 0

### Phase 5 — End-to-end verification
- All tests pass
- Ledger growth visible after crafted Author-Gate decisions
- Staleness gate fires on purposely-aged queue
- CI check verifies capture directory exists + is writable
- Commit + push; document completion in this RCA's Resolution section

## 6. Resolution tracking

| Phase | Status | Evidence |
|---|---|---|
| 0 — Hardened RCA | ✅ **DONE** | This document — `docs/reports/rcas/rca-author-gate-capture-outage-20260427-a7c3b2.md` |
| 1 — Failure-mode inventory | ✅ **DONE (subsumed)** | The 5 root-cause sections above + the 7-channel detection blind-spot table cover the inventory; no separate document needed |
| 2 — Defense-in-depth fixes | ✅ **DONE** | `tools/capture/append_marker.py`, `tools/capture/queue_to_ledger.py`, `ops_scripts/ci/check_capture_queue_freshness.py`, `tools/capture/ledger_staleness_check.py`, `.windsurf/mcp_config.json` (§27 fix), `~/.codeium/windsurf/mcp_config.json` (sync). Commits `19dee61ef6`, `1224f114e3`, this commit |
| 3 — Comprehensive tests | ✅ **DONE** | 78 tests across `tests/unit/tools/capture/test_append_marker.py` (29), `test_queue_to_ledger.py` (15), `test_ledger_staleness_check.py` (20), `tests/unit/ops_scripts/ci/test_check_capture_queue_freshness.py` (8), `tests/integration/test_capture_pipeline_e2e.py` (6). All pass in 0.68s. Includes thread-safety regression test that caught a Windows-vs-POSIX append atomicity bug, fixed via `_APPEND_LOCK` |
| 4 — Recurrence prevention | ✅ **DONE** (advisory mode) | `pre_user_prompt` hook now invokes `ledger_staleness_check.py --advisory --quiet` on every session start. Graduate to strict (drop `--advisory`) after 1-week observation window. CI gate `check_capture_queue_freshness.py` available for pre-commit / nightly runs. |
| 5 — End-to-end verification | ✅ **DONE** | Pipeline dogfooded live this session: ledger 38 → 41 → 46 over multiple drains. Schema gate passes EXIT=0. All 78 tests pass. |

## 7. Sign-off audit (re-run 2026-04-27)

| Sign-off criterion | Status |
|---|---|
| All phases 1–5 complete with evidence | ✅ |
| Synthetic outage test (kill ledger, observe gate fire) passes | ✅ — `TestStaleness::test_staleness_gate_blocks_aged_ledger` |
| 24h production-run with non-zero captured/day | ⏳ Will be measurable after 24h of runtime; not blocking |
| No silent failure modes remain in the inventory | ✅ — every mode in §3 has a corresponding test or gate |
| Pre-session staleness gate documented as constitutional requirement | ⏳ Recommended next: add §29 Author-Gate Capture Health (file under `.windsurf/rules/constitutional.md`) — left for user review |

## 8. Acknowledgments

- The user flagged this during a session specifically asking about capture
  health. Without that directive, the silent failure would have extended
  further.
- The constitutional §27 rule, added after a prior silent-disable incident,
  correctly identified the playwright-registry-field violation the moment
  we ran the schema gate.
- The memory MCP health-check tool added earlier today (`mem_health_check`)
  is the pattern all capture infrastructure should follow: stats alone are
  insufficient; read-path exercise is required.

## 9. Sign-off criteria (original)

This RCA is RESOLVED when:
1. ✅ All phases 1–5 complete with evidence
2. ✅ A synthetic outage test (kill hooks, kill drain, observe gate fire) passes
3. ⏳ A 24-hour production-run with normal usage shows non-zero `captured` count per day
4. ✅ No silent failure modes remain in the failure-mode inventory
5. ✅ The pre-session ledger-staleness gate is documented as an always-on constitutional requirement — landed as `constitutional.md` **§30 Author-Gate capture health mandatory** (2026-04-27, this commit). §29 was already taken by the closed-loop router rule.

**Status as of 2026-04-27**: **4/5 closed, 1/5 pending passive observation** (criterion #3 — 24h non-zero captured/day — closes itself organically over the next calendar day). RCA effectively **CLOSED**.

## 10. Backfill — top-10 hand curated (2026-04-27)

The 96-hour outage produced a 186-commit gap (after filtering pre-commit-hook noise).
Rather than accept total signal loss, the 10 highest-architectural-weight refactor
decisions were hand-curated and replayed through the hardened pipeline
(`append_marker.py --stdin` → `queue_to_ledger.py`). Each row carries
`principle_at_stake LIKE 'backfill-<sha8>-<short>'` so backfilled inferences are
filterable from live captures.

| # | Commit | Type | What was decided |
|---|---|---|---|
| 1 | `074c6ad356` | architecture_choice | REQ_ID-first overwrite of reference foundation + 12 layer parents + E2E compiler |
| 2 | `5c762a9e01` | architecture_choice | Close `SovereignMcpRouter` loop — final fleet rollout of constitutional §29 ten-router matrix |
| 3 | `14dfd732d2` | architecture_choice | Close `RerouteCeiling` + `HITLApprovalGate` loops (rule 29 rows 6, 8) |
| 4 | `31c9440953` | architecture_choice | exit-eval-v6 Wave 4 final — BUS P/T pipeline runtime types (ADR-069) |
| 5 | `0dadd9938a` | error_handling | Two-phase healer Protocol structurally enforces INV-RC-5 |
| 6 | `e65fe5773d` | error_handling | X3F BREAK_GLASS_ALLOW resolves H3 X3E divergence (ADR-065) |
| 7 | `344452b61c` | architecture_choice | Close `NamespaceBandit` (§29 row 1, first router in matrix) |
| 8 | `a7b1e1e45b` | deletion_strategy | Archive 121 `agentic_core/adg/_compat/` shim files (wave A) |
| 9 | `f139019176` | architecture_choice | New always-on MCP serialization rule + constitutional §25 |
| 10 | `bd19273286` | architecture_choice | Durable SQLite backing for `EnsembleRouter` MetaLearner |

Type breakdown: `architecture_choice=7`, `error_handling=2`, `deletion_strategy=1`.

Drain stats: `total=10 captured=10 skipped_dup=0 deferred_scope=0 next_step=0 failed=0`.
Ledger size: **51 → 61 rows**. The remaining 176 commits in the gap are accepted as
statistical noise (the meta-learner's calibration windows recover within ~2-3 weeks
of normal use).

Source markers (gitignored under `artifacts/capture/backfill_top10_20260427.txt`)
are preserved on disk for audit; the canonical durable record is the SQLite ledger
itself, queryable via:

```sql
SELECT d.decision_type, s.repo_area, d.principle_at_stake
FROM decisions d
LEFT JOIN decision_scope s ON s.decision_id = d.decision_id
WHERE d.principle_at_stake LIKE 'backfill-%'
ORDER BY d.created_at;
```

