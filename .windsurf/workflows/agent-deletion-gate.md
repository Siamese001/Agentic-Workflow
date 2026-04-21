---
description: Authorization gate before deleting any *Agent.py file - invoke when deleting agents
---

> **Cascade workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Agent Deletion Gate

Invoke with `/agent-deletion-gate`. Use BEFORE deleting any `*Agent.py` file.

---

## Policy

**Zero-tolerance for unauthorized agent deletion.** Deleting any `*Agent.py` file is a destructive operation requiring the same rigor as database schema changes.

## Required Authorization (ALL mandatory)

1. **AGENT-DELETION-AUTHORIZED:** marker in commit message with justification (min 50 chars)
2. **REPLACEMENT:** Specify replacement agent or 'none'/'unused'
3. **DEPRECATION-DATE:** Date agent was deprecated (YYYY-MM-DD) or 'N/A'
4. **REFERENCES-MIGRATED:** 'yes' if all references migrated, 'no' if none existed
5. **Minimum deprecation period:** 90 days from DEPRECATION-DATE to deletion
6. **Zero references:** Reference scan must show zero active references (excluding tests and deletion registry)

**Enforcement:** Pre-commit hook `guard-agent-deletion` blocks commits deleting `*Agent.py` files without proper authorization.

## When Deletion IS Acceptable

- Duplicate/redundant agent with zero references
- Test fixture agent in test support directory
- Experimental agent never used in production
- After full migration with zero references confirmed

## When Deletion is NEVER Acceptable

- Active agent with references
- Deprecated agent still in deprecation period (<90 days)
- Agent with incomplete migration
- "Just to make tests pass"
- Without replacement specified

## Example Authorization

```
refactor: Remove deprecated LocationAgent shim

AGENT-DELETION-AUTHORIZED: Shim fully migrated after 90-day deprecation period.
All 80 references redirected to LocationHealerAgent and LocationValidatorAgent.
REPLACEMENT: LocationHealerAgent + LocationValidatorAgent
DEPRECATION-DATE: 2026-02-07
REFERENCES-MIGRATED: yes
```

## Step 1: Verify Zero References

```
python tools/adg/adg_redis_query.py search-nodes --query <AgentName>
```

Confirm zero active references outside tests and deletion registry.

## Step 2: Author-Gate Confirmation

Present user with:
- Agent name and file path
- Reference count (should be 0)
- Deprecation date and age
- Replacement agent(s)

Get explicit "proceed" before deletion.

## Step 3: Commit with Authorization

Include ALL required markers in commit message per format above.

## References

- Constitutional Rule: `.windsurf/rules/constitutional.md` §1.6
- Pre-commit hook: `guard-agent-deletion`
