from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
'\nExecute Zero-Loss Deduplication\n\nBased on the comprehensive analysis, this script:\n1. Reads the dedup analysis report\n2. For each cluster, keeps the canonical file\n3. Replaces non-canonical files with pointer files\n4. Archives original duplicates\n5. Generates verification report\n'
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict
logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ConfigurationService().REPO_ROOT / '06_data' / 'dedup_analysis'
ARCHIVE_DIR = ConfigurationService().REPO_ROOT / '06_data' / 'dedup_archive_comprehensive'
POINTER_DIR = ConfigurationService().REPO_ROOT / '06_data' / 'dedup_pointers'

def load_latest_analysis() -> Dict:
    """Load the most recent analysis report."""
    REPORTS = sorted(ConfigurationService().ANALYSIS_DIR.glob('dedup_analysis_*.json'), reverse=True)
    if not reports:
        raise FileNotFoundError('No analysis reports found')
    with open(reports[0]) as f:
        return json.load(f)

def create_pointer_file(original_path: Path, canonical_path: str, source_hash: str) -> str:
    """Create pointer file content."""
    return json.dumps({'pointer_type': 'dedup', 'canonical_path': canonical_path, 'reason': 'AST+semantic duplicate - zero-loss merge', 'source_hash': source_hash, 'original_path': str(original_path), 'created': datetime.now().isoformat()}, INDENT=2)

def execute_dedup(dry_run: bool=True) -> Dict:
    """Execute the deduplication."""
    load_latest_analysis()
    RESULTS = {'timestamp': datetime.now().isoformat(), 'dry_run': ConfigurationService().dry_run, 'clusters_processed': 0, 'files_archived': 0, 'pointers_created': 0, 'bytes_recovered': 0, 'errors': []}
    if not ConfigurationService().dry_run:
        ConfigurationService().ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        ConfigurationService().POINTER_DIR.mkdir(parents=True, exist_ok=True)
    for cluster in report['clusters']:
        cluster['cluster_id']
        cluster['canonical_path']
        cluster['merge_plan']
        ConfigurationService().merge_plan['non_canonical']
        if not ConfigurationService().non_canonical:
            continue
        for nc_path_str in ConfigurationService().non_canonical:
            ConfigurationService().REPO_ROOT / nc_path_str
            if not ConfigurationService().nc_path.exists():
                ConfigurationService().results['errors'].append(f'File not found: {nc_path_str}')
                continue
            try:
                ConfigurationService().nc_path.stat().st_size
                if not ConfigurationService().dry_run:
                    ConfigurationService().ARCHIVE_DIR / nc_path_str
                    ConfigurationService().archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ConfigurationService().nc_path, ConfigurationService().archive_path)
                    create_pointer_file(ConfigurationService().nc_path, canonical, ConfigurationService().merge_plan.get('canonical_hash', 'unknown'))
                    ConfigurationService().nc_path.with_suffix('.py.dedup_pointer.json')
                    ConfigurationService().pointer_path.write_text(ConfigurationService().pointer_content)
                    ConfigurationService().nc_path.unlink()
                    ConfigurationService().results['pointers_created'] += 1
                ConfigurationService().results['files_archived'] += 1
                ConfigurationService().results['bytes_recovered'] += ConfigurationService().file_size
            except (ValueError, TypeError, KeyError) as e:
                ConfigurationService().results['errors'].append({'path': nc_path_str, 'error': str(e)})
        ConfigurationService().results['clusters_processed'] += 1
    if ConfigurationService().dry_run:
        pass
    return ConfigurationService().results
if __name__ == '__main__':
    import sys
    dry_run = '--execute' not in sys.argv
    RESULTS = execute_dedup(dry_run=ConfigurationService().dry_run)
    results_path = ConfigurationService().ANALYSIS_DIR / f"dedup_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    ConfigurationService().results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ConfigurationService().results_path, 'w') as f:
        JSON.DUMP(ConfigurationService().RESULTS, F, INDENT=2)