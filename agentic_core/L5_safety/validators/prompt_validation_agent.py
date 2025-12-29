# [CANON KEY 1] PromptValidationAgent - Batch Validator (Read-Only Safety Check)
# Territory: agentic_core/L5_safety/validators
# Purpose: Sovereign validation of all prompt templates and code-level usage
# Logic: Enforces registration, secrets-blocking, and template-migration-laws

import re
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

    FORBIDDEN_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{48}"),  # Standard OpenAI-style keys
        re.compile(r"anthropic", re.IGNORECASE),
        re.compile(r"claude", re.IGNORECASE),
        re.compile(r"gpt-[34]", re.IGNORECASE),
        re.compile(r"openai", re.IGNORECASE),
    ]

    INLINE_THRESHOLD = 50  # Hard limit for shadow prompts in .py files

    async def execute(self, ctx: Any) -> None:
        """
        Phase 2 batch validation of prompt governance.
        """
        if not hasattr(ctx, "project_root") or not hasattr(ctx, "python_files"):
            # Safety check: ensure mission context is fully formed
            return

        project_root = Path(ctx.project_root)
        registry = get_prompt_registry()
        violations: List[str] = []

        print("\n[*] PROMPT GOVERNANCE VALIDATION: Auditing templates and shadow prompts...")

        # --- SUB-TASK 1: TEMPLATE AUDIT ---
        # Scans the prompt_governance zones exclusively
        templates_dir = project_root / "agentic_core" / "prompt_governance" / "templates"
        meta_dir = project_root / "agentic_core" / "prompt_governance" / "meta_prompts"

        search_paths = []
        if templates_dir.exists(): search_paths.append(templates_dir)
        if meta_dir.exists(): search_paths.append(meta_dir)

        for base_path in search_paths:
            for template_path in base_path.rglob("*.jinja"):
                rel_path = template_path.relative_to(project_root)
                try:
                    content = template_path.read_text(encoding="utf-8")
                except Exception:
                    continue

                # Check for Provider Leaks (Neutrality Violation)
                for pattern in self.FORBIDDEN_PATTERNS:
                    if pattern.search(content):
                        violations.append(f"Neutrality/Secret Violation: {rel_path} contains forbidden pattern '{pattern.pattern}'")

                # Check for Ghost Templates (Registry Violation)
                # template_name should match the key used in registration
                template_name = template_path.name
                if registry.get_active_version(template_name) is None:
                    violations.append(f"Ghost Template: {rel_path} exists on disk but is not registered in version_registry")

        # --- SUB-TASK 2: SHADOW PROMPT DETECTION ---
        # Scans the rest of the codebase for prompt-bloat
        for file_str in ctx.python_files:
            file_path = Path(file_str)
            if "prompt_governance" in file_path.parts:
                continue  # Skip the oracle territory

            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                
                in_string = False
                current_string_lines = 0
                start_line = 0

                for i, line in enumerate(lines):
                    # Heuristic for triple-quoted prompt detection
                    if '"""' in line or "'''" in line:
                        if not in_string:
                            in_string = True
                            start_line = i + 1
                            current_string_lines = 1
                        else:
                            if current_string_lines > self.INLINE_THRESHOLD:
                                violations.append(f"Shadow Prompt: {file_path.name}:{start_line} contains an inline string of {current_string_lines} lines. Refactor to templates/.")
                            in_string = False
                    elif in_string:
                        current_string_lines += 1
            except Exception:
                continue

        # --- SUB-TASK 3: REPORTING ---
        if violations:
            print(f"   [!] {len(violations)} prompt governance violation(s) detected")
            for v in violations[:10]:
                print(f"       - {v}")
            if len(violations) > 10:
                print(f"       ... and {len(violations)-10} more")
            ctx.report(self.__class__.__name__, 1, False, f"{len(violations)} prompt violations")
        else:
            print("   [OK] Prompt governance compliant — templates registered and shadow prompts absent.")
            ctx.report(self.__class__.__name__, 1, True, "Prompt governance compliant")

def get_prompt_validation_agent():
    return PromptValidationAgent()
