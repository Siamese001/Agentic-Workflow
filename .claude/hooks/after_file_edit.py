import json
import os
import subprocess
import sys
from pathlib import Path

from lib.claude_hook_common import (
    allow,
    block_exit_code,
    contains_legacy_execution_token,
    payload_path,
    read_payload,
    text_from_payload,
    warn,
    write_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


# NOTE (cursor-decommission W6): the legacy MCP-mirror sync (root .mcp.json -> .cursor/mcp.json)
# is retired. The .cursor/mcp.json mirror no longer exists; root .mcp.json is the sole SSOT,
# so no post-edit mirror sync is triggered.


payload = read_payload()
text = text_from_payload(payload)
file_path = payload_path(payload)
legacy = contains_legacy_execution_token(text + "\n" + file_path)
if legacy and "/plans/_archive/" not in file_path:
    reason = "Edit references legacy execution surface outside archive: " + ", ".join(legacy)
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))

if file_path.startswith(".claude/plans/_archive/") or "/plans/_archive/" in file_path:
    reason = "Edited archived historical plan material; confirm this was intentional reference maintenance."
    write_receipt("afterFileEdit", payload, "warn", reason)
    raise SystemExit(warn(reason))


def _audit_plan_wave_summary_top(norm_path: str) -> int | None:
    """Return hook exit code when plan violates consolidated wave summary at top."""
    # Forward-only relocation (c1a17d): canonical repo-root plans/ + legacy
    # .claude/plans/. A plan file is a *.md whose parent dir is named "plans"
    # and is not under an _archive/ or reports/ tree (matches
    # post_write_plan_reconcile.py / plan_driven_closer.py).
    _np = norm_path.replace("\\", "/")
    if Path(_np).parent.name != "plans" or "reports" in Path(_np).parts:
        return None
    if not norm_path.endswith(".md"):
        return None
    if "/plans/_archive/" in _np:
        return None

    plan_file = REPO_ROOT / norm_path.replace("/", os.sep)
    if not plan_file.is_file():
        return None

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from ops_scripts.ci.plan_wave_summary_top import (
        WaveSummarySeverity,
        is_plan_format_v2,
        validate_plan_format,
    )

    rel = norm_path.replace("\\", "/")
    try:
        content = plan_file.read_text(encoding="utf-8")
    except OSError:
        return None

    v2 = is_plan_format_v2(content)
    fails = [
        v for v in validate_plan_format(content, rel) if v.severity == WaveSummarySeverity.FAIL
    ]
    if not fails:
        return None

    first = fails[0]
    reason = (
        f"Plan violates the v2 format standard ({first.rule_id}): {first.message} "
        "Plans must carry Wave + Phase summary tables (canonical columns) under `## Status Tables` "
        "before the first `## Wave N` section, with waves in ascending execution order. "
        "See .claude/rules/plan-location.md."
    )
    # v2 plans (created from the template) are enforced going forward → block. Legacy plans warn
    # unless PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT=1 opts them into strict too.
    strict = v2 or os.environ.get("PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT", "").strip() in (
        "1",
        "true",
        "yes",
    )
    decision = "block" if strict else "warn"
    write_receipt("afterFileEdit", payload, decision, reason)
    if strict:
        print(
            '{"decision": "block", "reason": '
            + json.dumps(reason)
            + "}",
            flush=True,
        )
        return block_exit_code()
    raise SystemExit(warn(reason))


_wave_top_exit = _audit_plan_wave_summary_top(file_path.replace("\\", "/"))
if _wave_top_exit is not None:
    raise SystemExit(_wave_top_exit)


