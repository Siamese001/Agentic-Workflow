# Pre-Commit High-Signal Issue Summary Enhancement

Enhance the `.pre-commit-config.yaml` to provide a terminal-based summary table at the end of each run, displaying all governance and security hook results categorized by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO) with explanations, even when pre-commit passes.

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1 | Create `ops_scripts/ci/pre_commit_summary_reporter.py` — JSON-based issue collector and table formatter | 8,000 | Hooks output machine-parseable JSON; terminal width ≥80 chars | 🔵 PENDING | Reporter module exists with severity classification |
| Wave 2 | P2 | Modify governance hooks to emit structured JSON output for the reporter | 6,000 | Hooks can write to temp files; no performance regression | 🔵 PENDING | adg_burndown_gate, guardian_exemption_gate, hollow_file_gate, adg_python_ban_gate emit structured output |
| Wave 3 | P3 | Add `.pre-commit-config.yaml` wrapper hooks and finalize integration | 4,000 | Pre-commit environment has temp file access; Windows compatible | 🔵 PENDING | Config updated with summary hooks; end-of-run table displays |
| Wave 4 | P4 | Validation and edge case handling | 3,000 | Test environment has staged changes to trigger hooks | 🔵 PENDING | Manual test shows formatted table; graceful fallback on parse errors |

**Total: ~21,000 tokens across 4 waves, all BLUE (pending)**

---

## Gap Register

**GAP-1: Machine-Readable Hook Output**
Current governance hooks print plain text to stdout/stderr. The summary reporter needs structured data (severity, message, file, explanation). Need to either parse text output or modify hooks to emit JSON.
- Impact: Core requirement for the summary table

**GAP-2: Cross-Hook State Sharing**
Pre-commit hooks run in isolation. Need a mechanism to aggregate issues from multiple hooks into a single summary table at the end.
- Impact: Requires temp file or shared state mechanism

**GAP-3: Severity Normalization**
Different hooks use different severity terminology ("BLOCK" vs "FAIL" vs "CRITICAL"). Need mapping to canonical severity levels.
- Impact: Table consistency

---

## Execution Plan

