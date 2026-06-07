---
plan_id: notion-backlog-residual-cleanup-c3d8f2
plan_type: tracker
---

# Notion Backlog Residual Cleanup

Apply the 5 deferred cleanups from the 2026-04-24 walkthrough: 4 valid Pass 1 scores, 4 questionable Pass 1 scores (investigate per-row), 3 Pass 2 PARTIAL rewrites, 68 unscorable band-extraction recovery, and push 2 local commits to origin/main.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/notion/_pending_rescore.json` | Pass 1 dry-run output | ✅ |
| `artifacts/notion/_pending_audit.json` | Pass 2 dry-run output | ✅ |
| `artifacts/notion/open_rows_with_ids.json` | Source of truth for 153 rows | ✅ |
| `artifacts/adg/adg_indexed_04242026_0513.sqlite` | ADG snapshot for re-validation | ✅ |
| `tools/debug/_backlog_two_pass.py` | Existing dry-run engine | ✅ |
| `tools/debug/_apply_landed.py` | Existing apply engine | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|---|---|---|---|---|
| Wave A | Apply 4 valid Pass 1 scores | Notion PATCH x4 | A | ~2K 🟢 |
| Wave B | Investigate 4 questionable scores | Per-row ADG re-check + decide | B | ~6K 🟢 |
| Wave C | Rewrite 3 PARTIAL Blocking Items | Notion PATCH x3 | C | ~3K 🟢 |
| Wave D | Band-extraction for 68 unscorable | Regex + Notion PATCH | D | ~8K 🟢 |
| Wave E | Push 2 commits to origin/main | git push | E | ~1K 🟢 |

**Total: ~20K tokens across 5 waves, all GREEN.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| A.1 | Apply 4 valid Pass 1 scores | tools/debug/_apply_pass1_valid.py | PP-A1 | ~2K | 🔲 TODO |
| B.1 | GAP-4 re-investigate (overscored) | _backlog_two_pass.py logic | PP-B1 | ~2K | 🔲 TODO |
| B.2 | W5/5.1 re-investigate | per-row ADG check | PP-B2 | ~1K | 🔲 TODO |
| B.3 | Wave 3/3.2 re-investigate | per-row ADG check | PP-B3 | ~1K | 🔲 TODO |
| B.4 | W1-P0/1.2 re-investigate (zero impact) | per-row ADG check | PP-B4 | ~1K | 🔲 TODO |
| C.1 | Rewrite W2/2.8 HITL SVP Calibration | Notion PATCH | PP-C1 | ~1K | 🔲 TODO |
| C.2 | Rewrite W2/2.2 Policy Cleanup | Notion PATCH | PP-C2 | ~1K | 🔲 TODO |
| C.3 | Rewrite W2/2.5 MCP Config Version Check | Notion PATCH | PP-C3 | ~1K | 🔲 TODO |
| D.1 | Band-extraction script | tools/debug/_extract_embedded_bands.py | PP-D1 | ~3K | 🔲 TODO |
| D.2 | Apply extracted bands | Notion PATCH bulk | PP-D2 | ~5K | 🔲 TODO |
| E.1 | Push to origin/main | git push | PP-E1 | ~1K | 🔲 TODO |

---

## Gap Register

**GAP-A1**: 4 valid Pass 1 scores (W2-P1/2.1 P1, F4/F4.2 P2, W3/P3.1 P3, W4/W4 P3) sat in dry-run JSON; never applied because user chose conservative path in prior turn.

**GAP-B1–B4**: 4 questionable Pass 1 scores need per-row investigation. The naive scorer matched broad symbols (`_constants.py`, `init.py`) and inflated fan-in. Each requires manual ADG verification of the actual target file before applying any band.

**GAP-C1–C3**: 3 Pass 2 PARTIAL rows have ambiguous evidence — some rule files exist but not referenced in constitutional, or generic keywords matched. Blocking Items needs rewrite stating exactly what's missing for promotion to Done.

**GAP-D1**: 68 unscorable rows mostly have `[Pn]` band already embedded in title text (e.g. `[P1] H10 H10.1 — CVE OSV client...`). Extracting the band from title preserves human-assigned priority that the dry-run scorer missed.

**GAP-E1**: 2 local commits (`dc25b6eb9d` W4+W5 L1 reasoning, `4b8cb87304` w1: phase2 disposition processor) sit on local main; not pushed. Nothing else gates the push.

---

## Execution Plan

### Wave A — Apply 4 valid Pass 1 scores

**Scope**: PATCH 4 Wave/Phase Convergence rows with computed P-Band + Impact Score from dry-run.

**Targets** (from `_pending_rescore.json`):
| Wave/Phase | Page ID | Proposed | Computed |
|---|---|---|---|
| W2-P1/2.1 | (in JSON) | P1 | impact 384.5, layer L0, fan_in 3, surface State |
| F4/F4.2 | (in JSON) | P2 | impact 156.1, layer L_TOOLS, fan_in 1, surface State |
| W3/P3.1 | (in JSON) | P3 | impact 130.0, layer L_UNKNOWN, fan_in 0, surface Execution |
| W4/W4 | (in JSON) | P3 | impact 120.0, layer L_APP, fan_in 0, surface State |

**Acceptance**: 4 PATCH 200 OK, P-Band field updated, Impact Score field updated, Blocking Items prepended with `RESCORED 2026-04-24:` evidence.

### Wave B — Investigate 4 questionable scores

**Scope**: For each of GAP-4, W5/5.1, Wave 3/3.2, W1-P0/1.2 — re-run ADG lookup with corrected target file extraction. Decide per row: (a) apply corrected score, (b) leave UNSCORED with note, or (c) descope.

**B.1 GAP-4** — re-extract real target. The row says "10 files import `_constants.py` directly". Need to identify which `_constants.py`. ADG query: `SELECT adg_name FROM nodes WHERE adg_name LIKE '%_constants.py%' AND entity_type='module' GROUP BY adg_name`. Pick the one matching the plan slug `streamline-constants`.

**B.2 W5/5.1** — title is "Post-W4 resnapshot to refresh ADR-024 Part B promotion counts". Action item, not file work. Mark UNSCORABLE with note.

**B.3 Wave 3/3.2** — "Clean __init__.py re-exports". The script matched a literal `init.py` token. Real targets are `__init__.py` files in the structure_blueprint_config retirement scope. Check parent plan `structure-blueprint-config-retirement-*.md`.

**B.4 W1-P0/1.2** — `register_embedding_client` callers. Tests exist (impact 0). Verify by running coverage on those 3 callers; if coverage truly ≥ 80%, mark Done; else keep UNSCORED.

**Acceptance**: 4 decisions documented, 4 PATCH (or skip) applied, Blocking Items records the reasoning.

### Wave C — Rewrite 3 PARTIAL Blocking Items

**Scope**: Patch each PARTIAL row's Blocking Items field with specific gap text.

**C.1 W2/2.8 HITL SVP Calibration** — rewrite to: "PARTIAL: rule files exist (`author-gate-svp-calibration.md`, `hitl-svp-calibration.md`, `judge-calibration-cadence.md`); GAP: not referenced in constitutional.md. Promote to Done by adding §-reference in constitutional or descope if intentional."

**C.2 W2/2.2 Policy Cleanup** — rewrite to: "PARTIAL: keyword 'cleanup' too generic for verification. Plan author should restate scope in concrete terms (which policy file, what cleanup) before promotion."

**C.3 W2/2.5 MCP Config Version Check** — rewrite to: "PARTIAL: gate `ops_scripts/ci/check_mcp_sync_integrity.py` exists (covers 'check' keyword) but row title doesn't name a specific version-check mechanism. Likely covered by sync_integrity gate; verify intent and either close as Done or restate."

**Acceptance**: 3 PATCH 200 OK, Blocking Items text updated, Status remains Todo (no auto-close on PARTIAL).

### Wave D — Band-extraction for 68 unscorable

**Scope**: Build regex extractor for `\[P([1-5])\]` pattern in row titles. For each match, PATCH P-Band field. No impact-score recomputation (preserves user-assigned priority intent).

**Script**: `tools/debug/_extract_embedded_bands.py`
- Load 68 unscorable rows
- Regex: `r'\[(P[1-5])\]'`
- For each match, PATCH `{"P-Band": {"select": {"name": match}}}` + Blocking Items prepend `BAND-EXTRACTED 2026-04-24:`
- Log to receipts JSONL

**Expected hits**: ~30–40 rows have `[Pn]` in title. Remaining ~28 stay UNSCORED.

**Acceptance**: PATCH N rows where N = regex hit count, receipts logged, summary print shows band distribution change.

### Wave E — Push to origin/main

**Scope**: `git push` to push 2 commits ahead.

**Commands**:
```bash
git status --short
git log --oneline origin/main..HEAD
git push origin main
```

**Acceptance**: `git status` clean re upstream, `git push` exit 0, no auth/conflict errors.

---

## Rules

- All Notion writes use direct REST API (not MCP) — batched into single Python scripts per wave, not one-PATCH-per-response.
- Receipts MUST append to `artifacts/notion/_writeback_receipts.jsonl` (existing log).
- No descoping of MISSING (real work) rows — Wave B may descope only if investigation proves the row is duplicate or obsolete.
- Wave D must NOT recompute impact scores — only extract embedded P-Band. Impact stays null for these rows.
- All scripts in `tools/debug/` (consistent with prior session).

---

## Success Criteria

- [ ] Wave A: 4 rows PATCHed with P-Band + Impact Score
- [ ] Wave B: 4 rows decided (apply / skip / descope) with documented reasoning
- [ ] Wave C: 3 rows PATCHed with rewritten Blocking Items
- [ ] Wave D: ≥25 of 68 unscorable rows recovered via band-extraction
- [ ] Wave E: branch pushed, `origin/main` matches `HEAD`
- [ ] All ops in `_writeback_receipts.jsonl` with `ok: true`
- [ ] Plan file registered in Notion Plans DB with row pointing here
- [ ] One Wave/Phase Convergence summary row per wave (5 rows total) created with Status=Done after wave completes

---

## Implementation Commands

```bash
# Wave A
python tools/debug/_apply_pass1_valid.py

