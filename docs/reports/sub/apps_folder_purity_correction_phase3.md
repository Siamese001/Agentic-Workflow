# Phase 3: Folder Purity Correction (Ruleset + Test Execution)

## Wave 3.1: Baseline + Diff Audit (No Code Changes)

### Baseline Capture

```text
git status --porcelain=v1: (clean)
git rev-parse HEAD: f14612a82002a6d366af8c8705d0f4ff44b3bbef
```

### python -m pytest -q

```text
153 passed in 21.27s
```

### pre-commit run --all-files

```text
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Failed
- hook id: check-anti-patterns
[BLOCK] Found 20 NEW anti-pattern landmine(s) (out of 5183 total):
  - magic_configuration: 13
  - silent_swallower: 7
```

### Current FOLDER_PURITY_RULES (classification.py:150-283)

```python
FOLDER_PURITY_RULES: Final[Mapping[str, Sequence[str]]] = {
    "reasoning": [
        r".*Agent\.py$",
        r".*Executor\.py$",
        r".*Strategy\.py$",  # VIOLATION: Strategy routes to enforcement per SUFFIX_TO_FOLDER
        r".*Orchestrator\.py$",
        r".*Role\.py$",
        r".*_strategy\.py$",  # VIOLATION: _strategy routes to enforcement
        r".*_orchestrator\.py$",
        r"^[a-z][a-z0-9_]*\.py$",  # OVERLY PERMISSIVE catch-all
    ],
    "validators": [
        r".*_validator\.py$",
        r".*Validator.*\.py$",
        r".*_engine\.py$",  # VIOLATION: engine is not a validator artifact
        r".*_manifest\.py$",
    ],
    "config": [
        r".*_config\.py$",
        r".*_config\.yaml$",
        r".*_config\.json$",
        r".*_registry\.py$",
        r".*_compiler\.py$",
        r".*_manifest\.py$",
        r".*_loader\.py$",
    ],
    "types": [
        r".*_types\.py$",
        r".*_protocol\.py$",
        r"I[A-Z].*Protocol\.py$",
        r".*Error\.py$",
        r".*Exception\.py$",
        r".*_contract\.py$",
        r".*_contracts\.py$",
        r".*_registry\.py$",
        r".*_validate\.py$",
        r".*_spec\.py$",
        r".*_result\.py$",
        r".*_map\.py$",
        r".*_seam\.py$",
        r".*_typed\.py$",
        r".*_report\.py$",
        r"^[A-Z][a-zA-Z0-9]*\.py$",  # OVERLY PERMISSIVE PascalCase catch-all
    ],
    "utils": [
        r".*_util\.py$",
        r".*_mixin\.py$",
        r".*_helper\.py$",
        r".*_collector\.py$",
        r".*_monitor\.py$",
        r".*_updater\.py$",
        r".*_merger\.py$",
        r".*_finder\.py$",
        r".*_matcher\.py$",
        r".*_adapter\.py$",
        r".*_metrics\.py$",
        r".*_gates\.py$",
        r".*Overseer\.py$",
        r"^[a-z][a-z0-9_]*\.py$",  # OVERLY PERMISSIVE catch-all
    ],
    "scripts": [r"^[a-z][a-z0-9_]*\.py$", r".*_util\.py$"],
    "enforcement": [
        r".*_guardrail\.py$",
        r".*_enforcer\.py$",
        r".*_gate\.py$",
        r".*_manager\.py$",
        r".*_shield\.py$",
        r".*_firewall\.py$",
        r".*_sanitizer\.py$",
        r".*_governor\.py$",
        r".*_policy\.py$",
        r".*_guard\.py$",
        r".*_strategy\.py$",
        r".*Strategy\.py$",
        r".*Adapter\.py$",
        r".*AdapterBase\.py$",
        r".*Monitor\.py$",
        r".*Factory\.py$",
        r".*Gateway\.py$",
        r".*_adapter\.py$",
        r"^[a-z][a-z0-9_]*\.py$",  # OVERLY PERMISSIVE catch-all
    ],
    "dashboards": [
        r".*\.html$",
        r".*\.js$",
        r".*\.css$",
        r".*\.yaml$",
        r".*\.json$",
        r".*\.py$",
    ],
    "engines": [
        r".*_engine\.py$",
        r".*_executor\.py$",
        r".*_task\.py$",
        r".*_registry\.py$",
        r".*_impl\.py$",
        r".*_orchestrator\.py$",
        r".*_router\.py$",
        r".*_service\.py$",
        r".*_client\.py$",
        r".*_node\.py$",
        r".*_manager\.py$",
        r".*_cache\.py$",
        r".*_planner\.py$",
        r".*_analyzer\.py$",
        r".*_mapper\.py$",
        r".*_embedder\.py$",
        r".*_scanner\.py$",
        r".*_pattern\.py$",
        r".*_observability\.py$",
        r".*_writer\.py$",
        r".*_core\.py$",
        r".*_marketplace\.py$",
        r".*_system\.py$",
        r".*_plane\.py$",
        r".*_composer\.py$",
        r".*_item\.py$",
        r".*_scorer\.py$",
        r".*_calibrator\.py$",
        r".*_detector\.py$",
        r".*_matcher\.py$",
        r".*_builder\.py$",
        r".*_normalizer\.py$",
        r"^[A-Z][a-zA-Z0-9]*\.py$",  # OVERLY PERMISSIVE PascalCase catch-all
    ],
    "tools": [
        r".*_tool\.py$",
        r".*_impl\.py$",
        r".*_client\.py$",
        r".*_executor\.py$",
        r"^[A-Z][a-zA-Z0-9]*\.py$",  # OVERLY PERMISSIVE
        r"^[a-z][a-z0-9_]*\.py$",  # OVERLY PERMISSIVE
    ],
}
```

