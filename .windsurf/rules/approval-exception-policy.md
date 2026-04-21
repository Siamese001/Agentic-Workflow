---
trigger: model_decision
description: Use this rule when evaluating guardian exemptions, approval classes, or exception evidence requirements.
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Approval & Exception Policy

**Status**: ACTIVE  
**Phase**: Wave 2 Phase 2.10  
**Authority**: `.windsurf/rules/constitutional.md` Section 8 Guardian Exemption Discipline  
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
| New `# guardian: allow-*` comment | Section 8 | `/antipattern-hitl-gate` |
| Agent (`*Agent.py`) deletion | Section 1.6 / Section 3 | `/agent-deletion-gate` |
| New external PyPI/npm dependency | Section HITL-1.5 | `/hitl-decision-gate` |
| Architectural approach selection (>=2 valid paths) | Section 6 / Section HITL-1.1 | `/hitl-decision-gate` |
| Production file deletion | Section HITL-1.6 | `/hitl-decision-gate` |
| Cross-layer refactor scope | Section HITL-1.2 | `/hitl-decision-gate` |
| Governance/policy config change | Section HITL-1.7 | `/hitl-decision-gate` |

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
4. After approval: add guardian comment with specific justification
   Format: # guardian: allow-broad-exception -- <specific reason>
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
- `artifacts/windsurf/mcp_lint_audit.jsonl` - MCP config changes
- Git commit history - Author-Gate-APPROVED prefix marks all approved exceptions
- `ops_scripts/ci/guardian_exemption_gate.py` - ratchet state tracks exemption counts

---

## References

- Constitutional Section 6 (Author-Gate), Section 8 (Guardian), Section 3 (Agent deletion)
- `.windsurf/rules/hitl-enforcement.md` - Author-Gate protocol
- `.windsurf/rules/anti-pattern-hitl-gate.md` - Anti-pattern approval flow
- `.windsurf/rules/hitl-svp-calibration.md` - When Author-Gate is required vs forbidden