# Wave B (interactive — script outputs decisions, manual review)
python tools/debug/_investigate_questionable.py

# Wave C
python tools/debug/_apply_partial_rewrites.py

# Wave D
python tools/debug/_extract_embedded_bands.py

# Wave E
git push origin main
```

---

## Rollback Strategy

1. **Notion PATCH rollback**: re-query Wave/Phase Convergence with the same page IDs, restore prior Status/P-Band/Blocking Items from the `_writeback_receipts.jsonl` history. The receipts log preserves the prior values inline; replay is mechanical.
2. **Wave B descope rollback**: if a wrongly-descoped row is identified, PATCH Status back to Todo with note "ROLLBACK 2026-04-24: descoped in error".
3. **Wave E rollback**: `git push origin main` cannot be cleanly rolled back without force-push (forbidden per repo policy). If commits are wrong, follow up with a revert commit.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Wave A PATCHes | 4/4 ok | `grep -c PATCH-pass1-valid _writeback_receipts.jsonl` |
| Wave B decisions | 4/4 documented | inspect `artifacts/notion/_wave_b_decisions.json` |
| Wave C PATCHes | 3/3 ok | `grep -c PATCH-partial-rewrite _writeback_receipts.jsonl` |
| Wave D band recovery | ≥25 PATCHes | `grep -c PATCH-band-extracted _writeback_receipts.jsonl` |
| Wave E push | exit 0 | `git rev-parse origin/main == HEAD` |

