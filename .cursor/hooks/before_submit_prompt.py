from lib.cursor_hook_common import read_payload, text_from_payload, write_receipt, warn, allow

payload = read_payload()
text = text_from_payload(payload)
legacy = [t for t in ('.cursor', 'post_cursor_agent', 'pre_cursor_agent', 'mcp.json') if t in text]
if legacy:
    reason = 'Prompt references legacy compatibility surface: ' + ', '.join(legacy)
    write_receipt('beforeSubmitPrompt', payload, 'warn', reason)
    raise SystemExit(warn(reason))
write_receipt('beforeSubmitPrompt', payload, 'allow', 'no legacy Cursor-surface issue detected')
raise SystemExit(allow('no legacy Cursor-surface issue detected'))
