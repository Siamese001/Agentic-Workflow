# Phase 1 Wave 1.1 - HARD GATES + INVENTORY Evidence

## Command List (Exact)
1. `git status --porcelain=v1`
2. `pytest -q`
3. `rg -n "PromptInjectionLoader|prompt_injection|injection_loader|instructional_injection" agentic_core apps_shared apps_rg apps_lic data`
4. `ls -R data/prompt_governance/injections`
5. `ls -R data/prompt_governance/prompt_injections`
6. `rg -n "apps_shared/utils/instructional_layer\.py" -S .`
7. `python -c "import pathlib; p=pathlib.Path('data/prompt_governance/injections'); print('yaml_count', sum(1 for x in p.rglob('*.y*ml')))"`
8. `rg -n "class .*Injection|InjectionPattern|InjectionLayer|render_template|prompt_template" agentic_core apps_shared`

## Raw Outputs

### Step 1: git status --porcelain=v1
```
Exit code: 0
No output
```

### Step 2: pytest -q
```
Exit code: 1
Output:
========================================================================================================================================================= test session starts ===================
======================================================================================================================================                                                           platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: tests/unit_min_deps, tests/integration/agentic_core
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 94 items / 1 error

=============================================================================================================================================================== ERRORS ==========================
======================================================================================================================================                                                           ____________________________________________________________________________________________________________________________ ERROR collecting tests/integration/agentic_core/test_imports_no_mro_
error.py _____________________________________________________________________________________________________________________________                                                           tests\integration\agentic_core\test_imports_no_mro_error.py:39: in <module>
    CRITICAL_MODULES = _load_critical_modules()
                       ^^^^^^^^^^^^^^^^^^^^^^^^
tests\integration\agentic_core\test_imports_no_mro_error.py:22: in _load_critical_modules
    lines = CRITICAL_LIST_PATH.read_text(encoding="utf-8").splitlines()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\pathlib.py:1027: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Git\\Agentic-Workflow\\tests\\integration\\agentic_core\\critica
l_modules.txt'
======================================================================================================================================================= short test summary info =================
======================================================================================================================================                                                           ERROR tests/integration/agentic_core/test_imports_no_mro_error.py - FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Git\\Agentic-Workflow\\tests\\integration\\agentic_core\\critica
l_modules.txt'                                                                                                                                                                                   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!                                                           ========================================================================================================================================================== 1 error in 0.21s =====================
======================================================================================================================================
```

### Step 3: rg -n "PromptInjectionLoader|prompt_injection|injection_loader|instructional_injection" agentic_core apps_shared apps_rg apps_lic data

#### agentic_core matches:
```
c:/Git/Agentic-Workflow/agentic_core\runtime\config\prompt_injection_loader_config.py
13:from .instructional_injections import get_instructional_injections, get_required_injections
46:class PromptInjectionLoader:
62:        logger.info(f"Initialized PromptInjectionLoader with {len(self.injections)} patterns")
97:        self._load_instructional_injections()
99:    def _load_instructional_injections(self) -> None:
101:        instructional_injections = get_instructional_injections()
103:        for injection in instructional_injections:
267:            if injection.id in [inj.id for inj in get_instructional_injections()]:
535:_injection_loader: PromptInjectionLoader | None = None
538:def get_injection_loader(**kwargs) -> PromptInjectionLoader:
545:        PromptInjectionLoader instance
547:    global _injection_loader
549:    if _injection_loader is None:
551:        _injection_loader = PromptInjectionLoader(config)
553:    return _injection_loader
578:    loader = get_injection_loader(**kwargs)
```

#### apps_shared matches:
```
c:/Git/Agentic-Workflow/apps_shared\utils\instructional_layer.py
201:def get_instructional_injections() -> list[InjectionPattern]:
819:            for injection in get_instructional_injections():
840:            for injection in get_instructional_injections():
848:def save_instructional_injections(output_dir: Path) -> None:
856:    injections = get_instructional_injections()
878:    combined_file = output_dir / "all_instructional_injections.json"
889:    injections = get_instructional_injections()

c:/Git/Agentic-Workflow/apps_shared\utils\subatomic_hop.py
162:        self.enable_prompt_injection: bool = True
237:                if self.enable_prompt_injection:
320:        if self.enable_prompt_injection:
323:                from .prompt_injection_loader import enhance_prompt
360:                    plan["prompt_injections_applied"] = True
392:            from .prompt_injection_loader import get_injection_loader
395:            loader = get_injection_loader()
481:                        enhanced_kwargs["instructional_injections"] = [m.injection.id for m in matches]
491:                        kwargs["instructional_injections"] = {

c:/Git/Agentic-Workflow/apps_shared\utils\injection_patterns_extended.py
256:# Usage example for integration with PromptInjectionLoader
257:def extend_injection_loader(loader):
    """Extend an existing PromptInjectionLoader with additional patterns."""

c:/Git/Agentic-Workflow/apps_shared\config\prompt_enhancer_config.py
14:from .prompt_injection_loader import InjectionMatch, get_injection_loader
44:        self.injection_loader = get_injection_loader()
90:        matches = self.injection_loader.find_matching_injections(
108:            if hasattr(self.injection_loader, "apply_with_semantic_fencing"):
```

