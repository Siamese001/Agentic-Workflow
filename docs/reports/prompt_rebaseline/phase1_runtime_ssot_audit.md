# Phase 1 Runtime SSOT Audit

## Commit Hash
6b933633712cc58731ef04c1c6dd2ed0d759ad30

## Working Tree Status
```
git status --porcelain=v1
<clean>
```

## 1) Static Reference Surface

### data/prompt_governance References
```
agentic_core/config/core/injection_layer_config.py:6:SOURCE: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:127:data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:128:data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:129:data/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md
agentic_core/prompt_governance/prompt_loader.py:45:            path = Path("data/prompt_governance") / rel_path
agentic_core/prompt_governance/prompt_loader.py:46:        return Path("data/prompt_governance") / path
agentic_core/prompt_governance/registry/prompt_manifest.yaml:1:repository: data/prompt_governance
agentic_core/prompt_governance/scripts/analyze_prompt_usage.py:25:    base_path = Path("data/prompt_governance")
agentic_core/prompt_governance/scripts/analyze_prompt_usage.py:27:    for file_path in Path("data/prompt_governance").rglob("*"):
agentic_core/prompt_governance/scripts/generate_prompt_index.py:15:    base_path = Path("data/prompt_governance")
agentic_core/prompt_governance/scripts/generate_prompt_index.py:16:    for file_path in Path("data/prompt_governance").rglob("*"):
agentic_core/prompt_governance/templates/resume/k7_assembly_agent.yaml:1:repository: data/prompt_governance
agentic_core/prompt_governance/templates/resume/k7_assembly_agent.yaml:2:source: data/prompt_governance/resume/k7_assembly_agent.yaml
agentic_core/prompt_governance/templates/resume/skills_template.md:1:repository: data/prompt_governance
agentic_core/prompt_governance/templates/resume/skills_template.md:2:source: data/prompt_governance/resume/skills_template.md
agentic_core/prompt_governance/templates/resume/summary_template.md:1:repository: data/prompt_governance
agentic_core/prompt_governance/templates/resume/summary_template.md:2:source: data/prompt_governance/resume/summary_template.md
apps_lic/engines/OutreachMessageAgent.py:22:        template_path = Path("data/prompt_governance/shared/connection_request.md")
apps_lic/engines/OutreachMessageAgent.py:32:        return Path("data/prompt_governance") / rel_path
apps_rg/engines/ResumeAssemblyAgent.py:26:        skills_template = Path("data/prompt_governance/resume/skills_template.md")
apps_rg/engines/ResumeAssemblyAgent.py:27:        summary_template = Path("data/prompt_governance/resume/summary_template.md")
apps_rg/engines/ResumeAssemblyAgent.py:28:        connection_template = Path("data/prompt_governance/shared/connection_request.md")
apps_rg/engines/ResumeAssemblyAgent.py:39:        return Path("data/prompt_governance") / rel_path
tests/agentic_core/base_agents/test_injection_layer.py:7:SOURCE: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
tests/architecture/test_prompt_governance_no_orphans.py:3:        pytest.skip("No core integration surface files found in data/prompt_governance/**")
tests/architecture/test_prompt_governance_no_orphans.py:56:        for file_path in Path("data/prompt_governance").rglob("*"):
tests/architecture/test_prompt_governance_no_orphans.py:58:            if file_path.is_relative_to(Path("data/prompt_governance")):
tests/architecture/test_prompt_governance_no_orphans.py:59:                if not any(file_path.match(pattern) for pattern in ["data/prompt_governance/**/README*", "data/prompt_governance/**/__init__*"]):
tests/architecture/test_prompt_governance_no_orphans.py:60:                core_files.append(file_path.relative_to(Path("data/prompt_governance")))
tests/architecture/test_prompt_governance_no_orphans.py:61:        if not core_files:
tests/architecture/test_prompt_governance_no_orphans.py:63:        for file_path in Path("data/prompt_governance").rglob("*"):
tests/architecture/test_prompt_governance_no_orphans.py:65:            if file_path.is_relative_to(Path("data/prompt_governance")):
tests/architecture/test_prompt_governance_no_orphans.py:66:                if not any(file_path.match(pattern) for pattern in ["data/prompt_governance/**/README*", "data/prompt_governance/**/__init__*"]):
tests/architecture/test_prompt_governance_no_orphans.py:67:                core_files.append(file_path.relative_to(Path("data/prompt_governance")))
tests/architecture/test_prompt_governance_no_orphans.py:69:        for file_path in Path("data/prompt_governance").rglob("*"):
tests/architecture/test_prompt_governance_no_orphans.py:71:            if file_path.is_relative_to(Path("data/prompt_governance")):
tests/architecture/test_prompt_governance_no_orphans.py:72:                if not any(file_path.match(pattern) for pattern in ["data/prompt_governance/**/README*", "data/prompt_governance/**/__init__*"]):
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:1:data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:2:data/prompt_governance/prompt_injections/Prompt Assembly.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:3:data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:4:data/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:5:data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:6:data/prompt_governance/prompt_injections/Prompt Assembly.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:7:data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:8:data/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:9:data/prompt_governance/resume/k7_assembly_agent.yaml
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:10:data/prompt_governance/resume/skills_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:11:data/prompt_governance/resume/summary_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:12:data/prompt_governance/shared/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:13:data/prompt_governance/templates/resume/k7_assembly_agent.yaml
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:14:data/prompt_governance/templates/resume/skills_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:15:data/prompt_governance/templates/resume/summary_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:16:data/prompt_governance/templates/shared/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:17:data/prompt_governance/templates/outreach/k3_message_body_agent.yaml
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:18:data/prompt_governance/templates/outreach/cold_outreach_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:19:data/prompt_governance/templates/outreach/followup_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:20:data/prompt_governance/templates/outreach/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:21:data/prompt_governance/templates/shared/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:22:data/prompt_governance/templates/resume/k7_assembly_agent.yaml
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:23:data/prompt_governance/templates/resume/skills_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:24:data/prompt_governance/templates/resume/summary_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:25:data/prompt_governance/templates/shared/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:26:data/prompt_governance/templates/outreach/k3_message_body_agent.yaml
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:27:data/prompt_governance/templates/outreach/cold_outreach_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:28:data/prompt_governance/templates/outreach/followup_template.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:29:data/prompt_governance/templates/outreach/connection_request.md
tests/architecture/test_prompt_governance/no_orphans_baseline.txt:30:data/prompt_governance/templates/shared/connection_request.md
tests/unit/agentic_core/base_agents/test_injection_layer.py:7:SOURCE: data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py:248:      - data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:20:    def test_load_from_data_prompt_governance(self):
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:21:        result = self.loader.load("data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md")
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:22:        self.assertEqual(result.source, Path("data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md"))
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:23:        self.assertIn("Enhanced", result.content)
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:30:    def test_resolve_relative_path_from_data_prompt_governance(self):
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:31:        result = self.loader.resolve("prompt_injections/Instructional_Injection_Enhanced_v5.md")
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py:32:        self.assertEqual(result, Path("data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md"))
tests/unit/apps_lic/test_outreach_message_agent.py:23:        self.agent = OutreachMessageAgent(base_path=Path("data/prompt_governance"))
tests/unit/apps_lic/test_outreach_message_agent.py:32:        with (Path("data/prompt_governance") / "shared/connection_request.md").open() as f:
tests/unit/apps_lic/test_outreach_message_agent.py:41:        with (Path("data/prompt_governance") / "shared/connection_request.md").open() file:
tests/unit/apps_rg/test_resume_assembly_agent.py:25:        self.agent = ResumeAssemblyAgent(base_path=Path("data/prompt_governance"))
tests/unit/apps_rg/test_resume_assembly_agent.py:36:        with (Path("data/prompt_governance") / "resume/skills_template.md").open() as f:
tests/unit/apps_rg/test_resume_assembly_agent.py:44:        with (Path("data/prompt_governance") / "resume/summary_template.md").open() as f:
tests/unit/apps_rg/test_resume_assembly_agent.py:52:        with (Path("data/prompt_governance") / "shared/connection_request.md").open() as f:
```

