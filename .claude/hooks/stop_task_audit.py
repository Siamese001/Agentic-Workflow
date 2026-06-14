from lib.claude_hook_common import PROOF_WORDS, STATUS_WORDS, allow, block, read_payload, resolve_response_text, warn, write_receipt

payload = read_payload()
# Real Claude `Stop` payloads carry no inline response — resolve via the shared SSOT
# (inline -> cursor text keys -> transcript recovery) so the STATUS-floor / PASS-without-proof
# blocks actually see the final assistant turn instead of silently no-opping.
text = resolve_response_text(payload)
if not text.strip():
    write_receipt("stop", payload, "allow", "empty stop payload accepted")
    raise SystemExit(allow("empty stop payload accepted"))

upper = text.upper()
repo_work_cues = ("FILES_CHANGED", "COMMANDS_RUN", "TESTS_GATES", "IMPLEMENTED", "PATCHED", "CREATED", "MODIFIED", "TESTS PASS", "GATE")
status_present = any(word in upper for word in STATUS_WORDS)
repo_work_present = any(cue in upper for cue in repo_work_cues)

if repo_work_present and not status_present:
    reason = "Repo-work final response missing STATUS: PASS | PARTIAL | FAIL | BLOCKED."
    write_receipt("stop", payload, "block", reason)
    raise SystemExit(block(reason))

if "STATUS: PASS" in upper:
    missing = [word for word in PROOF_WORDS if word not in upper]
    if missing:
        reason = "PASS response missing proof sections: " + ", ".join(missing)
        write_receipt("stop", payload, "block", reason)
        raise SystemExit(block(reason))

if "SHOULD PASS" in upper or "LIKELY PASS" in upper:
    reason = "Speculative pass language detected; use PASS, PARTIAL, FAIL, or BLOCKED with evidence."
    write_receipt("stop", payload, "block", reason)
    raise SystemExit(block(reason))

write_receipt("stop", payload, "allow", "stop audit accepted")
raise SystemExit(allow("stop audit accepted"))
