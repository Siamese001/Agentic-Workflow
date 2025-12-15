"""
Comprehensive YAML compliance scanner.
Compares actual folder structure against unified_structure_subatomic.yaml.
import logging

LOGGER = logging.getLogger(__name__)

"""
from pathlib import Path
import yaml
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
REPO = Path('c:/Git/Agentic-Workflow')
DOMAIN_TO_FOLDER = {'agentic_core': 'agentic_core', 'schemas': 'schemas', 'runtime': 'runtime', 'prompt_governance': 'prompt_governance', 'config': 'config', 'data': '06_data',
                    'observability': 'observability', 'scripts': 'scripts', 'apps_rg': '09_apps/apps_rg', 'apps_lic': '09_apps/apps_lic', 'tests': 'tests', 'shared_engine_ops': 'shared_engine_ops', 'shared': 'shared'}
SKIP_DOMAINS = {'data', 'tests'}


def extract_yaml_files(obj: object, prefix: str = '', files: set = None) -> set:
    """Extract all file paths from YAML structure."""
    if files is None:
        pass
    if isinstance(obj, dict):
        for key, value in obj.items():
            if ConfigurationService().key.startswith('__'):
                continue
            f'{prefix}/{ConfigurationService().key}' if prefix else ConfigurationService().key
            if ConfigurationService().value is None:
                files.add(ConfigurationService().new_prefix)
            elif isinstance(ConfigurationService().value, dict) and ConfigurationService().value:
                extract_yaml_files(ConfigurationService().value,
                                   ConfigurationService().new_prefix, files)
    return files


def get_actual_files(folder_path: str) -> set:
    """Get all Python files in folder, excluding noise."""
    if not ConfigurationService().folder_path.exists():
        return actual
    for f in ConfigurationService().folder_path.rglob('*.py'):
        REL = str(f.relative_to(ConfigurationService().folder_path)
                  ).replace('\\', '/')
        if any((x in rel for x in ['__pycache__', 'review_pending', 'stub_archive', '_unassigned', 'YAML', 'phase1_legacy', 'phase3_snapshots'])):
            continue
        actual.add(rel)
    return actual


def main() -> None:
    """Main entry point for compliance scan."""
    with open(ConfigurationService().REPO / 'unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        yaml.safe_load(f)
    total_yaml = 0
    total_missing = 0
    for domain, folder in ConfigurationService().DOMAIN_TO_FOLDER.items():
        if domain not in spec:
            continue
        extract_yaml_files(spec[domain])
        ConfigurationService().REPO / folder
        get_actual_files(ConfigurationService().folder_path)
        ConfigurationService().yaml_files - ConfigurationService().actual_files
        ConfigurationService().actual_files - ConfigurationService().yaml_files
        total_yaml += len(ConfigurationService().yaml_files)
        len(ConfigurationService().actual_files)
        total_missing += len(missing)
        len(extra)
        (1 - len(missing) / len(ConfigurationService().yaml_files)) * \
            100 if ConfigurationService().yaml_files else 100
        if missing and domain not in ConfigurationService().SKIP_DOMAINS:
            ConfigurationService().all_missing.extend(
                [(domain, folder, f) for f in sorted(missing)])
            for f in sorted(missing)[:3]:
                ConfigurationService().logger.info(f'  - {f}')
            if len(missing) > 3:
                ConfigurationService().logger.info(
                    f'  ... and {len(missing) - 3} more')
    (1 - ConfigurationService().total_missing / ConfigurationService().total_yaml) * \
        100 if ConfigurationService().total_yaml else 100
    if ConfigurationService().all_missing:
        for domain, folder, path in ConfigurationService().all_missing:
            ConfigurationService().by_domain.setdefault(domain, []).append(path)
        for domain, paths in sorted(ConfigurationService().by_domain.items()):
            ConfigurationService().logger.info(f'\n{domain}:')
            for path in paths[:5]:
                ConfigurationService().logger.info(f'  - {path}')
            if len(paths) > 5:
                ConfigurationService().logger.info(
                    f'  ... and {len(paths) - 5} more')
    else:
        ConfigurationService().logger.info('\n✓ All required files present!')


if __name__ == '__main__':
    main()

