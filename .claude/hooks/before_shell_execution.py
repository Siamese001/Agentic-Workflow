from lib.claude_hook_common import allow, block, contains_legacy_execution_token, read_payload, text_from_payload, write_receipt

payload = read_payload()
text = text_from_payload(payload)
legacy = contains_legacy_execution_token(text)
if legacy:
    reason = "Shell command targets legacy execution surface: " + ", ".join(legacy)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

risky = []
for token in ("rm -rf .cursor", "rmdir /s .cursor", "del /s .cursor", "Remove-Item .cursor"):
    if token in text:
        risky.append(token)
if risky:
    reason = "Shell command risks deleting active Cursor controls: " + ", ".join(risky)
    write_receipt("beforeShellExecution", payload, "block", reason)
    raise SystemExit(block(reason))

write_receipt("beforeShellExecution", payload, "allow", "command accepted")
raise SystemExit(allow("command accepted"))