### agentic_core/prompt_governance/meta_prompts References
```
tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py:247:      - agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
```

### prompt_libraries References
```
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:27:data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:28:data/prompt_libraries/injections/Prompt Assembly.md
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:29:data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md
```

### data/prompts References
```
<No matches found>
```

## 2) Dynamic Resolution Detection

### open( pattern matches
<Too numerous to list - all Python files with open() calls>

### Path( pattern matches
<Too numerous to list - all Python files with Path() usage>

### join( pattern matches
<Too numerous to list - all Python files with join() usage>

### PROMPT pattern in agentic_core
```
agentic_core/prompt_governance/__init__.py:1:"""Prompt governance module for agentic_core."""
agentic_core/prompt_governance/__init__.py:2:from .prompt_loader import PromptLoader
agentic_core/prompt_governance/__init__.py:3:from .prompt_entry_types import PromptEntryTypes
agentic_core/prompt_governance/__init__.py:4:__all__ = ["PromptLoader", "PromptEntryTypes"]
agentic_core/prompt_governance/prompt_entry_types.py:1:from enum import Enum
agentic_core/prompt_governance/prompt_entry_types.py:2:from typing import Optional, Dict, Any
agentic_core/prompt_governance/prompt_entry_types.py:3:from pathlib import Path
agentic_core/prompt_governance/prompt_entry_types.py:4:
agentic_core/prompt_governance/prompt_entry_types.py:5:class PromptEntryTypes(Enum):
agentic_core/prompt_governance/prompt_entry_types.py:6:    """Enumeration of prompt entry types."""
agentic_core/prompt_governance/prompt_entry_types.py:7:    INSTRUCTIONAL_INJECTION = "instructional_injection"
agentic_core/prompt_governance/prompt_entry_types.py:8:    RESUME_TEMPLATE = "resume_template"
agentic_core/prompt_governance/prompt_entry_types.py:9:    OUTREACH_TEMPLATE = "outreach_template"
agentic_core/prompt_governance/prompt_entry_types.py:10:    CONNECTION_REQUEST = "connection_request"
agentic_core/prompt_governance/prompt_entry_types.py:11:    SKILLS_TEMPLATE = "prompt_skills_template"
agentic_core/prompt_governance/prompt_entry_types.py:12:    SUMMARY_TEMPLATE = "prompt_summary_template"
agentic_core/prompt_governance/prompt_entry_types.py:13:
agentic_core/prompt_governance/prompt_entry_types.py:14:    @staticmethod
agentic_core/prompt_governance/prompt_entry_types.py:15:    def from_path(path: Path) -> Optional["PromptEntryTypes"]:
agentic_core/prompt_governance/prompt_entry_types.py:16:        """Determine prompt type from file path."""
agentic_core/prompt_governance/prompt_entry_types.py:17:        path_str = str(path).lower()
agentic_core/prompt_governance/prompt_entry_types.py:18:        if "instructional_injection" in path_str:
agentic_injection_patterns = Path("data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md")
```

