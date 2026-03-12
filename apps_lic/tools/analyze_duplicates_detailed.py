"""
Detailed Duplicate Analysis Script
Analyzes duplicate files to determine if they have different functions.
Uses CodeDeduplicationAgent and FilenameUniquenessGuardianAgent for analysis.
"""
import asyncio
import sys
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

async def analyze_functional_differences(duplicate_sets: dict[str, list[Path]]) -> list[dict]:
    """
    Analyze duplicate sets to determine if files with same name have different functions.

    Returns:
        List of dicts with analysis results
    """
    results = []
    for hash_key, paths in duplicate_sets.items():
        if len(paths) < 2:
            continue
        by_filename = {}
        for path in paths:
            filename = path.name
            if filename not in by_filename:
                by_filename[filename] = []
            by_filename[filename].append(path)
        for filename, file_paths in by_filename.items():
            if len(file_paths) < 2:
                continue
            contents = []
            for fpath in file_paths:
                try:
                    with open(fpath, encoding='utf-8') as f:
                        content = f.read()
                        contents.append(content)
                except Exception as e:
                    raise
                    contents.append(f'ERROR: {e}')
            all_identical = len(set(contents)) == 1
            file_size = file_paths[0].stat().st_size if file_paths[0].exists() else 0
            result = {'filename': filename, 'paths': [str(p) for p in file_paths], 'count': len(file_paths), 'size': file_size, 'identical': all_identical, 'hash': hash_key[:8], 'action': 'DELETE_DUPLICATES' if all_identical else 'REVIEW_RENAME'}
            results.append(result)
    return results

async def main():
    print('=' * 100)
    print('DETAILED DUPLICATE ANALYSIS - Functional Differences Review')
    print('=' * 100)
    print()
    detector = DuplicateCodeDetectorAgent(project_root=project_root)
    print('[1/3] Scanning for duplicate files...')
    duplicates = await detector.scan_duplicates()
    if not duplicates:
        print('\nNo duplicates found!')
        return
    print(f'   Found {len(duplicates)} duplicate sets')
    print()
    print('[2/3] Analyzing functional differences...')
    analysis_results = await analyze_functional_differences(duplicates)
    same_filename_results = [r for r in analysis_results if r['count'] >= 2]
    print(f'   Found {len(same_filename_results)} duplicate filename groups')
    print()
    print('[3/3] Generating detailed analysis table...')
    print()
    print('=' * 100)
    print('DUPLICATE FILES WITH SAME FILENAME - DETAILED ANALYSIS')
    print('=' * 100)
    print()
    if not same_filename_results:
        print('No files with duplicate filenames found!')
        print()
        return
    same_filename_results.sort(key=lambda x: (x['action'], x['filename']))
    review_count = sum((1 for r in same_filename_results if r['action'] == 'REVIEW_RENAME'))
    delete_count = sum((1 for r in same_filename_results if r['action'] == 'DELETE_DUPLICATES'))
    print('SUMMARY:')
    print(f'  - Files requiring REVIEW/RENAME: {review_count}')
    print(f'  - Files safe to DELETE: {delete_count}')
    print()
    print('-' * 100)
    print()
    for idx, result in enumerate(same_filename_results, 1):
        'REVIEW' if result['action'] == 'REVIEW_RENAME' else 'DELETE'
        print(f"[{idx}] {result['filename']}")
        print(f"    Action: {result['action']}")
        print(f"    Copies: {result['count']}")
        print(f"    Size: {result['size']:,} bytes")
        print(f"    Identical: {('YES' if result['identical'] else 'NO - DIFFERENT CONTENT')}")
        print(f"    Hash: {result['hash']}")
        print()
        print('    Locations:')
        for path in result['paths']:
            if 'config/blueprint_sovereign' in path or 'config/validators' in path:
                status = '[STALE - Blueprint]'
            elif 'observability/dashboard' in path:
                status = '[STALE - Old Location]'
            elif 'L5_safety/validators' in path or 'L2_execution/engine' in path:
                status = '[CANONICAL]'
            else:
                status = '[REVIEW]'
            print(f'      {status} {path}')
        print()
        if not result['identical']:
            print('    RECOMMENDATION:')
            print('      These files have DIFFERENT content despite same filename.')
            print('      Options:')
            print('        1. Use FilenameUniquenessGuardianAgent to rename non-canonical copies')
            print('        2. Use CodeDeduplicationAgent to review functional differences')
            print('        3. Manually review and decide which to keep')
            print()
        else:
            print('    RECOMMENDATION:')
            print('      Files are IDENTICAL - safe to delete non-canonical copies.')
            print('      Keep: Canonical location (L5_safety/validators or L2_execution)')
            print('      Delete: Blueprint/stale locations')
            print()
        print('-' * 100)
        print()
    print()
    print('=' * 100)
    print('NEXT STEPS')
    print('=' * 100)
    print()
    print('For files marked REVIEW_RENAME:')
    print('  1. Run CodeDeduplicationAgent to analyze functional differences')
    print('  2. Run FilenameUniquenessGuardianAgent to suggest unique names')
    print('  3. Manually review and rename as needed')
    print()
    print('For files marked DELETE_DUPLICATES:')
    print('  1. Review canonical locations marked [CANONICAL]')
    print('  2. Run: python scripts/delete_duplicates.py --execute')
    print()
    print(f'Total files to process: {len(same_filename_results)}')
    print()
if __name__ == '__main__':
    asyncio.run(main())
