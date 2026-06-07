# DEPRECATED — MCP serialization rule retired (W5 claude-native-supersession-9d3f7a, ADR-097)

> ⛔ The "one remote-MCP tool call per model tool block" batching constraint was a legacy-IDE
> transport limitation. Claude Code issues parallel MCP tool calls natively and safely, so the
> serialization rule is retired.

## What remains

`pre_mcp_gate.py` still enforces the substantive MCP checks (Notion token presence, GitKraken
upstream) — only the *batching/serialization sentinel* is moot. There is no per-block MCP-call limit.