def _enqueue_plan_if_eligible(norm_path: str) -> None:
    """File-driven plan registration trigger (W2 plan-ssot-notion-pipeline-d2f7a1).

    After a plan write passes all format checks, enqueue the plan for Notion registration
    ONLY when the file is a valid SSOT plan path AND passes completeness:
      - v2 plans: ``validate_plan_format`` returns 0 FAIL violations.
      - legacy plans: has valid frontmatter (``---`` … ``---``).

    Carries ``content_digest`` (sha256) + ``ai_summary`` (from frontmatter) in the queue
    row so the Notion row is created complete, not as a metadata-only stub.

    Fail-soft: any exception is silently swallowed — never blocks the edit.  The legacy
    PLAN_CREATED: marker capture path remains as an advisory fallback.
    """
    try:
        _np = norm_path.replace("\\", "/")
        from pathlib import Path as _Path
        _parent = _Path(_np).parent.name
        if _parent != "plans":
            return
        if not _np.endswith(".md"):
            return
        if "/plans/_archive/" in _np:
            return
        _parts = {p.lower() for p in _Path(_np).parts}
        if "docs" in _parts or "reports" in _parts:
            return

        plan_file = REPO_ROOT / norm_path.replace("/", os.sep)
        if not plan_file.is_file():
            return

        # Extract slug from filename
        import re as _re
        _PLAN_FILE_RE = _re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]*-[0-9a-f]{6})\.md$")
        _m = _PLAN_FILE_RE.match(plan_file.name)
        if not _m:
            return
        slug = _m.group("slug")

        content = plan_file.read_text(encoding="utf-8")

        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))

        from ops_scripts.ci.plan_wave_summary_top import (
            WaveSummarySeverity,
            is_plan_format_v2,
            validate_plan_format,
        )

        v2 = is_plan_format_v2(content)
        rel = norm_path.replace("\\", "/")

        if v2:
            # v2 plans must pass the format gate before we register them — no stubs.
            fails = [
                v for v in validate_plan_format(content, rel)
                if v.severity == WaveSummarySeverity.FAIL
            ]
            if fails:
                return  # incomplete / malformed — don't register; user will fix and re-write
        else:
            # Legacy: at minimum needs a closed frontmatter block.
            import importlib.util as _ilu
            _helper_path = REPO_ROOT / ".claude" / "governance/scripts" / "_plan_registration.py"
            if not _helper_path.exists():
                return
            _spec = _ilu.spec_from_file_location("_plan_reg_fde_legacy", _helper_path)
            if _spec is None or _spec.loader is None:
                return
            _helper_legacy = _ilu.module_from_spec(_spec)
            try:
                _spec.loader.exec_module(_helper_legacy)
            except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
                return
            if not _helper_legacy.has_valid_frontmatter(content):
                return

        # Load helper for enqueue + metadata extraction.
        import importlib.util as _ilu2
        _helper_path2 = REPO_ROOT / ".claude" / "governance/scripts" / "_plan_registration.py"
        if not _helper_path2.exists():
            return
        _spec2 = _ilu2.spec_from_file_location("_plan_reg_fde", _helper_path2)
        if _spec2 is None or _spec2.loader is None:
            return
        _helper = _ilu2.module_from_spec(_spec2)
        try:
            _spec2.loader.exec_module(_helper)
        except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
            return

        meta = _helper.extract_plan_metadata(content)
        path_str = f"plans/{slug}.md"
        enqueued = _helper.enqueue_plan(
            slug,
            path_str,
            "Not Started",
            content_digest=meta.get("content_digest"),
            ai_summary=meta.get("ai_summary"),
        )
        if enqueued:
            digest_short = (meta.get("content_digest") or "")[:8]
            print(
                f"[after_file_edit] file-driven plan registration: queued {slug} "
                f"(digest={digest_short}..., ai_summary={str(meta.get('ai_summary'))[:40]!r})",
                file=sys.stderr,
            )
    except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
        pass


_enqueue_plan_if_eligible(file_path.replace("\\", "/"))


