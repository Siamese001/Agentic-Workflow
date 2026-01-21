#!/usr/bin/env python3
"""Compare archived files against current codebase to identify restoration candidates."""
from pathlib import Path
import hashlib

def file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except:
        return ""

def find_in_current(filename: str, current_dirs: list) -> list:
    """Find files with same name in current codebase."""
    matches = []
    for d in current_dirs:
        for f in Path(d).rglob(filename):
            if '__pycache__' not in str(f):
                matches.append(f)
    return matches

def main():
    # Candidate files from archive analysis
    restore_candidates = [
        # apps_lic candidates
        ('archives/apps_lic/L1_cognition/P1_retrieve/check_outreach/check_outreach_policy.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_message_filters.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/build_personalization_query.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/extract_contact_info.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/fetch_recipient_interactions.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/match_recipient_patterns.py', 'apps_lic'),
        ('archives/apps_lic/L1_cognition/P1_retrieve/get_info/query_past_campaigns.py', 'apps_lic'),

        # apps_rg candidates
        ('archives/apps_rg/L1_cognition/P1_retrieve/check_resume/check_resume_policy.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_search_filters.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/build_skill_query.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/fetch_user_preferences.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/match_job_patterns.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/parse_job_description.py', 'apps_rg'),
        ('archives/apps_rg/L1_cognition/P1_retrieve/get_info/query_past_generations.py', 'apps_rg'),

        # apps_shared candidates
        ('archives/apps_shared/cache/semantic_cache.py', 'apps_shared'),
        ('archives/apps_shared/core/meta_ranking.py', 'apps_shared'),

        # Reachout Engine Archive candidates
        ('archives/Reachout Engine Archive/Agentic LIC/hop_agents_LIC.py', 'apps_lic'),
        ('archives/Reachout Engine Archive/Agentic LIC/models_LIC.py', 'apps_shared'),
        ('archives/Reachout Engine Archive/Agentic LIC/workflow_LIC.py', 'apps_lic'),
        ('archives/Reachout Engine Archive/Agentic LIC/state_manager_LIC.py', 'apps_shared'),
    ]

    current_dirs = ['agentic_core', 'apps_rg', 'apps_lic', 'apps_shared', 'scripts']

    print('=' * 80)
    print('ARCHIVE vs CURRENT CODEBASE COMPARISON')
    print('=' * 80)

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
            to_restore.append({
                'archive': archive_path,
                'target': target_app,
                'filename': filename,
                'reason': 'No matching file in current codebase',
                'action': 'RESTORE'
            })
        else:
            # Check if any match has same content
            identical = False
            for match in current_matches:
                if file_hash(match) == archive_hash:
                    identical = True
                    already_exists.append({
                        'archive': archive_path,
                        'current': str(match),
                        'reason': 'Identical file exists',
                        'action': 'SKIP'
                    })
                    break

            if not identical:
                # Different content - may need review
                to_restore.append({
                    'archive': archive_path,
                    'target': target_app,
                    'filename': filename,
                    'current_matches': [str(m) for m in current_matches],
                    'reason': 'File exists but content differs',
                    'action': 'REVIEW'
                })

    # Print results
    print(f"\n## FILES TO RESTORE ({len(to_restore)} files)")
    print("-" * 60)
    for item in to_restore:
        print(f"\n  [{item['action']}] {item['filename']}")
        print(f"    Archive: {item['archive']}")
        print(f"    Target:  {item['target']}/engines/utils/")
        print(f"    Reason:  {item['reason']}")
        if 'current_matches' in item:
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
        for path, target, reason in not_found:
            print(f"  {path}: {reason}")

    # Summary
    print("\n" + "=" * 80)
    print("RESTORATION PLAN SUMMARY")
    print("=" * 80)

    restore_count = len([x for x in to_restore if x['action'] == 'RESTORE'])
    review_count = len([x for x in to_restore if x['action'] == 'REVIEW'])

    print(f"\n  RESTORE (new files):     {restore_count}")
    print(f"  REVIEW (content differs): {review_count}")
    print(f"  SKIP (already exists):    {len(already_exists)}")
    print(f"  NOT FOUND:                {len(not_found)}")

if __name__ == '__main__':
    main()
