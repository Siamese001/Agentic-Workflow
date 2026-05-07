"""apps_architect engines package."""

from apps_architect.engines.adg_client import ADGClient
from apps_architect.engines.core_pattern_engine import CorePatternEngine
from apps_architect.engines.deep_history_scanner import DeepHistoryScanner
from apps_architect.engines.delta_engine import DeltaEngine
from apps_architect.engines.enforcement_engine import EnforcementEngine
from apps_architect.engines.file_watcher import FileWatcher
from apps_architect.engines.migration_executor import MigrationExecutor
from apps_architect.engines.pattern_scanner import PatternScanner
from apps_architect.engines.plan_pattern_engine import PlanPatternEngine
from apps_architect.engines.readme_assembler import ReadmeAssembler
from apps_architect.engines.rule_generator import RuleGenerator
from apps_architect.engines.rule_pattern_engine import RulePatternEngine

__all__ = [
    "ADGClient",
    "CorePatternEngine",
    "DeepHistoryScanner",
    "DeltaEngine",
    "EnforcementEngine",
    "FileWatcher",
    "MigrationExecutor",
    "PatternScanner",
    "PlanPatternEngine",
    "ReadmeAssembler",
    "RuleGenerator",
    "RulePatternEngine",
]
