"""post_cascade_scope_drift_detector.py — files-touched vs. plan-scope audit.

Scans the Cascade response for file-write invocations (`write_to_file`,
`edit`, `multi_edit`, `edit_notebook`, `edit_file`) and cross-checks the
target paths against the active plan's `## Phase-Level Summary · Scope
(files)` column. Any write to a file NOT in scope is logged as drift.

Fail-open: any internal error → exit 0 + stderr diagnostic.

Sibling to `pre_write_plan_scope_gate.py` (the pre-hook). This post-hook
captures drift that slipped past the advisory pre-hook (e.g., strict mode
disabled + warning ignored).

Violations log: `artifacts/windsurf/scope_drift_violations.jsonl`

Bypass: `SCOPE_DRIFT_BYPASS=1` (logs row with bypass=true).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "scope_drift_violations.jsonl"
PLAN_FRESHNESS_SEC = 24 * 3600

# Capture the `TargetFile` / `file_path` parameter of write-ish tools.
# Matches parameter blocks like:
#   <parameter name="TargetFile">c:\path\to\file.py</parameter>
#   <parameter name="file_path">/path/to/file.py</parameter>
_WRITE_TOOL_RE = re.compile(
    r'<invoke\s+name="(write_to_file|edit|multi_edit|edit_notebook|edit_file)"[^>]*>'
    r"(?P<body>.*?)</invoke>",
    re.IGNORECASE | re.DOTALL,
)
_PATH_PARAM_RE = re.compile(
    r'<parameter\s+name="(?:TargetFile|file_path|absolute_path|path)">\s*(?P<path>[^<]+)</parameter>',
    re.IGNORECASE,
)
_PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]+")


def _latest_active_plan() -> Path | None:
    if not PLANS_DIR.is_dir():
        return None
    now = time.time()
    candidates = []
    for p in PLANS_DIR.glob("*.md"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if (now - mtime) <= PLAN_FRESHNESS_SEC:
            candidates.append((mtime, p))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _extract_scope_tokens(plan_text: str) -> set[str]:
    tokens: set[str] = set()
    idx = plan_text.find("## Phase-Level Summary")
    if idx < 0:
        return tokens
    section = plan_text[idx:]
    end = section.find("\n## ", 2)
    if end > 0:
        section = section[:end]
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        scope_cell = cells[2]
        for m in _PATH_TOKEN_RE.findall(scope_cell):
            tokens.add(m.replace("\\", "/"))
    return tokens


def _normalize(path: str) -> str:
    p = path.strip().replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return p


def _in_scope(target: str, scope: set[str]) -> bool:
    t = _normalize(target)
    base = t.rsplit("/", 1)[-1]
    for tok in scope:
        n = _normalize(tok)
        if not n:
            continue
        if n in t or t.endswith(n) or base == n.rsplit("/", 1)[-1]:
            return True
    return False


def _read_response() -> str:
    try:
        raw = sys.stdin.read() or ""
    except (OSError, ValueError):
        return ""
    if not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            for key in ("response_text", "response", "text", "content"):
                v = payload.get(key)
                if isinstance(v, str):
                    return v
            return json.dumps(payload)
        return raw
    except (ValueError, TypeError):
        return raw


def _extract_written_paths(text: str) -> list[tuple[str, str]]:
    """Return list of (tool_name, target_path) pairs."""
    out: list[tuple[str, str]] = []
    for m in _WRITE_TOOL_RE.finditer(text):
        tool = m.group(1)
        body = m.group("body")
        path_m = _PATH_PARAM_RE.search(body)
        if path_m:
            out.append((tool, path_m.group("path").strip()))
    return out


def _append(row: dict) -> None:
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    try:
        text = _read_response()
        if not text:
            return 0
        written = _extract_written_paths(text)
        if not written:
            return 0
        plan = _latest_active_plan()
        if plan is None:
            return 0
        try:
            plan_text = plan.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0
        scope = _extract_scope_tokens(plan_text)
        if not scope:
            return 0
        bypass = os.environ.get("SCOPE_DRIFT_BYPASS", "").strip() == "1"
        drifted = [(t, p) for (t, p) in written if not _in_scope(p, scope)]
        if not drifted and not bypass:
            return 0
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan": plan.name,
            "writes_total": len(written),
            "drifted_count": len(drifted),
            "drifted": [{"tool": t, "path": p} for (t, p) in drifted],
            "bypass": bypass,
        }
        _append(row)
        if drifted and not bypass:
            sys.stderr.write(
                f"[scope-drift] {len(drifted)}/{len(written)} writes outside plan scope "
                f"({plan.name}). See scope-containment.md.\n"
            )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"[scope-drift] fail-open: {exc}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
