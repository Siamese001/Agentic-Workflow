# Structured Reasoning - Step Failure Template

Use this when an execution or verification step fails.

```
## STEP_FAILURE
Failed step: N - <step title>
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
  OPTION A - Roll back and retry:
    <restore/revert commands>
    Retry from step N with: <corrected approach>

  OPTION B - Route around:
    Skip step N; proceed to step N+1 with caveat: <what is now missing>
    Document gap: [GAP - <description>]

  OPTION C - Abstain:
    Cannot safely proceed. Recommend: <specific user action>

Selected: OPTION <A|B|C>
Reason: <why this option>

MCP failure? YES | NO
  If YES: which MCP: <name>
  Recovery: /mcp-failure-rca executed | route-around documented | BLOCKED
```

---

## MCP Hang Recovery

1. STOP; do not retry the hung call in a loop.
2. If ADG (`adg_sqlite`) is required, run `/mcp-failure-rca`.
3. If Task Manager is unavailable, skip durable tracking unless the user requested it.
4. If Filesystem MCP is unavailable, use the native file tools.
5. If Pytest MCP is unavailable, use the repo pytest command.
6. If GitKraken is unavailable, use the git CLI.
7. Note `[MCP UNAVAILABLE - <name> - proceeding with fallback]` in the response.
8. Never use grep as an ADG substitute for structural dependency evidence.
