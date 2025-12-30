import re
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from agentic_core.prompt_governance.version_registry.prompt_registry import get_prompt_registry

class PromptValidationAgent:
    """
    Validates prompt governance integrity across the entire repository.

    Responsibilities (per Master Constitution):
    - Block hardcoded secrets or provider-specific keys in templates.
    - Enforce provider-neutrality (no 'GPT', 'Claude' references).
    - Verify every physical template has a 'v1+' entry in the Registry.
    - Detect and flag 'Shadow Prompts' (inline strings > 50 lines).
    """
    FORBIDDEN_PATTERNS: Any = [re.compile('sk-[a-zA-Z0-9]{48}'), re.compile('anthropic', re.IGNORECASE), re.compile('claude', re.IGNORECASE), re.compile('gpt-[34]', re.IGNORECASE), re.compile('openai', re.IGNORECASE)]
    INLINE_THRESHOLD: Any = 50

    async def execute(self, ctx: Any) -> None:
        """
        Phase 2 batch validation of prompt governance.
        """
        if not hasattr(ctx, 'project_root') or not hasattr(ctx, 'python_files'):
            return
        project_root: Any = Path(ctx.project_root)
        registry: Any = get_prompt_registry()
        violations: List[str] = []
        print('\n[*] PROMPT GOVERNANCE VALIDATION: Auditing templates and shadow prompts...')
        templates_dir: Any = project_root / 'agentic_core' / 'prompt_governance' / 'templates'
        meta_dir: Any = project_root / 'agentic_core' / 'prompt_governance' / 'meta_prompts'
        search_paths: Any = []
        if templates_dir.exists():
            search_paths.append(templates_dir)
        if meta_dir.exists():
            search_paths.append(meta_dir)
        for base_path in search_paths:
            for template_path in base_path.rglob('*.jinja'):
                rel_path: Any = template_path.relative_to(project_root)
                try:
                    content: Any = template_path.read_text(encoding='utf-8')
                except Exception:
                    continue
                for pattern in self.FORBIDDEN_PATTERNS:
                    if pattern.search(content):
                        violations.append(f"Neutrality/Secret Violation: {rel_path} contains forbidden pattern '{pattern.pattern}'")
                template_name: Any = template_path.name
                if registry.get_active_version(template_name) is None:
                    violations.append(f'Ghost Template: {rel_path} exists on disk but is not registered in version_registry')
        for file_str in ctx.python_files:
            file_path: Any = Path(file_str)
            if 'prompt_governance' in file_path.parts:
                continue
            try:
                content: Any = file_path.read_text(encoding='utf-8')
                lines: Any = content.splitlines()
                in_string: Any = False
                current_string_lines: Any = 0
                start_line: Any = 0
                for i, line in enumerate(lines):
                    if '"""' in line or "'''" in line:
                        if not in_string:
                            in_string: Any = True
                            start_line: Any = i + 1
                            current_string_lines: Any = 1
                        else:
                            if current_string_lines > self.INLINE_THRESHOLD:
                                violations.append(f'Shadow Prompt: {file_path.name}:{start_line} contains an inline string of {current_string_lines} lines. Refactor to templates/.')
                            in_string: Any = False
                    elif in_string:
                        current_string_lines += 1
            except Exception:
                continue
        if violations:
            print(f'   [!] {len(violations)} prompt governance violation(s) detected')
            for v in violations[:10]:
                print(f'       - {v}')
            if len(violations) > 10:
                print(f'       ... and {len(violations) - 10} more')
            ctx.report(self.__class__.__name__, 1, False, f'{len(violations)} prompt violations')
        else:
            print('   [OK] Prompt governance compliant — templates registered and shadow prompts absent.')
            ctx.report(self.__class__.__name__, 1, True, 'Prompt governance compliant')

def get_prompt_validation_agent() -> Any:
    """Brief description of functionality and purpose."""
    return PromptValidationAgent()
