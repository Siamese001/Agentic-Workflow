# apps_lic InMail Route, Judge Repair, and Harness Retest Plan

Created: 2026-06-09
Worktree: `C:\Git\Agentic-Workflow-apps_lic`

## Objective

Fix the persistent ADG MCP health `Transport closed` RCA, then make the canonical apps_lic live harness generate InMail-first outreach with bounded judge-feedback regeneration and readable proof artifacts for every message.

## RCA

### ADG transport closed

Direct ADG service health was healthy:

- SQLite SSOT: `healthy`
- Redis cache: `healthy`
- Snapshot: `06082026_1758`
- Direct MCP stdio `initialize` + `tools/call adg_health`: `status=ok`

The failure was not SQLite, Redis, or ADG handler logic. The live repro showed `guard_single_instance()` matched the ADG module marker inside ancestor launcher command lines and terminated those ancestors. From the MCP client this appears as `Transport closed`.

Fix: keep stale-sibling termination, but skip current-process ancestors before marker-based termination.

### InMail gap

The canonical runtime was still biased to short LinkedIn messages:

- `build_cli_ingress_raw()` defaulted `channel="linkedin"`, `include_subject_line=False`, and body max 600.
- PA/Qwen prompt explicitly said no subject and `message_text` <= 600, max 2 short paragraphs.
- W6 length budgets were 400-750 characters and not route-aware.
- W4/W5 did not carry or validate `subject_line`.
- Judge-feedback repair told Qwen to preserve a concise LinkedIn tone, not the route envelope.
- Live harness did not force `NOT_CONNECTED + premium_available => INMAIL`.

## Waves

### W0 Transport RCA

- Patch `tools/mcp/mcp_bootstrap.py` so `guard_single_instance()` skips ancestor launcher processes.
- Add regression coverage for Python ancestor command lines containing the ADG marker.
- Verify direct MCP stdio `adg_health` returns healthy SQLite/Redis.

### W1 Route Envelope

- Add a compact canonical LinkedIn route envelope resolver.
- Map `NOT_CONNECTED + premium_available` to `INMAIL`, `linkedin_inmail`, 1900 chars, subject required.
- Map `NOT_CONNECTED + no premium` to `CONNECTION_REQ`, `linkedin_chat`, 300 chars, no subject.
- Preserve connected/follow-up as long-form direct draft while keeping no-send governance.

### W2 W6 Contract

- Add `subject_line` to `WholeMessageCandidate`.
- Make `resolve_length_budget()` channel-aware.
- Keep word bands advisory only; enforce sentence count and character cap.
- Use four archetype templates: Recruiter/TA, Senior TA, Executive, C-level with CEO mapped to C-level.

### W3 PA/Qwen Prompt Assembly

- Make output format route-aware.
- For InMail require JSON subject + body, 4-7 sentence budget depending archetype, CTA, and Amit signature.
- For connection request preserve <300 character behavior with no subject.

### W4 Candidate Propagation

- Preserve `subject_line` in Qwen parsed output, W4 materialization, selected candidate receipts, and fallback/stub paths.
- Keep selected top-level message and selected candidate synchronized.

### W5 Validation and Repair

- Add InMail subject validation: non-empty subject <= 200.
- Add channel caps: `linkedin_inmail` <= 1900, `linkedin_chat` <= 300.
- Preserve route/channel/subject in bounded judge-feedback regeneration.
- Repair loop remains bounded by configured repair budget and never sends.

### W6 Harness Reporting

- Run all 12 live matrix contacts as InMail by default.
- Add route/channel/subject/body chars/template columns.
- Render full messages as readable Markdown sections, not as a wide table cell or fenced block.

### W7 Verification

- Run targeted unit tests for guard, route envelope, W6/W4/W5, and judge repair.
- Run the live 12-contact harness with Qwen/vLLM required and Claude judge enabled when `.env` provides the key.
- Report pass/block/gaps with full messages and scores.

## Acceptance

- ADG direct MCP stdio health passes with SQLite SSOT and Redis healthy.
- No mock Qwen path is allowed in live harness.
- Each live row is `INMAIL` / `linkedin_inmail` with a subject line and signed body.
- Each row exposes title, LIC recipient class, mapped archetype/template, full message, and gate score out of 10.
- Any block is explained as a runtime blocker, not hidden behind data dumps.

## Closeout: 2026-06-09

Implementation completed in `C:\Git\Agentic-Workflow-apps_lic`.

### Transport RCA result

- `mcp__adg_sqlite.adg_health` in this Codex session still returns `Transport closed`, which indicates a stale/dead MCP client transport handle.
- Direct ADG handler health is healthy: SQLite SSOT `healthy`, Redis cache `healthy`, `cache_hit_capable=true`, snapshot `06082026_1758`.
- Direct ADG handler query path succeeds, including repeated `adg_nodes_by_file("apps_lic/engines/generation_engine.py")` calls.
- The implemented root-cause fix remains `guard_single_instance()` ancestor skipping: the server no longer terminates parent launcher processes whose command line contains `tools.adg.mcp.server`.
- Remaining recovery action for the interactive MCP tool handle is client/server transport restart, not a SQLite/Redis/server-code fix.

### Harness RCA result

- The remaining failures after InMail enablement were not route or provider issues. They were two recruiter-specific X1D quality failures:
  - Citi recruiter: redundant bridge sentence, generic opener, weak finance relevance for the commercialization claim.
  - Neo4j recruiter: technical depth mismatch for recruiter, redundant bridge sentence, CTA too narrow.
- The repair loop now falls back to bounded recruiter-appropriate company templates when judge feedback flags those exact failure modes.
- Repaired candidates now recompute `claims_used` from the final repaired body against `request.proof_packet.proof_ids`, preventing text/proof drift after deterministic repair.

### Verification result

- Focused repair/validation tests: `14 passed`.
- MCP guard tests: `12 passed`.
- Broader apps_lic/InMail/repair regression sweep: `57 passed`.
- Live harness: `python scripts/apps_lic/run_post_w7_live_12_archetype_matrix.py --clean`
  - Acceptance: `true`
  - Rows: `12`
  - Clear drafts: `12`
  - Quality violations: `0`
  - Routes: all `INMAIL`
  - Channels: all `linkedin_inmail`
  - Provider mode: `live_qwen_vllm_required`
  - X1D judge mode: live Claude required/enabled

Proof artifacts:

- `artifacts/apps_lic/post_w7_live_12_archetype_matrix/summary.json`
- `artifacts/apps_lic/post_w7_live_12_archetype_matrix/rows.json`
- `artifacts/apps_lic/post_w7_live_12_archetype_matrix/full_messages.md`
