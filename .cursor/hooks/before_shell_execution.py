from lib.cursor_hook_common import read_payload, text_from_payload, write_receipt, block, allow

payload = read_payload()
text = text_from_payload(payload)
blocked = [t for t in ('.cursor/scripts', 'post_cursor_agent', 'pre_cursor_agent', '~/.cursor/cursor', 'mcp.json') if t in text]
if blocked:
    reason = 'Shell command targets legacy automation surface: ' + ', '.join(blocked)
    write_receipt('beforeShellExecution', payload, 'block', reason)
    raise SystemExit(block(reason))
write_receipt('beforeShellExecution', payload, 'allow', 'command does not target legacy automation surface')
raise SystemExit(allow('command does not target legacy automation surface'))
