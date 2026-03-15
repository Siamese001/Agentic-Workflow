#!/usr/bin/env python3
"""Compare archived files against current codebase to identify restoration candidates."""

import hashlib
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "compare_archive_to_current_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "compare_archive_to_current_util", "p0_governance")
_emit_snapshots_state("p0", "compare_archive_to_current_util", "state_snapshot")


def file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    # guardian: allow-silent-swallow
    except:
        return ""


def find_in_current(filename: str, current_dirs: list) -> list:
    """Find files with same name in current codebase."""
    matches = []
    for d in current_dirs:
        for f in Path(d).rglob(filename):
            if "__pycache__" not in str(f):
                matches.append(f)
    return matches


def main():
    # Candidate files from archive analysis
    restore_candidates = [
        # apps_lic candidates
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_message_filters.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_personalization_query.py",
            APPS_LIC_DIR,
        ),
        ("archives/apps_lic/L1_cognition/P1_retrieve/get_info/extract_contact_info.py", APPS_LIC_DIR),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/fetch_recipient_interactions.py",
            APPS_LIC_DIR,
        ),
        (
            "archives/apps_lic/L1_cognition/P1_retrieve/get_info/match_recipient_patterns.py",
            APPS_LIC_DIR,
        ),
        ("archives/apps_lic/L1_cognition/P1_retrieve/get_info/query_past_campaigns.py", APPS_LIC_DIR),
        # apps_rg candidates
        (
            "archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py",
            APPS_RG_DIR,
        ),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_search_filters.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_skill_query.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/fetch_user_preferences.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/match_job_patterns.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/parse_job_description.py", APPS_RG_DIR),
        ("archives/apps_rg/L1_cognition/P1_retrieve/get_info/query_past_generations.py", APPS_RG_DIR),
        # apps_shared candidates
        ("archives/apps_shared/cache/semantic_cache.py", APPS_SHARED_DIR),
        ("archives/apps_shared/core/meta_ranking.py", APPS_SHARED_DIR),
        # Reachout Engine Archive candidates
        ("archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py", APPS_LIC_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/models_LIC.py", APPS_SHARED_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py", APPS_LIC_DIR),
        ("archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py", APPS_SHARED_DIR),
    ]

    current_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]

    print("=" * 80)
    print("ARCHIVE vs CURRENT CODEBASE COMPARISON")
    print("=" * 80)

    to_restore = []
    already_exists = []
    not_found = []

    for archive_path, target_app in restore_candidates:
        archive_file = Path(archive_path)
        if not archive_file.exists():
            not_found.append((archive_path, target_app, "Archive file not found"))
            continue

        filename = archive_file.name
        archive_hash = file_hash(archive_file)

        # Find matching files in current codebase
        current_matches = find_in_current(filename, current_dirs)

        if not current_matches:
            # No match - candidate for restoration
            to_restore.append(
                {
                    "archive": archive_path,
                    "target": target_app,
                    "filename": filename,
                    "reason": "No matching file in current codebase",
                    "action": "RESTORE",
                },
            )
        else:
            # Check if any match has same content
            identical = False
            for match in current_matches:
                if file_hash(match) == archive_hash:
                    identical = True
                    already_exists.append(
                        {
                            "archive": archive_path,
                            "current": str(match),
                            "reason": "Identical file exists",
                            "action": "SKIP",
                        },
                    )
                    break

            if not identical:
                # Different content - may need review
                to_restore.append(
                    {
                        "archive": archive_path,
                        "target": target_app,
                        "filename": filename,
                        "current_matches": [str(m) for m in current_matches],
                        "reason": "File exists but content differs",
                        "action": "REVIEW",
                    },
                )

    # Print results
    print(f"\n## FILES TO RESTORE ({len(to_restore)} files)")
    print("-" * 60)
    for item in to_restore:
        print(f"\n  [{item['action']}] {item['filename']}")
        print(f"    Archive: {item['archive']}")
        print(f"    Target:  {item['target']}/engines/utils/")
        print(f"    Reason:  {item['reason']}")
        if "current_matches" in item:
            print(f"    Current: {item['current_matches']}")

    print(f"\n## ALREADY EXISTS ({len(already_exists)} files)")
    print("-" * 60)
    for item in already_exists:
        print(f"\n  [SKIP] {Path(item['archive']).name}")
        print(f"    Archive: {item['archive']}")
        print(f"    Current: {item['current']}")

    if not_found:
        print(f"\n## NOT FOUND ({len(not_found)} files)")
        print("-" * 60)
        for path, _target, reason in not_found:
            print(f"  {path}: {reason}")

    # Summary
    print("\n" + "=" * 80)
    print("RESTORATION PLAN SUMMARY")
    print("=" * 80)

    restore_count = len([x for x in to_restore if x["action"] == "RESTORE"])
    review_count = len([x for x in to_restore if x["action"] == "REVIEW"])

    print(f"\n  RESTORE (new files):     {restore_count}")
    print(f"  REVIEW (content differs): {review_count}")
    print(f"  SKIP (already exists):    {len(already_exists)}")
    print(f"  NOT FOUND:                {len(not_found)}")


if __name__ == "__main__":
    main()
