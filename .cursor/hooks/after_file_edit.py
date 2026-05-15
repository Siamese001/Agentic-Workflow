from lib.cursor_hook_common import read_payload, text_from_payload, write_receipt, warn, allow

payload = read_payload()
text = text_from_payload(payload)
legacy = [t for t in ('.cursor', 'post_cursor_agent', 'pre_cursor_agent', '~/.cursor/cursor', 'mcp.json') if t in text]
if legacy:
    reason = 'Edited payload/path contains legacy token; run .cursor/scripts/check_cursor_native_config.py --strict: ' + ', '.join(legacy)
    write_receipt('afterFileEdit', payload, 'warn', reason)
    raise SystemExit(warn(reason))
write_receipt('afterFileEdit', payload, 'allow', 'edit audit accepted')
raise SystemExit(allow('edit audit accepted'))