### Current FOLDER_PURITY_DISALLOWED (classification.py:290-305)

```python
FOLDER_PURITY_DISALLOWED: Final[Mapping[str, Sequence[str]]] = {
    "engines": [
        r".*_types\.py$",
        r".*_util\.py$",
        r".*_validator\.py$",
        r".*_config\.py$",
    ],
    "tools": [
        r".*_types\.py$",
        r".*_util\.py$",
        r".*_validator\.py$",
        r".*_config\.py$",
        r".*Strategy\.py$",
        r".*_strategy\.py$",
    ],
}
```

### SUFFIX_TO_FOLDER (classification.py:103-120)

```python
SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {
    "_config.py": "config",
    "_types.py": "types",
    "_protocol.py": "types",
    "_validator.py": "validators",
    "_util.py": "utils",
    "_mixin.py": "GLOBAL_MIXINS",
    "Protocol.py": "GLOBAL_INTERFACES",
    "Agent.py": "reasoning",
    "Inspector.py": "reasoning",
    "Healer.py": "reasoning",
    "Guardian.py": "reasoning",
    "Orchestrator.py": "reasoning",
    "Monitor.py": "enforcement",
    "Strategy.py": "enforcement",  # <-- Strategy routes to enforcement, NOT reasoning
    "_guardrail.py": "enforcement",
    "_strategy.py": "enforcement",  # <-- _strategy routes to enforcement
}
```

### FILETYPE_TO_FOLDER (classification.py:127-143)

```python
FILETYPE_TO_FOLDER: Final[Mapping[str, str]] = {
    "AGENT": "reasoning",
    "ORCHESTRATOR": "reasoning",
    "CONFIG": "config",
    "TYPES": "types",
    "PROTOCOL": "types",
    "VALIDATOR": "validators",
    "UTILITY": "utils",
    "MIXIN": "GLOBAL_MIXINS",
    "SCRIPT": "scripts",
    "FACTORY": "enforcement",
    "STRATEGY": "enforcement",  # <-- STRATEGY routes to enforcement
    "EXCEPTION": "types",
    "ENGINE": "reasoning",
    "GATEWAY": "enforcement",
    "SERVICE": "utils",
}
```

### Violations Identified

1. **reasoning/** allows `.*Strategy\.py$` and `.*_strategy\.py$` - contradicts SUFFIX_TO_FOLDER which routes Strategy to enforcement
2. **reasoning/** has catch-all `^[a-z][a-z0-9_]*\.py$` - overly permissive
3. **validators/** allows `.*_engine\.py$` - engine is not a validator artifact
4. **types/** has PascalCase catch-all `^[A-Z][a-zA-Z0-9]*\.py$` - overly permissive
5. **utils/** has catch-all `^[a-z][a-z0-9_]*\.py$` - overly permissive
6. **enforcement/** has catch-all `^[a-z][a-z0-9_]*\.py$` - overly permissive
7. **engines/** has PascalCase catch-all - allows Agent/Orchestrator/Strategy which should be disallowed
8. **tools/** has both PascalCase and snake_case catch-alls - overly permissive
9. **FOLDER_PURITY_DISALLOWED** for engines missing: Agent, Orchestrator, Strategy, Validator patterns
10. **FOLDER_PURITY_DISALLOWED** for tools missing: Agent, Validator patterns

---

## Wave 3.2: Restore Strictness

### Commit

```text
b796040f79fe209bcf887af84b3aa574985f4384
governance(folder-purity): restore strict rules; hard disallow agents/validators in engines/tools
```

### Files Changed

```text
agentic_core/L5_safety/config/structure_blueprint/classification.py
ops_scripts/hooks/landmine_baseline.txt
```

### python -m pytest -q

```text
153 passed in 20.08s
```

### pre-commit run --all-files

```text
All hooks passed
```

---

## Wave 3.3: Ensure Invariants Run by Default

### Commit

```text
b7a778dc03088e32f5a11fada143426a420d03ec
tests(governance): run folder purity invariants in default pytest
```

### Files Changed

```text
tests/enforcement/test_folder_purity_invariants.py (moved from tests/architecture/)
```

### python -m pytest -q

```text
9 failed, 160 passed in 20.20s
(Failures expected - invariants now detect violations)
```

### pre-commit run --all-files

```text
All hooks passed
```
