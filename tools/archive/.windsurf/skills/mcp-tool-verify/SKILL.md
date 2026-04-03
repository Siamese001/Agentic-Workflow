---
name: mcp-tool-verify
description: Enforces post-call verification for all MCP filesystem tool calls and prevents use of invented/non-existent tool parameters. Use after any mcp5_write_file, mcp5_create_directory, or write_to_file call, and before using any MCP tool parameter that has not been confirmed in documentation. Prevents silent write failures and hallucinated API usage.
---

# MCP Tool Verify Skill

Enforces mandatory post-call verification for MCP tool calls and prohibits invented parameters.

## Files

- **`post_write_verification.md`** — Mandatory verification steps after any file write tool call. Defines the exact verification sequence (read-back or stat check) and the fallback chain when primary write tool fails.

- **`tool_parameter_discipline.md`** — Checklist for validating tool parameters before use. Prohibits asserting a parameter exists without prior confirmation. Defines how to confirm parameters are real vs. hallucinated.

## When to use

- Immediately after ANY `mcp5_write_file` call
- Immediately after ANY `write_to_file` call
- Immediately after ANY `mcp5_create_directory` call
- Before using any MCP tool parameter not previously confirmed in this session
- When a tool call returns success but downstream reads fail

## Verification Protocol (MANDATORY)

After every write:
1. Call `mcp5_get_file_info` OR `mcp5_read_text_file` on the written path
2. Confirm file exists and size > 0
3. If verification fails → use fallback write tool (`write_to_file`)
4. Re-verify after fallback
5. Document verification result in evidence

**NEVER declare "file written" without completing verification step.**

## Fallback Chain

```
mcp5_write_file → fails or silent → write_to_file → verify → done
write_to_file   → fails          → STOP, report to user
```

## Constitutional Requirements Enforced

- **§2.1:** Evidence MUST reflect actual state (no unverified success claims)
- **§1.8:** Side-effect tests MUST assert file writes succeeded
