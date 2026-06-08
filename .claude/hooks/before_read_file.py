from pathlib import Path

from lib.claude_hook_common import allow, payload_path, read_payload, text_from_payload, warn, write_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]


def _repo_relative(path: str) -> str:
    norm = path.replace("\\", "/")
    root = str(REPO_ROOT).replace("\\", "/").rstrip("/")
    if norm.startswith(root + "/"):
        norm = norm[len(root) + 1 :]
    if norm.startswith("./"):
        norm = norm[2:]
    return norm


def _is_active_plan_path(path: str) -> bool:
    rel = _repo_relative(path)
    if rel.startswith("plans/_archive/") or rel.startswith(".claude/plans/_archive/") or "/plans/_archive/" in rel:
        return False
    return rel.startswith("plans/") or rel.startswith(".claude/plans/")

payload = read_payload()
text = text_from_payload(payload)
path = payload_path(payload)
# Active plans (root plans/* plus legacy .claude/plans/*, excluding _archive/) are non-sensitive:
# they are live execution material and must never warn on read.
active_plan = _is_active_plan_path(path)
if not active_plan and (
    "/plans/_archive/" in path
    or "/_zero_loss_originals/" in path
    or "windsurf_compat" in path
    or "plans/_archive" in text
):
    reason = "Reading archived historical material; reference only, not active execution instruction."
    write_receipt("beforeReadFile", payload, "warn", reason)
    raise SystemExit(warn(reason))
write_receipt("beforeReadFile", payload, "allow", "read accepted")
raise SystemExit(allow("read accepted"))
