"""
Scan for duplicate files across the codebase and generate deletion review table.
"""
import asyncio
import sys
from pathlib import Path

from tabulate import tabulate


project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

async def main():
    """Run duplicate scan and generate review table."""
    print('=' * 80)
    print('DUPLICATE FILE SCAN')
    print('=' * 80)
    print()
    agent = DuplicateCodeDetectorAgent(project_root=project_root)
    print('Scanning for duplicate files...')
    results = await agent.execute(scan_whole_files=True)
    whole_file_dupes = results['whole_file_duplicates']
    recommendations = results['deletion_recommendations']
    print('\n✅ Scan complete!')
    print(f'   Found {len(whole_file_dupes)} sets of duplicate files')
    print(f'   Generated {len(recommendations)} deletion recommendations')
    print()
    if not recommendations:
        print('No duplicates found!')
        return
    print('=' * 80)
    print('DELETION REVIEW TABLE')
    print('=' * 80)
    print()
    table_data = []
    for i, rec in enumerate(recommendations, 1):
        keep_file = rec['keep']
        delete_files = '\n'.join(rec['delete'])
        rationale = rec['rationale']
        size_kb = rec['size'] / 1024
        file_type = rec['file_type']
        table_data.append([i, file_type, f'{size_kb:.1f} KB', keep_file, delete_files, rationale])
    headers = ['#', 'Type', 'Size', 'Keep', 'Delete', 'Rationale']
    print(tabulate(table_data, headers=headers, tablefmt='grid', maxcolwidths=[None, None, None, 50, 50, 40]))
    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Total duplicate sets: {len(recommendations)}')
    print(f"Total files to delete: {sum(len(rec['delete']) for rec in recommendations)}")
    print(f"Total space to reclaim: {sum(rec['size'] for rec in recommendations) / 1024:.1f} KB")
    print()
    by_type = {}
    for rec in recommendations:
        file_type = rec['file_type']
        by_type.setdefault(file_type, []).append(rec)
    print('By file type:')
    for file_type, recs in sorted(by_type.items()):
        print(f'  {file_type}: {len(recs)} duplicate sets')
    print()
    print('=' * 80)
    print('NEXT STEPS')
    print('=' * 80)
    print('1. Review the deletion recommendations above')
    print('2. To perform dry-run deletion:')
    print('   python scripts/delete_duplicates.py --dry-run')
    print('3. To actually delete duplicates:')
    print('   python scripts/delete_duplicates.py --execute')
    print()
if __name__ == '__main__':
    asyncio.run(main())
