"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-2 for Apps/Tests and Depth-3 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.

CONSOLIDATED VERSION: Reduced redundancy while preserving all information.
"""
import os
import re
from typing import Any, Dict, List, Optional, Protocol, Set
CANON_KEY_EXCEPTIONS: Dict[int, Dict[str, Any]] = {23: {'files': {'agentic_core/L2_execution/mcp/fetch_client_sovereign.py'}, 'patterns': ['if TYPE_CHECKING:', '\\"\\"\\".*requests.*\\"\\"\\"']}, 20: {'files': {'canon_validator_agentic_v2.py', 'pyproject.toml'}, 'patterns': []}}
active_canon_keys: Any = list(range(0, 20))
CANON_KEY_TO_FOLDER_MAP: Dict[int, List[str]] = {0: ['.'], 1: ['agentic_core/prompt_governance'], 2: ['agentic_core/schemas'], 3: ['agentic_core/L1_cognition'], 4: ['agentic_core/L3_orchestration'], 5: ['agentic_core/L4_state'], 6: ['agentic_core/L5_safety'], 7: ['agentic_core/L0_maintenance'], 8: ['agentic_core/L2_execution', 'agentic_core/patterns', 'agentic_core/semantic_memory', 'agentic_core/knowledge'], 9: ['agentic_core/config', 'agentic_core/runtime'], 10: ['agentic_core/utils', 'agentic_core/observability'], 11: ['apps_shared', 'apps_rg', 'apps_lic'], 12: ['tests'], 13: ['*'], 14: ['*'], 15: ['*'], 16: ['*'], 17: ['*'], 18: ['*'], 19: ['*']}
sovereign_registry: Any = {'agentic_core': {'depth': 3, 'subfolders': ['L0_maintenance', 'L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety', 'config', 'schemas', 'prompt_governance', 'runtime', 'observability', 'utils', 'patterns', 'semantic_memory', 'knowledge']}, 'apps_rg': {'depth': 2, 'subfolders': ['logic_nodes', 'asset_library', 'system_flow', 'engines', 'templates']}, 'apps_lic': {'depth': 2, 'subfolders': ['logic_nodes', 'asset_library', 'system_flow', 'engines', 'templates']}, 'apps_shared': {'depth': 2, 'subfolders': ['base_definitions', 'common_utils', 'core_components', 'base_agents', 'models', 'utils']}, 'tests': {'depth': 2, 'subfolders': ['unit', 'integration', 'e2e', 'functional', 'fixtures', 'automation', 'core', 'data', 'performance', 'security']}}
core_subfolder_map: Any = {'L0_maintenance': ['scripts', 'logs', 'benchmarks'], 'L1_cognition': ['thought_engine', 'intent_analysis', 'planning'], 'L2_execution': ['tool_registry', 'action_handlers', 'mcp'], 'L3_orchestration': ['workflow_engines', 'fission_logic', 'S3_vitality', 'mcp', 'meta_learning'], 'L4_state': ['validation_context', 'ledger', 'filesystem', 'memory'], 'L5_safety': ['guardrails', 'red_teaming', 'gravity', 'validators'], 'schemas': ['models', 'messages', 'types', 'validators'], 'config': ['blueprint_sovereign', 'environments', 'feature_flags', 'secrets_manager'], 'prompt_governance': ['meta_prompts', 'version_registry', 'rendering', 'templates'], 'runtime': ['shared_runtime', 'environment_setup', 'shared', 'resource_management'], 'observability': ['metrics', 'telemetry', 'tracing', 'compliance'], 'utils': ['core_extensions', 'wrappers', 'general_helpers', 'naming'], 'patterns': ['agent_roles', 'communication_flow', 'interaction_patterns', 'reasoning_patterns'], 'semantic_memory': ['store', 'embeddings', 'retrieval', 'index'], 'knowledge': ['document_loaders', 'static_index', 'research_cache']}
apps_rg_subfolder_map: Any = {'logic_nodes': ['node_definitions', 'node_helpers'], 'asset_library': ['asset_definitions', 'asset_helpers'], 'system_flow': ['flow_definitions', 'flow_helpers'], 'engines': ['engine_definitions', 'engine_helpers'], 'templates': ['template_definitions', 'template_helpers']}
apps_lic_subfolder_map: Any = apps_rg_subfolder_map
apps_shared_subfolder_map: Any = {'base_definitions': ['definition_helpers', 'definition_types'], 'common_utils': ['utility_helpers', 'utility_types'], 'core_components': ['component_definitions', 'component_helpers'], 'base_agents': ['agent_definitions', 'agent_helpers'], 'models': ['model_definitions', 'model_helpers'], 'utils': ['utility_helpers', 'utility_types']}
tests_l2_subfolder_map: Any = {'unit': ['test_definitions', 'test_helpers'], 'integration': ['test_definitions', 'test_helpers'], 'e2e': ['test_definitions', 'test_helpers'], 'functional': ['test_definitions', 'test_helpers'], 'fixtures': ['fixture_definitions', 'fixture_helpers'], 'automation': ['automation_definitions', 'automation_helpers'], 'core': ['core_definitions', 'core_helpers'], 'data': ['data_definitions', 'data_helpers'], 'performance': ['performance_definitions', 'performance_helpers'], 'security': ['security_definitions', 'security_helpers']}
agentic_core_registry: Any = core_subfolder_map
tests_subfolder_map: Any = tests_l2_subfolder_map
CANON_SIGNALS: set[str] = {'agent', 'manager', 'engine', 'validator', 'healer', 'auditor', 'enforcer', 'detector', 'orchestrator', 'coordinator', 'pruner', 'mapper', 'handler', 'guardian', 'governor', 'sentinel', 'strategy', 'reasoning', 'fission', 'workflow', 'state', 'memory', 'cache', 'safety', 'guardrail', 'prompt', 'persona', 'schema', 'blueprint', 'template', 'context', 'ledger', 'historian', 'audit', 'coverage', 'vector', 'embedding', 'pinecone', 'redis', 'compliance', 'drift', 'hierarchy', 'span', 'depth', 'naming', 'rescue', 'integrity', 'gravity', 'subatomic', 'gemini'}

# === COMPREHENSIVE NAMING CONVENTIONS (SSOT) ===
# All naming rules for all file types in the repository

NAMING_CONVENTIONS: Dict[str, Dict[str, Any]] = {
    # Python Agent files - PascalCase, must end with Agent
    "agent": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*Agent\.py$",
        "description": "PascalCase ending with 'Agent'",
        "examples": ["HealerAgent.py", "NamingAgent.py", "CodeDeduplicationAgent.py"],
        "anti_examples": ["healer_agent.py", "naming_agent.py", "Healer.py"],
        "extensions": [".py"],
        "min_words": 2,  # At least 2 words (e.g., HealerAgent = Healer + Agent)
        "max_words": 4,  # Max 4 words (e.g., CodeDeduplicationAgent)
    },
    
    # Python scripts - snake_case, high-signal, 2-3 words
    "script": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){1,2}\.py$",
        "description": "snake_case with 2-3 words containing high-signal keyword",
        "examples": ["sovereign_ingestion.py", "canon_validator.py", "healing_strategies.py"],
        "anti_examples": ["utils.py", "helper.py", "main.py", "my_super_long_script_name.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 3,
        "require_signal": True,  # Must contain CANON_SIGNALS keyword
    },
    
    # Python core modules - snake_case, high-signal, 2-3 words
    "core_module": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){1,2}\.py$",
        "description": "snake_case with 2-3 words containing high-signal keyword",
        "examples": ["inference_engine.py", "hybrid_retriever.py", "semantic_cache.py"],
        "anti_examples": ["utils.py", "base.py", "core.py", "a_very_long_module_name_here.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 3,
        "require_signal": True,
    },
    
    # Python base classes - snake_case ending with _base
    "base_class": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+)*_base\.py$",
        "description": "snake_case ending with '_base'",
        "examples": ["outreach_base.py", "resume_base.py", "canon_base.py"],
        "anti_examples": ["base_agent.py", "BaseAgent.py", "base.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 3,
    },
    
    # Jinja templates - snake_case, descriptive, 2-3 words
    "jinja_template": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){1,2}\.(jinja|jinja2|j2)$",
        "description": "snake_case with 2-3 words",
        "examples": ["resume_template.jinja", "email_outreach.jinja2", "prompt_system.j2"],
        "anti_examples": ["template.jinja", "t.jinja", "my_super_long_template_name.jinja"],
        "extensions": [".jinja", ".jinja2", ".j2"],
        "min_words": 2,
        "max_words": 3,
    },
    
    # JSON config files - snake_case, descriptive, 2-3 words
    "json_config": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.json$",
        "description": "snake_case with 1-3 words",
        "examples": ["registry.json", "agent_config.json", "prompt_templates.json"],
        "anti_examples": ["data.json", "config.json", "a_very_long_config_name_here.json"],
        "extensions": [".json"],
        "min_words": 1,
        "max_words": 3,
    },
    
    # YAML config files - snake_case, descriptive, 2-3 words
    "yaml_config": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.(yaml|yml)$",
        "description": "snake_case with 1-3 words",
        "examples": ["config.yaml", "agent_registry.yml", "prompt_config.yaml"],
        "anti_examples": ["c.yaml", "a_very_long_config_name_here.yml"],
        "extensions": [".yaml", ".yml"],
        "min_words": 1,
        "max_words": 3,
    },
    
    # Markdown documentation - snake_case or SCREAMING_SNAKE for special files
    "markdown_doc": {
        "pattern": r"^([a-z][a-z0-9]*(_[a-z0-9]+){0,3}|[A-Z][A-Z0-9]*(_[A-Z0-9]+)*)\.md$",
        "description": "snake_case or SCREAMING_SNAKE_CASE",
        "examples": ["README.md", "CHANGELOG.md", "api_reference.md", "getting_started.md"],
        "anti_examples": ["doc.md", "a.md"],
        "extensions": [".md"],
        "min_words": 1,
        "max_words": 4,
    },
    
    # Text files - snake_case, descriptive
    "text_file": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.txt$",
        "description": "snake_case with 1-3 words",
        "examples": ["requirements.txt", "test_results.txt", "mission_audit.txt"],
        "anti_examples": ["t.txt", "a_very_long_text_file_name.txt"],
        "extensions": [".txt"],
        "min_words": 1,
        "max_words": 3,
    },
}

# File extensions that NamingAgent should validate
VALIDATED_FILE_EXTENSIONS: frozenset[str] = frozenset({
    # Python
    '.py',
    # Templates
    '.jinja', '.jinja2', '.j2',
    # Config
    '.json', '.yaml', '.yml', '.toml',
    # Documentation
    '.md', '.txt', '.rst',
    # Web
    '.html', '.css', '.js', '.ts',
})

# Files exempt from naming validation (infrastructure files)
NAMING_EXEMPT_FILES: frozenset[str] = frozenset({
    # Python infrastructure
    '__init__.py', '__main__.py', 'conftest.py', 'setup.py',
    # Config files
    'pyproject.toml', '.env', '.gitignore', '.dockerignore',
    'Dockerfile', 'Makefile', 'requirements.txt',
    # Documentation
    'README.md', 'CHANGELOG.md', 'LICENSE', 'LICENSE.md',
    'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
    # IDE/Editor
    '.editorconfig', '.prettierrc', '.eslintrc',
    # Git
    '.gitattributes',
})

# Directories exempt from naming validation
NAMING_EXEMPT_DIRS: frozenset[str] = frozenset({
    'archives', 'data', 'legacy_code', 'legacy_engines',
    '__pycache__', '.git', '.venv', 'venv', 'node_modules',
    '.pytest_cache', '.mypy_cache', 'coverage_html',
    'dist', 'build', '.tox', 'logs',
})
forbidden_patterns: Any = [re.compile('^utils\\.py$'), re.compile('^helper\\.py$'), re.compile('^temp\\.py$'), re.compile('.*_v\\d+\\.py$'), re.compile('^main\\.py$'), re.compile('^test\\.py$'), re.compile('.*_final\\.py$'), re.compile('.*_new\\.py$'), re.compile('.*_old\\.py$'), re.compile('.*_copy\\.py$'), re.compile('.*_backup\\.py$'), re.compile('^legacy_.*\\.py$'), re.compile('^.+_\\d+\\.py$'), re.compile('^draft_.*\\.py$')]
root_protected_files: Any = {'canon_validator_agentic_v2.py', 'canon_validator_agentic_v2_thin.py', 'pyproject.toml', 'README.md', 'langgraph.json', '.env', 'windsurfrules.md', '.gitignore'}
SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset({'.git', '.venv', 'venv', 'venv_stable', '__pycache__', '.pytest_cache', '.ruff_cache', 'node_modules', '.mypy_cache', '.tox', 'archives', 'legacy_code', 'legacy_engines', 'legacy_resume_gen', 'data', 'docs', 'env', 'build', 'dist', '_build', 'Lib', 'site-packages', 'google', 'gapic', 'logging', 'licenses', 'src', 'pip', 'dist-info', 'raw', 'golden_state', 'logs', 'processed', 'shared', 'refs', 'remotes', 'v', 'stubs', '.sovereign_healing_backup', '.idea', '.vscode', '.DS_Store', 'Thumbs.db'})
forbidden_folder_pattern: Any = re.compile('^\\d+_')
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset({'legacy_code', 'legacy_engines', 'legacy_resume_gen', 'old_core'})
TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset({'conftest.py', 'sovereign_smoke_test.py', 'test_autonomous_improvements.py'})
AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset({'autonomous_checkpoint_manager.py', 'autonomous_state_guardian.py', 'self_updating_safety_engine.py', 'neural_auto_immune_agent.py'})
protected_folders: Any = SOVEREIGN_EXCLUDED_FOLDERS
ignore_dirs: Any = SOVEREIGN_EXCLUDED_FOLDERS
sovereign_ignored_folders: Any = SOVEREIGN_EXCLUDED_FOLDERS
healing_config: Any = {
    "max_rounds": int(os.getenv('MAX_HEALING_ROUNDS', '10')),
    "max_per_file": int(os.getenv('MAX_HEALING_PER_FILE', '8')),
    "global_budget": int(os.getenv('GLOBAL_HEALING_BUDGET', '500')),  # [TEMP BOOST] Unblock 10k violation backlog
    "max_moves_per_run": 250,      # New constraint for Key 15 volume
    "max_fissions_per_run": 50,     # Prevent file system explosion
    "dust_threshold": 40            # Minimum lines for a module to exist (Span-of-Two)
}
agent_resilience_config: Any = {'retry_count': int(os.getenv('AGENT_RETRY_COUNT', '3')), 'backoff_base': float(os.getenv('AGENT_RETRY_BACKOFF_BASE', '0.5'))}
mission_config: Any = {'gravity_surgery_enabled': True, 'hierarchy_healing_enabled': True, 'span_surgery_enabled': True, 'fission_enabled': True, 'run_full_mission': True, 'run_hierarchy_healing': True, 'run_gravity_refactor': True, 'run_sprawl_surgery': True, 'structural_only_mode': False, 'timeout_seconds': int(os.getenv('MISSION_TIMEOUT_SECONDS', '1800'))}
mcp_capabilities: Any = {'router': {'enabled': True, 'path': 'agentic_core.L3_orchestration.mcp'}, 'marketplace_filter': {'enabled': True, 'path': 'agentic_core.L3_orchestration.mcp'}, 'filesystem': {'enabled': True, 'path': 'agentic_core.L4_state.filesystem'}, 'figma': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'}, 'fetch': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'}, 'semantic_cache': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'}}
SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({'stubs', '.sovereign_healing_backup', '__pycache__'})

# === ALLOWED DUPLICATE FILENAMES ===
# These files are permitted to exist with the same name across multiple directories.
# This is the SSOT for filename uniqueness exceptions - all agents must respect this list.
ALLOWED_DUPLICATE_FILENAMES: frozenset[str] = frozenset({
    # Python package infrastructure (MUST exist in every package)
    '__init__.py',
    '__main__.py',
    
    # Testing infrastructure (pytest requires these in test directories)
    'conftest.py',
    
    # Common module patterns (legitimate per-package definitions)
    'context.py',
    'config.py',
    'constants.py',
    'exceptions.py',
    'types.py',
    'models.py',
    'base.py',
    'utils.py',
    'helpers.py',
    'common.py',
    
    # Observability patterns (per-engine instrumentation)
    'observability.py',
    'metrics.py',
    'logging.py',
    'tracing.py',
    
    # Autonomous agent patterns (per-engine autonomy)
    'proactive.py',
    'autonomous.py',
    'self_healing.py',
    
    # Prompt patterns (per-domain prompts)
    'prompts.py',
    'templates.py',
})


def safe_prefixed_filename(prefix: str, filename: str) -> str:
    """
    SSOT safeguard: Generate a prefixed filename WITHOUT duplicate prefixes.
    
    Prevents name sprawl like:
        healing_strategies.py -> healing_healing_strategies.py (BAD)
        
    Instead produces:
        healing_strategies.py -> healing_strategies.py (already has prefix)
        strategies.py -> healing_strategies.py (prefix added)
    
    Args:
        prefix: The prefix to add (e.g., 'healing', 'auditors')
        filename: The original filename
        
    Returns:
        Filename with prefix added only if not already present
    """
    if not prefix:
        return filename
    
    # Normalize prefix (remove trailing underscore if present)
    prefix = prefix.rstrip('_')
    
    # Check if filename already starts with the prefix
    stem = filename.rsplit('.', 1)[0] if '.' in filename else filename
    suffix = '.' + filename.rsplit('.', 1)[1] if '.' in filename else ''
    
    # If already has prefix, return unchanged
    if stem.startswith(prefix + '_') or stem == prefix:
        return filename
    
    # Add prefix
    return f"{prefix}_{filename}"


def validate_no_duplicate_prefix(filename: str) -> tuple[bool, str]:
    """
    SSOT safeguard: Detect if a filename has duplicate prefixes.
    
    Examples of violations:
        healing_healing_strategies.py -> True, "Duplicate prefix: healing_"
        auditors_auditors_report.py -> True, "Duplicate prefix: auditors_"
        
    Returns:
        (has_violation, message)
    """
    stem = filename.rsplit('.', 1)[0] if '.' in filename else filename
    parts = stem.split('_')
    
    # Check for consecutive duplicate parts
    for i in range(len(parts) - 1):
        if parts[i] == parts[i + 1] and parts[i]:  # Non-empty consecutive duplicates
            return True, f"Duplicate prefix detected: '{parts[i]}_' repeated in '{filename}'"
    
    return False, ""
DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset({'runtime_shared', 'legacy_code', 'legacy_engines', 'archives', 'stubs', 'examples'})
PYTHON_STDLIB_MODULES: frozenset[str] = frozenset({'os', 'sys', 'pathlib', 'logging', 'asyncio', 'typing', 'dataclasses', 'collections', 'json', 're', 'datetime', 'functools', 'itertools', 'abc', 'enum', 'contextlib', 'threading', 'time', 'random', 'math', 'urllib', 'http', 'socket', 'subprocess', 'shutil', 'hashlib', 'uuid', 'copy', 'io', 'traceback', 'inspect', 'importlib', 'warnings', 'pickle'})
ROOT_WHITELIST: set[str] = set(sovereign_registry.keys())
gravity_config: Any = {'enabled': True, 'upstream_sovereign_roots': ['agentic_core'], 'downstream_domains': ['apps_rg', 'apps_lic', 'apps_shared', 'tests'], 'exemptions': []}
gravity_surgery_enabled: Any = gravity_config['enabled']
upstream_sovereign_roots: Any = frozenset(gravity_config['upstream_sovereign_roots'])
downstream_roots: Any = frozenset(gravity_config['downstream_domains'])
_semantic_templates = {'node_pattern': {'entity_types': ['Class'], 'examples_suffix': ['Node', 'ExtractNode', 'DraftNode']}, 'flow_pattern': {'entity_types': ['Class'], 'bases': ['BaseFlow'], 'examples_suffix': ['Flow', 'Pipeline', 'Campaign']}, 'engine_pattern': {'entity_types': ['Class'], 'bases': ['BaseEngine'], 'examples_suffix': ['Engine', 'Builder', 'Driver']}, 'template_pattern': {'entity_types': ['Class', 'Dict'], 'bases': ['BaseTemplate'], 'examples_suffix': ['Template', 'Layout', 'Format']}}
# === AST PLACEMENT SIGNAL REGISTRY ===
# Maps AST patterns to exact L1/L2 paths for file placement
# This is the SSOT for AST-based file placement decisions
AST_PLACEMENT_SIGNALS: Dict[str, Dict[str, Any]] = {
    # L1_cognition placements
    "agentic_core/L1_cognition/thought_engine": {
        "class_patterns": [".*Node$", ".*Thought.*", ".*Reason.*", ".*Chain.*"],
        "base_classes": ["BaseNode", "ThoughtNode", "ReActNode"],
        "function_patterns": ["think_.*", "reason_.*", "decompose_.*"],
        "import_signals": ["langchain", "langgraph", "thought_engine"],
        "keyword_signals": ["thought", "reasoning", "decomposition", "chain_of_thought", "react"],
        "decorator_signals": ["@thought_node", "@reasoning_step"],
        "weight": 10,  # High confidence signal
    },
    "agentic_core/L1_cognition/intent_analysis": {
        "class_patterns": [".*Intent.*", ".*Parser.*", ".*Classifier.*"],
        "base_classes": ["IntentClassifier", "QueryParser"],
        "function_patterns": ["parse_intent.*", "classify_.*", "extract_intent.*"],
        "import_signals": ["intent", "classification"],
        "keyword_signals": ["intent", "classify", "parse", "extract", "query"],
        "weight": 8,
    },
    "agentic_core/L1_cognition/planning": {
        "class_patterns": [".*Planner.*", ".*Strategy.*", ".*Plan.*"],
        "base_classes": ["BasePlanner", "StrategyPlanner"],
        "function_patterns": ["plan_.*", "strategize_.*", "decompose_task.*"],
        "import_signals": ["planning", "strategy"],
        "keyword_signals": ["planner", "strategy", "plan", "goal", "objective"],
        "weight": 8,
    },
   
    # L2_execution placements
    "agentic_core/L2_execution/tool_registry": {
        "class_patterns": [".*Agent$", ".*Tool$", ".*Handler$"],
        "base_classes": ["SubAtomicAgent", "BaseTool", "ToolHandler"],
        "function_patterns": ["execute_.*", "run_tool.*", "invoke_.*"],
        "import_signals": ["tool_registry", "SubAtomicAgent"],
        "keyword_signals": ["tool", "execute", "invoke", "action", "handler"],
        "decorator_signals": ["@tool", "@action"],
        "weight": 9,
    },
    "agentic_core/L2_execution/action_handlers": {
        "class_patterns": [".*ActionHandler$", ".*Executor$"],
        "base_classes": ["ActionHandler", "BaseExecutor"],
        "function_patterns": ["handle_action.*", "execute_action.*"],
        "import_signals": ["action_handlers"],
        "keyword_signals": ["action", "handler", "execute", "perform"],
        "weight": 7,
    },
    "agentic_core/L2_execution/mcp": {
        "class_patterns": [".*MCP.*", ".*Client$", ".*Server$"],
        "base_classes": ["MCPClient", "MCPServer"],
        "function_patterns": ["mcp_.*", "fetch_.*", "connect_.*"],
        "import_signals": ["mcp", "model_context_protocol"],
        "keyword_signals": ["mcp", "model_context_protocol", "fetch", "client", "server"],
        "weight": 9,
    },
   
    # L3_orchestration placements
    "agentic_core/L3_orchestration/workflow_engines": {
        "class_patterns": [".*Engine$", ".*Orchestrator$", ".*Controller$", ".*Coordinator$"],
        "base_classes": ["BaseEngine", "WorkflowEngine", "Orchestrator"],
        "function_patterns": ["orchestrate_.*", "coordinate_.*", "run_workflow.*"],
        "import_signals": ["workflow_engines", "orchestration"],
        "keyword_signals": ["orchestrator", "workflow", "engine", "coordinate", "mission", "controller"],
        "decorator_signals": ["@workflow", "@orchestrate"],
        "weight": 10,
    },
    "agentic_core/L3_orchestration/fission_logic": {
        "class_patterns": [".*Fission.*", ".*Split.*", ".*Decompose.*"],
        "base_classes": ["FissionEngine", "TaskSplitter"],
        "function_patterns": ["fission_.*", "split_.*", "decompose_.*"],
        "import_signals": ["fission_logic"],
        "keyword_signals": ["fission", "split", "decompose", "parallel", "distribute"],
        "weight": 8,
    },
    "agentic_core/L3_orchestration/meta_learning": {
        "class_patterns": [".*MetaLearn.*", ".*Adaptive.*", ".*SelfImprove.*"],
        "base_classes": ["MetaLearner", "AdaptiveAgent"],
        "function_patterns": ["meta_learn.*", "adapt_.*", "self_improve.*"],
        "import_signals": ["meta_learning"],
        "keyword_signals": ["meta", "learning", "adaptive", "self_improve", "evolve"],
        "weight": 7,
    },
   
    # L4_state placements
    "agentic_core/L4_state/validation_context": {
        "class_patterns": [".*Context.*", ".*State.*", ".*Session.*"],
        "base_classes": ["ValidationContext", "StateManager"],
        "function_patterns": ["get_context.*", "set_state.*", "validate_context.*"],
        "import_signals": ["validation_context"],
        "keyword_signals": ["context", "state", "session", "validation"],
        "weight": 8,
    },
    "agentic_core/L4_state/ledger": {
        "class_patterns": [".*Ledger.*", ".*Audit.*", ".*Log.*", ".*Historian.*"],
        "base_classes": ["BaseLedger", "AuditLog"],
        "function_patterns": ["log_.*", "record_.*", "audit_.*"],
        "import_signals": ["ledger"],
        "keyword_signals": ["ledger", "audit", "log", "record", "historian", "trail"],
        "weight": 8,
    },
    "agentic_core/L4_state/memory": {
        "class_patterns": [".*Memory.*", ".*Cache.*", ".*Store.*"],
        "base_classes": ["MemoryStore", "CacheManager"],
        "function_patterns": ["store_.*", "retrieve_.*", "cache_.*"],
        "import_signals": ["pinecone", "redis", "memory"],
        "keyword_signals": ["memory", "cache", "store", "retrieve", "embedding", "vector"],
        "weight": 9,
    },
   
    # L5_safety placements
    "agentic_core/L5_safety/guardrails": {
        "class_patterns": [".*Guardrail.*", ".*Limit.*", ".*Throttle.*", ".*Healer.*"],
        "base_classes": ["BaseGuardrail", "RateLimiter", "CircuitBreaker"],
        "function_patterns": ["guard_.*", "limit_.*", "throttle_.*", "heal_.*"],
        "import_signals": ["guardrails", "safety"],
        "keyword_signals": ["guardrail", "safety", "limit", "throttle", "heal", "circuit", "breaker"],
        "decorator_signals": ["@guardrail", "@rate_limit"],
        "weight": 10,
    },
    "agentic_core/L5_safety/validators": {
        "class_patterns": [".*Validator.*", ".*Enforcer.*", ".*Checker.*", ".*Agent$"],
        "base_classes": ["BaseValidator", "Enforcer"],
        "function_patterns": ["validate_.*", "enforce_.*", "check_.*"],
        "import_signals": ["validators", "compliance"],
        "keyword_signals": ["validator", "enforce", "compliance", "check", "verify", "audit"],
        "weight": 9,
    },
    "agentic_core/L5_safety/gravity": {
        "class_patterns": [".*Gravity.*", ".*Import.*", ".*Waterfall.*"],
        "base_classes": ["GravityEnforcer", "ImportValidator"],
        "function_patterns": ["check_gravity.*", "validate_import.*"],
        "import_signals": ["gravity"],
        "keyword_signals": ["gravity", "import", "waterfall", "upstream", "downstream"],
        "weight": 8,
    },
    "agentic_core/L5_safety/red_teaming": {
        "class_patterns": [".*RedTeam.*", ".*Adversarial.*", ".*Attack.*"],
        "base_classes": ["RedTeamAgent", "AdversarialTester"],
        "function_patterns": ["attack_.*", "probe_.*", "fuzz_.*"],
        "import_signals": ["red_teaming"],
        "keyword_signals": ["redteam", "adversarial", "attack", "probe", "jailbreak", "exploit"],
        "weight": 8,
    },
   
    # Utils placements
    "agentic_core/utils/core_extensions": {
        "class_patterns": [".*Extension.*", ".*Mixin.*", ".*Helper.*"],
        "base_classes": ["ExtensionMixin"],
        "function_patterns": ["extend_.*", "enhance_.*"],
        "import_signals": ["core_extensions"],
        "keyword_signals": ["extension", "mixin", "enhance", "utility"],
        "weight": 6,
    },
    "agentic_core/utils/naming": {
        "class_patterns": [".*Naming.*", ".*Case.*"],
        "base_classes": [],
        "function_patterns": ["to_snake_case.*", "to_pascal_case.*", "validate_name.*"],
        "import_signals": ["naming"],
        "keyword_signals": ["naming", "snake_case", "pascal_case", "case", "convention"],
        "weight": 7,
    },
   
    # Observability placements
    "agentic_core/observability/metrics": {
        "class_patterns": [".*Metric.*", ".*Counter.*", ".*Gauge.*"],
        "base_classes": ["MetricCollector"],
        "function_patterns": ["collect_metric.*", "record_.*", "measure_.*"],
        "import_signals": ["prometheus", "metrics"],
        "keyword_signals": ["metric", "counter", "gauge", "measure", "telemetry"],
        "weight": 7,
    },
    "agentic_core/observability/tracing": {
        "class_patterns": [".*Tracer.*", ".*Span.*"],
        "base_classes": ["Tracer", "SpanContext"],
        "function_patterns": ["trace_.*", "start_span.*"],
        "import_signals": ["opentelemetry", "tracing"],
        "keyword_signals": ["trace", "span", "opentelemetry", "jaeger"],
        "weight": 7,
    },
    "agentic_core/observability/compliance": {
        "class_patterns": [".*Compliance.*", ".*Report.*"],
        "base_classes": ["ComplianceReporter"],
        "function_patterns": ["report_.*", "generate_compliance.*"],
        "import_signals": ["compliance"],
        "keyword_signals": ["compliance", "report", "audit", "coverage"],
        "weight": 7,
    },
   
    # Schemas placements
    "agentic_core/schemas/models": {
        "class_patterns": [".*Model$", ".*Schema$", ".*DTO$"],
        "base_classes": ["BaseModel", "pydantic.BaseModel"],
        "function_patterns": [],
        "import_signals": ["pydantic", "dataclasses"],
        "keyword_signals": ["model", "schema", "dto", "dataclass"],
        "decorator_signals": ["@dataclass"],
        "weight": 9,
    },
   
    # Prompt governance placements
    "agentic_core/prompt_governance/templates": {
        "class_patterns": [".*Template.*", ".*Prompt.*"],
        "base_classes": ["PromptTemplate"],
        "function_patterns": ["render_prompt.*", "format_template.*"],
        "import_signals": ["jinja2", "prompt_governance"],
        "keyword_signals": ["prompt", "template", "jinja", "render"],
        "decorator_signals": ["@registers_prompt"],
        "weight": 8,
    },
    "agentic_core/prompt_governance/meta_prompts": {
        "class_patterns": [".*MetaPrompt.*", ".*SystemPrompt.*"],
        "base_classes": ["MetaPrompt"],
        "function_patterns": ["generate_meta_prompt.*"],
        "import_signals": ["meta_prompts"],
        "keyword_signals": ["meta_prompt", "system_prompt", "persona"],
        "weight": 7,
    },
}

# === PLACEMENT CONFIDENCE THRESHOLDS ===
PLACEMENT_CONFIDENCE = {
    "HIGH": 0.8,      # Auto-move without confirmation
    "MEDIUM": 0.5,    # Suggest move, require confirmation
    "LOW": 0.3,       # Log suggestion only
    "REJECT": 0.0,    # Cannot determine placement
}

# === REVERSE LOOKUP: L2 -> L1 MAPPING ===
# For quick parent resolution
L2_TO_L1_MAP: Dict[str, str] = {
    "thought_engine": "L1_cognition",
    "intent_analysis": "L1_cognition",
    "planning": "L1_cognition",
    "tool_registry": "L2_execution",
    "action_handlers": "L2_execution",
    "mcp": "L2_execution",
    "workflow_engines": "L3_orchestration",
    "fission_logic": "L3_orchestration",
    "meta_learning": "L3_orchestration",
    "S3_vitality": "L3_orchestration",
    "validation_context": "L4_state",
    "ledger": "L4_state",
    "memory": "L4_state",
    "filesystem": "L4_state",
    "guardrails": "L5_safety",
    "validators": "L5_safety",
    "gravity": "L5_safety",
    "red_teaming": "L5_safety",
    "core_extensions": "utils",
    "naming": "utils",
    "wrappers": "utils",
    "general_helpers": "utils",
    "metrics": "observability",
    "tracing": "observability",
    "telemetry": "observability",
    "compliance": "observability",
    "models": "schemas",
    "messages": "schemas",
    "types": "schemas",
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "blueprint_sovereign": "config",
    "environments": "config",
    "feature_flags": "config",
    "scripts": "L0_maintenance",
    "logs": "L0_maintenance",
    "benchmarks": "L0_maintenance",
}

# === UPPERCASE ALIASES FOR BACKWARD COMPATIBILITY ===
SOVEREIGN_REGISTRY = sovereign_registry
CORE_SUBFOLDER_MAP = core_subfolder_map
APPS_RG_SUBFOLDER_MAP = apps_rg_subfolder_map
APPS_LIC_SUBFOLDER_MAP = apps_lic_subfolder_map
APPS_SHARED_SUBFOLDER_MAP = apps_shared_subfolder_map
TESTS_SUBFOLDER_MAP = tests_subfolder_map
TESTS_L2_SUBFOLDER_MAP = tests_l2_subfolder_map
FORBIDDEN_PATTERNS = forbidden_patterns
ROOT_PROTECTED_FILES = root_protected_files
FORBIDDEN_FOLDER_PATTERN = forbidden_folder_pattern
ACTIVE_CANON_KEYS = active_canon_keys
HEALING_CONFIG = healing_config
AGENT_RESILIENCE_CONFIG = agent_resilience_config
MISSION_CONFIG = mission_config
MCP_CAPABILITIES = mcp_capabilities
GRAVITY_CONFIG = gravity_config
GRAVITY_SURGERY_ENABLED = gravity_surgery_enabled
UPSTREAM_SOVEREIGN_ROOTS = upstream_sovereign_roots
DOWNSTREAM_ROOTS = downstream_roots

# [PHASE 17] AGENT REGISTRY - Complete PascalCase Agent Discovery Map
# Generated from AST analysis - 64 total agents across all layers
agent_registry: Any = {"L0": [{"name": "BootstrapAgent", "file": "agentic_core/L0_maintenance/scripts/BootstrapAgent.py", "methods": 6, "fingerprint": "fcfd5e27416abb4c"}], "L1": [{"name": "CanonBaseAgent", "file": "agentic_core/L1_cognition/thought_engine/CognitionCanonBaseAgent.py", "methods": 8, "fingerprint": "ea8e7e56381918dc"}, {"name": "DependencySentinelAgent", "file": "agentic_core/L1_cognition/thought_engine/DependencySentinelAgent.py", "methods": 9, "fingerprint": "3773a3e6e7e65f7d"}, {"name": "GovernanceAgent", "file": "agentic_core/L1_cognition/thought_engine/GovernanceAgent.py", "methods": 12, "fingerprint": "3bab1afa3cbc06ee"}, {"name": "MetaLearningAgent", "file": "agentic_core/L1_cognition/thought_engine/MetaLearningAgent.py", "methods": 6, "fingerprint": "da27f331da4c5e37"}, {"name": "ReflectionAgent", "file": "agentic_core/L1_cognition/thought_engine/ReflectionAgent.py", "methods": 9, "fingerprint": "c58961965bf91d5c"}], "L2": [{"name": "CanonBaseAgent", "file": "agentic_core/L2_execution/tool_registry/ExecutionCanonBaseAgent.py", "methods": 13, "fingerprint": "00b4b4376214468b"}, {"name": "CodeDeduplicationAgent", "file": "agentic_core/L2_execution/tool_registry/CodeDeduplicationAgent.py", "methods": 11, "fingerprint": "1c26bf7b92ef3fb8"}, {"name": "CodeJanitorAgent", "file": "agentic_core/L2_execution/tool_registry/CodeJanitorAgent.py", "methods": 12, "fingerprint": "ae825674e1abeb55"}, {"name": "ContextCuratorAgent", "file": "agentic_core/L2_execution/tool_registry/ContextCuratorAgent.py", "methods": 13, "fingerprint": "b55bbeb3cc150054"}, {"name": "DependencyDiplomatAgent", "file": "agentic_core/L2_execution/tool_registry/DependencyDiplomatAgent.py", "methods": 11, "fingerprint": "15bc567d77279e31"}, {"name": "DynamicModelRouterAgent", "file": "agentic_core/L2_execution/tool_registry/DynamicModelRouterAgent.py", "methods": 11, "fingerprint": "e6532e4040366631"}, {"name": "GitAgent", "file": "agentic_core/L2_execution/tool_registry/GitAgent.py", "methods": 12, "fingerprint": "82c9b049e6fd5597"}, {"name": "IntegrityGateExecutorAgent", "file": "agentic_core/L2_execution/tool_registry/IntegrityGateExecutorAgent.py", "methods": 8, "fingerprint": "cc6465bde4266c9f"}, {"name": "MemoryArchitectAgent", "file": "agentic_core/L2_execution/tool_registry/MemoryArchitectAgent.py", "methods": 13, "fingerprint": "b07bc5ecfbb20791"}, {"name": "SovereignActionPlaneAgent", "file": "agentic_core/L2_execution/tool_registry/SovereignActionPlaneAgent.py", "methods": 11, "fingerprint": "91faa15364d0a1a5"}, {"name": "StructuralEngineerAgent", "file": "agentic_core/L2_execution/tool_registry/StructuralEngineerAgent.py", "methods": 8, "fingerprint": "37d55e1531ee303e"}, {"name": "SystemArchitectAgent", "file": "agentic_core/L2_execution/tool_registry/SystemArchitectAgent.py", "methods": 8, "fingerprint": "e340d23c73eb4451"}, {"name": "ToolsmithAgent", "file": "agentic_core/L2_execution/tool_registry/ToolsmithAgent.py", "methods": 17, "fingerprint": "920d8dc7ea2d38d4"}], "L3": [{"name": "DagEngineAgent", "file": "agentic_core/L3_orchestration/workflow_engines/DagEngineAgent.py", "methods": 14, "fingerprint": "e58f4699d9aa84e5"}, {"name": "MockAgent", "file": "agentic_core/L3_orchestration/workflow_engines/NervousSystemAgent.py", "methods": 2, "fingerprint": "b644392cf05e5442"}, {"name": "NervousSystemAgent", "file": "agentic_core/L3_orchestration/workflow_engines/NervousSystemAgent.py", "methods": 12, "fingerprint": "c3a187f4f4fd9eeb"}, {"name": "SemanticGatekeeperAgent", "file": "agentic_core/L3_orchestration/workflow_engines/SemanticGatekeeperAgent.py", "methods": 6, "fingerprint": "40da7e8727c03cdc"}, {"name": "SubatomicHopAgent", "file": "agentic_core/L3_orchestration/workflow_engines/SubatomicHopAgent.py", "methods": 14, "fingerprint": "7c2a442208c79cd7"}, {"name": "TestPilotAgent", "file": "agentic_core/L3_orchestration/workflow_engines/TestPilotAgent.py", "methods": 15, "fingerprint": "5948ee871695c65f"}], "L4": [{"name": "AutonomousCheckpointManagerAgent", "file": "agentic_core/L4_state/validation_context/AutonomousCheckpointManagerAgent.py", "methods": 13, "fingerprint": "41e505612b995ed9"}, {"name": "AutonomousStateGuardianAgent", "file": "agentic_core/L4_state/validation_context/AutonomousStateGuardianAgent.py", "methods": 10, "fingerprint": "5ebb94cbbdf1aa58"}, {"name": "PineconeSovereignAgent", "file": "agentic_core/L4_state/validation_context/PineconeSovereignAgent.py", "methods": 12, "fingerprint": "4dd0d1e4b0e3e220"}, {"name": "RedisSovereignAgent", "file": "agentic_core/L4_state/validation_context/RedisSovereignAgent.py", "methods": 6, "fingerprint": "b040e351f725cddb"}, {"name": "SchemaEvolverAgent", "file": "agentic_core/L4_state/validation_context/SchemaEvolverAgent.py", "methods": 14, "fingerprint": "895c1f48e33df32e"}, {"name": "SovereignPineconeStoreAgent", "file": "agentic_core/L4_state/validation_context/SovereignPineconeStoreAgent.py", "methods": 10, "fingerprint": "f441583d3a2a4cd2"}, {"name": "SubAtomicRegistryAgent", "file": "agentic_core/L4_state/validation_context/SubAtomicRegistryAgent.py", "methods": 7, "fingerprint": "78801bbc67f74db4"}], "L5": [{"name": "AdversarialRedTeamerAgent", "file": "agentic_core/L5_safety/guardrails/AdversarialRedTeamerAgent.py", "methods": 24, "fingerprint": "f7b28e4a681e38f8"}, {"name": "AutonomousThreatEvolutionAgent", "file": "agentic_core/L5_safety/guardrails/AutonomousThreatEvolutionAgent.py", "methods": 11, "fingerprint": "c181817ddf232911"}, {"name": "DocstringComplianceAgent", "file": "agentic_core/L5_safety/validators/DocstringComplianceAgent.py", "methods": 3, "fingerprint": "667c2361a762cd69"}, {"name": "FilenameUniquenessGuardianAgent", "file": "agentic_core/L5_safety/validators/FilenameUniquenessGuardianAgent.py", "methods": 5, "fingerprint": "823711cf0f58b0ff"}, {"name": "FilesystemAgent", "file": "agentic_core/L5_safety/validators/FilesystemAgent.py", "methods": 6, "fingerprint": "404bc60482eb1646"}, {"name": "GravityLeakRepairAgent", "file": "agentic_core/L5_safety/gravity/GravityLeakRepairAgent.py", "methods": 3, "fingerprint": "51dbad0a31ea9c72"}, {"name": "HallucinationHunterAgent", "file": "agentic_core/L5_safety/guardrails/HallucinationHunterAgent.py", "methods": 9, "fingerprint": "88a8355c3b923aa1"}, {"name": "HealerAgent", "file": "agentic_core/L5_safety/guardrails/HealerAgent.py", "methods": 14, "fingerprint": "f7be54e968a04313"}, {"name": "HierarchyAgent", "file": "agentic_core/L5_safety/validators/HierarchyAgent.py", "methods": 14, "fingerprint": "c4ba74a74c6e27d2"}, {"name": "HygieneGuardianAgent", "file": "agentic_core/L5_safety/validators/HygieneGuardianAgent.py", "methods": 4, "fingerprint": "3aa2327dde094b31"}, {"name": "ImportAgent", "file": "agentic_core/L5_safety/gravity/ImportAgent.py", "methods": 7, "fingerprint": "f1dad62889a51085"}, {"name": "InferenceTypeHintAgent", "file": "agentic_core/L5_safety/validators/InferenceTypeHintAgent.py", "methods": 3, "fingerprint": "0fd4fbfb4402be61"}, {"name": "L5IntegrityGateExecutorAgent", "file": "agentic_core/L5_safety/guardrails/L5IntegrityGateExecutorAgent.py", "methods": 17, "fingerprint": "790a1b648be58757"}, {"name": "LocationAgent", "file": "agentic_core/L5_safety/validators/LocationAgent.py", "methods": 9, "fingerprint": "5e49cfc8aebe839e"}, {"name": "NeuralAutoImmuneAgent", "file": "agentic_core/L5_safety/guardrails/NeuralAutoImmuneAgent.py", "methods": 3, "fingerprint": "78dc1bb327996dcf"}, {"name": "RedTeamAgent", "file": "agentic_core/L5_safety/red_teaming/RedTeamAgent.py", "methods": 3, "fingerprint": "d76f6932c53b7a77"}, {"name": "RegressionOracleAgent", "file": "agentic_core/L5_safety/validators/RegressionOracleAgent.py", "methods": 4, "fingerprint": "65c42eea1de011b7"}, {"name": "SSOTRefactorAgent", "file": "agentic_core/L5_safety/validators/SSOTRefactorAgent.py", "methods": 4, "fingerprint": "29f31ace7a8982fb"}, {"name": "SelfUpdatingSafetyEngineAgent", "file": "agentic_core/L5_safety/guardrails/SelfUpdatingSafetyEngineAgent.py", "methods": 14, "fingerprint": "ce122c5e1c1fe306"}, {"name": "TerritoryHealerAgent", "file": "agentic_core/L5_safety/guardrails/TerritoryHealerAgent.py", "methods": 7, "fingerprint": "6fdffa7306e70169"}, {"name": "TypeHintEnforcementAgent", "file": "agentic_core/L5_safety/validators/TypeHintEnforcementAgent.py", "methods": 3, "fingerprint": "9bf27471e887b95c"}], "L6-OBS": [{"name": "BenchmarkingAgent", "file": "agentic_core/observability/metrics/BenchmarkingAgent.py", "methods": 14, "fingerprint": "aaccf245087d7b9a"}, {"name": "CoordinateObservabilityOperationsAgent", "file": "agentic_core/observability/metrics/CoordinateObservabilityOperationsAgent.py", "methods": 3, "fingerprint": "b79b37e264d36fb5"}, {"name": "MetricsAgent", "file": "agentic_core/observability/metrics/MetricsAgent.py", "methods": 14, "fingerprint": "c857ceb2e36799b9"}, {"name": "PredictiveCostAuditorAgent", "file": "agentic_core/observability/metrics/PredictiveCostAuditorAgent.py", "methods": 12, "fingerprint": "8ef66dd746dd7e50"}, {"name": "ReportingAgent", "file": "agentic_core/observability/compliance/ReportingAgent.py", "methods": 5, "fingerprint": "2c9e248f2f70804b"}, {"name": "SignatureVerifierAgent", "file": "agentic_core/observability/metrics/SignatureVerifierAgent.py", "methods": 3, "fingerprint": "60824e83630f2650"}, {"name": "TelemetryAgent", "file": "agentic_core/observability/telemetry/TelemetryAgent.py", "methods": 11, "fingerprint": "d026b54bad957126"}, {"name": "TracingAgent", "file": "agentic_core/observability/tracing/TracingAgent.py", "methods": 15, "fingerprint": "8c951c49ffa5b5ed"}, {"name": "TrackObservabilityCostAgent", "file": "agentic_core/observability/metrics/TrackObservabilityCostAgent.py", "methods": 3, "fingerprint": "15b577bc8c1d7075"}], "UTILS": [{"name": "NamingAgent", "file": "agentic_core/utils/naming/NamingAgent.py", "methods": 13, "fingerprint": "27645aed97c3aa01"}, {"name": "NamingNormalizationAgent", "file": "agentic_core/utils/naming/NamingNormalizationAgent.py", "methods": 4, "fingerprint": "e09b6daa7f5988eb"}]}
AGENT_REGISTRY = agent_registry

semantic_l2_registry: Any = {'L5_safety': {'guardrails': {'purpose': 'Hard safety limits, mutation controls, deletion guards, circuit breakers, rate limits, throttling, and emergency stop mechanisms', 'entity_types': ['Class'], 'keywords': ['guardrail', 'safety', 'limit', 'constraint', 'circuit', 'breaker', 'throttle', 'rate', 'quota', 'mutate', 'delete', 'emergency', 'stop', 'block', 'prevent'], 'imports': ['agentic_core.L5_safety.guardrails'], 'bases': ['BaseGuardrail', 'safety_guardrail', 'CircuitBreaker', 'RateLimiter'], 'examples': ['MutationGuardrail', 'DeletionGuardrail', 'RateLimitGuardrail', 'EmergencyStopGuardrail', 'ContentFilterGuardrail']}, 'red_teaming': {'purpose': 'Adversarial testing agents, automated threat simulation, exploit probing, jailbreak attempts, prompt injection testing, and attack vector generation', 'entity_types': ['Class', 'Function'], 'keywords': ['redteam', 'red_team', 'adversary', 'adversarial', 'attack', 'exploit', 'probe', 'jailbreak', 'threat', 'simulate', 'fuzz', 'injection', 'poison'], 'imports': ['agentic_core.L5_safety.red_teaming'], 'bases': ['RedTeamAgent', 'AdversarialAgent', 'ThreatSimulator'], 'examples': ['JailbreakProber', 'PromptInjectionAttacker', 'ThreatSimulator', 'AdversarialFuzzer', 'ExploitGenerator']}, 'gravity': {'purpose': 'Import waterfall enforcement, dependency direction control, layer authority validation, gravity surgery execution, and upstream/downstream violation detection', 'entity_types': ['Class', 'Function'], 'keywords': ['gravity', 'waterfall', 'import', 'dependency', 'direction', 'layer', 'authority', 'upstream', 'downstream', 'violation', 'enforce', 'surgery'], 'imports': ['agentic_core.L5_safety.gravity', 'agentic_core.runtime.shared_runtime.void_compliance'], 'bases': ['GravityEnforcer', 'WaterfallValidator'], 'examples': ['GravityValidator', 'ImportWaterfallChecker', 'DependencyDirectionGuard', 'GravitySurgeryEngine', 'LayerAuthorityAuditor']}, 'validators': {'purpose': 'Canon constitution validators, structural policy enforcement, naming law validation, runtime compliance auditing, and architectural drift detection', 'entity_types': ['Class'], 'keywords': ['validator', 'canon', 'constitution', 'rule', 'policy', 'enforce', 'compliance', 'audit', 'drift', 'naming', 'law', 'check', 'verify'], 'imports': ['agentic_core.L5_safety.validators', 'structure_blueprint'], 'bases': ['CanonBaseAgent', 'KeyValidator', 'StructureValidator', 'ComplianceAuditor', 'DriftDetector'], 'examples': ['CanonKeyValidator', 'NamingLawValidator', 'DepthValidator', 'GravityComplianceValidator', 'StructuralPolicyValidator', 'RuntimeComplianceAuditor']}}, 'L0_maintenance': {'scripts': {'purpose': 'Autonomous healing scripts, checkpoint management, self-updating systems, neural immune agents, and sovereign improvement missions', 'entity_types': ['Class', 'Function'], 'keywords': ['autonomous', 'heal', 'repair', 'checkpoint', 'guardian', 'self_update', 'immune', 'mission', 'surgery', 'refactor', 'evolution'], 'imports': ['agentic_core.L0_maintenance.scripts', 'structure_blueprint'], 'bases': ['CanonBaseAgent', 'AutonomousAgent', 'HealingEngine'], 'examples': ['AutonomousCheckpointManager', 'AutonomousStateGuardian', 'SelfUpdatingSafetyEngine', 'NeuralAutoImmuneAgent', 'SovereignHealingMission']}, 'logs': {'purpose': 'Structured diagnostic logs, healing operation records, mission transcripts, and maintenance audit trails', 'entity_types': ['Class', 'Function'], 'keywords': ['log', 'diagnostic', 'record', 'transcript', 'audit', 'maintenance_log', 'healing_trace', 'mission_log'], 'imports': ['agentic_core.L0_maintenance.logs', 'logging', 'json'], 'bases': ['DiagnosticLogger', 'MissionTranscript', 'MaintenanceAudit'], 'examples': ['HealingOperationLogger', 'AutonomousMissionLog', 'SovereignDiagnosticWriter', 'MaintenanceTrace']}, 'benchmarks': {'purpose': 'Performance benchmarking suites, timing profiles, resource usage metrics, and autonomous optimization baselines', 'entity_types': ['Class', 'Function'], 'keywords': ['benchmark', 'perf', 'timing', 'profile', 'metric', 'baseline', 'optimize', 'resource', 'efficiency'], 'imports': ['agentic_core.L0_maintenance.benchmarks', 'time', 'asyncio', 'psutil'], 'bases': ['BenchmarkSuite', 'PerformanceProfiler', 'ResourceMonitor'], 'examples': ['SovereignBenchmarkRunner', 'ReasoningSpeedTest', 'MemoryEfficiencyBenchmark', 'HealingCycleProfiler']}}, 'L1_cognition': {'thought_engine': {'purpose': 'Core reasoning primitives, thought nodes, chain-of-thought execution, internal monologue structures, and advanced deliberation patterns', 'entity_types': ['Class', 'Protocol'], 'keywords': ['thought', 'reason', 'node', 'chain', 'cot', 'tot', 'react', 'monologue', 'step', 'decompose', 'analyze', 'reflect', 'critique', 'socratic', 'deliberate', 'ponder', 'contemplate', 'self_reflect'], 'imports': ['agentic_core.L1_cognition.thought_engine', 'pydantic', 'typing'], 'bases': ['ThoughtNode', 'ReasoningStep', 'BaseThought', 'ChainOfThought', 'TreeOfThoughts', 'ReActStep', 'BaseReasoningEngine'], 'examples': ['ReasoningNode', 'CritiqueStep', 'ReflectionThought', 'ChainOfThoughtExecutor', 'SocraticReasoner', 'TreeOfThoughtsNode', 'ReActAgentStep']}, 'intent_analysis': {'purpose': 'User intent detection, goal extraction, multi-turn request classification, ambiguity resolution, and command parsing', 'entity_types': ['Class', 'Function'], 'keywords': ['intent', 'goal', 'objective', 'request', 'classify', 'detect', 'extract', 'parse', 'understand', 'ambiguity', 'user_goal', 'task_type', 'command', 'query_type', 'multi_turn', 'conversation'], 'imports': ['agentic_core.L1_cognition.intent_analysis', 'google.generativeai', 're', 'pydantic'], 'bases': ['IntentClassifier', 'GoalExtractor', 'RequestParser', 'AmbiguityResolver'], 'examples': ['IntentClassifier', 'GoalDecomposer', 'AmbiguityResolver', 'UserRequestParser', 'TaskTypeDetector', 'MultiTurnIntentTracker']}, 'planning': {'purpose': 'Mission decomposition, strategy formulation, step sequencing, dependency mapping, plan validation, and execution roadmap generation', 'entity_types': ['Class', 'Function'], 'keywords': ['plan', 'strategy', 'decompose', 'sequence', 'step', 'task', 'subtask', 'dependency', 'order', 'validate', 'breakdown', 'hierarchy', 'outline', 'roadmap', 'execute_order', 'priority', 'milestone'], 'imports': ['agentic_core.L1_cognition.planning', 'networkx', 'pydantic', 'typing'], 'bases': ['Planner', 'DecompositionEngine', 'PlanValidator', 'StrategyBuilder', 'BasePlanner', 'TaskGraph'], 'examples': ['MissionDecomposer', 'TaskSequencer', 'DependencyResolver', 'PlanValidator', 'StrategicPlanner', 'StepHierarchyBuilder', 'PriorityScheduler']}}, 'L2_execution': {'tool_registry': {'purpose': 'Registration and discovery of external tools, base tool definitions, and tool metadata management', 'entity_types': ['Class', 'Function'], 'keywords': ['tool', 'registry', 'register', 'discover', 'metadata', 'available_tools', 'toolset'], 'imports': ['agentic_core.L2_execution.tool_registry', 'pydantic', 'typing'], 'bases': ['BaseTool', 'ToolRegistry'], 'examples': ['ToolRegistry', 'register_tool', 'AvailableToolsList', 'ToolMetadata']}, 'action_handlers': {'purpose': 'Action dispatch logic, handler mapping, execution routing, and fallback strategies for tool calls', 'entity_types': ['Class', 'Function'], 'keywords': ['action', 'handler', 'execute', 'dispatch', 'route', 'fallback', 'perform', 'invoke', 'call_action'], 'imports': ['agentic_core.L2_execution.action_handlers'], 'bases': ['ActionHandler', 'BaseActionDispatcher'], 'examples': ['ActionDispatcher', 'HandlerMap', 'DefaultActionExecutor', 'ToolCallRouter', 'FallbackHandler']}, 'mcp': {'purpose': 'Multi-Component Protocol clients and tool implementations (figma, fetch, filesystem, semantic_cache, router, marketplace_filter)', 'entity_types': ['Class'], 'keywords': ['mcp', 'client', 'figma', 'fetch', 'filesystem', 'semantic_cache', 'router', 'marketplace', 'filter', 'protocol'], 'imports': ['agentic_core.L2_execution.mcp', 'requests', 'playwright', 'selenium', 'pinecone'], 'bases': ['BaseTool', 'MCPClientBase'], 'examples': ['FigmaClient', 'FetchClientSovereign', 'FilesystemMCPClient', 'SemanticCacheClient', 'MCPRouter', 'MarketplaceFilter']}}, 'L3_orchestration': {'workflow_engines': {'purpose': 'High-level agent orchestration, multi-agent workflow engines, task routing, mission lifecycle management, and coordination primitives', 'entity_types': ['Class'], 'keywords': ['orchestrator', 'coordinator', 'workflow', 'engine', 'manager', 'supervisor', 'crew', 'team', 'mission', 'lifecycle', 'route', 'dispatch', 'schedule'], 'imports': ['agentic_core.L3_orchestration.workflow_engines', 'langgraph', 'pydantic'], 'bases': ['CanonBaseAgent', 'WorkflowEngine', 'OrchestratorBase', 'MissionManager'], 'examples': ['SovereignOrchestrator', 'MultiAgentWorkflow', 'TaskRouter', 'MissionLifecycleManager', 'AgentSupervisor']}, 'fission_logic': {'purpose': 'Agent fission mechanics, dynamic sub-agent spawning, division of labor, and recursive self-delegation systems', 'entity_types': ['Class', 'Function'], 'keywords': ['fission', 'spawn', 'subagent', 'divide', 'delegate', 'recursive', 'split', 'branch', 'fork', 'proliferate'], 'imports': ['agentic_core.L3_orchestration.fission_logic'], 'bases': ['FissionEngine', 'SubAgentSpawner', 'CanonBaseAgent'], 'examples': ['fission_manager', 'DynamicSubAgentCreator', 'RecursiveDelegator', 'TaskFissionLogic']}, 'S3_vitality': {'purpose': 'System vitality monitoring, health checks, self-preservation protocols, anomaly detection, and resilience mechanisms', 'entity_types': ['Class', 'Function'], 'keywords': ['vitality', 'health', 'monitor', 'heartbeat', 'anomaly', 'resilience', 'self_preserve', 'watchdog', 'liveness', 'readiness'], 'imports': ['agentic_core.L3_orchestration.S3_vitality'], 'bases': ['VitalityMonitor', 'HealthChecker', 'CanonBaseAgent'], 'examples': ['VitalityGuardian', 'SystemHealthMonitor', 'AnomalyDetector', 'ResilienceEngine', 'WatchdogAgent']}, 'mcp': {'purpose': 'Orchestration-level Multi-Component Protocol components (router, marketplace_filter, coordination logic)', 'entity_types': ['Class'], 'keywords': ['mcp', 'router', 'marketplace', 'filter', 'orchestrate', 'coordinate', 'gateway', 'proxy'], 'imports': ['agentic_core.L3_orchestration.mcp'], 'bases': ['MCPRouterBase', 'MarketplaceFilter', 'CanonBaseAgent'], 'examples': ['MCPRouter', 'MarketplaceToolFilter', 'OrchestrationGateway', 'MCPCoordinator']}}, 'L4_state': {'validation_context': {'purpose': 'Runtime validation contexts, state integrity containers, and scoped validation environments', 'entity_types': ['Class'], 'keywords': ['validation', 'context', 'scope', 'integrity', 'state_check', 'validate_in_context'], 'imports': ['agentic_core.L4_state.validation_context', 'pydantic', 'typing'], 'bases': ['ValidationContext', 'BaseStateContext'], 'examples': ['SovereignValidationContext', 'MissionValidationScope', 'StateIntegrityContainer']}, 'ledger': {'purpose': 'Immutable audit ledgers, historical state records, event sourcing, and tamper-evident logs', 'entity_types': ['Class'], 'keywords': ['ledger', 'immutable', 'audit', 'trail', 'history', 'event_source', 'append_only', 'commit_log'], 'imports': ['agentic_core.L4_state.ledger'], 'bases': ['ImmutableLedger', 'AuditTrail', 'EventLedger'], 'examples': ['SovereignLedger', 'MissionHistoryLedger', 'StateCommitLog', 'TamperEvidentRecord']}, 'filesystem': {'purpose': 'Sovereign filesystem abstractions, MCP filesystem operations, and persistent file state management', 'entity_types': ['Class'], 'keywords': ['filesystem', 'mcp', 'file', 'directory', 'path', 'persistent', 'storage', 'disk'], 'imports': ['agentic_core.L4_state.filesystem', 'pathlib'], 'bases': ['FilesystemMCP', 'BaseFilesystemClient', 'BaseTool'], 'examples': ['SovereignFilesystemClient', 'PersistentStateStore', 'FileLedgerAdapter']}, 'memory': {'purpose': 'In-memory state stores, session management, ephemeral caches, and short-term memory systems', 'entity_types': ['Class'], 'keywords': ['memory', 'session', 'cache', 'ephemeral', 'short_term', 'in_memory', 'working_memory'], 'imports': ['agentic_core.L4_state.memory', 'redis', 'typing'], 'bases': ['MemoryStore', 'SessionManager', 'EphemeralCache'], 'examples': ['SovereignWorkingMemory', 'SessionState', 'ShortTermCache', 'InMemoryLedger']}}, 'config': {'blueprint_sovereign': {'purpose': 'Sovereign structure blueprints, constitution enforcement, and registry of registries', 'entity_types': ['Dict', 'Class'], 'keywords': ['blueprint', 'sovereign', 'constitution', 'registry', 'structure', 'map', 'ssot'], 'imports': ['agentic_core.config.blueprint_sovereign'], 'bases': ['BaseConfiguration', 'Constitution'], 'examples': ['StructureBlueprint', 'CanonRegistry', 'SovereignConstitution']}, 'environments': {'purpose': 'Environment-specific configuration loaders, .env parsers, and context switching', 'entity_types': ['Class', 'Function'], 'keywords': ['env', 'config', 'loader', 'dotenv', 'dev', 'prod', 'staging', 'variable'], 'imports': ['os', 'dotenv'], 'bases': ['ConfigLoader', 'EnvironmentContext'], 'examples': ['EnvLoader', 'ProductionConfig', 'DevContext', 'DotenvParser']}, 'feature_flags': {'purpose': 'Feature toggle management, rollout controls, and A/B testing switches', 'entity_types': ['Class'], 'keywords': ['flag', 'feature', 'toggle', 'rollout', 'switch', 'beta', 'enable', 'disable'], 'imports': ['agentic_core.config.feature_flags'], 'bases': ['FeatureToggle', 'FlagManager'], 'examples': ['LaunchDarklyAdapter', 'FeatureFlagStore', 'BetaRolloutSwitch']}, 'secrets_manager': {'purpose': 'Secure secret retrieval, vault integration, and credential rotation', 'entity_types': ['Class'], 'keywords': ['secret', 'vault', 'key', 'credential', 'token', 'password', 'encrypt', 'decrypt'], 'imports': ['agentic_core.config.secrets_manager'], 'bases': ['SecretsVault', 'CredentialProvider'], 'examples': ['VaultClient', 'AWSSystemManager', 'SecureTokenStore']}}, 'runtime': {'shared_runtime': {'purpose': 'Shared runtime environment setup, void compliance, and global initialization', 'entity_types': ['Class', 'Function'], 'keywords': ['runtime', 'shared', 'void', 'compliance', 'init', 'bootstrap', 'setup', 'global'], 'imports': ['agentic_core.runtime.shared_runtime'], 'bases': ['RuntimeContext'], 'examples': ['VoidComplianceCheck', 'RuntimeBootstrapper', 'GlobalInit']}, 'resource_management': {'purpose': 'Resource allocation, throttling quotas, thread pool management, and cleanup', 'entity_types': ['Class'], 'keywords': ['resource', 'throttle', 'quota', 'cleanup', 'pool', 'thread', 'limit', 'allocate'], 'imports': ['concurrent.futures'], 'bases': ['ResourceManager', 'QuotaEnforcer'], 'examples': ['ThreadPoolManager', 'MemoryQuotaGuard', 'ResourceCleaner']}}, 'observability': {'metrics': {'purpose': 'Metric collection, counters, gauges, and prometheus exports', 'entity_types': ['Class'], 'keywords': ['metric', 'counter', 'gauge', 'histogram', 'prometheus', 'stat'], 'imports': ['prometheus_client'], 'bases': ['MetricCollector'], 'examples': ['PerformanceMetrics', 'RequestCounter', 'SystemGauge']}, 'telemetry': {'purpose': 'Distributed telemetry, event emission, and structured observability events', 'entity_types': ['Class'], 'keywords': ['telemetry', 'event', 'emit', 'signal', 'observe'], 'imports': ['opentelemetry'], 'bases': ['TelemetryProvider'], 'examples': ['EventEmitter', 'TelemetrySignal', 'StructuredObserver']}, 'tracing': {'purpose': 'Span tracing, context propagation, and distributed trace ids', 'entity_types': ['Class'], 'keywords': ['trace', 'span', 'context', 'propagate', 'id', 'parent'], 'imports': ['opentelemetry.trace'], 'bases': ['TracerBase'], 'examples': ['SpanContext', 'DistributedTracer', 'ContextPropagator']}, 'compliance': {'purpose': 'Compliance reporting, canon drift detection logs, and policy violation records', 'entity_types': ['Class', 'Function'], 'keywords': ['compliance', 'drift', 'report', 'canon', 'violation', 'audit'], 'imports': [], 'bases': ['ComplianceReporter'], 'examples': ['DriftReportGenerator', 'CanonComplianceLog', 'ViolationTracker']}}, 'utils': {'core_extensions': {'purpose': 'Core Python extensions, polyfills, and monkey-patches', 'entity_types': ['Function', 'Class'], 'keywords': ['extension', 'polyfill', 'monkey', 'patch', 'enhance'], 'imports': [], 'bases': [], 'examples': ['StringExtensions', 'DictMergePolyfill', 'CoreMonkeyPatch']}, 'wrappers': {'purpose': 'Decorators, generic wrappers, and function proxies', 'entity_types': ['Function'], 'keywords': ['wrapper', 'decorator', 'retry', 'cache', 'proxy', 'intercept'], 'imports': ['functools'], 'bases': [], 'examples': ['retry_with_backoff', 'cached_property_wrapper', 'LogExecutionDecorator']}, 'general_helpers': {'purpose': 'Domain-agnostic helper functions and miscellaneous core utilities', 'entity_types': ['Function'], 'keywords': ['helper', 'util', 'misc', 'common', 'format'], 'imports': [], 'bases': [], 'examples': ['date_helper', 'string_formatter', 'generic_util']}, 'naming': {'purpose': 'Naming law enforcement logic, casing validators, and canon signal checks', 'entity_types': ['Class', 'Function'], 'keywords': ['naming', 'canon', 'signal', 'law', 'case', 'snake', 'camel'], 'imports': ['agentic_core.utils.naming', 're'], 'bases': ['NamingValidator'], 'examples': ['SnakeCaseValidator', 'CanonSignalChecker', 'NamingLawEnforcer']}}, 'patterns': {'agent_roles': {'purpose': 'Pre-defined agent personas, role templates, and behavioral archetypes', 'entity_types': ['Class', 'Dict'], 'keywords': ['role', 'persona', 'agent_type', 'archetype', 'behavior'], 'imports': [], 'bases': ['CanonBaseAgent'], 'examples': ['SocraticPersona', 'CriticRole', 'ArchitectArchetype']}, 'communication_flow': {'purpose': 'Inter-agent message passing patterns and handoff protocols', 'entity_types': ['Class'], 'keywords': ['communication', 'message', 'flow', 'protocol', 'handoff', 'channel'], 'imports': [], 'bases': ['CommunicationProtocol'], 'examples': ['MessageBusPattern', 'HandoffProtocol', 'ChannelPattern']}, 'interaction_patterns': {'purpose': 'Common human-agent and agent-tool interaction patterns (CLI, Chat, etc)', 'entity_types': ['Class'], 'keywords': ['interaction', 'pattern', 'ui', 'cli', 'chat', 'ux'], 'imports': [], 'bases': [], 'examples': ['CliInteractionPattern', 'ChatLoopPattern', 'ToolUsePattern']}, 'reasoning_patterns': {'purpose': 'Reusable reasoning strategies (CoT, ToT, ReAct) as abstract patterns', 'entity_types': ['Class'], 'keywords': ['reasoning', 'strategy', 'cot', 'tot', 'react', 'chain', 'tree'], 'imports': ['agentic_core.patterns.reasoning_patterns'], 'bases': ['BaseReasoningEngine'], 'examples': ['ChainOfThoughtPattern', 'TreeOfThoughtsStrategy', 'ReActLoopPattern']}}, 'knowledge': {'document_loaders': {'purpose': 'Document ingestion, parsing, and unstructured data loading utilities', 'entity_types': ['Class'], 'keywords': ['loader', 'ingest', 'parse', 'document', 'pdf', 'txt', 'html'], 'imports': ['unstructured', 'langchain'], 'bases': ['BaseLoader'], 'examples': ['PDFLoader', 'TextIngestor', 'HTMLParser']}, 'static_index': {'purpose': 'Hard-coded knowledge bases, static facts, and lookup tables', 'entity_types': ['Dict', 'Class'], 'keywords': ['static', 'index', 'facts', 'knowledge', 'lookup', 'table', 'constants'], 'imports': [], 'bases': [], 'examples': ['WorldFactsIndex', 'ConstantLookup', 'StaticKnowledgeBase']}, 'research_cache': {'purpose': 'Cached research results, external knowledge snapshots, and query history', 'entity_types': ['Class'], 'keywords': ['research', 'cache', 'snapshot', 'history', 'query', 'stored'], 'imports': [], 'bases': ['CacheStore'], 'examples': ['ResearchResultCache', 'KnowledgeSnapshot', 'QueryHistoryLog']}}, 'schemas': {'models': {'purpose': 'Pydantic data models, domain objects, and structured data contracts', 'entity_types': ['Class'], 'keywords': ['model', 'pydantic', 'dataclass', 'schema', 'dto', 'definition'], 'imports': ['pydantic'], 'bases': ['BaseModel']}, 'messages': {'purpose': 'API message formats, request/response schemas, and protocol buffers', 'entity_types': ['Class'], 'keywords': ['message', 'request', 'response', 'payload', 'packet'], 'imports': ['pydantic'], 'bases': ['BaseModel']}}, 'prompt_governance': {'templates': {'purpose': 'Reusable prompt fragments, system instructions, and jinja templates', 'entity_types': ['Class', 'str constant'], 'keywords': ['prompt', 'template', 'system', 'instruction', 'jinja', 'persona'], 'imports': ['jinja2'], 'bases': []}, 'rendering': {'purpose': 'Dynamic prompt assembly, variable substitution, and rendering logic', 'entity_types': ['Class', 'Function'], 'keywords': ['render', 'assemble', 'build', 'format', 'interpolate'], 'imports': ['jinja2'], 'bases': []}}, 'semantic_memory': {'embeddings': {'purpose': 'Embedding generation, caching, and dimension management', 'entity_types': ['Class', 'Function'], 'keywords': ['embedding', 'embed', 'vectorize', 'dimension', 'latent'], 'imports': ['google.generativeai'], 'bases': []}, 'retrieval': {'purpose': 'Semantic search, similarity scoring, and RAG retrieval', 'entity_types': ['Class', 'Function'], 'keywords': ['retriev', 'search', 'similarity', 'rag', 'query', 'lookup'], 'imports': ['pinecone'], 'bases': []}}, 'apps_rg': {'logic_nodes': {'purpose': 'Business logic nodes for resume extraction, parsing, and section formatting', 'entity_types': ['Class'], 'keywords': ['resume', 'cv', 'node', 'section', 'experience', 'education', 'skill', 'extract', 'format', 'parse'], 'imports': ['apps_rg.logic_nodes', 'pydantic'], 'bases': ['BaseNode', 'ResumeNode', 'ExtractionNode'], 'examples': ['ExperienceNode', 'SkillExtractNode', 'EducationFormatter', 'HeaderLogicNode']}, 'asset_library': {'purpose': 'Static assets, hardcoded strings, action verbs, and skill taxonomies for resumes', 'entity_types': ['Class', 'Dict'], 'keywords': ['asset', 'string', 'text', 'resource', 'copy', 'wording', 'verbs', 'skills', 'taxonomy'], 'imports': [], 'bases': ['BaseAsset'], 'examples': ['ResumeAssets', 'ActionVerbs', 'SkillTaxonomy', 'ResumeTemplateStrings']}, 'system_flow': {'purpose': 'Linear and branching pipelines for the resume generation lifecycle', 'entity_types': ['Class'], 'keywords': ['flow', 'pipeline', 'sequence', 'generate', 'create', 'process', 'workflow', 'lifecycle'], 'imports': ['apps_rg.system_flow'], 'bases': ['BaseFlow', 'ResumeGenerationFlow'], 'examples': ['GenerationFlow', 'ReviewPipeline', 'PdfGenerationWorkflow', 'ContentRefinementFlow']}, 'engines': {'purpose': 'Core rendering engines for document export (PDF, Docx, HTML)', 'entity_types': ['Class'], 'keywords': ['engine', 'render', 'export', 'pdf', 'docx', 'builder', 'latex', 'jinja'], 'imports': ['apps_rg.engines', 'jinja2'], 'bases': ['BaseEngine', 'DocumentBuilder'], 'examples': ['PdfEngine', 'DocxBuilder', 'HtmlRenderer', 'LatexCompiler']}, 'templates': {'purpose': 'Visual layouts, CSS/Style definitions, and structural blueprints for documents', 'entity_types': ['Class', 'Dict'], 'keywords': ['template', 'layout', 'style', 'theme', 'design', 'format', 'css', 'blueprint'], 'imports': [], 'bases': ['BaseTemplate', 'ResumeLayout'], 'examples': ['ModernTemplate', 'ClassicLayout', 'ExecutiveBlueprint', 'MinimalistStyle']}}, 'apps_lic': {'logic_nodes': {'purpose': 'Business logic nodes for profile analysis, connection requests, and message generation', 'entity_types': ['Class'], 'keywords': ['linkedin', 'lic', 'node', 'message', 'connect', 'invite', 'profile', 'scrutinize', 'analyze'], 'imports': ['apps_lic.logic_nodes'], 'bases': ['BaseNode', 'LicNode', 'MessagingNode'], 'examples': ['ConnectNode', 'MessageDraftNode', 'ProfileScrutinyNode', 'LeadValidationNode']}, 'asset_library': {'purpose': 'Outreach scripts, message templates, connection notes, and sequence assets', 'entity_types': ['Class', 'Dict'], 'keywords': ['asset', 'note', 'message', 'template', 'script', 'outreach', 'sequence', 'hook'], 'imports': [], 'bases': ['BaseAsset'], 'examples': ['ConnectionNotes', 'FollowUpScripts', 'OutreachTemplates', 'MessageHooks']}, 'system_flow': {'purpose': 'Outreach campaign management, multi-step drip sequences, and cadence logic', 'entity_types': ['Class'], 'keywords': ['flow', 'campaign', 'sequence', 'cadence', 'outreach', 'drip', 'funnel', 'pipeline'], 'imports': ['apps_lic.system_flow'], 'bases': ['BaseFlow', 'OutreachCampaign'], 'examples': ['OutreachCampaign', 'DailyFlow', 'DripSequenceFlow', 'FollowUpCadence']}, 'engines': {'purpose': 'Automated browser drivers for LinkedIn navigation and interaction', 'entity_types': ['Class'], 'keywords': ['engine', 'driver', 'navigate', 'automate', 'browser', 'playwright', 'selenium', 'scrape'], 'imports': ['apps_lic.engines', 'playwright', 'selenium'], 'bases': ['BaseEngine', 'BrowserDriver'], 'examples': ['NavigationEngine', 'BrowserDriver', 'ScrapingEngine', 'InteractionDriver']}, 'templates': {'purpose': 'Message formatting schemas and campaign structural blueprints', 'entity_types': ['Class'], 'keywords': ['template', 'structure', 'format', 'blueprint', 'schema'], 'imports': [], 'bases': ['BaseTemplate', 'LicTemplate'], 'examples': ['CampaignTemplate', 'MessageFormat', 'OutreachBlueprint']}}, 'apps_shared': {'base_definitions': {'purpose': 'Abstract base classes, core interfaces, and type contracts shared across all application domains', 'entity_types': ['Class', 'Protocol', 'TypeAlias'], 'keywords': ['base', 'definition', 'type', 'shared', 'interface', 'abstract', 'contract', 'blueprint', 'abc'], 'imports': ['abc', 'typing'], 'bases': ['ABC', 'Protocol'], 'examples': ['BaseNode', 'BaseFlow', 'BaseEngine', 'BaseTemplate', 'BaseAsset']}, 'common_utils': {'purpose': 'Shared application-level utility functions for data manipulation, formatting, and common logic', 'entity_types': ['Function', 'Class'], 'keywords': ['util', 'common', 'shared', 'helper', 'date', 'string', 'collection', 'formatter', 'converter'], 'imports': ['datetime', 're', 'json'], 'bases': [], 'examples': ['date_utils', 'string_helpers', 'collection_transformers', 'CurrencyFormatter']}, 'core_components': {'purpose': 'Reusable architectural widgets and modular components used across multiple app flows', 'entity_types': ['Class'], 'keywords': ['component', 'module', 'widget', 'part', 'element', 'plugin', 'extension'], 'imports': [], 'bases': ['BaseComponent'], 'examples': ['LoggerComponent', 'ConfigLoader', 'NotificationWidget', 'AppPluginBase']}, 'base_agents': {'purpose': 'Shared application-level agent templates and worker base classes', 'entity_types': ['Class'], 'keywords': ['agent', 'base_agent', 'worker', 'bot', 'task_executor', 'app_worker'], 'imports': ['agentic_core.L3_orchestration.workflow_engines'], 'bases': ['CanonBaseAgent', 'AppBaseAgent'], 'examples': ['AppBaseAgent', 'TaskWorker', 'AsyncAppWorker', 'StatefulAppAgent']}, 'models': {'purpose': 'Shared Pydantic data models, Data Transfer Objects (DTOs), and domain-agnostic schemas', 'entity_types': ['Class'], 'keywords': ['model', 'dto', 'data', 'struct', 'object', 'payload', 'contract', 'pydantic'], 'imports': ['pydantic'], 'bases': ['BaseModel'], 'examples': ['UserProfile', 'TaskResult', 'CommonMetadata', 'SharedDataPacket']}}}
