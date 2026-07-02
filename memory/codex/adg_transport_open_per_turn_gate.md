# ProceduralPattern:ADGTransportOpenPerTurnGate

```json
{
  "entities": [{
    "name": "ProceduralPattern:ADGTransportOpenPerTurnGate",
    "entityType": "ProceduralPattern",
    "observations": [
      "INVARIANT: Ordinary T2/T3 prompts must require ADG SQLite SSOT health and active-session ADG MCP transport proof before graph-dependent work proceeds.",
      "scope: .codex/governance/scripts/pre_user_prompt_adg_ssot_gate.py, tools/adg/mcp/supervisor.py, .codex/hooks/after_mcp_execution.py, scripts/governance/codex_readiness.py",
      "enforcement: UserPromptSubmit blocks unless tools.adg.mcp.supervisor.transport_status(session_id).status is open; PostToolUse writes artifacts/mcp_heartbeat/adg_sqlite_callable_proof.json only after adg_health/adg_runtime_info/adg_process_identity succeeds.",
      "violation_examples: treating a live ADG Python process, a fresh heartbeat, or readable artifacts/adg/adg_indexed_*.sqlite as proof that Codex can call mcp__adg_sqlite tools.",
      "canonical_pattern: let explicit ADG transport recovery/RCA prompts proceed, but keep ordinary T2/T3 prompts blocked until env or file proof matches a live authoritative heartbeat PID.",
      "doctrine_ref: .codex/rules/constitutional.md §13; tools/adg/mcp/OPERATIONS.md",
      "discovered: 2026-07-01, validated: 2026-07-01"
    ]
  }]
}
```