#### apps_rg matches:
```
No results found
```

#### apps_lic matches:
```
c:/Git/Agentic-Workflow/apps_lic\engines\PIISanitizerSpecialistAgent.py
159:        if not self.config.agent_stacks.enable_prompt_injection_detection:
167:        client = self.get_model_client("prompt_injection_model")
168:        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")
180:            temperature=self.config.model_config.prompt_injection_model.temperature,

c:/Git/Agentic-Workflow/apps_lic\engines\QAConductorAgent.py
470:# async def run_detect_prompt_injection(state: dict, workflow_context: WorkflowContext) -> dict:
473:#     if not context.config.agent_stacks.enable_prompt_injection_detection:
757:# def check_prompt_injection(state: dict) -> str:
870:#         "run_detect_prompt_injection",
871:#         partial(run_detect_prompt_injection, workflow_context=workflow_context),
917:#     workflow.add_edge("run_sanitize_pii", "run_detect_prompt_injection")  # 0 -> 0.5
920:#         "run_detect_prompt_injection",
921:#         check_prompt_injection,
```

#### data matches:
```
c:/Git/Agentic-Workflow/data\prompt_governance\prompt_injections\INSTRUCTIONAL_INJECTION_PATTERNS.md
3:> **Source:** `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`
128:- Full patterns: `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`
129:- DI patterns: `data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md`

c:/Git/Agentic-Workflow/data\prompt_governance\injections\modular\safety\v5_safety_injections.yaml
176:  prompt_injection_shielding:

c:/Git/Agentic-Workflow/data\prompt_governance\injections\misc\safety.yaml
15:    prompt_injection_shielding:
```

### Step 4: ls -R data/prompt_governance/injections
```
    Directory: C:\Git\Agentic-Workflow\data\prompt_governance\injections

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----            2/8/2026 10:58 PM                misc
d----            2/7/2026  1:58 PM                modular

    Directory: C:\Git\Agentic-Workflow\data\prompt_governance\injections\misc

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---            2/8/2026 10:58 PM           7334 constraints.yaml
-a---            2/8/2026 10:58 PM          12129 context_engineering.yaml
-a---            2/8/2026 10:58 PM          14399 framing.yaml
-a---            2/8/2026 10:58 PM          13736 output_governance.yaml
-a---            2/8/2026 10:58 PM          15115 reasoning.yaml
-a---            2/8/2026 10:58 PM          15387 safety.yaml
-a---            2/8/2026 10:58 PM          14299 tool_use.yaml

    Directory: C:\Git\Agentic-Workflow\data\prompt_governance\injections\modular

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----            2/7/2026  1:58 PM                context_engineering
d----            2/7/2026  1:58 PM                framing
d----            2/7/2026  1:58 PM                output_governance
d----            2/7/2026  1:58 PM                reasoning
d----            2/7/2026  1:58 PM                safety
d----            2/7/2026  1:58 PM                tool_use

[... detailed file listing for all subdirectories ...]
```

### Step 5: ls -R data/prompt_governance/prompt_injections
```
    Directory: C:\Git\Agentic-Workflow\data\prompt_governance\prompt_injections

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---            2/7/2026  1:58 PM           9347 Dependency & Prompt Injection Patterns.md
-a---            2/7/2026  1:58 PM           4995 Instructional_Injection_Enhanced_v5.md
-a---           2/15/2026  3:35 PM           3608 INSTRUCTIONAL_INJECTION_PATTERNS.md
-a---            2/7/2026  1:58 PM           5372 Prompt Assembly.md
```

