
<!-- Converted from `.claude/rules/approval-exception-policy.md`. Original Cursor trigger: `model_decision`. -->

> See `.cursor/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# Approval & Exception Policy

**Status**: ACTIVE  
**Phase**: Wave 2 Phase 2.10  
**Authority**: `.claude/rules/constitutional.md` Section 8 Guardian Exemption Discipline  
**Enforcement**: `ops_scripts/ci/guardian_exemption_gate.py`

---

## Purpose

Define who approves what, under what conditions, and what evidence is required.
Prevents both gateless anti-patterns and approval theater (approvals without substance).

---

## Approval Categories

### Category A - Author-Gate Approval (User Required)

These require explicit user selection via `ask_user_question` before proceeding:

| Action | Constitutional Basis | Workflow |
|--------|----------------------|----------|
| New `# guardian: allow-*` comment | Section 8 | `/antipattern-author-gate` |
| Agent (`*Agent.py`) deletion | Section 1.6 / Section 3 | `/agent-deletion-gate` |
| New external PyPI/npm dependency | Section AG-1.5 | `/author-gate-decision-gate` |
| Architectural approach selection (>=2 valid paths) | Section 6 / Section AG-1.1 | `/author-gate-decision-gate` |
| Production file deletion | Section AG-1.6 | `/author-gate-decision-gate` |
| Cross-layer refactor scope | Section AG-1.2 | `/author-gate-decision-gate` |
| Governance/policy config change | Section AG-1.7 | `/author-gate-decision-gate` |

**Format**: Must use `ask_user_question` tool - plain text approval is NOT accepted.

### Category B - CI Gate Approval (Automated Check)

These are enforced by CI gates without human interaction unless the gate fails:

| Action | Gate | Exit on Fail |
|--------|------|--------------|
| Commit with new anti-patterns | `guardian_exemption_gate.py` | Block commit |
| Commit with PowerShell usage | `pre_run_gate.py` + pre-commit T18 | Block commit |
| Commit with bare `except:` | `pre_write_gate.py` | Block commit |
| Commit with archives/ imports | `check_no_archives_imports.py` | Block commit |
| Commit with hollow file | `zero_loss_refactor_verifier.py` | Block commit |
| Commit with missing test coverage | `run_contract_gates.py` T1 | Block commit |

### Category C - No Approval Required (Self-Authorizing)

These require no explicit approval:

| Action | Condition |
|--------|-----------|
| T1 trivial edits (<=1 file, <=20 lines) | Verified with scoped tests |
| Adding/updating documentation | Non-production `.md` files |
| Updating test files | No weakening of assertions |
| Committing after green scoped tests | All affected tests pass |
| Pushing after successful commit | No additional gates |

---

## Exception Protocol

### Requesting a Guardian Exemption

When `pre_write_gate.py` blocks a `except Exception` or bare `except:`:

```
1. STOP - do not bypass with --no-verify
2. Present Author-Gate prompt with ask_user_question:
   - What: exact anti-pattern and file
   - Why: specific technical justification (not "needed" or "temporary")
   - Alternatives: at least 2 alternatives considered and why rejected
3. Wait for explicit user approval
4. After approval: add guardian comment with exemption token. Two canonical forms accepted (W17.b-tail, 2026-04-24):
   - **Long form (preferred for NEW exemptions)**: `# guardian: allow-broad-exception -- <specific reason>`
   - **Short form (accepted, grandfathered)**: `# guardian: allow-broad-exception`
   Both forms satisfy the scanner (`post_write_audit.py` regex is `#\s*guardian:\s*allow-([a-z0-9-]+)\b(.*)$`; `pre_write_gate.py` regex is `#\s*guardian:\s*allow-`). Long form is preferred because the justification text survives git-blame churn. Short form exists because ~1757 pre-existing sites use it and retroactive per-site justification invention would be audit noise without information gain.
   Comments that begin with `# guardian:` but do NOT start with `allow-` are **review-notes**, not exemption directives, and MUST use the `# review:` prefix instead (mechanically renamed in W17.b-tail 2026-04-24).
5. Commit with Author-Gate-APPROVED prefix in message
```

### Ratchet Ceiling Management

The `guardian_exemption_gate.py` maintains a ceiling of allowed exemptions:

- **Ceiling only decreases** - new exemptions require explicit Author-Gate approval
- **Initialization**: `ADG_EXEMPTION_INIT=1 python ops_scripts/ci/guardian_exemption_gate.py`
- **Check current ceiling**: `python ops_scripts/ci/guardian_exemption_gate.py --check`
- **Commit block**: Any commit adding exemptions above the ceiling is BLOCKED

### Emergency Bypass Protocol

`git commit --no-verify` is ONLY permitted:

| Scenario | Permitted? | Evidence Required |
|----------|------------|-------------------|
| Wave governance commits (policy docs, rules) | YES | Commit message explains why |
| Hook infrastructure fixes | YES | Commit message explains why |
| Any production code anti-pattern bypass | NO | Never permitted |
| Skipping failing tests | NO | Never permitted |

---

## Approval Evidence Requirements

Every Author-Gate-approved action MUST include in the commit message:

```
Author-Gate-APPROVED: <brief description>
- Approved: <what was approved>
- Justification: <specific reason>
- Alternatives rejected: <alt1> (reason), <alt2> (reason)
```

---

## Audit Trail

All approvals are logged in:
- `artifacts/cursor/mcp_lint_audit.jsonl` - MCP config changes
- Git commit history - Author-Gate-APPROVED prefix marks all approved exceptions
- `ops_scripts/ci/guardian_exemption_gate.py` - ratchet state tracks exemption counts

---

## References

- Constitutional Section 6 (Author-Gate), Section 8 (Guardian), Section 3 (Agent deletion)
- `.claude/rules/author-gate-enforcement.md` - Author-Gate protocol
- `.claude/rules/anti-pattern-author-gate.md` - Anti-pattern approval flow
- `.claude/rules/author-gate-svp-calibration.md` - When Author-Gate is required vs forbidden