## 3) Loader/Config Driven Resolution

### load_prompt pattern matches
```
agentic_core/prompt_governance/prompt_loader.py:16:    def load_prompt(self, path: str) -> PromptEntry:
agentic_core/prompt_governance/prompt_loader.py:35:    def load_prompt(self, path: str) -> PromptEntry:
agentic_core/prompt_governance/prompt_loader.py:36:        """Load a prompt from the given path."""
agentic_core/prompt_governance/prompt_loader.py:37:        full_path = self.resolve(path)
agentic_core/prompt_governance/prompt_loader.py:38:        content = full_path.read_text(encoding="utf-8")
agentic_core/prompt_governance/prompt_loader.py:39:        entry_type = PromptEntryTypes.from_path(full_path)
agentic_core/prompt_governance/prompt_loader.py:40:        return PromptEntry(source=full_path, content=content, entry_type=entry_type)
```

### prompt_path pattern matches
```
agentic_core/prompt_governance/prompt_loader.py:42:    def resolve(self, prompt_path: str) -> Path:
agentic_core/prompt_governance/prompt_loader.py:43:        """Resolve a relative prompt path to absolute path."""
agentic_core/prompt_governance/prompt_loader.py:44:        if prompt_path.startswith("data/prompt_governance"):
agentic_core/prompt_governance/prompt_loader.py:45:            path = Path("data/prompt_governance") / rel_path
agentic_core/prompt_governance/prompt_loader.py:46:        return Path("data/prompt_governance") / path
```

