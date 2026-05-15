from lib.cursor_hook_common import read_payload, text_from_payload, write_receipt, block, allow

payload = read_payload()
text = text_from_payload(payload)
blocked = [t for t in ('io.cursor/mcp-playwright', '~/.cursor/cursor', 'mcp.json') if t in text]
if blocked:
    reason = 'MCP execution references legacy MCP identity/config: ' + ', '.join(blocked)
    write_receipt('beforeMCPExecution', payload, 'block', reason)
    raise SystemExit(block(reason))
write_receipt('beforeMCPExecution', payload, 'allow', 'MCP request passed Cursor-native preflight')
raise SystemExit(allow('MCP request passed Cursor-native preflight'))