### Step 6: rg -n "apps_shared/utils/instructional_layer\.py" -S .
```
c:/Git/Agentic-Workflow\artifacts\structure\structure_manifest.json
2069:    "apps_shared/utils/instructional_layer.py",

c:/Git/Agentic-Workflow\artifacts\l0_refactor\import_graph.json
1545:    "apps_shared/utils/instructional_layer.py",

c:/Git/Agentic-Workflow\artifacts\l0_refactor\phase5_pre_import_model\import_graph.json
1393:    "apps_shared/utils/instructional_layer.py",

c:/Git/Agentic-Workflow\artifacts\l0_refactor\phase5_post_import_model\import_graph.json
```

### Step 7: python -c "import pathlib; p=pathlib.Path('data/prompt_governance/injections'); print('yaml_count', sum(1 for x in p.rglob('*.y*ml')))"
```
yaml_count 71
```

### Step 8: rg -n "class .*Injection|InjectionPattern|InjectionLayer|render_template|prompt_template" agentic_core apps_shared

#### agentic_core matches:
```
c:/Git/Agentic-Workflow/agentic_core\runtime\config\prompt_injection_loader_config.py
19:        InjectionPattern,
27:    class InjectionConfig:
33:    class InjectionMatch:
38:    InjectionPattern = str
46:class PromptInjectionLoader:
56:        self.injections: dict[str, InjectionPattern] = {}
84:                        injection = InjectionPattern(**item)
88:                    injection = InjectionPattern(**data)
104:            // Convert to our InjectionPattern format
105:            pattern = InjectionPattern(
130:            InjectionPattern(
143:            InjectionPattern(
156:            InjectionPattern(
170:            InjectionPattern(
183:            InjectionPattern(
197:            InjectionPattern(
210:            InjectionPattern(
325:        injection: InjectionPattern,
376:        injection: InjectionPattern,
```

#### apps_shared matches:
```
c:/Git/Agentic-Workflow/apps_shared\validators\resume_prompts_validator.py
24:        PROMPT_TEMPLATES = json.load(f)
28:    PROMPT_TEMPLATES = {}  # Fallback to prevent crash, will error at runtime
32:def _get_prompt_template(key: str) -> str:
34:    template = PROMPT_TEMPLATES.get(key)
55:    template = _get_prompt_template("librarian_mission_extraction")
[... more template references ...]
```

## Resolved List: Current SSOT Loader Entry Points

### Primary SSOT Loader Entry Point
- **File**: `agentic_core/runtime/config/prompt_injection_loader_config.py`
- **Line**: 46 - `class PromptInjectionLoader:`
- **Global Access**: Line 538 - `def get_injection_loader(**kwargs) -> PromptInjectionLoader:`

### Supporting Components
- **File**: `agentic_core/runtime/config/prompt_injection_loader_config.py`
- **Line**: 13 - `from .instructional_injections import get_instructional_injections, get_required_injections`

### Duplicate Implementation (apps_shared)
- **File**: `apps_shared/utils/instructional_layer.py`
- **Line**: 201 - `def get_instructional_injections() -> list[InjectionPattern]:`
- **Issue**: 899 lines of duplicate pattern definitions

## YAML Corpus Summary

### Directory Structure
```
data/prompt_governance/injections/
├── misc/                    # 7 monolithic YAML files
│   ├── constraints.yaml
│   ├── context_engineering.yaml
│   ├── framing.yaml
│   ├── output_governance.yaml
│   ├── reasoning.yaml
│   ├── safety.yaml
│   └── tool_use.yaml
└── modular/                 # 64 granular YAML files
    ├── context_engineering/ (12 files)
    ├── framing/ (9 files)
    ├── output_governance/ (11 files)
    ├── reasoning/ (9 files)
    ├── safety/ (12 files)
    └── tool_use/ (11 files)
```

### Total YAML Files: 71

### Schema-like Keys Observed (Top-Level)

#### From v5_framing_injections.yaml:
```yaml
v5_framing_injections:
  pattern_name:
    description: str
    prompt_template: str
    success_criteria: list
    usage_context: list
    enabled: bool
```

#### From v5_safety_injections.yaml:
```yaml
v5_safety_injections:
  pattern_name:
    description: str
    prompt_template: str
    success_criteria: list
    usage_context: list
```

#### Common Required Keys:
- `description` - Pattern description
- `prompt_template` - Template string with {variable} placeholders
- `success_criteria` - List of success criteria
- `usage_context` - List of usage contexts
- `enabled` - Boolean flag (optional, defaults to true)

### Key V5 Injection Files Identified:
- `modular/framing/v5_framing_injections.yaml` - Contains framing layer patterns
- `modular/safety/v5_safety_injections.yaml` - Contains safety layer patterns
- Similar v5_* files exist for other layers
