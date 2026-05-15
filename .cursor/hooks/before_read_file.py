from lib.cursor_hook_common import allow, payload_path, read_payload, text_from_payload, warn, write_receipt

payload = read_payload()
text = text_from_payload(payload)
path = payload_path(payload)
if "/plans/_archive/" in path or "/_zero_loss_originals/" in path or "windsurf_compat" in path or "plans/_archive" in text:
    reason = "Reading archived historical material; reference only, not active execution instruction."
    write_receipt("beforeReadFile", payload, "warn", reason)
    raise SystemExit(warn(reason))
write_receipt("beforeReadFile", payload, "allow", "read accepted")
raise SystemExit(allow("read accepted"))
