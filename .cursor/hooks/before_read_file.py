from lib.cursor_hook_common import read_payload, text_from_payload, write_receipt, warn, allow

payload = read_payload()
text = text_from_payload(payload)
if '.cursor/cursor_compat' in text or '.cursor/scripts/_legacy_cursor' in text:
    reason = 'Reading legacy compatibility material; treat as archive/reference only'
    write_receipt('beforeReadFile', payload, 'warn', reason)
    raise SystemExit(warn(reason))
write_receipt('beforeReadFile', payload, 'allow', 'read path accepted')
raise SystemExit(allow('read path accepted'))