### Phase 1 — Create Summary Reporter Infrastructure
**Scope**: Build `ops_scripts/ci/pre_commit_summary_reporter.py` with:
- JSON issue collector (reads from temp files written by hooks)
- Severity classifier (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Table formatter with colored output and explanations
- Entry points: `--collect` (from hooks), `--report` (final display)

**Files to Create**:
- `ops_scripts/ci/pre_commit_summary_reporter.py` (~300 lines)
- `ops_scripts/ci/pre_commit_issue_schema.py` — dataclasses for issue structure

**Commands**:
```bash
# Verify script runs independently
python ops_scripts/ci/pre_commit_summary_reporter.py --test-table
```

**Acceptance**:
- [ ] Reporter can parse sample JSON and print formatted table
- [ ] Table has columns: Severity, Hook, File, Issue, Explanation
- [ ] Colors render correctly in terminal

### Phase 2 — Instrument Governance Hooks
**Scope**: Modify 5 governance/security hooks to emit structured JSON:
1. `adg_burndown_gate.py` — Anti-pattern violations
2. `guardian_exemption_gate.py` — Exemption quality issues
3. `hollow_file_gate.py` — Hollow file detections
4. `adg_python_ban_gate.py` — Banned pattern usage
5. `adg_yaml_grep_ban_gate.py` — YAML grep violations

**Changes per hook**:
- Add `--json-output <path>` argument
- Write `PreCommitIssue` objects as JSON lines
- Preserve existing console output for compatibility

**Commands**:
```bash
# Test each hook with JSON output
python ops_scripts/ci/adg_burndown_gate.py --json-output /tmp/burndown.json
python ops_scripts/ci/hollow_file_gate.py --changed-only --json-output /tmp/hollow.json
```

**Acceptance**:
- [ ] Each hook writes valid JSON when `--json-output` provided
- [ ] Console output unchanged (backwards compatible)
- [ ] Issues include severity, file path, message, explanation

### Phase 3 — Pre-Commit Config Integration
**Scope**: Add wrapper hooks to `.pre-commit-config.yaml`:

1. **Pre-run initializer** (T-1): Clears temp state, prepares for collection
2. **Post-run reporter** (T+1): Aggregates all JSON files, prints summary table

**Config Changes**:
- Add `pre-commit-summary-init` hook (runs first, always_run: true)
- Modify governance hooks to include `--json-output` with temp path
- Add `pre-commit-summary-report` hook (runs last, always_run: true)

**Commands**:
```bash
# Test pre-commit run
pre-commit run --all-files
```

**Acceptance**:
- [ ] Table displays at end of pre-commit run
- [ ] Table shows all severity levels
- [ ] Table includes passed hooks as "✓ Clean"
- [ ] No duplicate entries

### Phase 4 — Validation and Edge Cases
**Scope**: Handle edge cases and ensure robustness:
- Empty results (no issues found)
- Malformed JSON in temp files
- Very long file paths (truncation)
- Narrow terminals (<80 chars)
- Windows temp file path handling
- Hook failure vs. warning distinction

**Commands**:
```bash
# Test with various scenarios
pre-commit run --all-files  # Clean repo
pre-commit run adg-burndown-gate --all-files  # With issues
```

**Acceptance**:
- [ ] Table displays correctly with no issues (all green)
- [ ] Table displays correctly with 50+ issues
- [ ] Graceful handling when temp files missing
- [ ] Colors disabled when not TTY

---

## Rules

1. **Severity Mapping** — All hooks normalize to: CRITICAL (blocks commit), HIGH (should fix), MEDIUM (consider fixing), LOW (informational), INFO (passed/clean)
2. **Backwards Compatibility** — Existing hook console output must be preserved; JSON output is additive
3. **Performance** — JSON writing adds <100ms per hook; table rendering <500ms total
4. **Windows Compatibility** — All temp file paths use `Path(tempfile.gettempdir())` / `pre-commit-issues-*`
5. **Fail-Fast** — If JSON parsing fails, fall back to "Issues detected (parse error)" rather than crash

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| Summary table displays | 100% of pre-commit runs | Visual inspection |
| Issues categorized correctly | ≥95% accuracy | Manual audit of 20 issues |
| Performance overhead | <1s total | `time pre-commit run` |
| Backwards compatible | 100% | Existing scripts still work |
| Windows compatible | 100% | Test on Windows terminal |

---

## Implementation Commands

```bash
# Wave 1: Create reporter
python ops_scripts/ci/pre_commit_summary_reporter.py --test-table

# Wave 2: Test individual hooks
python ops_scripts/ci/adg_burndown_gate.py --json-output /tmp/test.json
python ops_scripts/ci/hollow_file_gate.py --changed-only --json-output /tmp/test.json

# Wave 3: Test full pre-commit
pre-commit run --all-files

# Wave 4: Validation
pre-commit run --all-files 2>&1 | grep -A 20 "PRE-COMMIT SUMMARY"
```

---

## Rollback Strategy

If issues arise:
1. Disable summary hooks by commenting out in `.pre-commit-config.yaml`
2. Revert to original hook versions without `--json-output` flag
3. Delete temp files: `rm /tmp/pre-commit-issues-*`
4. File backup location: `.backup/pre-commit-config.yaml.bak`

---

## Acceptance Criteria

- [ ] End-of-run summary table displays after every pre-commit invocation
- [ ] Table includes all governance hooks (T12-T18) with pass/fail status
- [ ] Issues categorized by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- [ ] Each issue has an explanation in the table
- [ ] Colors render correctly (red=CRITICAL, yellow=HIGH, blue=MEDIUM, white=LOW, green=pass)
- [ ] Performance overhead <1 second
- [ ] Backwards compatible (hooks work without JSON output flag)
- [ ] Windows compatible path handling
