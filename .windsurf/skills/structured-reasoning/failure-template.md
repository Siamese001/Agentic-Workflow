# Structured Reasoning — Step Failure Template

Emit this block when a step fails during Phase E (execution).

```
## SR_STEP_FAILURE
Failed step: N — <step title>
Timestamp: <ISO>
Error: <exact error message or behavior>

Root cause assessment:
  - Confirmed: <what is known>
  - Likely: <what is suspected>
  - Unknown: <what cannot be determined without more info>

Impact:
  - Files already changed: <list or NONE>
  - Partial state: <describe inconsistency, if any>

Recovery action:
  OPTION A — Rollback and retry:
    git reset --hard <baseline>
    <restore commands>
    Retry from step N with: <corrected approach>

  OPTION B — Route around:
    Skip step N; proceed to step N+1 with caveat: <what is now missing>
    Document gap: [GAP — <description>]

  OPTION C — Abstain:
    Cannot safely proceed. Recommend: <specific user action>

Selected: OPTION <A|B|C>
Reason: <why this option>

MCP failure? YES | NO
  If YES: which MCP: <name>
  Recovery: /mcp-failure-rca executed | route-around documented | BLOCKED
```

---

## MCP Hang Recovery (quick reference)

1. STOP — do not retry
2. If ADG (`mcp1`): run `/mcp-failure-rca` STEP 1
3. If Task Manager (`mcp13`): use `todo_list` fallback
4. If Filesystem (`mcp7`): use `read_file` native tool
5. If Pytest (`mcp11`): use `run_command` with pytest CLI
6. If GitKraken (`mcp0`): use `run_command` with git CLI
7. Note `[MCP UNAVAILABLE — <name> — proceeding with fallback]` in response
8. Never use grep as ADG substitute