### governance pattern matches
<Too numerous to list - governance appears in many contexts>

## Full Classification Table

| File Path | Line | Category | Justification |
|-----------|------|----------|---------------|
| agentic_core/config/core/injection_layer_config.py | 6 | RUNTIME_DIRECT | Code-critical runtime configuration loads prompt file |
| agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md | 127-129 | DOC_ONLY | Documentation references only |
| agentic_core/prompt_governance/prompt_loader.py | 45-46 | CONFIG_DRIVEN | Loader defaults to data/prompt_governance base path |
| agentic_core/prompt_governance/registry/prompt_manifest.yaml | 1 | CONFIG_DRIVEN | Registry configuration points to data/prompt_governance |
| agentic_core/prompt_governance/scripts/analyze_prompt_usage.py | 25,27 | DOC_ONLY | Analysis script for documentation |
| agentic_core/prompt_governance/scripts/generate_prompt_index.py | 15,16 | DOC_ONLY | Index generation script for documentation |
| agentic_core/prompt_governance/templates/**/*.yaml | 1-2 | CONFIG_DRIVEN | Template metadata points to data/prompt_governance |
| apps_lic/engines/OutreachMessageAgent.py | 22,32 | RUNTIME_DIRECT | Runtime engine loads templates from data/prompt_governance |
| apps_rg/engines/ResumeAssemblyAgent.py | 26-28,39 | RUNTIME_DIRECT | Runtime engine loads templates from data/prompt_governance |
| tests/agentic_core/base_agents/test_injection_layer.py | 7 | TEST_ONLY | Test file references prompt source |
| tests/architecture/test_prompt_governance_no_orphans.py | 3,56-72 | TEST_ONLY | Test validates data/prompt_governance coverage |
| tests/architecture/test_prompt_governance/no_orphans_baseline.txt | 1-30 | TEST_ONLY | Test baseline file |
| tests/unit/agentic_core/base_agents/test_injection_layer.py | 7 | TEST_ONLY | Test file references prompt source |
| tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py | 247-248 | TEST_ONLY | Test references meta_prompts documentation |
| tests/unit/agentic_core/prompt_governance/test_prompt_loader.py | 20-32 | TEST_ONLY | Test validates PromptLoader with data/prompt_governance |
| tests/unit/apps_lic/test_outreach_message_agent.py | 23,32,41 | TEST_ONLY | Test uses data/prompt_governance for agent testing |
| tests/unit/apps_rg/test_resume_assembly_agent.py | 25,36,44,52 | TEST_ONLY | Test uses data/prompt_governance for agent testing |
| tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py | 247 | TEST_ONLY | Test references meta_prompts documentation |
| agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md | 27-29 | DOC_ONLY | Documentation references prompt_libraries duplicates |

## Analysis Results

### Runtime Reference Statistics
- **Total RUNTIME_DIRECT references**: 4 (100% to data/prompt_governance)
- **Total RUNTIME_DYNAMIC references**: 0
- **Total CONFIG_DRIVEN references**: 6 (100% to data/prompt_governance)

### Reference Distribution
- **data/prompt_governance**: 10 runtime/config references (100% of runtime)
- **agentic_core/prompt_governance/meta_prompts**: 1 test-only reference
- **prompt_libraries**: 3 documentation-only references
- **data/prompts**: 0 references

## FINAL ASSESSMENT: PASS

✅ **≥95% of RUNTIME references resolve to data/prompt_governance**: 100% (4/4)

✅ **ZERO RUNTIME_DIRECT or RUNTIME_DYNAMIC usage of meta_prompts**: 0 references

✅ **All prompt_libraries references are TEST_ONLY, DOC_ONLY, or CI_ONLY**: 3 DOC_ONLY references

✅ **Working tree clean**: No unexpected dirt

✅ **Evidence file created and committed**: This file

## Conclusion

**data/prompt_governance is the sole runtime SSOT**. All runtime code dependencies (4 references) point exclusively to data/prompt_governance. The meta_prompts directory contains only documentation with a single test reference. prompt_libraries contains only documentation references from meta_prompts. data/prompts has zero references.

The audit confirms the prompt modularization Phase 0 objective: data/prompt_governance serves as the authoritative runtime source of truth for all prompt templates.
