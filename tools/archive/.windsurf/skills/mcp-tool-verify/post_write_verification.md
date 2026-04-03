# Post-Write Verification Protocol

Execute IMMEDIATELY after any file-write tool call.
Do NOT declare "file written successfully" before completing this protocol.

---

## Step 1 — Identify the Write Tool Used

| Tool Used | Verification Method |
|-----------|-------------------|
| `mcp5_write_file` | `mcp5_get_file_info` + size check |
| `write_to_file` | `mcp5_read_text_file` (first 5 lines) |
| `mcp5_create_directory` | `mcp5_list_directory` to confirm dir exists |
| `edit` / `multi_edit` | `read_file` on the edited lines |

---

## Step 2 — Execute Verification

### For file writes (`mcp5_write_file` / `write_to_file`):

```
1. Call mcp5_get_file_info(<written_path>)
   → Check: file exists (no error returned)
   → Check: size > 0 bytes

   IF check fails → go to Fallback Chain (Step 4)
   IF check passes → go to Step 3
```

### For directory creation (`mcp5_create_directory`):

```
1. Call mcp5_list_directory(<parent_directory>)
   → Confirm new directory appears in listing

   IF not present → retry once, then STOP and report to user
```

---

## Step 3 — Record Verification in Evidence

Add to phase evidence:

```
FILE WRITE VERIFIED:
  Path: <written_path>
  Tool used: <tool_name>
  Verification method: mcp5_get_file_info
  File exists: YES
  File size: <N> bytes
  Status: CONFIRMED
```

---

## Step 4 — Fallback Chain

If primary write tool fails verification:

```
Attempt 1 (Primary):   mcp5_write_file   → verify → FAILED
Attempt 2 (Fallback):  write_to_file     → verify → check again
Attempt 3 (Final):     If write_to_file also fails → STOP
                        Report exact error to user
                        Do NOT proceed with phase
```

---

## Step 5 — Silent Failure Indicators

Watch for these signs that a write silently failed:

- Tool returned success but `mcp5_get_file_info` returns error
- File size is 0 bytes after write
- `mcp5_read_text_file` returns empty content on a non-empty write
- Subsequent `read_file` shows old content unchanged

Any of the above = **silent failure** → execute Fallback Chain.

---

## FORBIDDEN Behaviors

- ❌ Stating "file has been written" without running verification
- ❌ Proceeding to next step before verifying the write
- ❌ Retrying the SAME failed tool more than once
- ❌ Ignoring a 0-byte file as "probably fine"