def _sync_plan_to_notion_if_registered(norm_path: str) -> None:
    """W3 re-sync: when a registered plan is edited, patch Notion plan properties.

    Re-derives content_digest from the current file and compares it to the stored digest
    in the queue row.  If they differ (plan was edited), patches the Notion page's
    ``AI Summary`` and wave-aware ``Summary`` properties, then updates the queue
    row's stored digest.

    Requires NOTION_TOKEN.  Fail-soft: any exception silently swallowed.
    """
    try:
        _np = norm_path.replace("\\", "/")
        from pathlib import Path as _Path
        if _Path(_np).parent.name != "plans" or not _np.endswith(".md"):
            return
        if "/plans/_archive/" in _np:
            return
        _parts = {p.lower() for p in _Path(_np).parts}
        if "docs" in _parts or "reports" in _parts:
            return

        plan_file = REPO_ROOT / norm_path.replace("/", os.sep)
        if not plan_file.is_file():
            return

        import re as _re
        _PFR = _re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]*-[0-9a-f]{6})\.md$")
        _m = _PFR.match(plan_file.name)
        if not _m:
            return
        slug = _m.group("slug")

        # Load _plan_registration helper (already loaded in sys.modules under various names;
        # just load fresh to avoid stale cache from the earlier enqueue call).
        import importlib.util as _ilu3
        _hp3 = REPO_ROOT / ".claude" / "governance/scripts" / "_plan_registration.py"
        if not _hp3.exists():
            return
        _spec3 = _ilu3.spec_from_file_location("_plan_reg_sync", _hp3)
        if _spec3 is None or _spec3.loader is None:
            return
        _helper3 = _ilu3.module_from_spec(_spec3)
        try:
            _spec3.loader.exec_module(_helper3)
        except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
            return

        # Check if plan is registered and if digest has changed.
        cache = _helper3.read_cache()
        if not _helper3.cache_is_fresh(cache):
            return
        cache_plans = (cache or {}).get("plans", {})
        entry = cache_plans.get(slug) if isinstance(cache_plans, dict) else None
        if not entry or not isinstance(entry, dict):
            return  # not registered yet — enqueue path handles initial registration
        page_id = entry.get("page_id")
        if not page_id:
            return  # no page_id in cache — can't patch

        # Compute current file digest and compare to queue row.
        content = plan_file.read_text(encoding="utf-8")
        meta = _helper3.extract_plan_metadata(content)
        current_digest = meta.get("content_digest") or ""

        rows = _helper3._read_queue()
        queued = next((r for r in rows if r.get("slug") == slug), None)
        stored_digest = (queued.get("content_digest") or "") if queued else ""

        if current_digest == stored_digest and stored_digest:
            return  # no change — skip patch

        # Content changed — patch Notion and update queue metadata.
        import os as _os
        token = (
            _os.environ.get("NOTION_TOKEN", "").strip()
            or _os.environ.get("NOTION_API_KEY", "").strip()
        )
        if not token:
            # No token — still update queue row so drift gate can detect the change.
            _helper3.update_plan_metadata(slug, content_digest=current_digest, ai_summary=meta.get("ai_summary"))
            return

        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        try:
            from tools.notion.plan_creation_helper import patch_plan_notion_properties as _patch
            from tools.notion.plan_wave_summary import (
                build_plan_notion_ai_summary as _ai_summary,
                build_plan_notion_summary as _summary,
            )

            computed_ai_summary = _ai_summary(content)
            patched = _patch(
                page_id,
                ai_summary=computed_ai_summary,
                summary=_summary(content),
                token=token,
            )
        except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
            computed_ai_summary = meta.get("ai_summary")
            patched = False

        _helper3.update_plan_metadata(slug, content_digest=current_digest, ai_summary=computed_ai_summary)
        if patched:
            print(
                f"[after_file_edit] W3 re-sync: patched Notion page {page_id} for {slug} "
                f"(digest {(stored_digest or '(none)')[:8]} → {current_digest[:8]})",
                file=sys.stderr,
            )
    except Exception:  # guardian: allow-broad-exception -- fail-soft hook contract
        pass


_sync_plan_to_notion_if_registered(file_path.replace("\\", "/"))

write_receipt("afterFileEdit", payload, "allow", "edit accepted")
raise SystemExit(allow("edit accepted"))
