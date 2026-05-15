from lib.cursor_hook_common import read_payload, write_receipt, allow

payload = read_payload()
write_receipt('stop', payload, 'allow', 'Cursor task stop audit recorded')
raise SystemExit(allow('Cursor task stop audit recorded'))
