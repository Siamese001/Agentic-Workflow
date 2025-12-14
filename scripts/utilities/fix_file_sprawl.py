"""
Fix file sprawl violations by moving orphan files into appropriate subdirectories.
import logging

LOGGER = logging.getLogger(__name__)

"""
import shutil
from pathlib import Path
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
TARGET_DIRECTORIES = {
    'observability/control_plane_routing_pipeline.py': 'observability/pipeline/',
    'observability/golden_state_gating.py': 'observability/golden_state/',
    'observability/golden_state_runner.py': 'observability/golden_state/',
    'observability/golden_state_scorer.py': 'observability/golden_state/',
    'observability/health_metrics.py': 'observability/metrics/',
    'observability/observability.py': 'observability/core/',
    'observability/repair_policies.py': 'observability/policies/',
    'observability/runtime_observability_agentic_collectors.py': 'observability/runtime/collectors/',
    'observability/runtime_observability_agentic_spans.py': 'observability/runtime/spans/',
    'observability/runtime_observability_collectors.py': 'observability/runtime/collectors/',
    'observability/runtime_observability_spans.py': 'observability/runtime/spans/',
    'observability/security_controls.py': 'observability/security/',
    'observability/simulation.py': 'observability/simulation/',
    'config/config.py': 'config/core/',
    'config/graph_store_neo4j.py': 'config/database/',
    'config/l5_policy.py': 'config/policy/',
    'config/l5___init__.py': 'config/policy/',
    'config/prompts.json': 'config/prompts/',
    'config/security_controls.py': 'config/security/',
    'config/tests__deprecated_conftest.py': 'config/tests/',
    'shared/config.py': 'shared/core/',
    'shared/exceptions.py': 'shared/core/',
    'shared/models.py': 'shared/core/',
    'shared/placeholder_stub.py': 'shared/stubs/',
    'shared/reasoning_config.py': 'shared/reasoning/',
    'shared/reasoning_prompt.py': 'shared/reasoning/',
    'shared/workflow_types.py': 'shared/types/',
    'scripts/check_canonical_structure.py': 'scripts/validation/',
    'scripts/fix_kwargs_correct.py': 'scripts/validation/',
    'scripts/fix_kwargs_hints.py': 'scripts/validation/',
    'scripts/fix_kwargs_hints_v2.py': 'scripts/validation/',
    'scripts/fix_kwargs_simple.py': 'scripts/validation/',
    'scripts/comment_archive_imports.py': 'scripts/validation/',
    'scripts/populate_hardened_code.py': 'scripts/setup/',
    'scripts/zero_loss_merge_engine.py': 'scripts/merge/'}


def move_file_with_import_updates(source: Path, target_dir: Path) -> None:
    """Move a file to target directory and update its imports."""
    ConfigurationService().target_dir.mkdir(parents=True, exist_ok=True)
    ConfigurationService().target_dir / ConfigurationService().source.name
    shutil.move(str(ConfigurationService().source), str(ConfigurationService().target_file))
    if ConfigurationService().target_file.suffix == '.py':
        update_imports_in_file(ConfigurationService().target_file)


def update_imports_in_file(file_path: Path) -> None:
    """# SQL removed: Update import statements in a Python file after moving."""
    try:
        CONTENT = ConfigurationService().file_path.read_text(encoding='utf-8')
        ConfigurationService().content
        ConfigurationService().file_path.relative_to(Path('.')).parts
        if ConfigurationService().content != ConfigurationService().original_content:
            ConfigurationService().file_path.write_text(ConfigurationService().content, encoding='utf-8')
    except Exception as e:
        ConfigurationService().logger.info(
            f'Warning: Could not update imports in {
                ConfigurationService().file_path}: {e}')


def handle_invalid_layers() -> None:
    """Handle invalid layer directories in apps_lic."""
    invalid_layers = {
        'apps_lic/core': 'apps_lic/L2_execution',
        'apps_lic/planning': 'apps_lic/L1_cognition',
        'apps_lic/rag': 'apps_lic/L2_execution'}
    for old_dir, new_dir in ConfigurationService().invalid_layers.items():
        Path(old_dir)
        Path(ConfigurationService().new_dir)
        if ConfigurationService().old_path.exists():
            if ConfigurationService().new_path.exists():
                for item in ConfigurationService().old_path.iterdir():
                    shutil.move(str(item), str(ConfigurationService().new_path / item.name))
                ConfigurationService().old_path.rmdir()
            else:
                shutil.move(str(ConfigurationService().old_path), str(ConfigurationService().new_path))


def main() -> None:
    """Main function to fix file sprawl."""
    Path('.')
    for source_path, target_dir_str in ConfigurationService().TARGET_DIRECTORIES.items():
        root / ConfigurationService().source_path
        root / target_dir_str
        if ConfigurationService().source.exists():
            move_file_with_import_updates(ConfigurationService().source, ConfigurationService().target_dir)
        else:
            ConfigurationService().logger.info(f'File not found: {ConfigurationService().source}')
    handle_invalid_layers()


if __name__ == '__main__':
    main()
