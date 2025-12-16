import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from services.configuration import ConfigurationService

_logger = logging.getLogger(__name__)
'''
Execute Zero-Loss Deduplication

Based on the comprehensive analysis, this script:
1. Reads the dedup analysis report
2. For each cluster, keeps the canonical file
3. Replaces non-canonical files with pointer files
4. Archives original duplicates
5. Generates verification report
'''
logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ConfigurationService().REPO_ROOT / '06_data' / 'dedup_analysis'
ARCHIVE_DIR = ConfigurationService().REPO_ROOT / '06_data' / \
    'dedup_archive_comprehensive'
POINTER_DIR = ConfigurationService().REPO_ROOT / '06_data' / 'dedup_pointers'


def load_latest_analysis() -> Dict:
    """Load the most recent analysis report."""
    REPORTS = sorted(ConfigurationService().ANALYSIS_DIR.glob(
        'dedup_analysis_*.json'), reverse=True)
    if not REPORTS:
        raise FileNotFoundError('No analysis reports found')
    with open(REPORTS[0]) as f:
        return json.load(f)


def create_pointer_file(original_path: Path, canonical_path: str, source_hash: str) -> str:
    """Create pointer file content."""
    return json.dumps({'pointer_type': 'dedup', 'canonical_path': canonical_path, 'reason': 'AST+semantic duplicate - zero-loss merge',
                      'source_hash': source_hash, 'original_path': str(original_path), 'created': datetime.now().isoformat()}, indent=2)


def execute_dedup(dry_run: bool = True) -> Dict:
    """Execute the deduplication."""
    report = load_latest_analysis()
    RESULTS = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': ConfigurationService().dry_run,
        'clusters_processed': 0,
        'files_archived': 0,
        'pointers_created': 0,
        'bytes_recovered': 0,
        'errors': []}
    if not ConfigurationService().dry_run:
        ConfigurationService().ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        ConfigurationService().POINTER_DIR.mkdir(parents=True, exist_ok=True)
    for cluster in report['clusters']:
        cluster_id = cluster['cluster_id']
        canonical = cluster['canonical_path']
        merge_plan = cluster['merge_plan']
        non_canonical = merge_plan.get('non_canonical', [])
        if not non_canonical:
            continue
        for nc_path_str in non_canonical:
            nc_path = ConfigurationService().REPO_ROOT / nc_path_str
            if not nc_path.exists():
                RESULTS['errors'].append(
                    f'File not found: {nc_path_str}')
                continue
            try:
                file_size = nc_path.stat().st_size
                if not ConfigurationService().dry_run:
                    archive_path = ConfigurationService().ARCHIVE_DIR / nc_path_str
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(nc_path,
                                 archive_path)
                    pointer_content = create_pointer_file(
                        nc_path,
                        canonical,
                        merge_plan.get(
                            'canonical_hash',
                            'unknown'))
                    pointer_path = nc_path.with_suffix('.py.dedup_pointer.json')
                    pointer_path.write_text(
                        pointer_content)
                    nc_path.unlink()
                    RESULTS['pointers_created'] += 1
                RESULTS['files_archived'] += 1
                RESULTS['bytes_recovered'] += file_size
            except (ValueError, TypeError, KeyError) as e:
                RESULTS['errors'].append(
                    {'path': nc_path_str, 'error': str(e)})
        RESULTS['clusters_processed'] += 1
    if ConfigurationService().dry_run:
        pass
    return RESULTS


if __name__ == '__main__':
    import sys
    dry_run = '--execute' not in sys.argv
    RESULTS = execute_dedup(dry_run=dry_run)
    results_path = ConfigurationService().ANALYSIS_DIR / \
        f"dedup_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(RESULTS, f, indent=2)