"""
Naming Law Healer Agent - File Identity Standardizer
Renames forbidden or low-signal files to comply with naming laws.
This agent prevents circular drift by ensuring all files have high-signal names.
"""
import json
import re
from pathlib import Path
from typing import Dict, List
from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_SIGNALS, FORBIDDEN_PATTERNS

class naming_law_healer_agent:
    """
    L1 Cognition: High-Signal Naming Law Healer — Key 49 Sovereign Enforcement
    The "Naming Surgeon" that standardizes file identities by renaming
    forbidden patterns or low-signal files to comply with naming laws.
    """
    SYSTEM_PROMPT: Any = '\nYou are the NamingLawHealerAgent — the final arbiter of signal purity (Key 49).\nYour mandate is absolute: Every file and class name must conform exactly to the eternal canon.\n\n=== CANONICAL NAMING LAWS (ZERO TOLERANCE) ===\n\n1. **File Names**:\n   - lowercase snake_case ONLY.\n   - Mandatory role suffixes:\n     - Agents: *_agent.py | Engines: *_engine.py | Managers: *_manager.py\n     - Validators: *_validator.py | Guardrails: *_guardrail.py\n     - Models/Enums: *_models.py / *_enums.py | Tools: *_tool.py\n   - Forbidden: utils.py, helper.py, misc.py, base.py, temp.py. \n   - Naming must reflect primary responsibility with high semantic signal.\n\n2. **Class Names**:\n   - PascalCase ONLY.\n   - Must explicitly match the file role (e.g., NamingHealerAgent).\n\n=== HEALING PROTOCOL ===\n1. Diagnose violations.\n2. Propose exact new filename (preserve path).\n3. Generate full import reconciliation plan for all impacted files.\n4. Output JSON ONLY.\n\n{\n  "current_path": "<full_path>",\n  "new_filename": "<new_basename>",\n  "reason": "<justification>",\n  "renamed": true,\n  "import_fixes": [{"file": "<path>", "old_import": "...", "new_import": "..."}]\n}\n\n=== CONSTRAINTS ===\n- No folder moves. No overwrites. No broken imports.\n- If target exists, return "renamed": false with conflict reason.\n\nEliminate noise. Amplify signal.\nCurrent date: December 24, 2025\n'

    def __init__(self, project_root: Path, ctx):
        self.root = project_root
        self.ctx = ctx
        self.healed_count = 0
        self.healed_files = []
        self.reasoning_steps = []
        self.scratchpad = ''

    async def execute(self, file_path: str=None) -> Any:
        """
        Execute the naming law healing pass.
        Can operate in batch mode (all files) or per-file mode with cognitive reasoning.
        """
        if file_path:
            return await self._execute_per_file(file_path)
        print(f'\n   [*] NamingLawHealerAgent: Scanning for naming violations...')
        self.healed_count = 0
        self.healed_files = []
        for py_file in self.root.rglob('*.py'):
            if py_file.name == '__init__.py' or self._is_protected_file(py_file):
                continue
            new_name: Any = self._determine_new_name(py_file)
            if new_name and new_name != py_file.name:
                new_path: Any = py_file.parent / new_name
                if new_path.exists():
                    print(f'   [!] Skipping {py_file.name}: target {new_name} already exists')
                    continue
                try:
                    print(f'   [HEALING] NamingLawHealer: Renaming {py_file.name} -> {new_name}')
                    py_file.rename(new_path)
                    self.healed_count += 1
                    self.healed_files.append({'old': str(py_file.relative_to(self.root)), 'new': str(new_path.relative_to(self.root))})
                    self.ctx.report('NamingLawHealer', 1, True, f'Renamed {py_file.name}')
                except Exception as e:
                    print(f'   [!] Failed to rename {py_file.name}: {e}')
        if self.healed_count > 0:
            print(f'   [✓] NamingLawHealerAgent: Standardized {self.healed_count} file identities.')
            print(f'      [WARNING] Manual import updates may be required for renamed files.')
        else:
            print(f'   [✓] NamingLawHealerAgent: All files comply with naming laws.')

    async def _execute_per_file(self, file_path: str) -> Dict:
        """Per-file execution with sovereign mutation and physical transformation."""
        response = await self.ctx.engine.resilient_mutation(prompt=f'{self.SYSTEM_PROMPT}\n\nTarget: {file_path}', response_format={'type': 'json_object'})
        result = json.loads(response)
        if result.get('renamed'):
            new_p = Path(file_path).parent / result['new_filename']
            if not new_p.exists():
                Path(file_path).rename(new_p)
                for fix in result.get('import_fixes', []):
                    importer = self.root / fix['file']
                    if importer.exists():
                        content = importer.read_text()
                        importer.write_text(content.replace(fix['old_import'], fix['new_import']))
                return {'status': 'HEALED', 'path': str(new_p)}
        return result

    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected from renaming."""
        if file_path.parent == self.root:
            protected = {'canon_validator_agentic_v2.py', 'pyproject.toml', 'README.md'}
            return file_path.name in protected
        rel_path = file_path.relative_to(self.root)
        parts = rel_path.parts
        if 'config' in parts or 'test' in parts[0].lower():
            return True
        return False

    def _determine_new_name(self, file_path: Path) -> str:
        """
        Determine if a file needs a new name based on naming laws.
        Returns the new name if needed, None if current name is compliant.
        """
        stem = file_path.stem.lower()
        current_name = file_path.name
        is_forbidden = any((re.match(p, current_name) for p in FORBIDDEN_PATTERNS))
        is_low_signal = not any((sig in stem for sig in CANON_SIGNALS))
        if is_forbidden or is_low_signal:
            if is_forbidden:
                if stem.endswith('_agent'):
                    new_name = f'sovereign_{current_name}'
                else:
                    new_name = f'sovereign_{stem}_agent.py'
            elif stem.endswith('_agent'):
                new_name = f'{stem}_core.py'
            else:
                new_name = f'{stem}_agent.py'
            return new_name
        return None

    def _think(self, thought: str) -> None:
        """Sovereign thought recording with size-limit shielding"""
        if len(thought) > 1000:
            thought = thought[:997] + '...'
        self.reasoning_steps.append(thought)
        self.scratchpad += f'- {thought}\n'

    def _detect_low_signal(self, code: str, current_name: str) -> List[str]:
        """Detect low-signal patterns in file name."""
        violations = []
        stem = current_name.lower()
        if any((re.match(p, current_name) for p in FORBIDDEN_PATTERNS)):
            violations.append('forbidden_pattern')
        if not any((sig in stem for sig in CANON_SIGNALS)):
            violations.append('low_signal_name')
        return violations

    def _generate_suggestions(self, current_name: str, code: str) -> List[str]:
        """Generate high-signal name suggestions based on code content."""
        suggestions = []
        stem = current_name.lower()
        class_matches = re.findall('class\\s+(\\w+)', code)
        for cls in class_matches:
            suggestions.append(f'{cls.lower()}')
        if not stem.endswith('_agent'):
            suggestions.append(f'{stem}_agent')
        suggestions.append(f'{stem}_core')
        return list(set(suggestions))

    def _rank_suggestions(self, suggestions: List[str], code: str) -> str:
        """Rank suggestions by signal strength."""
        if not suggestions:
            return None
        scores = {}
        for sug in suggestions:
            score = 0
            score += sum((1 for sig in CANON_SIGNALS if sig in sug.lower()))
            score -= len(sug) / 100
            scores[sug] = score
        return max(scores, key=scores.get) if scores else None

    def _apply_rename(self, code: str, old_name: str, new_name: str) -> str:
        """Apply rename to code (update class names if needed)."""
        return code

    def get_summary(self) -> Dict:
        """Return a summary of the healing pass."""
        return {'agent': 'NamingLawHealerAgent', 'healed_count': self.healed_count, 'healed_files': self.healed_files, 'canon_signals': list(CANON_SIGNALS), 'forbidden_patterns': list(FORBIDDEN_PATTERNS)}
